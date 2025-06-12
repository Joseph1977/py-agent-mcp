#!/usr/bin/env python3
"""
LiteLLM MCP Agent - Working Implementation
Based on the test_mcp_client.py pattern from Joseph1977/py-mcp-server
"""
import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool with its schema"""
    name: str
    description: str
    input_schema: dict


class LiteLLMAgent:
    """
    LiteLLM Agent that integrates with MCP tools.
    
    This agent:
    1. Connects to an MCP server to fetch available tools
    2. Converts MCP tools to LiteLLM function format
    3. Calls LiteLLM with the tools and user request
    4. Executes any tool calls on the MCP server
    5. Returns the final response
    """
    
    def __init__(
        self,
        mcp_server_url: str = None,
        litellm_base_url: str = None,
        litellm_api_key: str = None
    ):
        self.mcp_server_url = mcp_server_url or os.getenv("MCP_SERVER_URL", "http://localhost:8001/mcp")
        self.litellm_base_url = litellm_base_url or os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        self.litellm_api_key = litellm_api_key or os.getenv("LITELLM_API_KEY", "sk-1234")
        
        self.mcp_tools: List[MCPTool] = []
        logger.info(f"Initialized LiteLLMAgent with MCP server: {self.mcp_server_url}")
        logger.info(f"LiteLLM server: {self.litellm_base_url}")

    async def _fetch_mcp_tools(self) -> List[MCPTool]:
        """Fetch available tools from the MCP server using the official MCP client"""
        try:
            logger.info(f"Connecting to MCP server at {self.mcp_server_url}")
            
            # Use the same pattern as test_mcp_client.py from the GitHub repo
            async with streamablehttp_client(self.mcp_server_url) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    # Initialize the MCP session
                    logger.info("Initializing MCP session...")
                    await session.initialize()
                    logger.info("✅ MCP session initialized successfully!")
                    
                    # List available tools
                    logger.info("📋 Fetching available tools...")
                    tools_response = await session.list_tools()
                    
                    mcp_tools = []
                    for tool in tools_response.tools:
                        # Convert MCP tool to our internal format
                        input_schema = {}
                        if hasattr(tool, 'inputSchema') and tool.inputSchema:
                            # Convert the MCP input schema to dict
                            if hasattr(tool.inputSchema, '__dict__'):
                                input_schema = tool.inputSchema.__dict__
                            else:
                                input_schema = dict(tool.inputSchema)
                        
                        mcp_tool = MCPTool(
                            name=tool.name,
                            description=tool.description,
                            input_schema=input_schema
                        )
                        mcp_tools.append(mcp_tool)
                        
                        logger.info(f"  - {tool.name}: {tool.description}")
                    
                    logger.info(f"✅ Found {len(mcp_tools)} MCP tools")
                    return mcp_tools
                    
        except Exception as e:
            logger.error(f"Failed to fetch MCP tools: {e}")
            raise

    async def _execute_mcp_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool on the MCP server"""
        try:
            logger.info(f"Executing MCP tool: {tool_name} with args: {arguments}")
            
            async with streamablehttp_client(self.mcp_server_url) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    
                    # Call the tool
                    result = await session.call_tool(tool_name, arguments)
                    
                    # Extract the result content
                    if result.content:
                        # Return the text content from the first content item
                        return {"result": result.content[0].text if result.content[0].text else str(result.content[0])}
                    else:
                        return {"result": "Tool executed successfully but returned no content"}
                        
        except Exception as e:
            logger.error(f"Failed to execute MCP tool {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}

    def _convert_mcp_tools_to_litellm(self, mcp_tools: List[MCPTool]) -> List[dict]:
        """Convert MCP tools to LiteLLM function format"""
        litellm_functions = []
        
        for tool in mcp_tools:
            # Convert MCP tool schema to LiteLLM function format
            function_def = {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema if tool.input_schema else {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            litellm_functions.append(function_def)
            
        logger.info(f"Converted {len(litellm_functions)} MCP tools to LiteLLM format")
        return litellm_functions

    async def _call_litellm(
        self, 
        messages: List[dict], 
        model: str = "gpt-3.5-turbo",
        functions: List[dict] = None
    ) -> dict:
        """Call LiteLLM server with the request"""
        try:
            url = f"{self.litellm_base_url}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.litellm_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": messages
            }
            
            if functions:
                data["functions"] = functions
                data["function_call"] = "auto"
            
            logger.info(f"Calling LiteLLM at {url} with model {model}")
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data, timeout=60.0)
                
                if response.status_code != 200:
                    logger.error(f"LiteLLM request failed: {response.status_code} - {response.text}")
                    raise Exception(f"LiteLLM request failed: {response.status_code}")
                
                result = response.json()
                logger.info("✅ LiteLLM request successful")
                return result
                
        except Exception as e:
            logger.error(f"Failed to call LiteLLM: {e}")
            raise

    async def process_request(
        self, 
        request: str, 
        model: str = "gpt-3.5-turbo",
        max_tool_calls: int = 5
    ) -> dict:
        """
        Process a user request with MCP tools integration
        
        Args:
            request: User's request/prompt
            model: LiteLLM model to use
            max_tool_calls: Maximum number of tool calls to prevent infinite loops
            
        Returns:
            dict: Response with final answer and execution details
        """
        try:
            # 1. Fetch MCP tools
            logger.info("🔧 Fetching MCP tools...")
            self.mcp_tools = await self._fetch_mcp_tools()
            
            # 2. Convert tools for LiteLLM
            litellm_functions = self._convert_mcp_tools_to_litellm(self.mcp_tools)
            
            # 3. Prepare messages
            messages = [
                {"role": "user", "content": request}
            ]
            
            tool_call_count = 0
            
            # 4. Main conversation loop
            while tool_call_count < max_tool_calls:
                # Call LiteLLM
                logger.info(f"🤖 Calling LiteLLM (attempt {tool_call_count + 1})")
                llm_response = await self._call_litellm(
                    messages=messages,
                    model=model,
                    functions=litellm_functions if litellm_functions else None
                )
                
                # Get the assistant's response
                choice = llm_response.get("choices", [{}])[0]
                message = choice.get("message", {})
                
                # Add assistant message to conversation
                messages.append(message)
                
                # Check if the assistant wants to call a function
                function_call = message.get("function_call")
                if not function_call:
                    # No function call, return the final response
                    logger.info("✅ Request completed - no tool calls needed")
                    return {
                        "success": True,
                        "response": message.get("content", ""),
                        "tool_calls_made": tool_call_count,
                        "total_tokens": llm_response.get("usage", {}).get("total_tokens", 0)
                    }
                
                # Execute the function call
                tool_call_count += 1
                function_name = function_call.get("name")
                function_args_str = function_call.get("arguments", "{}")
                
                try:
                    function_args = json.loads(function_args_str)
                except json.JSONDecodeError:
                    function_args = {}
                
                logger.info(f"🔧 Executing tool: {function_name}")
                
                # Execute the MCP tool
                tool_result = await self._execute_mcp_tool(function_name, function_args)
                logger.info(f"MCP Tool Result ({function_name}): {json.dumps(tool_result, indent=2)}")

                # Add function result to conversation
                function_message = {
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(tool_result)
                }
                messages.append(function_message)
                
                logger.info(f"✅ Tool {function_name} executed successfully")
            
            # Max tool calls reached
            logger.warning(f"Maximum tool calls ({max_tool_calls}) reached")
            return {
                "success": False,
                "error": f"Maximum tool calls ({max_tool_calls}) reached",
                "tool_calls_made": tool_call_count,
                "partial_response": messages[-1].get("content", "") if messages else ""
            }
            
        except Exception as e:
            logger.error(f"Failed to process request: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_calls_made": tool_call_count if 'tool_call_count' in locals() else 0
            }


# Example usage and testing
async def main():
    """Example usage of the LiteLLMAgent"""
    agent = LiteLLMAgent()
    
    # Test request
    test_request = "What's the weather like in San Francisco?"
    
    print(f"🚀 Testing LiteLLM MCP Agent")
    print(f"Request: {test_request}")
    print("=" * 50)
    
    result = await agent.process_request(test_request)
    
    print("\n📋 Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
