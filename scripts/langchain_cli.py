#!/usr/bin/env python3
"""
Command-line interface for LangChain integration.
Simple script to handle CLI usage without embedding Python in shell scripts.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_integration import LangChainClient


def main():
    parser = argparse.ArgumentParser(description="LangChain CLI client")
    parser.add_argument("prompt", nargs='?', help="Prompt to send to the LLM")
    parser.add_argument("--provider", choices=["anthropic", "openai"], 
                       default="anthropic", help="LLM provider")
    parser.add_argument("--model", help="Specific model to use")
    parser.add_argument("--format", choices=["text", "json"], 
                       default="text", help="Response format")
    parser.add_argument("--type", choices=["chat", "architecture"], 
                       default="chat", help="Request type")
    parser.add_argument("--story-id", help="Story ID for architecture planning")
    
    args = parser.parse_args()
    
    try:
        client = LangChainClient(provider=args.provider, model=args.model)
        
        if args.type == "architecture":
            # Get story context for architecture planning
            if not args.story_id:
                print("Error: --story-id required for architecture planning", file=sys.stderr)
                sys.exit(1)
            
            # Import here to avoid circular imports
            sys.path.insert(0, "src")
            from database.models import get_user_story_model, get_research_result_model
            
            story_model = get_user_story_model()
            research_model = get_research_result_model()
            
            # Get story data
            stories = story_model.get_stories_by_research(args.story_id.split('_story_')[0])
            story = next((s for s in stories if s['story_id'] == args.story_id), None)
            
            if not story:
                print(f"Error: Story not found: {args.story_id}", file=sys.stderr)
                sys.exit(1)
            
            # Get research context
            research = research_model.get_result_by_job_id(story['research_id'])
            research_content = research['generated_content'] if research else ""
            
            # Format story for architecture planning
            story_text = f"Title: {story['title']}\nDescription: {story['description']}\nPriority: {story['priority']}"
            
            # Plan architecture (current_architecture is empty for now)
            response = client.plan_architecture("", research_content, story_text)
            import json
            print(json.dumps(response, indent=2))
            
        elif args.format == "json":
            if not args.prompt:
                print("Error: prompt required for JSON format", file=sys.stderr)
                sys.exit(1)
            response = client.split_into_array(args.prompt)
            import json
            print(json.dumps(response, indent=2))
        else:
            if not args.prompt:
                print("Error: prompt required for chat", file=sys.stderr)
                sys.exit(1)
            response = client.chat(args.prompt)
            print(response)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()