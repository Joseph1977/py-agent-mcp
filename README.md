# LiteLLM MCP Agent

A Python agent that integrates [LiteLLM](https://github.com/BerriAI/litellm) with Model Context Protocol (MCP) tools, enabling AI models to access and use tools from an MCP server.

This project demonstrates how to bridge LiteLLM's multi-model support with MCP's tool ecosystem, creating a powerful AI agent that can dynamically discover and execute tools.

## Features

- 🤖 **LiteLLM Integration**: Support for multiple AI models via LiteLLM server
- 🔧 **MCP Tools**: Dynamic tool discovery and execution from MCP server
- 💬 **Interactive CLI**: Command-line interface for easy interaction
- 🔄 **Async Operations**: Efficient async/await patterns for better performance
- 📝 **Type Safety**: Full type hints and structured error handling
- 🧪 **Test Suite**: Comprehensive testing utilities for debugging

## Prerequisites & Setup

### 1. MCP Server
You need an MCP server running at `http://localhost:8001/mcp`. We recommend using:

**[Joseph1977/py-mcp-server](https://github.com/Joseph1977/py-mcp-server)** - A production-ready MCP server with weather and web search tools.

```bash
# Clone and setup the MCP server
git clone https://github.com/Joseph1977/py-mcp-server.git
cd py-mcp-server
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python run.py  # Starts server at http://localhost:8001
```

### 2. LiteLLM Server
You need LiteLLM server running at `http://localhost:4000`. Install from:

**[BerriAI/litellm](https://github.com/BerriAI/litellm)** - Universal LLM API proxy.

```bash
# Install LiteLLM
pip install litellm[proxy]

# Start LiteLLM server
litellm --config your_config.yaml  # Starts at http://localhost:4000
```

### 3. This Agent
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your LiteLLM API key and server URLs
```

## Quick Start

1. **Verify servers are running**:
   ```bash
   python test_mcp_connection.py  # Test MCP server
   ```

2. **Run the agent**:
   ```bash
   # Interactive mode
   python cli.py

   # Single request
   python cli.py -p "What's the weather in Paris?" -m gpt-3.5-turbo

   # Run examples
   python examples.py
   ```

## Usage Examples

### Programmatic Usage
```python
import asyncio
from agent import LiteLLMAgent

async def main():
    agent = LiteLLMAgent()
    
    # Process request with automatic tool usage
    result = await agent.process_request(
        request="What's the weather in Tokyo?",
        model="gpt-3.5-turbo"
    )
    
    print(f"Response: {result['response']}")
    print(f"Success: {result['success']}")
    print(f"Tools used: {result['tool_calls_made']}")

asyncio.run(main())
```

### CLI Usage
```bash
# Interactive mode - start a conversation session
python cli.py

# Single request mode
python cli.py -p "Search for Python tutorials" -m gpt-3.5-turbo

# Use different models
python cli.py -p "Help me with data analysis" -m gpt-4
python cli.py -p "What tools are available?" -m claude-3-sonnet-20240229

# Get help
python cli.py --help
```

### Testing & Debugging
```bash
# Test MCP server connection
python test_mcp_connection.py

# Test basic MCP functionality
python test_mcp_basic.py

# Test CLI functionality
python test_cli.py
```

### Available Commands in Interactive Mode
- Type any request to get AI assistance with available tools
- `tools` - List all available MCP tools
- `models` - Show supported LiteLLM models  
- `quit` or `exit` - Exit the session

## Configuration

### Environment Variables (.env)
```bash
# LiteLLM Server Configuration (Required)
LITELLM_BASE_URL=http://localhost:4000
LITELLM_API_KEY=your_litellm_api_key

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8001/mcp

# Optional: Provider API Keys (if using direct model access)
OPENAI_API_KEY=sk-your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
```

### LiteLLM Server Setup
The agent requires a LiteLLM server running with authentication. Example config:

```yaml
# litellm_config.yaml
model_list:
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: your_openai_key
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: your_openai_key

general_settings:
  master_key: your_master_key  # This becomes your LITELLM_API_KEY
```

Start with: `litellm --config litellm_config.yaml`

## Architecture

```
User Request
     ↓
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    MCP      │───→│  LiteLLM     │───→│  AI Model   │
│   Agent     │    │  Server      │    │(GPT/Claude) │
└─────────────┘    └──────────────┘    └─────────────┘
     ↓                                          ↓
┌─────────────┐    ┌──────────────┐    Function Calls
│ MCP Client  │───→│  MCP Server  │           ↓
│             │    │   (Tools)    │    ┌─────────────┐
└─────────────┘    └──────────────┘    │Tool Results │
     ↑                                 └─────────────┘
     └─────────── Response Integration ←─────────────┘
```

### Flow:
1. **Request Processing**: Agent receives user request and model ID
2. **Tool Discovery**: Connects to MCP server to fetch available tools
3. **LiteLLM Call**: Sends request to LiteLLM server with tools as functions
4. **Tool Execution**: If AI decides to use tools, executes them via MCP server
5. **Response Integration**: Combines AI response with tool results

### Key Components
- **`LiteLLMAgent`**: Main orchestrator class
- **MCP Integration**: Uses official MCP SDK for tool discovery and execution
- **Error Handling**: Comprehensive error handling for network and API issues

## Supported Models

The agent supports any model available in your LiteLLM server configuration:

- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`, `gpt-4o`
- **Anthropic**: `claude-3-sonnet-20240229`, `claude-3-opus-20240229`, `claude-3-haiku-20240307`
- **Google**: `gemini-pro`, `gemini-pro-vision`, `gemini-1.5-pro`
- **Local Models**: Via Ollama, Llama.cpp, or other local providers
- **Many others**: See [LiteLLM documentation](https://docs.litellm.ai/docs/providers)

Model availability depends on your LiteLLM server configuration and API keys.

## Project Structure

```
├── agent.py                 # Main LiteLLMAgent implementation
├── cli.py                   # Interactive command-line interface
├── examples.py              # Usage examples and demonstrations
├── requirements.txt         # Python dependencies
├── .env.example            # Environment configuration template
├── test_mcp_connection.py  # MCP server connectivity test
├── test_mcp_basic.py       # Basic MCP functionality test
├── test_cli.py             # CLI functionality test
└── README.md               # This documentation
```

## Dependencies

- **[mcp>=1.9.3](https://pypi.org/project/mcp/)** - Official Model Context Protocol SDK
- **[httpx](https://httpx.encode.io/)** - Async HTTP client for API calls
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** - Environment variable management
- **Python 3.8+** - With async/await support

## Related Projects

This agent is designed to work with:

- **[Joseph1977/py-mcp-server](https://github.com/Joseph1977/py-mcp-server)** - Production-ready MCP server with weather, web search, and extensible tool framework
- **[BerriAI/litellm](https://github.com/BerriAI/litellm)** - Universal LLM API that provides unified interface for 100+ LLMs
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Open standard for connecting AI assistants to data sources and tools

## Troubleshooting

### Common Issues

1. **"MCP server not accessible"**
   ```bash
   # Test MCP server
   python test_mcp_connection.py
   # Ensure py-mcp-server is running at http://localhost:8001
   ```

2. **"LiteLLM authentication failed"**  
   - Check `LITELLM_API_KEY` in `.env`
   - Verify LiteLLM server is running at `http://localhost:4000`
   - Ensure API key matches your LiteLLM server config

3. **"No tools found"**
   ```bash
   # Test basic MCP functionality
   python test_mcp_basic.py
   ```

4. **Import/dependency errors**
   ```bash
   # Ensure MCP SDK is latest version
   pip install --upgrade mcp
   pip install -r requirements.txt
   ```

### Debug Mode
```bash
# Enable verbose logging
export LITELLM_LOG=DEBUG
python cli.py -p "test request" -m gpt-3.5-turbo
```

### Testing
```bash
# Test all components
python test_mcp_connection.py  # MCP server connectivity
python test_mcp_basic.py       # MCP tool discovery and calling
python test_cli.py             # CLI functionality
python examples.py             # Full examples
```

## Development

### Adding New Features
1. Follow async/await patterns for all operations
2. Use proper type hints and error handling  
3. Test with multiple models and tool combinations
4. Update examples and documentation

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

- **Joseph Benraz** - Creator and developer of this LiteLLM MCP Agent integration
- **[Model Context Protocol](https://modelcontextprotocol.io/)** by Anthropic for the open standard
- **[Joseph1977/py-mcp-server](https://github.com/Joseph1977/py-mcp-server)** for the excellent MCP server implementation
- **[BerriAI/litellm](https://github.com/BerriAI/litellm)** for the universal LLM proxy solution
