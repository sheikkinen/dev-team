#!/usr/bin/env python3
"""
Simple LangChain Claude wrapper for dev-team project.
Now refactored to use the langchain_integration module.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python langchain_wrapper.py 'your prompt here'")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    try:
        from langchain_integration import load_env, install_dependencies, chat_with_claude
        
        # Load environment
        load_env()
        print("📄 Loaded environment variables")
        
        # Install dependencies if needed
        if not install_dependencies():
            print("❌ Failed to install LangChain dependencies")
            sys.exit(1)
        
        print("🤖 Executing Claude via LangChain...")
        print(f"📝 Model: claude-3-haiku-20240307")
        print(f"🎯 Prompt: \"{prompt[:100]}{'...' if len(prompt) > 100 else ''}\"")
        print("🔄 Processing...")
        print("---")
        
        # Get response
        response = chat_with_claude(prompt)
        print(response)
        
        print("---")
        print("✅ LangChain Claude execution completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()