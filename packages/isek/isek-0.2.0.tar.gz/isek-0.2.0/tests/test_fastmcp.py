#!/usr/bin/env python3
"""
Test script for FastMCP toolkit
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
from isek.tools.fastmcp_toolkit import fastmcp_tools  # noqa: E402
from isek.utils.log import log  # noqa: E402


def test_fastmcp_basic():
    """Test basic FastMCP functionality"""
    print("=== FastMCP Basic Test ===")

    # Test with GitHub Copilot MCP server
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("❌ GITHUB_TOKEN not set")
        print("Please set GITHUB_TOKEN environment variable")
        print("Example: export GITHUB_TOKEN='your_github_token'")
        return False

    try:
        print("🔧 Using pre-created FastMCP toolkit...")
        toolkit = fastmcp_tools

        print("🔍 Checking connection health...")
        health = toolkit.health_check()
        print(f"Health check result: {health}")

        if health:
            print("✅ Connection successful!")

            print("📋 Listing available tools...")
            tools = toolkit.list_available_tools()
            print(f"Found {len(tools)} tools:")
            for i, tool in enumerate(tools[:5], 1):  # Show first 5 tools
                print(f"  {i}. {tool}")

            if len(tools) > 5:
                print(f"  ... and {len(tools) - 5} more")

            print("\n📝 Listing registered functions...")
            functions = toolkit.list_functions()
            print(f"Registered functions: {functions}")

            return True
        else:
            print("❌ Connection failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        log.error(f"FastMCP test failed: {e}")
        return False


def test_fastmcp_tool_call():
    """Test MCP tool calling"""
    print("\n=== FastMCP Tool Call Test ===")

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN not set, skipping tool call test")
        return False

    try:
        toolkit = fastmcp_tools

        # Get available tools
        tools = toolkit.list_available_tools()
        if not tools:
            print("❌ No tools available")
            return False

        # Try to call the first available tool
        first_tool = tools[0]
        print(f"🔧 Testing tool call: {first_tool}")

        result = toolkit.call_tool(first_tool, test="hello")
        print(f"Tool call result: {result}")

        return True

    except Exception as e:
        print(f"❌ Tool call test failed: {e}")
        return False


def test_github_search_repositories():
    """Test GitHub search_repositories with correct parameters"""
    print("\n=== GitHub Search Repositories Test ===")

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN not set, skipping GitHub test")
        return False

    try:
        toolkit = fastmcp_tools

        # Test with correct parameter name 'query'
        print("🔧 Testing search_repositories with 'query' parameter...")
        result = toolkit.call_tool(
            "search_repositories", query="Python machine learning"
        )
        print(f"Result with 'query': {result}")

        # Test with incorrect parameter name 'q'
        print("\n🔧 Testing search_repositories with 'q' parameter...")
        result = toolkit.call_tool("search_repositories", q="Python machine learning")
        print(f"Result with 'q': {result}")

        return True

    except Exception as e:
        print(f"❌ GitHub search test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting FastMCP Toolkit Tests")
    print("=" * 50)

    # Test basic functionality
    basic_success = test_fastmcp_basic()

    # Test tool calling
    tool_call_success = test_fastmcp_tool_call()

    # Test GitHub search repositories
    github_success = test_github_search_repositories()

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Basic functionality: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"  Tool calling: {'✅ PASS' if tool_call_success else '❌ FAIL'}")
    print(f"  GitHub search: {'✅ PASS' if github_success else '❌ FAIL'}")

    if basic_success and tool_call_success and github_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
