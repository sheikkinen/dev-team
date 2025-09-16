#!/usr/bin/env python3
"""
Export development process results to various formats
"""
import sys
import json
import argparse
from pathlib import Path
sys.path.insert(0, "src")

from database.models import (
    get_research_result_model, 
    get_user_story_model, 
    get_architecture_model
)

def export_json(research_id, output_file):
    """Export full project data as JSON"""
    research_model = get_research_result_model()
    story_model = get_user_story_model()
    arch_model = get_architecture_model()
    
    # Get all data
    research = research_model.get_result_by_job_id(research_id)
    stories = story_model.get_stories_by_research(research_id)
    architecture = arch_model.get_latest_architecture(research_id)
    
    export_data = {
        "research": research,
        "stories": stories,
        "architecture": architecture,
        "export_timestamp": "2025-01-30T00:00:00Z"  # Current time would be better
    }
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"Exported project data to: {output_file}")

def export_markdown(research_id, output_file):
    """Export project documentation as Markdown"""
    research_model = get_research_result_model()
    story_model = get_user_story_model()
    arch_model = get_architecture_model()
    
    research = research_model.get_result_by_job_id(research_id)
    stories = story_model.get_stories_by_research(research_id)
    architecture = arch_model.get_latest_architecture(research_id)
    
    md_content = []
    
    if research:
        md_content.append(f"# {research['research_topic']}")
        md_content.append("")
        md_content.append("## Research Overview")
        md_content.append(research['generated_content'])
        md_content.append("")
    
    if stories:
        md_content.append("## User Stories")
        md_content.append("")
        for story in stories:
            md_content.append(f"### {story['title']} (Priority: {story['priority']})")
            md_content.append(story['description'])
            if story['components']:
                md_content.append(f"**Components:** {', '.join(story['components'])}")
            md_content.append("")
    
    if architecture:
        md_content.append("## Architecture")
        md_content.append("")
        md_content.append(f"**Changes:** {architecture['changes_summary']}")
        md_content.append("")
        
        md_content.append("### Components")
        for comp in architecture['components']:
            md_content.append(f"- **{comp['name']}**: {comp['purpose']}")
            if comp.get('interfaces'):
                md_content.append(f"  - Interfaces: {', '.join(comp['interfaces'])}")
            if comp.get('dependencies'):
                md_content.append(f"  - Dependencies: {', '.join(comp['dependencies'])}")
        md_content.append("")
        
        if architecture['data_flow']:
            md_content.append("### Data Flow")
            for flow in architecture['data_flow']:
                md_content.append(f"- {flow['from']} → {flow['to']}: {flow['data']}")
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(md_content))
    
    print(f"Exported project documentation to: {output_file}")

def export_stories_csv(research_id, output_file):
    """Export user stories as CSV"""
    story_model = get_user_story_model()
    stories = story_model.get_stories_by_research(research_id)
    
    import csv
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Story ID', 'Title', 'Description', 'Priority', 'Components', 'Status'])
        
        for story in stories:
            components_str = ', '.join(story['components']) if story['components'] else ''
            writer.writerow([
                story['story_id'],
                story['title'],
                story['description'],
                story['priority'],
                components_str,
                story['status']
            ])
    
    print(f"Exported {len(stories)} stories to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Export development process results")
    parser.add_argument("research_id", help="Research ID to export")
    parser.add_argument("--format", choices=["json", "markdown", "csv"], 
                       default="json", help="Export format")
    parser.add_argument("--output", "-o", help="Output file (auto-generated if not specified)")
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        safe_id = args.research_id.replace('/', '_')
        if args.format == "json":
            args.output = f"{safe_id}_export.json"
        elif args.format == "markdown":
            args.output = f"{safe_id}_documentation.md"
        elif args.format == "csv":
            args.output = f"{safe_id}_stories.csv"
    
    try:
        if args.format == "json":
            export_json(args.research_id, args.output)
        elif args.format == "markdown":
            export_markdown(args.research_id, args.output)
        elif args.format == "csv":
            export_stories_csv(args.research_id, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()