#!/usr/bin/env python3
"""
LLM Claude Hello World Demo

Demonstrates int        print(f"🔄 Starting state machine...")
        print(f"Initial state: {engine.current_state}")
        
        # Execute state actions for the starting state
        await engine._execute_state_actions()
        
        # Trigger the initial event to move to claude calling state
        print(f"🎯 Triggering start_claude event...")
        await engine.process_event('start_claude')
        
        # Execute actions for the claude calling state  
        print(f"Current state: {engine.current_state}")
        await engine._execute_state_actions()
        
        # The bash action will return either 'claude_completed' or 'claude_failed'
        # We need to handle that event automatically based on the result
        print(f"📝 Note: Bash action execution will determine next event automatically")
        
        print(f"\n✅ Demo completed!")
        print(f"Final state: {engine.current_state}")laude.sh wrapper script as a bash action in the state machine.
This creates a job with a hello world prompt and processes it through the state machine.
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
    """Run the LLM Claude hello world demo."""
    print("🤖 LLM Claude Hello World Demo")
    print("=" * 50)
    
    try:
        # Initialize database
        print("Initializing database...")
        db = Database()
        job_model = get_job_model()
        print("Database initialized successfully")
        
        # Create a sample job with prompt parameter for the bash command
        job_data = {
            "prompt": "Hello, Claude! This is a test from the dev-team state machine. Please respond with a friendly greeting.",
            "event": "start_claude"
        }
        
        job_id = f"claude_hello_{int(asyncio.get_event_loop().time())}"
        job_model.create_job(
            job_id=job_id,
            input_image_path="/tmp/claude_demo.txt",
            user_prompt=job_data["prompt"]
        )
        print(f"📝 Created job {job_id}")
        print(f"🎯 Prompt: {job_data['prompt']}")
        print()
        
        # Initialize and run state machine
        engine = StateMachineEngine()
        await engine.load_config('config/claude_hello_world.yaml')
        
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
        
        print(f"� Starting state machine...")
        print(f"Initial state: {engine.current_state}")
        
        # Execute state actions for the starting state
        await engine._execute_state_actions()
        
        # Trigger the initial event
        await engine.process_event('start_claude')
        
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
        print(f"  Prompt: {job_data['prompt']}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())