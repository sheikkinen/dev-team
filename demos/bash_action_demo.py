#!/usr/bin/env python3
"""
Bash Action Demo - Test bash command execution with parameter substitution

This script demonstrates:
1. Creating a job with parameters for the bash command
2. Running the state machine with bash action
3. Parameter substitution in command execution
4. Event-driven state transitions
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from state_machine.engine import StateMachineEngine
from database.models import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Run bash action demonstration"""
    print("🚀 Bash Action Demo")
    print("=" * 50)
    
    try:
        # Initialize database
        print("Initializing database...")
        db = Database()
        print("Database initialized successfully")
    
    # Create a sample job with parameters for the bash command
    job_data = {
        "name": "Alice",
        "filename": "/tmp/sample.txt",
        "event": "start_processing"
    }
    
    job_id = db.add_job(
        job_type="bash_demo",
        status="pending",
        data=job_data
    )
    print(f"📝 Created job {job_id} with data: {job_data}")
    
    # Initialize and run state machine
    engine = StateMachineEngine()
    await engine.load_config('config/bash_demo.yaml')
    
    # Set up the job queue with our sample job
    jobs = [db.get_job(job_id)]
    engine.context['queue'] = type('MockQueue', (), {
        'get_pending_jobs': lambda: jobs,
        'complete_job': lambda job_id: db.update_job_status(job_id, "completed")
    })()
    
    # Set the current job in context for bash action
    engine.context['current_job'] = {
        'id': job_id,
        'data': job_data
    }
    
    print(f"\n🔄 Starting state machine...")
    print(f"Initial state: {engine.current_state}")
    
    # Trigger the initial event
    await engine.process_event('start_processing')
    
    # Run a few more events to complete the demo
    await engine.process_event('finish')
    
    print(f"\n✅ Demo completed!")
    print(f"Final state: {engine.current_state}")
    
    # Update job status
    db.update_job_status(job_id, "completed")
    
    # Show job history
    print(f"\n📊 Job Status:")
    job = db.get_job(job_id)
    print(f"  Job ID: {job['id']}")
    print(f"  Status: {job['status']}")
    
    print(f"  Data: {job['data']}")
    
    # Database doesn't need explicit close method

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()if __name__ == "__main__":
    asyncio.run(main())