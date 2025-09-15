#!/bin/bash

# LLM Claude Wrapper Script
# Usage: llm_claude.sh "Your prompt here"
# This script wraps the claude CLI with predefined options for consistent usage

set -e  # Exit on any error

# Check if prompt is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 \"prompt\""
    echo "Example: $0 \"Analyze this codebase and provide suggestions\""
    exit 1
fi

# Get the prompt from the first argument
prompt="$1"

# Check if claude command is available
if ! command -v claude &> /dev/null; then
    echo "Error: claude CLI is not installed or not in PATH"
    echo "Please install claude CLI first"
    exit 1
fi

# Create docs directory if it doesn't exist
if [ ! -d "./docs" ]; then
    mkdir -p "./docs"
    echo "Created ./docs directory"
fi

# Execute claude with the specified options
echo "🤖 Executing Claude with prompt: \"$prompt\""
echo "✅ Permission mode: acceptEdits"
echo "---"

claude --add-dir ./docs --allowed-tools "Bash, Glob, Grep, Read, Write, Edit, MultiEdit, WebFetch, TodoWrite, Task" --permission-mode acceptEdits -p "$prompt"

echo "---"
echo "✅ Claude execution completed"