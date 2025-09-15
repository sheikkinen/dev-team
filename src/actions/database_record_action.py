"""
Database action for recording development process steps

Records each step of the development process to the database for tracking and demo purposes.
"""

import asyncio
import logging
from typing import Dict, Any

from .base import BaseAction


class DatabaseRecordAction(BaseAction):
    """Records development process steps to database"""
    
    async def execute(self, context: Dict[str, Any]) -> str:
        """
        Record a development process step to the database.
        
        Args:
            context: State machine context containing current state info
            
        Returns:
            Event name to continue process
        """
        try:
            # Import here to avoid circular imports
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            from database.models import get_job_model, get_pipeline_model
            
            step_name = self.get_config_value('step_name', 'unknown_step')
            step_number = self.get_config_value('step_number', 0)
            description = self.get_config_value('description', step_name)
            
            # Create a job ID based on current time if not in context
            job_id = context.get('process_job_id', f"process_{int(asyncio.get_event_loop().time())}")
            context['process_job_id'] = job_id  # Store for subsequent steps
            
            # Record to pipeline results
            pipeline_model = get_pipeline_model()
            
            # Create metadata about this step
            metadata = {
                'process_name': context.get('process_name', 'Development Process'),
                'step_description': description,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            # Record to pipeline results (synchronous call since SQLite is fast)
            pipeline_model.record_step(
                job_id=job_id,
                step_name=step_name,
                step_number=step_number,
                metadata=metadata
            )
            
            self.logger.info(f"📊 Recorded step {step_number}: {step_name} to database")
            
            return self.get_config_value('success_event', 'work_done')
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record step to database: {e}")
            return self.get_config_value('error_event', 'error')