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
from database.models import Database, get_job_model

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
        job_model = get_job_model()
        print("Database initialized successfully")
        
        # Create a sample job with parameters for the bash command
        job_data = {
            "name": "Alice", 
            "filename": "/tmp/sample.txt",
            "event": "start_processing"
        }
        
        job_id = f"bash_demo_{int(asyncio.get_event_loop().time())}"
        job_model.create_job(
            job_id=job_id,
            input_image_path="/tmp/sample.txt",
            user_prompt="demo"
        )
        print(f"📝 Created job {job_id} with data: {job_data}")
        
        # Initialize and run state machine
        engine = StateMachineEngine()
        await engine.load_config('config/bash_demo.yaml')
        
        # Set up the job queue with our sample job
        job = job_model.get_job(job_id)
        engine.context['queue'] = type('MockQueue', (), {
            'get_pending_jobs': lambda: [job] if job else [],
            'complete_job': lambda job_id: job_model.complete_job(job_id)
        })()
        
        # Set the current job in context for bash action
        engine.context['current_job'] = {
            'id': job_id,
            'data': job_data
        }
        
        print(f"\n🔄 Starting state machine...")
        print(f"Initial state: {engine.current_state}")
        
        # Execute state actions for the starting state
        await engine._execute_state_actions()
        
        # Trigger the initial event
        await engine.process_event('start_processing')
        
        # Execute actions for the processing state  
        await engine._execute_state_actions()
        
        # Trigger finish event
        await engine.process_event('finish')
        
        print(f"\n✅ Demo completed!")
        print(f"Final state: {engine.current_state}")
        
        # Update job status
        job_model.complete_job(job_id)
        
        # Show job history
        print(f"\n📊 Job Status:")
        job = job_model.get_job(job_id)
        print(f"  Job ID: {job['id']}")
        print(f"  Status: {job['status']}")
        print(f"  Data: {job_data}")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())