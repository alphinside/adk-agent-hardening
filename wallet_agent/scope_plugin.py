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
        # TODO: refuse a customer_id that is not the caller's, and cap row_limit.
        return None
