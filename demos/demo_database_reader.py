#!/usr/bin/env python3
"""
Database Reader Demo Script

This script demonstrates reading and displaying database contents
in a readable format. It shows jobs, pipeline results, and statistics
without running the state machine.

Usage:
    python demo_database_reader.py
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database.models import get_job_model, get_pipeline_model


def show_database_summary():
    """Display a summary of database contents"""
    print("📊 Dev-Team Database Summary")
    print("=" * 40)
    
    job_model = get_job_model()
    
    # Show database statistics
    total_jobs = job_model.count_jobs()
    pending = job_model.count_jobs('pending')
    processing = job_model.count_jobs('processing') 
    completed = job_model.count_jobs('completed')
    failed = job_model.count_jobs('failed')
    
    print(f"\n📈 Database Statistics:")
    print(f"  Total Jobs: {total_jobs}")
    print(f"  Pending: {pending}")
    print(f"  Processing: {processing}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")
    print()


def show_all_jobs():
    """Display all jobs in the database"""
    print("📋 All Jobs in Database")
    print("=" * 30)
    
    job_model = get_job_model()
    jobs = job_model.list_jobs(limit=50)
    
    if not jobs:
        print("  No jobs found in database")
        return
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. Job: {job['job_id']}")
        print(f"   Status: {job['status']}")
        print(f"   Input: {job['input_image_path']}")
        print(f"   Prompt: {job['user_prompt']}")
        print(f"   Created: {job['created_at']}")
        if job['started_at']:
            print(f"   Started: {job['started_at']}")
        if job['completed_at']:
            print(f"   Completed: {job['completed_at']}")
        if job['error_message']:
            print(f"   Error: {job['error_message']}")


def show_pipeline_results():
    """Display all pipeline results"""
    print("\n🔧 Pipeline Results")
    print("=" * 25)
    
    job_model = get_job_model()
    pipeline_model = get_pipeline_model()
    
    # Get all jobs that have pipeline results
    jobs = job_model.list_jobs(limit=50)
    
    results_found = False
    for job in jobs:
        results = pipeline_model.get_job_results(job['job_id'])
        if results:
            results_found = True
            print(f"\n📝 Job: {job['job_id']} ({len(results)} steps)")
            
            for result in results:
                print(f"  {result['step_number']:2d}. {result['step_name']} - {result['completed_at'][:19]}")
                
                if result['metadata']:
                    desc = result['metadata'].get('step_description', '')
                    if desc:
                        print(f"      Description: {desc}")
                    
                    process_name = result['metadata'].get('process_name', '')
                    if process_name:
                        print(f"      Process: {process_name}")
    
    if not results_found:
        print("  No pipeline results found in database")


def show_recent_activity():
    """Show recent database activity"""
    print("\n🕒 Recent Activity")
    print("=" * 20)
    
    job_model = get_job_model()
    
    # Show recently created jobs
    recent_jobs = job_model.list_jobs(limit=5)
    if recent_jobs:
        print("\n📋 Recently Created Jobs:")
        for job in recent_jobs[:3]:
            print(f"  • {job['job_id']} - {job['status']} ({job['created_at'][:19]})")
    
    # Show recently completed jobs
    completed_jobs = job_model.list_jobs(status='completed', limit=5)
    if completed_jobs:
        print("\n✅ Recently Completed Jobs:")
        for job in completed_jobs[:3]:
            print(f"  • {job['job_id']} - completed ({job['completed_at'][:19]})")
    
    # Show failed jobs
    failed_jobs = job_model.list_jobs(status='failed', limit=5)
    if failed_jobs:
        print("\n❌ Failed Jobs:")
        for job in failed_jobs[:3]:
            print(f"  • {job['job_id']} - {job['error_message']}")


def main():
    """Main function to display database contents"""
    try:
        # Show database summary
        show_database_summary()
        
        # Show all jobs
        show_all_jobs()
        
        # Show pipeline results
        show_pipeline_results()
        
        # Show recent activity
        show_recent_activity()
        
        print("\n" + "=" * 50)
        print("💡 Available CLI Commands:")
        print("   python src/database/cli.py status")
        print("   python src/database/cli.py list")
        print("   python src/database/cli.py details <job_id>")
        print("   python src/database/cli.py add-job <job_id> <image_path>")
        print()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()