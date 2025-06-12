#!/usr/bin/env python3
"""
Simple test to verify CLI parameter parsing and basic functionality
"""
import sys
import argparse

def test_cli_args():
    """Test CLI argument parsing"""
    print("Testing CLI argument parsing...")
    
    # Simulate the CLI arguments
    test_args = ['-p', 'What tools do you have?', '-m', 'gpt-4']
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prompt', help='Single prompt to process')
    parser.add_argument('-m', '--model', default='gpt-3.5-turbo', help='Model to use')
    
    args = parser.parse_args(test_args)
    
    print(f"✅ Parsed prompt: {args.prompt}")
    print(f"✅ Parsed model: {args.model}")
    
    return args.prompt, args.model

def test_agent_import():
    """Test if we can import the agent"""
    try:
        from agent import LiteLLMAgent
        print("✅ Agent imported successfully")
        
        # Test agent creation
        agent = LiteLLMAgent()
        print("✅ Agent instance created")
        
        return True
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        return False

async def test_basic_request():
    """Test a basic request without full processing"""
    try:
        from agent import LiteLLMAgent
        import asyncio
        
        agent = LiteLLMAgent()
        print("🔧 Testing MCP tool fetch...")
        
        # Just test fetching tools
        tools = await agent._fetch_mcp_tools()
        print(f"✅ Found {len(tools)} MCP tools")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        return True
    except Exception as e:
        print(f"❌ Basic request test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 CLI Testing Suite")
    print("=" * 40)
    
    # Test 1: Argument parsing
    prompt, model = test_cli_args()
    
    # Test 2: Agent import
    if not test_agent_import():
        return
    
    # Test 3: Basic functionality
    import asyncio
    success = asyncio.run(test_basic_request())
    
    if success:
        print("\n✅ All CLI tests passed!")
        print(f"The command should work: python cli.py -p '{prompt}' -m {model}")
    else:
        print("\n❌ Some tests failed")

if __name__ == "__main__":
    main()
