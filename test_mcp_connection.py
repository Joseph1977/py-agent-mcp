#!/usr/bin/env python3
"""
Quick MCP server connection test
"""
import asyncio
import httpx

async def test_mcp_server():
    """Test if MCP server is accessible."""
    server_url = "http://localhost:8001"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health endpoint
            print(f"🔄 Testing MCP server at {server_url}...")
            
            health_response = await client.get(f"{server_url}/health")
            print(f"✅ Health check: {health_response.status_code}")
            print(f"   Response: {health_response.json()}")
            
            # Test info endpoint
            info_response = await client.get(f"{server_url}/info")
            print(f"✅ Info check: {info_response.status_code}")
            print(f"   Response: {info_response.json()}")
            
            return True
            
    except Exception as e:
        print(f"❌ MCP server not accessible: {e}")
        print(f"\n💡 To start your MCP server:")
        print(f"   1. Navigate to your py-mcp-server directory")
        print(f"   2. Run: python run.py")
        print(f"   3. Server should start at http://localhost:8001")
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
