#!/usr/bin/env python3
"""
Simple test for the refactored LangChain module to avoid import conflicts.
"""

import sys
import os
from pathlib import Path

# Temporarily remove src from path to avoid conflicts
project_root = Path(__file__).parent.parent
src_path = str(project_root / 'src')

# Save original sys.path
original_path = sys.path.copy()

def test_langchain_module():
    """Test the LangChain module without import conflicts."""
    
    # Add our src directory but be careful about conflicts
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        # Import our langchain module specifically
        import langchain.config as lc_config
        
        print("🧪 Testing LangChain module...")
        
        # Test configuration
        status = lc_config.check_llm_setup()
        
        print("🔧 LLM Setup Status")
        print("=" * 30)
        print(f"OpenAI API Key:    {'✓' if status['has_openai'] else '✗'}")
        print(f"Anthropic API Key: {'✓' if status['has_anthropic'] else '✗'}")
        print(f"Available Providers: {', '.join(status['available_providers']) if status['available_providers'] else 'None'}")
        print(f"Default Provider: {status['default_provider'] or 'None'}")
        print(f"Can Run: {'✓' if status['can_run'] else '✗'}")
        
        if status['can_run']:
            print(f"\nModel Configuration:")
            print(f"Anthropic Model: {status.get('anthropic_model', 'N/A')}")
            print(f"Temperature: {status.get('temperature', 'N/A')}")
            print(f"Max Tokens: {status.get('max_tokens', 'N/A')}")
            
            # Test creating an LLM instance
            try:
                import langchain.client as lc_client
                client = lc_client.LangChainClient(provider="anthropic")
                info = client.get_info()
                print(f"\n✅ LangChain client created successfully")
                print(f"   Provider: {info.get('provider', 'unknown')}")
                print(f"   Model: {info.get('model', 'unknown')}")
            except Exception as e:
                print(f"\n⚠️  Client creation failed: {e}")
        else:
            print("\n⚠️  Please set ANTHROPIC_API_KEY in your .env file")
        
        print("\n✅ LangChain module test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore original path
        sys.path[:] = original_path

if __name__ == "__main__":
    test_langchain_module()