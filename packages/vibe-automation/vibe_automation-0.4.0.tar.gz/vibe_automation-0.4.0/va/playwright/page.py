import logging
import asyncio
import atexit
from typing import Any, Dict, Optional

from playwright.sync_api import Locator
from stagehand import StagehandPage
from typing import Callable
from .locator import PromptBasedLocator
from .step import print_pending_modifications, AsyncStepContextManager, execute_step
from ..agent.agent import Agent

log = logging.getLogger("va.playwright")


# Register the cleanup function to run at exit
atexit.register(print_pending_modifications)


class Page:
    def __init__(self, page: StagehandPage):
        self._stagehand_page = page
        self._login_handler = None
        self._agent = Agent()
        # Track any background login tasks (only for fallback case)
        self._current_login_task = None

    def get_by_prompt(
        self,
        prompt: str,
    ) -> PromptBasedLocator:
        """
        Returns a PromptBasedLocator that can be used with or without fallback locators

        Parameters:
        -----------
        prompt (str): The natural language description of the element to locate.
        timeout (int) (optional): Timeout value in seconds for the connection with backend API service.
        wait_for_network_idle (bool) (optional): Whether to wait for network reaching full idle state before querying the page. If set to `False`, this method will only check for whether page has emitted [`load` event](https://developer.mozilla.org/en-US/docs/Web/API/Window/load_event).
        include_hidden (bool) (optional): Whether to include hidden elements on the page. Defaults to `True`.
        mode (ResponseMode) (optional): The response mode. Can be either `standard` or `fast`. Defaults to `fast`.
        experimental_query_elements_enabled (bool) (optional): Whether to use the experimental implementation of the query elements feature. Defaults to `False`.

        Returns:
        --------
        PromptBasedLocator: A locator that uses prompt-based element finding
        """
        return PromptBasedLocator(self, prompt)

    async def get_locator_by_prompt(
        self,
        prompt: str,
    ) -> Locator | None:
        """
        Internal method to get element by prompt - used by PromptBasedLocator

        Returns:
        --------
        Playwright [Locator](https://playwright.dev/python/docs/api/class-locator) | None: The found element or `None` if no matching elements were found.
        """

        results = await self._stagehand_page.observe(prompt)

        if not results:
            return None

        selector = results[0].selector
        return self._stagehand_page.locator(selector)

    async def _check_login_and_handle(self, login_handler):
        """Check if login is required and handle it"""
        try:
            # Use extract() to get a text response
            result = await self._stagehand_page.extract(
                "Is login required on this page? Answer with exactly 'yes' or 'no' (lowercase, no additional text)."
            )
            answer = result.extraction.lower()
            if answer == "yes":
                log.info("Login required detected, calling handler")
                if login_handler:
                    log.info("Calling login handler")
                    # handle sync and async login handlers
                    if asyncio.iscoroutinefunction(login_handler):
                        await login_handler()
                    else:
                        login_handler()
                    log.info("Login handler completed")
                else:
                    log.warning("Login required but no handler available")
            else:
                log.info("No login required")

        except Exception as e:
            log.error(f"Error in login check: {e}")
            raise Exception(f"Login check failed: {e}") from e

    def step(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> AsyncStepContextManager:
        """
        Execute a natural language command by generating and running Python code.

        This method returns a context manager that can be used with 'async with'.
        The LLM action generation is only triggered if the with block is empty (contains only pass).

        Parameters:
        -----------
        command (str): Natural language description of the action to perform
        context (Dict[str, Any], optional): Context variables available to the generated script
        max_retries (int): Maximum number of retry attempts. Defaults to 3.

        Returns:
        --------
        AsyncStepContextManager: Context manager for the step execution
        """
        if context is None:
            context = {}
        return AsyncStepContextManager(self, command, context, max_retries, self._agent)

    def _check_login_and_handle_on_page_load(self, *args, **kwargs):
        """Run the login handler if registered as a background task to block pending actions"""
        if self._login_handler:
            log.info("Page load detected, running login handler")
            self._current_login_task = asyncio.create_task(
                self._check_login_and_handle(self._login_handler)
            )
            self._current_login_task.add_done_callback(
                lambda t: setattr(self, "_current_login_task", None)
            )
        else:
            log.info("Page load detected but no login handler registered")

    async def _execute_step(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Internal method to execute a natural language command.
        Now delegates to the pure function in step.py.
        """
        return await execute_step(
            command=command,
            context=context,
            max_retries=max_retries,
            page=self._stagehand_page,
            agent=self._agent,
        )

    async def _wait_for_login_task(self):
        """Wait for any background login task to complete"""
        if self._current_login_task:
            await self._current_login_task
            log.info("Background login task completed")

    def __getattr__(self, name):
        """Forward attribute lookups to the underlying Stagehand page."""
        attr = getattr(self._stagehand_page, name)
        # TODO: this is a hack to wait for login task to complete before executing the method, this will cause a deadlock if the method has any other page methods. Since HITL won't call any page methods, this is fine for now. We will need to find a better way to handle this.
        if asyncio.iscoroutinefunction(attr):
            # create async wrapper that waits for login task
            async def async_wrapper(*args, **kwargs):
                await self._wait_for_login_task()
                return await attr(*args, **kwargs)

            return async_wrapper
        else:
            # create sync wrapper that waits for login task
            def sync_wrapper(*args, **kwargs):
                if self._current_login_task:
                    try:
                        asyncio.get_running_loop()
                        # In async context, proceed without waiting
                        log.warning(
                            "Sync method called while in async context with pending login task - proceeding without waiting"
                        )
                    except RuntimeError:
                        # No event loop running, we can create one
                        asyncio.run(self._wait_for_login_task())
                return attr(*args, **kwargs)

            return sync_wrapper

    def on(self, event: str, handler: Callable[[str], None]):
        """
        Register event handler for page. If the event is "login_required", we will register a handler that checks if login is required on page loads and calls the login handler if it is. If a new handler is registered for "login_required" when there is already a handler, the new handler will replace the existing one.

        Parameters:
        -----------
        event (str): The event to listen for
        handler (Callable[[str], None]): The handler function to call when the event occurs

        """
        if event == "login_required":
            # Only add page load listener if we don't have a handler yet
            if self._login_handler is None:
                self._stagehand_page.on(
                    "load", self._check_login_and_handle_on_page_load
                )
            # if handler is not the same as the existing handler, replace it
            if self._login_handler and handler != self._login_handler:
                log.info("Replacing existing login handler")
            self._login_handler = handler
        else:
            self._stagehand_page.on(event, handler)

    def remove_listener(self, event: str, handler: Callable[[str], None] | None = None):
        """
        Remove event handler for page. If the event is "login_required", we will remove the listener that checks if login is required on page loads.

        Parameters:
        -----------
        event (str): The event to remove listener for
        handler (Callable[[str], None] | None): The handler function to remove.
        """
        if event == "login_required":
            self._stagehand_page.remove_listener(
                "load", self._check_login_and_handle_on_page_load
            )
            self._login_handler = None
            log.info("Login handler removed")
        else:
            self._stagehand_page.remove_listener(event, handler)
