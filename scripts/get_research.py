#!/usr/bin/env python3
"""
Get research content by ID for backlog processing
"""
import sys
sys.path.insert(0, "src")

from database.models import get_research_result_model

def main():
    if len(sys.argv) != 2:
        print("Usage: get_research.py <research_id>", file=sys.stderr)
        sys.exit(1)
    
    research_id = sys.argv[1]
    model = get_research_result_model()
    
    result = model.get_result_by_job_id(research_id)
    if result:
        print(result['generated_content'])
    else:
        print(f"No research found for ID: {research_id}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()