#!/usr/bin/env python3
"""
Claude LLM Integration Demo - Test delegating tasks to Claude AI

This script demonstrates:
1. Creating a task file for Claude to process
2. Running the state machine with Claude bash action
3. Parameter substitution for task files and context directories
4. Error handling for various Claude CLI scenarios
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
    """Run Claude LLM integration demonstration"""
    print("🤖 Claude LLM Integration Demo")
    print("=" * 50)
    
    try:
        # Initialize database
        print("Initializing database...")
        db = Database()
        job_model = get_job_model()
        print("Database initialized successfully")
        
        # Create a sample job with parameters for the Claude task
        job_data = {
            "task_file": "hello_world_task.txt",
            "context_dir": ".",
            "event": "start_claude_task"
        }
        
        job_id = f"claude_demo_{int(asyncio.get_event_loop().time())}"
        job_model.create_job(
            job_id=job_id,
            input_image_path="claude_task",
            user_prompt="Hello World Claude Integration"
        )
        print(f"📝 Created job {job_id} with data: {job_data}")
        
        # Create the task file for Claude
        task_file_path = Path(job_data["task_file"])
        task_content = f"""Hello Claude! This is a test task from the dev-team project.

Job ID: {job_id}
Timestamp: {asyncio.get_event_loop().time()}

Task: Please respond with a friendly "Hello World" message and confirm that you received this task successfully.

Additional instructions:
1. Acknowledge receipt of this task
2. Provide a creative "Hello World" response
3. Comment on the integration between the dev-team state machine and Claude AI
4. Suggest one improvement for this integration

This task is being executed as part of a bash action in our state machine workflow.
"""
        
        task_file_path.write_text(task_content)
        print(f"📄 Created task file: {task_file_path}")
        
        # Initialize and run state machine
        engine = StateMachineEngine()
        await engine.load_config('config/claude_demo.yaml')
        
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
        
        # Trigger the Claude task
        print(f"\n🤖 Delegating task to Claude AI...")
        await engine.process_event('start_claude_task')
        
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
        
        # Clean up task file
        if task_file_path.exists():
            task_file_path.unlink()
            print(f"🧹 Cleaned up task file: {task_file_path}")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())