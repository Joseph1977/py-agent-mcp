"""
Example usage of the LiteLLM MCP Agent
"""

import asyncio
from agent import LiteLLMAgent

async def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    agent = LiteLLMAgent()
    await agent.initialize()
    
    try:
        # Simple request
        result = await agent.process_request(
            prompt="Hello! What can you help me with?",
            model_id="gpt-3.5-turbo"
        )
        
        print(f"Response: {result.get('response')}")
        
    finally:
        await agent.close()

async def example_with_tools():
    """Example that might trigger tool usage."""
    print("\n=== Tool Usage Example ===")
    
    agent = LiteLLMAgent()
    await agent.initialize()
    
    try:
        # Request that might use tools
        result = await agent.process_request(
            prompt="Can you help me list files in the current directory and read a configuration file?",
            model_id="gpt-4"
        )
        
        print(f"Response: {result.get('response')}")
        
        if result.get('tool_calls'):
            print(f"\nTools used: {len(result['tool_calls'])}")
            for call in result['tool_calls']:
                print(f"  - {call['tool']}: {call['arguments']}")
        
        if result.get('final_response'):
            print(f"\nFinal response: {result['final_response']}")
        
    finally:
        await agent.close()

async def example_different_models():
    """Example using different models."""
    print("\n=== Different Models Example ===")
    
    models = ["gpt-3.5-turbo", "gpt-4"]  # Add more models as needed
    prompt = "Explain what you can do in one sentence."
    
    agent = LiteLLMAgent()
    await agent.initialize()
    
    try:
        for model in models:
            print(f"\n--- Using {model} ---")
            result = await agent.process_request(prompt, model)
            
            if result.get('error'):
                print(f"Error with {model}: {result['error']}")
            else:
                print(f"Response: {result.get('response')}")
                print(f"Tokens: {result.get('total_tokens', 'N/A')}")
                
    finally:
        await agent.close()

async def main():
    """Run all examples."""
    await example_basic_usage()
    await example_with_tools()
    await example_different_models()

if __name__ == "__main__":
    asyncio.run(main())
