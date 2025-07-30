"""Code mutation utilities using libcst."""

import sys
import logging
from typing import Optional, Dict, Any

import libcst as cst

log = logging.getLogger("va.codegen.mutator")


class WithBlockReplacer(cst.CSTTransformer):
    """Transformer to replace the body of a with statement at a specific line."""

    METADATA_DEPENDENCIES = (cst.metadata.PositionProvider,)

    def __init__(
        self,
        target_line: int,
        new_code: str,
        context_dict: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self.target_line = target_line
        self.new_code = new_code
        self.context_dict = context_dict or {}
        self.replacement_made = False

    def leave_With(self, original_node: cst.With, updated_node: cst.With) -> cst.With:
        # Check if this is the target with statement
        try:
            position = self.get_metadata(cst.metadata.PositionProvider, original_node)
            if position and position.start.line == self.target_line:
                return self._replace_with_body(updated_node)
        except Exception:
            # Fallback: replace the first with statement
            if not self.replacement_made:
                return self._replace_with_body(updated_node)

        return updated_node

    def _replace_with_body(self, with_node: cst.With) -> cst.With:
        """Replace the body of the with statement with generated code."""
        # Check if we need to add "as context" to the with statement
        needs_context_var = (
            self.context_dict
            and ('context["' in self.new_code or "context['" in self.new_code)
            and not any(
                isinstance(item.asname, cst.AsName)
                and isinstance(item.asname.name, cst.Name)
                and item.asname.name.value == "context"
                for item in with_node.items
            )
        )

        # Update with statement to include "as context" if needed
        updated_with_node = with_node
        if needs_context_var:
            # Add "as context" to the first with item
            if with_node.items:
                first_item = with_node.items[0]
                new_item = first_item.with_changes(
                    asname=cst.AsName(name=cst.Name("context"))
                )
                updated_with_node = with_node.with_changes(
                    items=[new_item] + list(with_node.items[1:])
                )

        # Parse the new code into CST statements
        try:
            # Create a temporary module to parse the new code
            temp_module = cst.parse_module(self.new_code)
            new_statements = temp_module.body

            # Create new body with the parsed statements
            new_body = cst.IndentedBlock(body=new_statements)

            # Replace the body
            result = updated_with_node.with_changes(body=new_body)
            self.replacement_made = True
            return result

        except Exception as e:
            log.warning(f"Failed to parse new code as CST: {e}")
            # Fallback: create a simple pass statement
            pass_stmt = cst.SimpleStatementLine(body=[cst.Pass()])
            new_body = cst.IndentedBlock(body=[pass_stmt])
            result = updated_with_node.with_changes(body=new_body)
            self.replacement_made = True
            return result


class CodeMutator:
    """Main class for mutating source code."""

    def __init__(self, filename: str, line_number: int):
        self.filename = filename
        self.line_number = line_number

    def replace_with_block(
        self,
        new_code: str,
        context_dict: Optional[Dict[str, Any]] = None,
        pending_modifications: Optional[Dict[str, list]] = None,
    ) -> bool:
        """Replace the with block at the specified line with new code.

        Args:
            new_code: The new code to insert into the with block
            context_dict: Context variables that may be used in the new code
            pending_modifications: Dictionary to store pending file modifications

        Returns:
            True if replacement was successful, False otherwise
        """
        try:
            # Get the current state of the file (either from memory or disk)
            source_code = ""
            if pending_modifications and self.filename in pending_modifications:
                source_code = "".join(pending_modifications[self.filename])
            else:
                with open(self.filename, "r") as f:
                    source_code = f.read()

            # Parse the source code with libcst
            tree = cst.parse_module(source_code)

            # Find the with statement and replace its body
            transformer = WithBlockReplacer(self.line_number, new_code, context_dict)

            # Create metadata wrapper for accurate line tracking
            metadata_wrapper = cst.metadata.MetadataWrapper(tree)
            new_tree = metadata_wrapper.visit(transformer)

            if not transformer.replacement_made:
                log.warning(
                    f"Could not find with statement at line {self.line_number} for code replacement"
                )
                return False

            # Convert back to source code
            new_source_code = new_tree.code

            # Store the modified content
            if pending_modifications is not None:
                pending_modifications[self.filename] = new_source_code.splitlines(
                    keepends=True
                )
            else:
                # Write directly to file if no pending modifications dict provided
                with open(self.filename, "w") as f:
                    f.write(new_source_code)

            log.info(
                f"Successfully replaced with block in {self.filename} at line {self.line_number}"
            )
            return True

        except Exception as e:
            log.warning(f"Failed to replace with block: {e}")
            return False


def mutate_with_block_from_frame(
    new_code: str,
    context_dict: Optional[Dict[str, Any]] = None,
    frame_offset: int = 2,
    pending_modifications: Optional[Dict[str, list]] = None,
) -> bool:
    """Replace a with block from a stack frame.

    Frame offset determines which level of the call stack to target:
    - frame_offset=0: Current function (mutate_with_block_from_frame)
    - frame_offset=1: Function that called this one
    - frame_offset=2: Function that called the caller (default)
    - frame_offset=3: Three levels up the call stack

    Example call stack when used from AsyncStepContextManager:
        Frame 0: mutate_with_block_from_frame()
        Frame 1: _replace_empty_block_with_code()
        Frame 2: AsyncStepContextManager.__aexit__()
        Frame 3: User's "async with page.step(...)" ← Usually the target

    Args:
        new_code: The new code to insert
        context_dict: Context variables
        frame_offset: How many frames up the stack to look
        pending_modifications: Dictionary to store pending file modifications

    Returns:
        True if replacement was successful, False otherwise
    """
    frame = sys._getframe(frame_offset)
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno

    mutator = CodeMutator(filename, lineno)
    return mutator.replace_with_block(new_code, context_dict, pending_modifications)
