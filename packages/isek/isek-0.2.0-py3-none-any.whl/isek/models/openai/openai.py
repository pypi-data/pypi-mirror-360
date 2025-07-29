"""OpenAI model implementation."""

import os
from typing import Any, List, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletion

from isek.models.base import Model, SimpleMessage, SimpleModelResponse
from isek.utils.log import log


class OpenAIModel(Model):
    """Ultra-simplified OpenAI model implementation."""

    def __init__(
        self,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize the OpenAI model.

        Args:
            model_id: The OpenAI model ID (e.g., "gpt-3.5-turbo", "gpt-4")
            api_key: OpenAI API key
            base_url: Custom base URL for the API
        """
        # Get model ID with fallback
        _model_id = model_id or os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo")

        # Initialize base class
        super().__init__(id=_model_id, name=_model_id, provider="openai")

        # Set capabilities
        self.supports_native_structured_outputs = True
        self.supports_json_schema_outputs = True

        # Initialize OpenAI client
        _api_key = api_key or os.environ.get("OPENAI_API_KEY")
        _base_url = base_url or os.environ.get("OPENAI_BASE_URL")

        self.client = OpenAI(api_key=_api_key, base_url=_base_url)

        log.info(f"OpenAIModel initialized: {self.id}")

    def invoke(self, messages: List[SimpleMessage], **kwargs: Any) -> ChatCompletion:
        """Invoke the OpenAI model.

        Args:
            messages: List of messages to send
            **kwargs: Additional arguments for the API call

        Returns:
            Raw ChatCompletion response
        """
        # Convert SimpleMessage to OpenAI format
        formatted_messages = []
        for msg in messages:
            formatted_msg = {"role": msg.role, "content": msg.content}
            if msg.name:
                formatted_msg["name"] = msg.name
            if msg.role == "tool" and msg.tool_call_id:
                formatted_msg["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls is not None:
                formatted_msg["tool_calls"] = msg.tool_calls
            formatted_messages.append(formatted_msg)

        # Prepare request parameters
        params = {
            "model": self.id,
            "messages": formatted_messages,
        }
        # Only add 'tools' if present in kwargs and not None
        if "tools" in kwargs and kwargs["tools"]:
            params["tools"] = kwargs.pop("tools")
        # Filter out 'toolkits' parameter as OpenAI doesn't expect it
        kwargs.pop("toolkits", None)
        # Add any other kwargs
        params.update(kwargs)

        log.debug(f"OpenAI request: {self.id}")

        try:
            response = self.client.chat.completions.create(**params)
            log.debug(f"OpenAI response: {response.id}")
            return response
        except Exception as e:
            log.error(f"OpenAI API error: {e}")
            raise

    async def ainvoke(
        self, messages: List[SimpleMessage], **kwargs: Any
    ) -> ChatCompletion:
        """Async invoke the OpenAI model.

        Args:
            messages: List of messages to send
            **kwargs: Additional arguments for the API call

        Returns:
            Raw ChatCompletion response
        """
        # For now, just call the sync version
        # TODO: Implement proper async when needed
        return self.invoke(messages, **kwargs)

    def parse_provider_response(
        self, response: ChatCompletion, **kwargs: Any
    ) -> SimpleModelResponse:
        """Parse the OpenAI response.

        Args:
            response: Raw ChatCompletion response
            **kwargs: Additional arguments

        Returns:
            Parsed SimpleModelResponse
        """
        if not response.choices:
            return SimpleModelResponse(content="No response generated")

        choice = response.choices[0]
        message = choice.message

        # Extract tool calls if present
        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for tool_call in message.tool_calls:
                tool_calls.append(
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                )

        # Extract extra information
        extra = {
            "finish_reason": choice.finish_reason,
            "usage": response.usage.model_dump() if response.usage else None,
            "model": response.model,
            "id": response.id,
        }

        return SimpleModelResponse(
            content=message.content,
            role=message.role,
            tool_calls=tool_calls,
            extra=extra,
        )
