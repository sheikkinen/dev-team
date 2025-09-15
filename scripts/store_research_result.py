#!/usr/bin/env python3
"""
Store research result in database
Usage: python store_research_result.py <job_id> <topic> <prompt_file> <output_file>
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database.models import get_research_result_model

def main():
    if len(sys.argv) != 5:
        print("Usage: python store_research_result.py <job_id> <topic> <prompt_file> <output_file>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    topic = sys.argv[2]
    prompt_file = sys.argv[3]
    output_file = sys.argv[4]
    
    try:
        # Read the research output
        with open(output_file, 'r') as f:
            research_output = f.read()
        
        # Read the original prompt
        with open(prompt_file, 'r') as f:
            original_prompt = f.read()
        
        # Get model and store result
        research_model = get_research_result_model()
        
        result_id = research_model.create_result(
            job_id=job_id,
            research_topic=topic,
            generated_content=research_output,
            prompt_used=original_prompt,
            llm_model="langchain",
            metadata=json.dumps({"prompt_file": prompt_file, "output_file": output_file})
        )
        
        word_count = len(research_output.split())
        print(f"✅ Research result stored successfully with ID: {result_id}")
        print(f"📊 Word count: {word_count}")
        print(f"🔗 Job ID: {job_id}")
        
    except Exception as e:
        print(f"❌ Error storing research result: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()