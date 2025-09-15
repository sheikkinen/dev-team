"""
Database-backed persistent queue implementation
Replaces file-based queue.json with SQLite database
"""
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import get_job_model, JobModel

logger = logging.getLogger(__name__)

class DatabaseQueue:
    """
    Database-backed persistent queue
    Compatible with existing PersistentQueue interface
    """
    
    def __init__(self):
        self.job_model: JobModel = get_job_model()
        logger.debug("Initialized database-backed queue")
    
    def add_job(self, job_id: str, input_image: str, 
                user_prompt: str = "make this person more attractive",
                padding_factor: float = 1.5,
                mask_padding_factor: float = 1.2) -> None:
        """Add a job to the queue"""
        try:
            self.job_model.create_job(
                job_id=job_id,
                input_image_path=input_image,
                user_prompt=user_prompt,
                padding_factor=padding_factor,
                mask_padding_factor=mask_padding_factor
            )
            logger.info(f"Added job {job_id} to database queue")
        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {e}")
            raise
    
    def get_next_job(self) -> Optional[Dict[str, Any]]:
        """Get the next job from the queue"""
        try:
            job = self.job_model.get_next_job()
            if job:
                logger.debug(f"Retrieved job {job['job_id']} from database queue")
                # Convert to compatible format for existing code
                return {
                    'id': job['job_id'],
                    'input_image': job['input_image_path'],
                    'user_prompt': job['user_prompt'],
                    'padding_factor': job['padding_factor'],
                    'mask_padding_factor': job['mask_padding_factor'],
                    'event': 'new_job'
                }
            else:
                logger.debug("No jobs available in database queue")
                return None
        except Exception as e:
            logger.error(f"Failed to get next job: {e}")
            return None
    
    def complete_job(self, job_id: str) -> None:
        """Mark a job as completed"""
        try:
            # Check if job is already completed to avoid duplicate logging
            job_data = self.job_model.get_job(job_id)
            if job_data and job_data.get('status') == 'completed':
                logger.debug(f"Job {job_id} already completed, skipping")
                return
                
            self.job_model.complete_job(job_id)
            logger.debug(f"Marked job {job_id} as completed")
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
    
    def fail_job(self, job_id: str, error_message: str) -> None:
        """Mark a job as failed"""
        try:
            self.job_model.fail_job(job_id, error_message)
            logger.error(f"Marked job {job_id} as failed: {error_message}")
        except Exception as e:
            logger.error(f"Failed to mark job {job_id} as failed: {e}")
    
    def get_job_count(self) -> int:
        """Get total number of jobs"""
        try:
            return self.job_model.count_jobs()
        except Exception as e:
            logger.error(f"Failed to get job count: {e}")
            return 0
    
    def get_pending_count(self) -> int:
        """Get number of pending jobs"""
        try:
            return self.job_model.count_jobs('pending')
        except Exception as e:
            logger.error(f"Failed to get pending job count: {e}")
            return 0
    
    def clear_all_jobs(self) -> int:
        """Clear all jobs from the queue (for testing)"""
        try:
            with self.job_model.db._get_connection() as conn:
                # Get count before deletion
                count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
                
                # Delete all pipeline results first (foreign key constraint)
                conn.execute("DELETE FROM pipeline_results")
                conn.execute("DELETE FROM jobs")
                conn.commit()
                
                logger.info(f"Cleared {count} jobs from database queue")
                return count
        except Exception as e:
            logger.error(f"Failed to clear jobs: {e}")
            return 0
    
    def list_jobs(self, status: Optional[str] = None, limit: int = 50) -> list:
        """List jobs with optional status filter"""
        try:
            return self.job_model.list_jobs(status=status, limit=limit)
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []