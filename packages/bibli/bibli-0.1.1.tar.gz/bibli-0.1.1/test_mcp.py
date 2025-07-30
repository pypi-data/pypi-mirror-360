#!/usr/bin/env python3
"""
Test script for the Bible MCP server.

This script demonstrates how to connect to and use the Bible MCP server
from a Python client.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to the path so we can import bibli
sys.path.insert(0, str(Path(__file__).parent))

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def test_bible_mcp_server():
    """Test the Bible MCP server functionality."""

    # Set up server parameters to run the MCP server
    server_params = StdioServerParameters(
        command="python", args=["-m", "bibli", "mcp-server"]
    )

    print("🔌 Connecting to Bible MCP Server...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Successfully connected to Bible MCP Server!")

                # Test 1: List available tools
                print("\n📋 Available Tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"  • {tool.name}: {tool.description}")

                # Test 2: List available resources
                print("\n📚 Available Resources:")
                resources = await session.list_resources()
                for resource in resources.resources:
                    print(f"  • {resource.name}: {resource.description}")

                # Test 3: List available prompts
                print("\n💭 Available Prompts:")
                prompts = await session.list_prompts()
                for prompt in prompts.prompts:
                    print(f"  • {prompt.name}: {prompt.description}")

                # Test 4: Search for verses
                print("\n🔍 Testing verse search...")
                search_result = await session.call_tool(
                    "search_verses", {"query": "love", "limit": 3}
                )
                print("Search results:")
                for content in search_result.content:
                    print(f"  {content.text}")

                # Test 5: Get a specific verse
                print("\n📖 Testing get verse...")
                verse_result = await session.call_tool(
                    "get_verse", {"reference": "John 3:16"}
                )
                print("Verse result:")
                for content in verse_result.content:
                    print(f"  {content.text}")

                # Test 6: Read a resource
                print("\n📋 Testing resource reading...")
                books_resource = await session.read_resource("bible://books")
                print("Books resource preview:")
                print(f"  {books_resource.contents[0].text[:200]}...")

                # Test 7: Get a prompt
                print("\n💭 Testing prompt generation...")
                prompt_result = await session.get_prompt(
                    "verse-explanation",
                    {"verse": "John 3:16", "context_level": "basic"},
                )
                print("Generated prompt:")
                for message in prompt_result.messages:
                    print(f"  {message.content.text[:200]}...")

                print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        raise


if __name__ == "__main__":
    print("🧪 Testing Bible MCP Server")
    print("=" * 50)
    asyncio.run(test_bible_mcp_server())
