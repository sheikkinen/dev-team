#!/bin/bash
# LangChain wrapper script - Clean shell interface

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage function
usage() {
    echo "Usage: $0 'prompt' [--provider anthropic|openai] [--model MODEL] [--quiet]"
    echo "Example: $0 'Explain what a Python decorator is'"
    echo "Example: $0 'Review this code' --provider openai --model gpt-4o"
    exit 1
}

# Check if prompt is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No prompt provided${NC}"
    usage
fi

# Check if we're in the correct directory
if [ ! -d "src/langchain_integration" ]; then
    echo -e "${RED}Error: Script must be run from project root${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found. Run: python3 -m venv .venv${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 LangChain Wrapper${NC}"

# Activate virtual environment and call the Python CLI
source .venv/bin/activate && python scripts/langchain_cli.py "$@"