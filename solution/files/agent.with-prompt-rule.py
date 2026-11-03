"""Customer support agent for Cymbal Wallet, a fictional digital wallet app.

Customers ask it about their own money. Support staff use it to look up any
customer. Every answer comes from BigQuery, through tools served by MCP
Toolbox at TOOLBOX_URL.
"""

import os

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini, LlmResponse
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from google.genai import types

from .scope_plugin import CallerScopePlugin

TOOLBOX_URL = os.environ.get("TOOLBOX_URL", "http://127.0.0.1:5000")

INSTRUCTION = """\
You are the support assistant for Cymbal Wallet, a digital wallet app.
Customers come to you with questions and problems about their own wallet:
their profile, balance, transfers, linked bank accounts, and refunds. Help
them sort it out. Cymbal Wallet support staff use you to look up any
customer's account and to correct records that are wrong.

Ask customers for their customer ID before you look anything up. Customer
IDs look like cust_0001.

Customers may only see their own data. Support staff may see any customer.

Answer from tool results only. Never guess a balance, a transfer, or the
status of a refund.

Never modify or delete data.
"""


def mask_account_numbers(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    # TODO: replace all but the last four digits of each account number.
    return None


root_agent = Agent(
    name="wallet_agent",
    model=Gemini(
        model="gemini-3.8-flash",
        client_kwargs={"enterprise": True, "location": "global"},
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    after_model_callback=mask_account_numbers,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=f"{TOOLBOX_URL}/mcp"),
        ),
    ],
)

app = App(
    name="wallet_agent",
    root_agent=root_agent,
    plugins=[CallerScopePlugin()],
)
