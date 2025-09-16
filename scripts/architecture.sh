#!/bin/bash

# Architecture Script
# Usage: architecture.sh <story_id> <prompt_file> [job_id]
# Takes user story and current architecture, plans incremental architecture updates

set -e

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage: $0 <story_id> <prompt_file> [job_id]"
    exit 1
fi

story_id="$1"
prompt_file="$2"
job_id="${3:-unknown}"

if [ ! -f "$prompt_file" ]; then
    echo "Error: Prompt file '$prompt_file' does not exist"
    exit 1
fi

echo "🏗️ Starting architecture planning for story: '$story_id'"
echo "📄 Using prompt file: '$prompt_file'"
echo "🆔 Job ID: '$job_id'"
echo "---"

# Get user story and context from database
story_data=$(python scripts/get_story_context.py "$story_id")

if [ -z "$story_data" ]; then
    echo "Error: No story context found for ID '$story_id'"
    exit 1
fi

echo "📋 Retrieved story context"
echo "---"

# Use LangChain CLI with architecture planning
echo "🤖 Running LLM to plan architecture..."

temp_output_file=$(mktemp)
python scripts/langchain_cli.py --type architecture --story-id "$story_id" > "$temp_output_file" 2>&1

# Display the output
cat "$temp_output_file"

# Store architecture in database
echo "---"
echo "💾 Storing architecture in database..."

python scripts/store_architecture.py "$job_id" "$story_id" "$temp_output_file"

rm "$temp_output_file"

echo "---"
echo "✅ Architecture planning completed"
echo "🔗 Job ID: '$job_id'"