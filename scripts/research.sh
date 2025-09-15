#!/bin/bash

# Research Script
# Usage: research.sh <topic> <prompt_file>
# This script takes a topic and prompt file, substitutes the topic placeholder, and runs llm_langchain

set -e  # Exit on any error

# Check if required arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <topic> <prompt_file>"
    echo "Example: $0 'Mastermind Game Development' prompts/research_prompt.md"
    exit 1
fi

# Get arguments
topic="$1"
prompt_file="$2"

# Check if prompt file exists
if [ ! -f "$prompt_file" ]; then
    echo "Error: Prompt file '$prompt_file' does not exist"
    exit 1
fi

# Check if llm_langchain.sh exists
if [ ! -f "./scripts/llm_langchain.sh" ]; then
    echo "Error: llm_langchain.sh script not found at ./scripts/llm_langchain.sh"
    exit 1
fi

echo "🔍 Starting research on topic: '$topic'"
echo "📄 Using prompt file: '$prompt_file'"
echo "---"

# Read the prompt file and substitute the topic placeholder
prompt_content=$(cat "$prompt_file" | sed "s/{TOPIC}/$topic/g")

# Create a temporary file with the processed prompt
temp_prompt_file=$(mktemp)
echo "$prompt_content" > "$temp_prompt_file"

echo "📋 Generated research prompt:"
echo "$prompt_content"
echo "---"

# Execute llm_langchain with the processed prompt
echo "🤖 Running LLM LangChain with research prompt..."
./scripts/llm_langchain.sh "$(cat "$temp_prompt_file")"

# Clean up temporary file
rm "$temp_prompt_file"

echo "---"
echo "✅ Research completed for topic: '$topic'"