#!/usr/bin/env python3
"""
Simple Bash Action Test - Direct execution test

This script directly tests the bash action without the full state machine.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from actions.bash_action import BashAction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Test bash action directly"""
    print("🚀 Direct Bash Action Test")
    print("=" * 50)
    
    try:
        # Create bash action with sample configuration
        action_config = {
            'command': "echo 'Hello {name}! Processing file: {filename} at $(date)'",
            'timeout': 10,
            'description': "Sample echo command with parameter substitution"
        }
        
        # Create the action
        bash_action = BashAction(action_config)
        
        # Create context with sample job data
        context = {
            'current_job': {
                'id': 'test_job_123',
                'data': {
                    'name': 'Alice',
                    'filename': '/tmp/sample.txt'
                }
            }
        }
        
        print(f"Executing bash action...")
        print(f"Command template: {action_config['command']}")
        print(f"Job data: {context['current_job']['data']}")
        
        # Execute the action
        result = await bash_action.execute(context)
        
        print(f"\n✅ Bash action completed!")
        print(f"Result event: {result}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())