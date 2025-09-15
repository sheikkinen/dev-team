"""
Database queue checking action

IMPORTANT: Changes via Change Management, see CLAUDE.md

Replaces check_queue_action.py with database-backed implementation
"""
import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from actions.base import BaseAction
from queue.database_queue import DatabaseQueue
from database.models import get_job_model

logger = logging.getLogger(__name__)

class CheckDatabaseQueueAction(BaseAction):
    """
    Action to check database queue for jobs
    Compatible with existing CheckQueueAction interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.queue = DatabaseQueue()
        self.job_model = get_job_model()
    
    async def execute(self, context: Dict[str, Any]) -> str:
        """Check database queue for next job"""
        try:
            # First, clean up any processing jobs with missing input files
            self._cleanup_jobs_with_missing_files()
            
            job = self.queue.get_next_job()
            
            if job:
                # Store job in context in the same format as file-based queue
                context['current_job'] = {
                    'id': job['id'],
                    'data': {
                        'id': job['id'],  # Include job ID in data for template substitution
                        'input_image': job['input_image'],
                        'user_prompt': job['user_prompt'],
                        'padding_factor': job['padding_factor'],
                        'mask_padding_factor': job['mask_padding_factor'],
                        'event': job['event']
                    }
                }
                
                # Store queue in context for job completion
                context['queue'] = self.queue
                
                logger.debug(f"Job {job['id']} retrieved from database queue")
                logger.debug(f"Job {job['id']} specifies event: {job['event']}")
                
                return job['event']
            else:
                # Reduce verbosity for idle cycles
                return "no_jobs"
                
        except Exception as e:
            logger.error(f"Error checking database queue: {e}")
            return "error"
    
    def _cleanup_jobs_with_missing_files(self):
        """Reset processing jobs that reference non-existent files"""
        try:
            problem_jobs = self.job_model.get_processing_jobs_with_missing_files()
            
            for job in problem_jobs:
                job_id = job['job_id']
                input_path = job['input_image_path']
                reason = f"Input file not found: {input_path}"
                
                logger.warning(f"Resetting job {job_id} - {reason}")
                self.job_model.reset_job_to_pending(job_id, reason)
                
            if problem_jobs:
                logger.info(f"Reset {len(problem_jobs)} jobs with missing input files to pending")
                
        except Exception as e:
            logger.error(f"Error during job cleanup: {e}")