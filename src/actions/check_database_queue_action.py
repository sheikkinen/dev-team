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
from database.models import get_job_model

logger = logging.getLogger(__name__)

class CheckDatabaseQueueAction(BaseAction):
    """
    Action to check database queue for jobs
    Compatible with existing CheckQueueAction interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.job_model = get_job_model()
    
    async def execute(self, context: Dict[str, Any]) -> str:
        print("CheckDatabaseQueueAction: Executing")
        
        # Get next job directly from JobModel
        job = self.job_model.get_next_job()
        
        if job:
            print(f"CheckDatabaseQueueAction: Found job {job['job_id']}: {job['user_prompt']}")
            
            # Set up context for bash_action parameter substitution
            # bash_action expects context['current_job']['data'][param_name]
            context['current_job'] = {
                'id': job['job_id'],
                'data': {
                    'topic': job['user_prompt']  # research topic for parameter substitution
                }
            }
            
            # Also keep the original job format for compatibility
            context['job'] = {
                'id': job['job_id'],
                'topic': job['user_prompt'],  # research topic is stored as user_prompt
                'status': job['status'],
                'created_at': job['created_at']
            }
            
            # Mark job as completed
            self.job_model.complete_job(job['job_id'])
            print(f"CheckDatabaseQueueAction: Marked job {job['job_id']} as completed")
            
            # Return event to trigger state transition to researching
            return "job_added"
        else:
            print("CheckDatabaseQueueAction: No jobs found")
            # Return no event (None or empty string) to stay in current state
            return ""
    
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