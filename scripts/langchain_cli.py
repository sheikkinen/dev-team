#!/usr/bin/env python3
"""
Command-line interface for LangChain integration.
Simple script to handle CLI usage without embedding Python in shell scripts.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_integration import LangChainClient


def main():
    parser = argparse.ArgumentParser(description="LangChain CLI client")
    parser.add_argument("prompt", help="Prompt to send to the LLM")
    parser.add_argument("--provider", choices=["anthropic", "openai"], 
                       default="anthropic", help="LLM provider")
    parser.add_argument("--model", help="Specific model to use")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Only output the response")
    
    args = parser.parse_args()
    
    try:
        client = LangChainClient(provider=args.provider, model=args.model)
        
        if not args.quiet:
            status = client.get_status()
            print(f"🤖 Model: {status['provider']} - {status['model'] or 'default'}")
            prompt_preview = args.prompt[:100] + ('...' if len(args.prompt) > 100 else '')
            print(f"🎯 Prompt: \"{prompt_preview}\"")
            print("🔄 Processing...")
            print("---")
        
        response = client.chat(args.prompt)
        print(response)
        
        if not args.quiet:
            print("---")
            print("✅ Completed")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()