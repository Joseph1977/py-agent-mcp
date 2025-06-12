#!/usr/bin/env python3
"""
Simple test to verify MCP connection using the working pattern
"""
import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def test_mcp_basic():
    """Test basic MCP connection and tool listing"""
    server_url = "http://localhost:8001/mcp"
    
    try:
        print(f"🔗 Connecting to MCP server at {server_url}")
        
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                print("📋 Initializing MCP session...")
                await session.initialize()
                print("✅ MCP session initialized successfully!")
                
                # List available tools
                print("\n🔧 Listing available tools...")
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} tools:")
                
                for i, tool in enumerate(tools.tools, 1):
                    print(f"  {i}. {tool.name}")
                    print(f"     Description: {tool.description}")
                    
                    # Show input schema
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        schema = tool.inputSchema
                        if hasattr(schema, 'properties') and schema.properties:
                            print(f"     Parameters: {list(schema.properties.keys())}")
                    print()
                
                # Test calling the weather tool
                if any(tool.name == "weather" for tool in tools.tools):
                    print("🌤️ Testing weather tool...")
                    try:
                        result = await session.call_tool("weather", {"location": "San Francisco, CA"})
                        print(f"✅ Weather result: {result.content[0].text[:200] if result.content else 'No content'}...")
                    except Exception as e:
                        print(f"❌ Weather tool error: {e}")
                
                print("\n🎉 MCP test completed successfully!")
                return True
                
    except Exception as e:
        print(f"❌ MCP test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_basic())
    if success:
        print("✅ MCP connection working correctly!")
    else:
        print("❌ MCP connection failed!")
