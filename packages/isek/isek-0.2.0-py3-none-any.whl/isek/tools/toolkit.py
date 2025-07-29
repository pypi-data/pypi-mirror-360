from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from isek.utils.log import log
from isek.utils.tools import function_to_schema


@dataclass
class SimpleFunction:
    """Ultra-simplified function wrapper."""

    name: str
    entrypoint: Callable
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {"type": "object", "properties": {}, "required": []}

    def to_dict(self) -> Dict[str, Any]:
        """Convert function to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    def execute(self, **kwargs) -> Any:
        """Execute the function with given arguments."""
        return self.entrypoint(**kwargs)


class Toolkit:
    """Ultra-simplified Toolkit class with minimal features."""

    def __init__(
        self,
        name: str = "toolkit",
        tools: Optional[List[Callable]] = None,
        instructions: Optional[str] = None,
        auto_register: bool = True,
        debug: bool = False,
    ):
        """Initialize a new Toolkit.

        Args:
            name: A descriptive name for the toolkit
            tools: List of tools to include in the toolkit
            instructions: Instructions for the toolkit
            auto_register: Whether to automatically register all tools
            debug: Enable debug output
        """
        self.name: str = name
        self.tools: List[Callable] = tools or []
        self.functions: Dict[str, SimpleFunction] = {}
        self.instructions: Optional[str] = instructions
        self.debug: bool = debug

        # Automatically register all tools if auto_register is True
        if auto_register and self.tools:
            self._register_tools()

    def _register_tools(self) -> None:
        """Register all tools."""
        for tool in self.tools:
            self.register(tool)

    def register(
        self, function: Callable, name: Optional[str] = None
    ) -> SimpleFunction:
        """Register a function with the toolkit.

        Args:
            function: The callable to register
            name: Optional custom name for the function

        Returns:
            The registered SimpleFunction
        """
        tool_name = name or function.__name__
        schema = function_to_schema(function)
        parameters = schema["function"][
            "parameters"
        ]  # Extract just the parameters schema
        simple_function = SimpleFunction(
            name=tool_name,
            entrypoint=function,
            description=getattr(function, "__doc__", None),
            parameters=parameters,
        )
        self.functions[tool_name] = simple_function
        if self.debug:
            log.debug(f"[Toolkit: {self.name}] Registered function: {tool_name}")
        return simple_function

    def get_function(self, name: str) -> Optional[SimpleFunction]:
        """Get a function by name."""
        return self.functions.get(name)

    def list_functions(self) -> List[str]:
        """List all registered function names."""
        if self.debug:
            log.debug(f"[Toolkit: {self.name}] Listing functions:")
            for fname in self.functions:
                log.debug(f"  - {fname}")
        return list(self.functions.keys())

    def execute_function(self, name: str, **kwargs) -> Any:
        """Execute a function by name."""
        function = self.get_function(name)
        if function is None:
            raise ValueError(f"Function '{name}' not found in toolkit '{self.name}'")
        result = function.execute(**kwargs)
        if self.debug:
            log.debug(
                f"[Toolkit: {self.name}] Executed '{name}' with args {kwargs} -> {result}"
            )
        return result

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} functions={list(self.functions.keys())}>"

    def __str__(self) -> str:
        return self.__repr__()
