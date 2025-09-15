"""
SleepAction - Simple action that sleeps for a specified duration as a demo implementation

This action serves as a demo implementation for the development process state machine.
Each step in the development process will execute this action with a 1-second sleep
to simulate work being done.
"""

import asyncio
import logging
from typing import Dict, Any
from .base import BaseAction

logger = logging.getLogger(__name__)


class SleepAction(BaseAction):
    """
    Action that sleeps for a specified duration to simulate work.
    
    Configuration:
    - duration: Number of seconds to sleep (default: 1)
    - message: Optional message to log (default: based on action description)
    
    Returns:
    - 'work_done' event after sleeping
    """
    
    async def execute(self, context: Dict[str, Any]) -> str:
        """
        Execute sleep action.
        
        Args:
            context: State machine context
            
        Returns:
            'work_done' event after sleeping
        """
        duration = self.get_config_value('duration', 1)
        message = self.get_config_value('message', f"Executing {self.get_description()}")
        
        logger.info(f"🛠️  {message}")
        logger.info(f"💤 Sleeping for {duration} second(s) to simulate work...")
        
        await asyncio.sleep(duration)
        
        logger.info(f"✅ Work completed: {self.get_description()}")
        return 'work_done'