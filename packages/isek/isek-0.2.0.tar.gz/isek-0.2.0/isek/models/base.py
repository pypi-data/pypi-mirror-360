from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SimpleMessage:
    """Ultra-simplified message model."""

    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "role": self.role,
            "content": self.content,
        }
        if self.name:
            d["name"] = self.name
        if self.role == "tool" and self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        if self.tool_calls is not None:
            d["tool_calls"] = self.tool_calls
        return d


@dataclass
class SimpleModelResponse:
    """Ultra-simplified model response."""

    content: Optional[str] = None
    role: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "role": self.role,
            "tool_calls": self.tool_calls,
            "extra": self.extra,
        }


class Model(ABC):
    """Ultra-simplified abstract base model class."""

    def __init__(
        self,
        id: str,
        name: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        """Initialize the model.

        Args:
            id: The model ID
            name: The model name
            provider: The model provider
        """
        self.id = id
        self.name = name or id
        self.provider = provider or "unknown"

        # Basic configuration
        self.supports_native_structured_outputs: bool = False
        self.supports_json_schema_outputs: bool = False
        self.tool_message_role: str = "tool"
        self.assistant_message_role: str = "assistant"

    def get_provider(self) -> str:
        """Get the provider name."""
        return self.provider

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {"id": self.id, "name": self.name, "provider": self.provider}

    @abstractmethod
    def invoke(self, messages: List[SimpleMessage], **kwargs) -> Any:
        """Invoke the model with messages.

        Args:
            messages: List of messages to send to the model
            **kwargs: Additional arguments

        Returns:
            Raw response from the model
        """
        pass

    @abstractmethod
    async def ainvoke(self, messages: List[SimpleMessage], **kwargs) -> Any:
        """Async invoke the model with messages.

        Args:
            messages: List of messages to send to the model
            **kwargs: Additional arguments

        Returns:
            Raw response from the model
        """
        pass

    @abstractmethod
    def parse_provider_response(self, response: Any, **kwargs) -> SimpleModelResponse:
        """Parse the raw response from the model provider.

        Args:
            response: Raw response from the model provider
            **kwargs: Additional arguments

        Returns:
            Parsed model response
        """
        pass

    def response(self, messages: List[SimpleMessage], **kwargs) -> SimpleModelResponse:
        """Generate a response from the model.

        Args:
            messages: List of messages to send to the model
            **kwargs: Additional arguments including:
                - tools: List of tool schemas for the model
                - toolkits: List of actual toolkits for execution
        Returns:
            Parsed model response
        """
        # Check if tools are provided
        tools = kwargs.get("tools")
        toolkits = kwargs.get("toolkits", [])

        if not tools:
            # No tools, simple single call
            raw_response = self.invoke(messages, **kwargs)
            return self.parse_provider_response(raw_response, **kwargs)

        # Tools provided, handle tool calling loop internally
        messages_for_model = messages.copy()

        for _ in range(10):  # Prevent infinite loops
            # Call the model
            raw_response = self.invoke(messages_for_model, **kwargs)
            model_response = self.parse_provider_response(raw_response, **kwargs)

            # If the model returns a final text response (no tool calls), return it
            if model_response.content and not model_response.tool_calls:
                return model_response

            # If the model requests tool calls, execute them and continue
            if model_response.tool_calls:
                # Add the assistant message (with tool_calls) to the conversation history
                assistant_msg = SimpleMessage(
                    role="assistant",
                    content="" if model_response.tool_calls else model_response.content,
                    tool_calls=model_response.tool_calls,
                )
                messages_for_model.append(assistant_msg)

                # Execute each tool call and add results
                tool_messages = []
                for tool_call in model_response.tool_calls:
                    tool_name = tool_call.get("function", {}).get("name")
                    tool_args = tool_call.get("function", {}).get("arguments")
                    tool_call_id = tool_call.get("id")

                    # Parse tool arguments
                    if isinstance(tool_args, str):
                        import json

                        try:
                            tool_args = json.loads(tool_args)
                        except Exception:
                            tool_args = {}
                    if not isinstance(tool_args, dict):
                        tool_args = {}

                    # Execute the tool using the provided toolkits
                    tool_result = self._execute_tool(tool_name, tool_args, toolkits)

                    # Add tool result to conversation
                    tool_msg = SimpleMessage(
                        role="tool", content=str(tool_result), tool_call_id=tool_call_id
                    )
                    tool_messages.append(tool_msg)
                # Find the last assistant message (with tool_calls)
                last_assistant_idx = None
                for i in range(len(messages_for_model) - 1, -1, -1):
                    msg = messages_for_model[i]
                    if getattr(msg, "role", None) == "assistant":
                        last_assistant_idx = i
                        break
                if last_assistant_idx is not None:
                    messages_for_model = (
                        messages_for_model[: last_assistant_idx + 1] + tool_messages
                    )
                else:
                    messages_for_model = messages_for_model + tool_messages
            else:
                # If neither content nor tool_calls, return what we have
                return model_response

        # If we reach here, we hit the loop limit
        return model_response

    def _execute_tool(self, tool_name: str, tool_args: dict, toolkits: List) -> str:
        """Execute a tool by name with arguments using the provided toolkits.

        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            toolkits: List of toolkits to search for the tool

        Returns:
            Result of tool execution as string
        """
        # Search for the tool in the provided toolkits
        for toolkit in toolkits:
            if hasattr(toolkit, "functions") and tool_name in toolkit.functions:
                try:
                    result = toolkit.execute_function(tool_name, **(tool_args or {}))
                    return str(result)
                except Exception as e:
                    return f"Error executing tool '{tool_name}': {e}"

        return f"Tool '{tool_name}' not found in any toolkit"

    async def aresponse(
        self, messages: List[SimpleMessage], **kwargs
    ) -> SimpleModelResponse:
        """Generate an async response from the model.

        Args:
            messages: List of messages to send to the model
            **kwargs: Additional arguments

        Returns:
            Parsed model response
        """
        # Get raw response from model (pass SimpleMessage objects directly)
        raw_response = await self.ainvoke(messages, **kwargs)

        # Parse the response
        return self.parse_provider_response(raw_response, **kwargs)

    def _format_messages(self, messages: List[SimpleMessage]) -> List[Dict[str, Any]]:
        """Format messages for the model provider.

        Args:
            messages: List of SimpleMessage objects

        Returns:
            List of formatted message dictionaries
        """
        return [msg.to_dict() for msg in messages]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id='{self.id}' provider='{self.provider}'>"

    def __str__(self) -> str:
        return self.__repr__()


# Example concrete implementation
class SimpleModel(Model):
    """Simple model implementation for testing."""

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
