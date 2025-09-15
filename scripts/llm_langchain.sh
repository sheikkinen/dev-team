#!/bin/bash
# LangChain Claude wrapper script
# Uses the langchain_integration module for consistent integration

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Usage function
usage() {
    echo "Usage: $0 'prompt'"
    echo "Example: $0 'Explain what a Python decorator is'"
    exit 1
}

# Check if prompt is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No prompt provided${NC}"
    usage
fi

PROMPT="$1"

# Check if we're in the correct directory
if [ ! -f "src/langchain_wrapper.py" ]; then
    echo -e "${RED}Error: Script must be run from project root (langchain_wrapper.py not found)${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found. Run: python3 -m venv .venv${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 LangChain Claude Wrapper${NC}"
echo -e "${BLUE}📍 Using virtual environment and langchain_integration module${NC}"

# Activate virtual environment and execute the Python wrapper
source .venv/bin/activate && python src/langchain_wrapper.py "$PROMPT"