"""
AcceptedAction - Simple action that triggers the 'accepted' event for demo completion

This action serves as a demo mechanism to automatically accept work and complete
the development process state machine.
"""

import asyncio
import logging
from typing import Dict, Any
from .base import BaseAction

logger = logging.getLogger(__name__)


class AcceptedAction(BaseAction):
    """
    Action that automatically triggers acceptance to complete the process.
    
    Returns:
    - 'accepted' event to transition to completed state
    """
    
    async def execute(self, context: Dict[str, Any]) -> str:
        """
        Execute acceptance action.
        
        Args:
            context: State machine context
            
        Returns:
            'accepted' event to complete the process
        """
        message = self.get_config_value('message', "Work automatically accepted for demo")
        
        logger.info(f"✅ {message}")
        
        return 'accepted'