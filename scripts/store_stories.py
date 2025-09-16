#!/usr/bin/env python3
"""
Store user stories from backlog processing
"""
import sys
import json
sys.path.insert(0, "src")

from database.models import get_user_story_model

def main():
    if len(sys.argv) != 4:
        print("Usage: store_stories.py <job_id> <research_id> <output_file>", file=sys.stderr)
        sys.exit(1)
    
    job_id = sys.argv[1]
    research_id = sys.argv[2]
    output_file = sys.argv[3]
    
    try:
        with open(output_file, 'r') as f:
            content = f.read().strip()
        
        # Parse JSON output
        stories = json.loads(content)
        
        # Store in database
        model = get_user_story_model()
        story_ids = model.create_stories(research_id, stories)
        
        print(f"Stored {len(story_ids)} stories for research {research_id}")
        for story_id in story_ids:
            print(f"  - {story_id}")
            
    except Exception as e:
        print(f"Error storing stories: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()