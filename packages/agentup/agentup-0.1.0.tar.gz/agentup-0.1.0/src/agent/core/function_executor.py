"""Function Execution Logic for Function Dispatcher."""

import logging
import re
from typing import Any

from a2a.types import Task

logger = logging.getLogger(__name__)


class FunctionExecutor:
    """Handles execution of local and MCP functions."""

    def __init__(self, function_registry, task: Task):
        self.function_registry = function_registry
        self.task = task

    async def execute_function_calls(self, llm_response: str) -> str:
        """Execute function calls parsed from LLM response."""
        lines = llm_response.split("\n")
        function_results = []
        natural_response = []

        for line in lines:
            line = line.strip()
            if line.startswith("FUNCTION_CALL:"):
                # Parse function call
                function_call = line.replace("FUNCTION_CALL:", "").strip()
                try:
                    result = await self._execute_single_function_call(function_call)
                    function_results.append(result)
                except Exception as e:
                    logger.error(f"Function call failed: {function_call}, error: {e}")
                    function_results.append(f"Error: {str(e)}")
            else:
                # Natural language response
                if line and not line.startswith("FUNCTION_CALL:"):
                    natural_response.append(line)

        # Combine function results with natural response
        if function_results and natural_response:
            return f"{' '.join(natural_response)}\n\nResults: {'; '.join(function_results)}"
        elif function_results:
            return "; ".join(function_results)
        else:
            return " ".join(natural_response)

    async def _execute_single_function_call(self, function_call: str) -> str:
        """Execute a single function call (legacy method for backward compatibility)."""
        # Simple parsing - in production, would use proper parsing

        # Extract function name and parameters
        match = re.match(r"(\w+)\((.*)\)", function_call)
        if not match:
            raise ValueError(f"Invalid function call format: {function_call}")

        function_name, params_str = match.groups()

        # Parse parameters (simplified - would need proper parsing in production)
        params = {}
        if params_str:
            # Basic parameter parsing
            param_pairs = params_str.split(",")
            for pair in param_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    key = key.strip().strip('"')
                    value = value.strip().strip('"')
                    params[key] = value

        # Use the new function call method
        return await self.execute_function_call(function_name, params)

    async def execute_function_call(self, function_name: str, arguments: dict[str, Any]) -> str:
        """Execute a single function call (local handler or MCP tool)."""
        # Check if this is an MCP tool
        if self.function_registry.is_mcp_tool(function_name):
            try:
                result = await self.function_registry.call_mcp_tool(function_name, arguments)
                return str(result)
            except Exception as e:
                logger.error(f"MCP tool call failed: {function_name}, error: {e}")
                raise

        # Handle local function
        handler = self.function_registry.get_handler(function_name)
        if not handler:
            raise ValueError(f"Function not found: {function_name}")

        # Create task with function parameters
        task_with_params = self.task
        if hasattr(self.task, "metadata"):
            if self.task.metadata is None:
                self.task.metadata = {}
            self.task.metadata.update(arguments)

        # Execute handler
        result = await handler(task_with_params)
        return str(result)
