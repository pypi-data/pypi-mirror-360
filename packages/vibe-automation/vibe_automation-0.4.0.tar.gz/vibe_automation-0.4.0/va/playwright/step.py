import json
import logging
import difflib
from typing import Any, Dict, Optional

from stagehand import StagehandPage
from stagehand.a11y.utils import get_accessibility_tree

from va.codegen import inspect_with_block_from_frame, mutate_with_block_from_frame
from ..agent.agent import Agent, create_user_message

log = logging.getLogger("va.playwright")

# Global registry for pending file modifications
_pending_file_modifications = {}


def print_pending_modifications():
    """Generate and print diffs for pending file modifications instead of writing to disk."""
    for filename, new_lines in _pending_file_modifications.items():
        try:
            # Read the current file content
            with open(filename, "r") as f:
                original_content = f.read()

            # Convert new_lines to a single string if it's a list
            if isinstance(new_lines, list):
                new_content = "".join(new_lines)
            else:
                new_content = new_lines

            # Split into lines for diff comparison
            original_lines = original_content.splitlines(keepends=True)
            new_lines_list = new_content.splitlines(keepends=True)

            # Generate diff
            diff = difflib.unified_diff(
                original_lines,
                new_lines_list,
                fromfile=f"{filename} (original)",
                tofile=f"{filename} (modified)",
                lineterm="",
            )

            diff_lines = list(diff)

            if diff_lines:
                print(f"\n{'=' * 60}")
                print(f"DIFF for {filename}")
                print("=" * 60)
                # Print each diff line, stripping any trailing newlines to avoid double spacing
                for line in diff_lines:
                    print(line.rstrip())
                print("=" * 60)
                log.info(f"Generated diff for {filename}")
            else:
                log.info(f"No changes detected for {filename}")

        except Exception as e:
            log.error(f"Failed to generate diff for {filename}: {e}")

    _pending_file_modifications.clear()


def build_step_script_prompt(
    command: str,
    context: Dict[str, Any],
    accessibility_tree: Optional[str] = None,
) -> str:
    """Build the prompt for the LLM to generate Python code."""
    context_str = json.dumps(context, indent=2) if context else "{}"
    accessibility_section = (
        f"\n\nAccessibility Tree:\n{accessibility_tree}\n" if accessibility_tree else ""
    )

    return f"""
You are an expert Python automation engineer. Generate Python code to execute the following command on a web page using Playwright.

Command: {command}

Context dictionary: {context_str}{accessibility_section}

Context:
- You have access to a Playwright page object called 'page'
- You have access to a context dictionary called 'context' with the values shown above
- The page is already loaded and ready for interaction
- Generate code that uses standard Playwright methods like click(), fill(), select_option(), etc.
- The code should be executable Python that accomplishes the requested task
- Use the accessibility tree above to understand the page structure and identify elements

Requirements:
- Return your response as JSON in this exact format: {{"script": "# Python script here"}}
- The script should be complete and executable
- Use the 'page' variable for page interactions and 'context' dictionary for accessing values
- Access context values using context["key"] syntax
- Include error handling where appropriate
- Use async/await syntax for page interactions
- Use element selectors based on the accessibility tree when possible

Example response:
{{"script": "await page.fill('#username', context['username'])\\nawait page.click('#login-button')"}}

Generate the Python script now:
"""


async def call_llm_for_code_generation(agent: Agent, prompt: str) -> str:
    """Call the LLM to generate Python code based on the prompt."""
    try:
        # Create user message for the agent
        user_message = create_user_message(prompt)

        # Call the Anthropic API using the agent's client
        response = agent.client.messages.create(
            model=agent.model, max_tokens=4000, messages=[user_message]
        )

        # Extract the text content from the response
        if response.content and len(response.content) > 0:
            content = response.content[0]
            if hasattr(content, "text"):
                return content.text
            else:
                return str(content)
        else:
            return '{"script": "# No response from LLM"}'

    except Exception as e:
        log.error(f"Error calling LLM for code generation: {e}")
        return '{"script": "# Error calling LLM"}'


async def execute_script(
    script: str, context_vars: Dict[str, Any], page: StagehandPage
) -> Dict[str, Any]:
    """Execute the generated Python script with the page context."""
    try:
        # Prepare the execution context - pass context as a variable instead of unwrapping
        execution_context = {"page": page, "context": context_vars}

        # Check if the script contains await statements
        if "await " in script:
            # Wrap the script in an async function and execute it
            async_script = f"""
async def __execute_script():
{chr(10).join("    " + line for line in script.split(chr(10)))}

__result = __execute_script()
"""
            # Execute the script to define the function
            exec(compile(async_script, "<string>", "exec"), execution_context)

            # Get the coroutine and await it
            if "__result" in execution_context:
                await execution_context["__result"]
        else:
            # Execute synchronous script normally
            exec(script, execution_context)

        return {"success": True, "error": None}

    except Exception as e:
        return {"success": False, "error": str(e)}


async def verify_step_success(
    command: str, screenshot_before: bytes, screenshot_after: bytes
) -> Dict[str, Any]:
    """Verify if the step was successful by comparing screenshots."""
    # This is a placeholder for screenshot-based verification
    # In a real implementation, you would:
    # 1. Send both screenshots to an LLM
    # 2. Ask it to verify if the command was executed successfully
    # 3. Return the verification result

    # For now, return a basic success response
    return {
        "success": True,
        "message": "Verification completed (placeholder implementation)",
    }


async def execute_step(
    command: str,
    context: Optional[Dict[str, Any]],
    max_retries: int,
    page: StagehandPage,
    agent: Agent,
) -> Dict[str, Any]:
    """
    Execute a natural language command using LLM-generated code.

    Parameters:
    -----------
    command (str): Natural language description of the action to perform
    context (Dict[str, Any], optional): Context variables available to the generated script
    max_retries (int): Maximum number of retry attempts
    page (StagehandPage): The page to execute the command on
    agent (Agent): The agent to use for LLM calls

    Returns:
    --------
    Dict[str, Any]: Result containing success status, message, and generated script
    """
    if context is None:
        context = {}

    for attempt in range(max_retries):
        try:
            # Take initial screenshot for context
            screenshot_before = await page.screenshot()

            # Get accessibility tree
            accessibility_tree_result = await get_accessibility_tree(
                page, page._stagehand.logger
            )
            accessibility_tree = accessibility_tree_result["simplified"]

            # Prepare prompt for LLM
            prompt = build_step_script_prompt(command, context, accessibility_tree)

            # Call LLM to generate Python code
            llm_response = await call_llm_for_code_generation(agent, prompt)

            # Parse the JSON response
            try:
                response_data = json.loads(llm_response)
                script = response_data.get("script", "")
            except (json.JSONDecodeError, KeyError) as e:
                log.error(f"Failed to parse LLM response: {e}")
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "message": f"Failed to parse LLM response: {e}",
                        "script": "",
                        "attempt": attempt + 1,
                    }
                continue

            # Execute the generated Python code
            execution_result = await execute_script(script, context, page)

            if not execution_result["success"]:
                log.warning(
                    f"Script execution failed on attempt {attempt + 1}: {execution_result['error']}"
                )
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "message": f"Script execution failed: {execution_result['error']}",
                        "script": script,
                        "attempt": attempt + 1,
                    }
                continue

            # Take screenshot after execution for verification
            screenshot_after = await page.screenshot()

            # Verify success using screenshots
            verification_result = await verify_step_success(
                command, screenshot_before, screenshot_after
            )

            if verification_result["success"]:
                return {
                    "success": True,
                    "message": "Command executed successfully",
                    "script": script,
                    "attempt": attempt + 1,
                }
            else:
                log.warning(
                    f"Verification failed on attempt {attempt + 1}: {verification_result['message']}"
                )
                if attempt == max_retries - 1:
                    return {
                        "success": False,
                        "message": f"Verification failed: {verification_result['message']}",
                        "script": script,
                        "attempt": attempt + 1,
                    }

        except Exception as e:
            log.error(f"Error during interaction attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return {
                    "success": False,
                    "message": f"Unexpected error: {e}",
                    "script": "",
                    "attempt": attempt + 1,
                }

    return {
        "success": False,
        "message": "All retry attempts exhausted",
        "script": "",
        "attempt": max_retries,
    }


class AsyncStepContextManager:
    """Async context manager for Page.step method."""

    def __init__(self, page, command, context, max_retries, agent):
        self.page = page
        self.command = command
        self.context = context
        self.max_retries = max_retries
        self.agent = agent
        self.step_result = None

    async def __aenter__(self):
        # Return the context dict so users can access variables
        return self.context

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Check if the with block is empty by examining the source code
        is_empty_block = self._is_with_block_empty()

        if is_empty_block:
            log.info(
                f"Empty with block detected, triggering LLM action generation for: {self.command}"
            )
            # Use the pure function for step execution
            self.step_result = await execute_step(
                command=self.command,
                context=self.context,
                max_retries=self.max_retries,
                page=self.page._stagehand_page,
                agent=self.agent,
            )

            # Log the step result
            if self.step_result and self.step_result.get("success"):
                script = self.step_result.get("script", "")
                log.info(
                    f"Step completed successfully: {self.step_result.get('message', 'No message')}"
                )
                if script:
                    log.info(f"Generated Python script:\n{script}")
                    # Replace the empty with block with the generated code
                    self._replace_empty_block_with_code(script)
            else:
                log.error(
                    f"Step failed: {self.step_result.get('message', 'No message')}"
                )
        else:
            log.info(f"Manual execution detected for step: {self.command}")
            self.step_result = {
                "success": True,
                "message": "Manual execution completed",
                "script": "# Manual execution",
                "attempt": 1,
            }

        return False  # Don't suppress exceptions

    def _is_with_block_empty(self):
        """Check if the with block contains only pass or is empty using va.codegen."""
        try:
            # Frame offset explanation:
            # Frame 0: inspect_with_block_from_frame()
            # Frame 1: _is_with_block_empty() (this method)
            # Frame 2: AsyncStepContextManager.__aexit__()
            # Frame 3: User's "async with page.step(...)" statement ← TARGET
            #
            # We need frame_offset=3 to reach the user's actual with statement
            # that we want to inspect for empty blocks.
            inspector = inspect_with_block_from_frame(frame_offset=3)
            return inspector.is_with_block_empty()
        except Exception as e:
            log.debug(f"Error checking if with block is empty: {e}")
            # If we can't determine, assume it's not empty to be safe
            return False

    def _replace_empty_block_with_code(self, generated_script: str):
        """Replace the empty with block with the generated code using va.codegen."""
        try:
            # Same frame offset logic as _is_with_block_empty():
            # We need frame_offset=3 to reach the user's "async with" statement
            # so we can replace the empty block with the generated code.
            success = mutate_with_block_from_frame(
                new_code=generated_script,
                context_dict=self.context,
                frame_offset=3,
                pending_modifications=_pending_file_modifications,
            )

            if success:
                log.info(
                    "Queued replacement of empty with block (will be applied at exit)"
                )
            else:
                log.warning("Failed to queue empty with block replacement")
        except Exception as e:
            log.warning(f"Error during with block replacement: {e}")

    def __getattr__(self, name):
        """Forward attribute access to delegate to page."""
        return getattr(self.page._stagehand_page, name)
