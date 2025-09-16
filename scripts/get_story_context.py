#!/usr/bin/env python3
"""
Get story context for architecture planning
"""
import sys
import json
sys.path.insert(0, "src")

from database.models import get_user_story_model, get_research_result_model

def main():
    if len(sys.argv) != 2:
        print("Usage: get_story_context.py <story_id>", file=sys.stderr)
        sys.exit(1)
    
    story_id = sys.argv[1]
    story_model = get_user_story_model()
    research_model = get_research_result_model()
    
    # Get story data
    research_id = story_id.split('_story_')[0]
    stories = story_model.get_stories_by_research(research_id)
    story = next((s for s in stories if s['story_id'] == story_id), None)
    
    if not story:
        print(f"No story found for ID: {story_id}", file=sys.stderr)
        sys.exit(1)
    
    # Get research context
    research = research_model.get_result_by_job_id(research_id)
    
    context = {
        "story": story,
        "research": research['generated_content'] if research else ""
    }
    
    print(json.dumps(context))

if __name__ == "__main__":
    main()