"""LiteLLM model implementation."""

import os
from typing import Any, List, Optional
from litellm import completion

from isek.models.base import Model, SimpleMessage, SimpleModelResponse
from isek.models.provider import PROVIDER_MAP, DEFAULT_PROVIDER
from isek.utils.log import log


class LiteLLMModel(Model):
    """Ultra-simplified LiteLLM model implementation."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize the LiteLLM model.

        Args:
            provider: The provider name (e.g., "openai", "anthropic", "gemini")
            model_id: The model ID (e.g., "gpt-3.5-turbo", "claude-3-sonnet")
            api_key: API key for the provider
            base_url: Custom base URL for the API
        """
        # Get provider with fallback
        _provider = provider or DEFAULT_PROVIDER
        if _provider not in PROVIDER_MAP:
            raise ValueError(
                f"Unsupported provider: {_provider}. "
                f"Supported providers are: {', '.join(PROVIDER_MAP.keys())}."
            )

        # Get provider configuration
        provider_config = PROVIDER_MAP[_provider]
        model_env_key = provider_config.get("model_env_key")
        default_model = provider_config.get("default_model")
        api_env_key = provider_config.get("api_env_key")
        base_url_env_key = provider_config.get("base_url_env_key")

        # Validate required configuration
        if not model_env_key or not default_model or not api_env_key:
            raise ValueError(f"Invalid provider configuration for {_provider}")

        # Get model ID with fallback
        _model_id = model_id or os.environ.get(model_env_key, default_model)

        # Initialize base class
        super().__init__(id=_model_id, name=_model_id, provider=_provider)

        # Set capabilities
        self.supports_native_structured_outputs = True
        self.supports_json_schema_outputs = True

        # Store configuration
        self.api_key = api_key or os.environ.get(api_env_key)
        self.base_url = base_url or (
            os.environ.get(base_url_env_key) if base_url_env_key else None
        )

        log.info(f"LiteLLMModel initialized: {self.id} (provider: {_provider})")

    def invoke(self, messages: List[SimpleMessage], **kwargs: Any) -> Any:
        """Invoke the LiteLLM model.

        Args:
            messages: List of messages to send
            **kwargs: Additional arguments for the API call

        Returns:
            Raw ModelResponse
        """
        # Convert SimpleMessage to LiteLLM format
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
        # Filter out 'toolkits' parameter as LiteLLM doesn't expect it
        kwargs.pop("toolkits", None)
        # Add any other kwargs
        params.update(kwargs)

        log.debug(f"LiteLLM request: {self.id}")

        try:
            response = completion(**params)
            log.debug("LiteLLM response received")
            return response
        except Exception as e:
            log.error(f"LiteLLM API error: {e}")
            raise

    async def ainvoke(self, messages: List[SimpleMessage], **kwargs: Any) -> Any:
        """Async invoke the LiteLLM model.

        Args:
            messages: List of messages to send
            **kwargs: Additional arguments for the API call

        Returns:
            Raw ModelResponse
        """
        # For now, just call the sync version
        # TODO: Implement proper async when needed
        return self.invoke(messages, **kwargs)

    def parse_provider_response(
        self, response: Any, **kwargs: Any
    ) -> SimpleModelResponse:
        """Parse the LiteLLM response.

        Args:
            response: Raw ModelResponse
            **kwargs: Additional arguments

        Returns:
            Parsed SimpleModelResponse
        """
        if not response.choices:
            return SimpleModelResponse(content="No response generated")

        choice = response.choices[0]

        # Safely access message
        if hasattr(choice, "message"):
            message = choice.message
        else:
            # For streaming responses, the choice might be the message itself
            message = choice

        # Extract tool calls if present
        tool_calls = None
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_calls = []
            for tool_call in message.tool_calls:
                tool_calls.append(
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                )

        # Extract extra information
        extra = {
            "finish_reason": getattr(choice, "finish_reason", None),
            "usage": getattr(response, "usage", None),
            "model": getattr(response, "model", None),
            "id": getattr(response, "id", None),
        }

        return SimpleModelResponse(
            content=getattr(message, "content", None),
            role=getattr(message, "role", "assistant"),
            tool_calls=tool_calls,
            extra=extra,
        )
