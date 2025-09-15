#!/usr/bin/env python3
"""
Demo script for dev-team database functionality

This script demonstrates the database functionality by:
1. Adding demo jobs to the database
2. Running the development process with database tracking
3. Showing the results from the database

Usage:
    python demo_database.py
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database.models import get_job_model, get_pipeline_model, get_database
from state_machine.engine import StateMachineEngine


def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_demo_jobs():
    """Create some demo jobs in the database"""
    print("🗄️  Creating demo jobs in database...")
    
    job_model = get_job_model()
    
    demo_jobs = [
        {
            'job_id': 'demo_job_1',
            'input_image_path': '/dev/team/project1/main.py',
            'user_prompt': 'Create a modern web application with user authentication',
            'padding_factor': 1.0,
            'mask_padding_factor': 1.0
        },
        {
            'job_id': 'demo_job_2', 
            'input_image_path': '/dev/team/project2/api.py',
            'user_prompt': 'Build RESTful API with database integration',
            'padding_factor': 1.2,
            'mask_padding_factor': 1.1
        },
        {
            'job_id': 'demo_job_3',
            'input_image_path': '/dev/team/project3/ui.html',
            'user_prompt': 'Design responsive user interface with modern styling',
            'padding_factor': 1.5,
            'mask_padding_factor': 1.3
        }
    ]
    
    for job_data in demo_jobs:
        try:
            # Check if job already exists
            existing = job_model.get_job(job_data['job_id'])
            if existing:
                print(f"  ✅ Job {job_data['job_id']} already exists")
            else:
                db_id = job_model.create_job(**job_data)
                print(f"  ✅ Created job {job_data['job_id']} (DB ID: {db_id})")
        except Exception as e:
            print(f"  ❌ Error creating job {job_data['job_id']}: {e}")
    
    print()


async def run_demo_process():
    """Run the development process demo with database tracking"""
    print("🚀 Running development process with database tracking...")
    print()
    
    try:
        # Change to parent directory for correct config path
        import os
        original_cwd = os.getcwd()
        parent_dir = Path(__file__).parent.parent
        os.chdir(parent_dir)
        
        # Create and configure state machine
        engine = StateMachineEngine()
        await engine.load_config('config/development_process_demo_db.yaml')
        
        # Run the state machine with initial context
        initial_context = {
            'process_name': 'Development Process Database Demo',
            'start_time': asyncio.get_event_loop().time()
        }
        
        await engine.execute_state_machine(initial_context)
        
        # Restore original working directory
        os.chdir(original_cwd)
        
    except Exception as e:
        # Restore original working directory on error
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
        print(f"❌ Error running development process: {e}")
        return None
    
    return True


def show_database_contents():
    """Display the contents of the database in a readable format"""
    print("📊 Database Contents:")
    print("=" * 50)
    
    job_model = get_job_model()
    pipeline_model = get_pipeline_model()
    
    # Show jobs
    jobs = job_model.list_jobs(limit=10)
    print(f"\n📋 Jobs ({len(jobs)} total):")
    for job in jobs:
        print(f"  🔹 {job['job_id']}")
        print(f"    Status: {job['status']}")
        print(f"    Input: {job['input_image_path']}")
        print(f"    Prompt: {job['user_prompt']}")
        print(f"    Created: {job['created_at']}")
        print()
    
    # Show pipeline results for jobs that have them
    print(f"\n🔧 Pipeline Results:")
    for job in jobs:
        results = pipeline_model.get_job_results(job['job_id'])
        if results:
            print(f"  📝 Job: {job['job_id']} ({len(results)} steps)")
            for result in results:
                print(f"    {result['step_number']:2d}. {result['step_name']} - {result['completed_at'][:19]}")
                if result['metadata']:
                    desc = result['metadata'].get('step_description', '')
                    if desc:
                        print(f"        {desc}")
            print()
    
    # Show database status
    print(f"\n📊 Database Statistics:")
    total_jobs = job_model.count_jobs()
    pending = job_model.count_jobs('pending')
    processing = job_model.count_jobs('processing') 
    completed = job_model.count_jobs('completed')
    failed = job_model.count_jobs('failed')
    
    print(f"  Total Jobs: {total_jobs}")
    print(f"  Pending: {pending}")
    print(f"  Processing: {processing}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")
    print()


async def main():
    """Main demo function"""
    setup_logging()
    
    print("🎬 Dev-Team Database Demo")
    print("=" * 40)
    print()
    
    # Step 1: Create demo jobs
    create_demo_jobs()
    
    # Step 2: Run development process
    success = await run_demo_process()
    
    if not success:
        print("❌ Demo process failed")
        return
    
    print()
    print("=" * 50)
    
    # Step 3: Show database contents
    show_database_contents()
    
    print("🎉 Demo completed successfully!")
    print()
    print("💡 You can also use the database CLI:")
    print("   python src/database/cli.py status")
    print("   python src/database/cli.py list")
    print("   python src/database/cli.py details <job_id>")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)