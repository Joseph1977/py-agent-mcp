#!/usr/bin/env python3
"""
Interactive CLI for the LiteLLM MCP Agent
"""

import asyncio
import argparse
import sys
from agent import LiteLLMAgent

async def interactive_mode():
    """Run the agent in interactive mode."""
    agent = LiteLLMAgent()
    
    try:
        print("\n" + "="*60)
        print("LiteLLM MCP Agent - Interactive Mode")
        print("="*60)
        print("Type 'quit', 'exit', or 'q' to exit")
        print("Type 'tools' to list available MCP tools")
        print("Type 'models' to see example supported models")
        print("-"*60)
        
        while True:
            try:
                # Get user input
                prompt = input("\nEnter your request: ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    break
                
                if prompt.lower() == 'tools':
                    print("\nFetching available MCP tools...")
                    try:
                        tools = await agent._fetch_mcp_tools()
                        print(f"\nAvailable MCP tools ({len(tools)}):")
                        for tool in tools:
                            print(f"  • {tool.name}: {tool.description}")
                    except Exception as e:
                        print(f"❌ Error fetching tools: {e}")
                    continue
                
                if prompt.lower() == 'models':
                    print("\nExample supported models:")
                    print("  • gpt-3.5-turbo")
                    print("  • gpt-4")
                    print("  • gpt-4-turbo")
                    print("  • claude-3-sonnet-20240229")
                    print("  • claude-3-haiku-20240307")
                    print("  • gemini-pro")
                    print("  • ollama/llama2 (if Ollama is running)")
                    continue
                
                if not prompt:
                    continue
                
                # Get model preference
                model = input("Model (press Enter for gpt-3.5-turbo): ").strip()
                if not model:
                    model = "gpt-3.5-turbo"
                
                print(f"\nProcessing with {model}...")
                print("-" * 40)
                
                # Process the request
                result = await agent.process_request(prompt, model)
                
                # Display results
                if not result.get('success'):
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                else:
                    print(f"🤖 Response: {result.get('response', 'No response')}")
                    
                    if result.get('tool_calls_made', 0) > 0:
                        print(f"\n🔧 Tools used: {result['tool_calls_made']}")
                    
                    if result.get('total_tokens'):
                        print(f"\n📊 Tokens used: {result['total_tokens']}")
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
    
    finally:
        print("\nGoodbye! 👋")

async def single_request_mode(prompt: str, model: str):
    """Process a single request and exit."""
    agent = LiteLLMAgent()
    
    try:
        result = await agent.process_request(prompt, model)
        
        # Output as JSON for programmatic usage
        import json
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description="LiteLLM MCP Agent - AI Assistant with MCP Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s -p "What files are in my directory?" -m gpt-4
  %(prog)s --prompt "Analyze this data" --model claude-3-sonnet-20240229
        """
    )
    
    parser.add_argument(
        '-p', '--prompt',
        help='Single prompt to process (non-interactive mode)'
    )
    
    parser.add_argument(
        '-m', '--model',
        default='gpt-3.5-turbo',
        help='Model to use (default: gpt-3.5-turbo)'
    )
    
    parser.add_argument(
        '--mcp-url',
        default='http://localhost:8001/mcp',
        help='MCP server URL (default: http://localhost:8001/mcp)'
    )
    
    args = parser.parse_args()
    
    # Override MCP URL if provided
    if args.mcp_url != 'http://localhost:8001/mcp':
        # This would require modifying the agent initialization
        print(f"Note: Custom MCP URL not yet supported in CLI. Using default.")
    
    try:
        if args.prompt:
            # Single request mode
            asyncio.run(single_request_mode(args.prompt, args.model))
        else:
            # Interactive mode
            asyncio.run(interactive_mode())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
