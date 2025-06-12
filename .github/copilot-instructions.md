<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# LiteLLM MCP Agent Project Instructions

This project is a Python-based AI agent that integrates LiteLLM with Model Context Protocol (MCP) tools.

## Project Structure
- `agent.py` - Main agent class that handles LiteLLM and MCP integration
- `cli.py` - Command-line interface for interactive and batch usage
- `examples.py` - Usage examples and demonstrations
- `requirements.txt` - Python dependencies

## Key Components
- **LiteLLMAgent**: Main class that processes requests using LiteLLM with MCP tools
- **MCPClient**: Handles communication with MCP server at localhost:8001/mcp
- **MCPTool**: Data class representing MCP tools and their schemas

## Development Guidelines
- Use async/await patterns for all LiteLLM and HTTP operations
- Handle errors gracefully with proper logging
- Follow type hints and dataclass patterns established in the codebase
- Ensure compatibility with various LiteLLM-supported models (OpenAI, Anthropic, Google, etc.)
- Use environment variables for API keys and configuration

## MCP Integration
- Tools are fetched dynamically from the MCP server
- MCP tool schemas are converted to LiteLLM function calling format
- Tool calls are executed on the MCP server and results integrated into the conversation

You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt
