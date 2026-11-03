"""Decides whose data a tool call may touch, from who is calling.

The caller is the ADK session's user_id. It comes from the app that opened
the session, not from anything said in the chat, so no prompt can change it.
"""

from typing import Any

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

# Callers allowed to look up any customer. Everyone else is a customer and
# sees only their own account.
SUPPORT_STAFF = {"support_0001"}

# A support conversation never needs more than the last 20 transfers.
MAX_ROW_LIMIT = 20


class CallerScopePlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__(name="caller_scope")

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
    ) -> dict | None:
        caller = tool_context.user_id
        if caller not in SUPPORT_STAFF and tool_args.get("customer_id", caller) != caller:
            return {"error": "Customers can only look up their own account."}
        if "row_limit" in tool_args:
            tool_args["row_limit"] = min(int(tool_args["row_limit"]), MAX_ROW_LIMIT)
        return None
