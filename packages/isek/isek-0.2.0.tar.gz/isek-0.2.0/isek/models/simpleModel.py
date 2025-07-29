from __future__ import annotations

from typing import Any, List
from isek.models.base import SimpleMessage, SimpleModelResponse
from isek.models.base import Model


class SimpleModel(Model):
    """Simple model implementation for testing that echoes user messages."""

    def __init__(self, model_id: str = "simple-model"):
        super().__init__(id=model_id)

    def invoke(self, messages: List[SimpleMessage], **kwargs) -> Any:
        """Simple mock implementation."""
        # Just return the last user message as a response
        for msg in reversed(messages):
            if msg.role == "user" and msg.content:
                return {"content": f"Echo: {msg.content}"}
        return {"content": "No user message found"}

    async def ainvoke(self, messages: List[SimpleMessage], **kwargs) -> Any:
        """Simple async mock implementation."""
        return self.invoke(messages, **kwargs)

    def parse_provider_response(self, response: Any, **kwargs) -> SimpleModelResponse:
        """Parse the mock response."""
        if isinstance(response, dict):
            return SimpleModelResponse(
                content=response.get("content"), role="assistant"
            )
        return SimpleModelResponse(content=str(response), role="assistant")
