# isek/tools/fastmcp_toolkit.py

import asyncio
from typing import Any, Dict, List, Optional
from fastmcp import Client
from isek.tools.toolkit import Toolkit
from isek.utils.log import log


class FastMCPToolkit(Toolkit):
    """
    FastMCP-based toolkit for MCP server integration.
    Provides simplified access to MCP tools with automatic discovery and registration.
    """

    def __init__(
        self,
        server_source: str,
        name: str = "fastmcp",
        timeout: float = 30.0,
        auto_register: bool = True,
        debug: bool = False,
        auth_token: Optional[str] = None,
    ):
        """Initialize FastMCP toolkit.

        Args:
            server_source: MCP server source (URL, file path, or FastMCP instance)
            name: Toolkit name
            timeout: Connection timeout in seconds
            auto_register: Whether to automatically discover and register tools
            debug: Enable debug output
            auth_token: Authentication token for the MCP server
        """
        self.server_source = server_source
        self.timeout = timeout
        self.auth_token = auth_token
        self.client = None

        super().__init__(
            name=name,
            tools=[],
            auto_register=False,
            debug=debug,
        )

        if auto_register:
            # Initialize connection and discover tools
            self._initialize_connection()

    def _initialize_connection(self):
        """Initialize MCP connection and discover tools."""
        try:
            # Create FastMCP client
            client_kwargs = {
                "transport": self.server_source,
                "timeout": self.timeout,
            }

            if self.auth_token:
                client_kwargs["auth"] = self.auth_token

            self.client = Client(**client_kwargs)

            # Discover and register tools
            self._discover_tools()

        except Exception as e:
            log.error(f"[FastMCPToolkit] Failed to initialize connection: {e}")
            if self.debug:
                raise

    def _discover_tools(self):
        """Discover tools from MCP server and register them."""
        if not self.client:
            return

        try:
            # Get tools list
            tools = self._run_async(self.client.list_tools())

            if self.debug:
                log.debug(f"[FastMCPToolkit] Discovered {len(tools)} tools")

            # Register each tool
            for tool in tools:
                self._register_mcp_tool(tool.name)

        except Exception as e:
            log.error(f"[FastMCPToolkit] Tool discovery failed: {e}")

    def _register_mcp_tool(self, tool_name: str):
        """Register a single MCP tool as a local function.

        Args:
            tool_name: Name of the MCP tool to register
        """

        def tool_wrapper(**kwargs: Any) -> Any:
            """Wrapper function that calls MCP tool."""
            try:
                # Parameter mapping for common tools
                mapped_kwargs = self._map_parameters(tool_name, kwargs)

                # Call the tool
                result = self._run_async(
                    self.client.call_tool(tool_name, mapped_kwargs)
                )

                return self._extract_text(result)

            except Exception as e:
                log.error(f"[FastMCPToolkit] Tool call failed for {tool_name}: {e}")
                return f"[Error] {e}"

        # Set function attributes
        tool_wrapper.__name__ = tool_name.replace(".", "_")
        tool_wrapper.__doc__ = f"MCP tool: {tool_name}"

        # Register with toolkit
        self.register(tool_wrapper, name=tool_wrapper.__name__)

        if self.debug:
            log.debug(f"[FastMCPToolkit] Registered tool: {tool_name}")

    def _map_parameters(self, tool_name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Map common parameter names to MCP tool specific parameter names.

        Args:
            tool_name: Name of the MCP tool
            kwargs: Original parameters

        Returns:
            Mapped parameters
        """
        mapped = kwargs.copy()

        # GitHub Copilot MCP parameter mappings
        if tool_name == "search_repositories":
            # Map 'q' to 'query' for GitHub search
            if "q" in mapped and "query" not in mapped:
                mapped["query"] = mapped.pop("q")

        return mapped

    def _run_async(self, coro):
        """Run async coroutine in new event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:

            async def run_with_client():
                async with self.client:
                    return await coro

            result = loop.run_until_complete(run_with_client())
            return result
        finally:
            loop.close()

    def _extract_text(self, result) -> str:
        """Extract text content from MCP result."""
        if not result or len(result) == 0:
            return str(result)

        first_result = result[0]

        # Try to get text content safely
        try:
            if hasattr(first_result, "text") and first_result.text is not None:
                return first_result.text
        except (AttributeError, TypeError):
            pass

        return str(first_result)

    def health_check(self) -> bool:
        """Check if MCP connection is healthy.

        Returns:
            True if connection is working, False otherwise
        """
        if not self.client:
            return False

        try:
            self._run_async(self.client.ping())
            return True
        except Exception as e:
            log.error(f"[FastMCPToolkit] Health check failed: {e}")
            return False

    def list_available_tools(self) -> List[str]:
        """Get list of available MCP tools.

        Returns:
            List of tool names
        """
        if not self.client:
            return []

        try:
            tools = self._run_async(self.client.list_tools())
            return [tool.name for tool in tools]
        except Exception as e:
            log.error(f"[FastMCPToolkit] Failed to get tools list: {e}")
            return []

    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a specific MCP tool.

        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool

        Returns:
            Tool execution result
        """
        if not self.client:
            return "[Error] No MCP client available"

        try:
            # Parameter mapping for common tools
            mapped_kwargs = self._map_parameters(tool_name, kwargs)

            # Call the tool
            result = self._run_async(self.client.call_tool(tool_name, mapped_kwargs))

            return self._extract_text(result)

        except Exception as e:
            log.error(f"[FastMCPToolkit] Tool call failed for {tool_name}: {e}")
            return f"[Error] {e}"


# Convenience function
def create_fastmcp_toolkit(
    server_source: str, auth_token: Optional[str] = None, debug: bool = False
) -> FastMCPToolkit:
    """Create a FastMCP toolkit instance."""
    return FastMCPToolkit(
        server_source=server_source, auth_token=auth_token, debug=debug
    )
