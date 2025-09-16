#!/usr/bin/env python3
"""
Store architecture from planning process
"""
import sys
import json
sys.path.insert(0, "src")

from database.models import get_architecture_model

def main():
    if len(sys.argv) != 4:
        print("Usage: store_architecture.py <job_id> <story_id> <output_file>", file=sys.stderr)
        sys.exit(1)
    
    job_id = sys.argv[1]
    story_id = sys.argv[2]
    output_file = sys.argv[3]
    
    try:
        with open(output_file, 'r') as f:
            content = f.read().strip()
        
        # Parse JSON output
        architecture_data = json.loads(content)
        
        # Extract research_id from story_id
        research_id = story_id.split('_story_')[0]
        
        # Store in database
        model = get_architecture_model()
        version_id = model.create_version(story_id, research_id, architecture_data)
        
        print(f"Stored architecture version: {version_id}")
        print(f"Components: {len(architecture_data.get('components', []))}")
        print(f"Data flows: {len(architecture_data.get('data_flow', []))}")
            
    except Exception as e:
        print(f"Error storing architecture: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()