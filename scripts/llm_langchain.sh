#!/bin/bash
# LangChain wrapper script

set -e

# Usage function
usage() {
    echo "Usage: $0 'prompt' [--provider anthropic|openai] [--model MODEL]"
    echo "Example: $0 'Explain what a Python decorator is'"
    exit 1
}

# Check if prompt is provided
if [ $# -eq 0 ]; then
    echo "Error: No prompt provided"
    usage
fi

# Check if we're in the correct directory
if [ ! -d "src/langchain_integration" ]; then
    echo "Error: Script must be run from project root"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Run: python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment and call the Python CLI
source .venv/bin/activate && python scripts/langchain_cli.py "$@"