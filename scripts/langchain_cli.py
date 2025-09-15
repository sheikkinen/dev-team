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
    
    args = parser.parse_args()
    
    try:
        client = LangChainClient(provider=args.provider, model=args.model)
        response = client.chat(args.prompt)
        print(response)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()