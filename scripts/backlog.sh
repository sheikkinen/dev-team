#!/bin/bash

# Backlog Script
# Usage: backlog.sh <research_id> <prompt_file> [job_id]
# Takes research from database, splits into user stories using LLM

set -e

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage: $0 <research_id> <prompt_file> [job_id]"
    exit 1
fi

research_id="$1"
prompt_file="$2"
job_id="${3:-unknown}"

if [ ! -f "$prompt_file" ]; then
    echo "Error: Prompt file '$prompt_file' does not exist"
    exit 1
fi

echo "📋 Starting backlog processing for research: '$research_id'"
echo "📄 Using prompt file: '$prompt_file'"
echo "🆔 Job ID: '$job_id'"
echo "---"

# Get research content from database
research_content=$(python scripts/get_research.py "$research_id")

if [ -z "$research_content" ]; then
    echo "Error: No research found for ID '$research_id'"
    exit 1
fi

# Process prompt template with research content using Python for multiline handling
temp_prompt_file=$(mktemp)
python3 -c "
import sys
with open('$prompt_file', 'r') as f:
    template = f.read()
research = '''$research_content'''
result = template.replace('{RESEARCH}', research)
with open('$temp_prompt_file', 'w') as f:
    f.write(result)
"


echo "📋 Generated backlog prompt"
echo "---"

# Use LangChain CLI with JSON format
echo "🤖 Running LLM to split stories..."

temp_output_file=$(mktemp)
python scripts/langchain_cli.py "$(cat "$temp_prompt_file")" --format json > "$temp_output_file" 2>&1

# Display the output
cat "$temp_output_file"

# Store stories in database
echo "---"
echo "💾 Storing stories in database..."

python scripts/store_stories.py "$job_id" "$research_id" "$temp_output_file"

rm "$temp_prompt_file"
rm "$temp_output_file"

echo "---"
echo "✅ Backlog processing completed"
echo "🔗 Job ID: '$job_id'"