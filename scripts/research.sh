#!/bin/bash

# Research Script
# Usage: research.sh <topic> <prompt_file> [job_id]
# This script takes a topic and prompt file, substitutes the topic placeholder, runs llm_langchain,
# and stores the result in the database

set -e  # Exit on any error

# Check if required arguments are provided
if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage: $0 <topic> <prompt_file> [job_id]"
    echo "Example: $0 'Mastermind Game Development' prompts/research_prompt.md research_abc123"
    exit 1
fi

# Get arguments
topic="$1"
prompt_file="$2"
job_id="${3:-unknown}"  # Default to 'unknown' if not provided

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
echo "🆔 Job ID: '$job_id'"
echo "---"

# Read the prompt file and substitute the topic placeholder
prompt_content=$(cat "$prompt_file" | sed "s/{TOPIC}/$topic/g")

# Create a temporary file with the processed prompt
temp_prompt_file=$(mktemp)
echo "$prompt_content" > "$temp_prompt_file"

echo "📋 Generated research prompt:"
echo "$prompt_content"
echo "---"

# Execute llm_langchain with the processed prompt and capture output
echo "🤖 Running LLM LangChain with research prompt..."

# Create temporary file for output
temp_output_file=$(mktemp)
./scripts/llm_langchain.sh "$(cat "$temp_prompt_file")" > "$temp_output_file" 2>&1

# Display the output
cat "$temp_output_file"

# Store the result in the database
echo "---"
echo "💾 Storing research result in database..."

# Use the separate Python script to store the result
python scripts/store_research_result.py "$job_id" "$topic" "$prompt_file" "$temp_output_file"

# Clean up temporary files
rm "$temp_prompt_file"
rm "$temp_output_file"

echo "---"
echo "✅ Research completed for topic: '$topic'"
echo "🔗 Job ID: '$job_id'"