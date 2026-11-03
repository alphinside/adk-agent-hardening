"""Screens the agent's input and output with Model Armor.

Two checkpoints: the caller's message and the agent's reply. The template
named by MODEL_ARMOR_TEMPLATE_ID decides what counts as a match.
"""

import base64
import binascii
import os
import re

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin
from google.api_core.client_options import ClientOptions
from google.cloud import modelarmor_v1
from google.genai import types

BASE64_RUN = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")

REMOVED_PROMPT = "[removed by Model Armor]"
BLOCKED_REPLY = "Sorry, I can't help with that."


def with_decoded_base64(text: str) -> str:
    """Appends the decoded text of every base64 run. Model Armor does not decode."""
    decoded = []
    for run in BASE64_RUN.findall(text):
        try:
            decoded.append(base64.b64decode(run, validate=True).decode("utf-8"))
        except (binascii.Error, UnicodeDecodeError):
            pass
    return "\n".join([text, *decoded])


class ModelArmorScreenPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__(name="model_armor_screen")
        location = os.environ["GOOGLE_CLOUD_LOCATION"]
        self._template = (
            f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/locations/{location}"
            f"/templates/{os.environ['MODEL_ARMOR_TEMPLATE_ID']}"
        )
        # Model Armor has regional endpoints only.
        self._client = modelarmor_v1.ModelArmorClient(
            client_options=ClientOptions(api_endpoint=f"modelarmor.{location}.rep.googleapis.com")
        )

    def _input_flagged(self, text: str) -> bool:
        result = self._client.sanitize_user_prompt(
            request=modelarmor_v1.SanitizeUserPromptRequest(
                name=self._template,
                user_prompt_data=modelarmor_v1.DataItem(text=with_decoded_base64(text)),
            )
        ).sanitization_result
        return result.filter_match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND

    def _output_flagged(self, text: str) -> bool:
        result = self._client.sanitize_model_response(
            request=modelarmor_v1.SanitizeModelResponseRequest(
                name=self._template,
                model_response_data=modelarmor_v1.DataItem(text=text),
            )
        ).sanitization_result
        return result.filter_match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND

    async def on_user_message_callback(
        self, *, invocation_context: InvocationContext, user_message: types.Content
    ) -> types.Content | None:
        text = "".join(part.text or "" for part in user_message.parts or [])
        if text and self._input_flagged(text):
            # Replacing the message keeps the attack out of the session history.
            return types.Content(role="user", parts=[types.Part(text=REMOVED_PROMPT)])
        return None

    async def before_run_callback(
        self, *, invocation_context: InvocationContext
    ) -> types.Content | None:
        message = invocation_context.user_content
        if message and message.parts and message.parts[0].text == REMOVED_PROMPT:
            # Returning content ends the turn before the model is called.
            return types.Content(role="model", parts=[types.Part(text=BLOCKED_REPLY)])
        return None

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> LlmResponse | None:
        parts = llm_response.content.parts if llm_response.content else None
        text = "".join(p.text for p in parts or [] if p.text and not p.thought)
        if text and self._output_flagged(text):
            return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=BLOCKED_REPLY)]))
        return None
