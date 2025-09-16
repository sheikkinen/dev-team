#!/usr/bin/env python3
"""
View development process results from database
"""
import sys
import json
import argparse
from datetime import datetime
sys.path.insert(0, "src")

from database.models import (
    get_research_result_model, 
    get_user_story_model, 
    get_architecture_model
)

def format_timestamp(ts_str):
    """Format timestamp for display"""
    if not ts_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return ts_str

def view_research(args):
    """View research results"""
    model = get_research_result_model()
    
    if args.id:
        result = model.get_result_by_job_id(args.id)
        if result:
            print(f"Research ID: {result['job_id']}")
            print(f"Topic: {result['research_topic']}")
            print(f"Model: {result['llm_model'] or 'N/A'}")
            print(f"Words: {result['word_count']}")
            print(f"Created: {format_timestamp(result['completion_timestamp'])}")
            print("\nContent:")
            print("-" * 50)
            print(result['generated_content'])
        else:
            print(f"No research found for ID: {args.id}")
    else:
        results = model.list_results(limit=args.limit)
        print(f"{'ID':<20} {'Topic':<30} {'Words':<8} {'Created':<16}")
        print("-" * 76)
        for r in results:
            print(f"{r['job_id']:<20} {r['research_topic'][:28]:<30} {r['word_count']:<8} {format_timestamp(r['completion_timestamp']):<16}")

def view_stories(args):
    """View user stories"""
    model = get_user_story_model()
    
    if args.research_id:
        stories = model.get_stories_by_research(args.research_id)
        print(f"Stories for research: {args.research_id}")
        print(f"{'Story ID':<25} {'Title':<30} {'Priority':<8} {'Status':<10}")
        print("-" * 75)
        for story in stories:
            print(f"{story['story_id']:<25} {story['title'][:28]:<30} {story['priority']:<8} {story['status']:<10}")
            if args.verbose:
                print(f"  Description: {story['description']}")
                if story['components']:
                    print(f"  Components: {', '.join(story['components'])}")
                print()
    else:
        print("Use --research-id to view stories for a specific research")

def view_architecture(args):
    """View architecture versions"""
    model = get_architecture_model()
    
    if args.research_id:
        arch = model.get_latest_architecture(args.research_id)
        if arch:
            print(f"Latest Architecture for: {args.research_id}")
            print(f"Version ID: {arch['version_id']}")
            print(f"Story: {arch['story_id']}")
            print(f"Created: {format_timestamp(arch['created_at'])}")
            print(f"Changes: {arch['changes_summary']}")
            print("\nComponents:")
            for comp in arch['components']:
                print(f"  - {comp['name']}: {comp['purpose']}")
                if comp.get('interfaces'):
                    print(f"    Interfaces: {', '.join(comp['interfaces'])}")
                if comp.get('dependencies'):
                    print(f"    Dependencies: {', '.join(comp['dependencies'])}")
            
            if arch['data_flow']:
                print("\nData Flow:")
                for flow in arch['data_flow']:
                    print(f"  {flow['from']} → {flow['to']}: {flow['data']}")
        else:
            print(f"No architecture found for research: {args.research_id}")
    else:
        print("Use --research-id to view architecture for a specific research")

def main():
    parser = argparse.ArgumentParser(description="View development process results")
    parser.add_argument("type", choices=["research", "stories", "architecture"], 
                       help="Type of results to view")
    parser.add_argument("--id", help="Specific ID to view")
    parser.add_argument("--research-id", help="Research ID for stories/architecture")
    parser.add_argument("--limit", type=int, default=10, help="Limit for list results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        if args.type == "research":
            view_research(args)
        elif args.type == "stories":
            view_stories(args)
        elif args.type == "architecture":
            view_architecture(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()