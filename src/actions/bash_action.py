"""
BashAction - Execute shell commands with template parameter substitution and error mapping

Executes bash commands defined in YAML configuration, substituting template parameters from job data
using {param_name} placeholders. Commands run with configurable timeout, and the action returns 
custom success events or mapped error events based on exit codes. Supports error mapping to specific 
events (e.g., exit code 1 → 'validation_failed') and prevents automatic job removal for recoverable 
errors that should be handled by state machine transitions.

KEY FEATURES:
- Parameter substitution: {param_name} placeholders replaced with job data values
- Error mapping: Map exit codes to specific error events
- Timeout support: Configurable command timeout
- Success events: Custom success event names

EXAMPLE CONFIG:
```yaml
action:
  type: bash
  command: echo "Processing {input_file} for user {user_id}"
  timeout: 30
  success: "command_completed"
  error_mappings:
    "1": "validation_failed"
    "2": "file_not_found"
```
"""

import asyncio
import logging
from typing import Dict, Any
from .base import BaseAction

logger = logging.getLogger(__name__)


class BashAction(BaseAction):
    """
    Action that executes bash commands with error mapping support.
    
    Returns:
    - Custom success event (from 'success' config) or 'job_done' on exit code 0
    - Mapped error event (from 'error_mappings' config) on specific exit codes  
    - Default 'error' event on unmapped failures
    
    Error Mapping Example:
    error_mappings:
      "1": "validation_failed"  # Exit code 1 → validation_failed event
      "2": "file_not_found"     # Exit code 2 → file_not_found event
    """
    
    async def execute(self, context: Dict[str, Any]) -> str:
        """
        Execute bash command and return event based on exit code.
        
        Args:
            context: State machine context containing current_job and queue
            
        Returns:
            - success event (config 'success' or 'job_done') on exit code 0
            - mapped error event (from 'error_mappings') on specific exit codes
            - 'error' on unmapped failures
            
        Error Handling:
            - Mapped errors preserve job for state machine handling
            - Unmapped errors auto-remove job to prevent infinite retries
            - Timeouts and exceptions also auto-remove job
        """
        # Get command from job data first, fall back to config with parameter substitution
        job = context.get('current_job')
        command = None
        
        if job and isinstance(job.get('data'), dict):
            job_data = job['data']
            command = job_data.get('command')
        
        # Use config command and substitute parameters from job data
        if not command:
            command = self.get_config_value('command')
            if command and job and isinstance(job.get('data'), dict):
                job_data = job['data']
                
                # Substitute parameters using {param_name} placeholders
                for key, value in job_data.items():
                    if key != 'event':  # Skip event field
                        placeholder = f"{{{key}}}"
                        if placeholder in command:
                            # Properly quote file paths and strings with spaces
                            # Use double quotes to handle apostrophes in filenames
                            quoted_value = f'"{value}"' if isinstance(value, str) and ('/' in value or ' ' in value) else str(value)
                            command = command.replace(placeholder, quoted_value)
            
        if not command:
            logger.error("No command specified in job data or bash action config")
            return 'error'
        
        timeout = self.get_config_value('timeout', 30)
        job_id = job['id'] if job else 'unknown'
        
        # Only log command details in debug mode - use description for concise info logging
        description = self.get_config_value('description', 'bash command')
        logger.info(f"🔧 {description[:50]} (job {job_id})")
        logger.debug(f"Executing bash command for job {job_id}: {command}")
        
        try:
            # Execute command with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            # Log output
            if stdout:
                logger.info(f"Command stdout: {stdout.decode().strip()}")
            if stderr:
                logger.warning(f"Command stderr: {stderr.decode().strip()}")
            
            # Check exit code
            if process.returncode == 0:
                logger.info(f"Command completed successfully for job {job_id}")
                
                # Return custom success event if specified, otherwise 'job_done'
                success_event = self.get_config_value('success', 'job_done')
                return success_event
            else:
                logger.error(f"Command failed with exit code {process.returncode} for job {job_id}")
                
                # Check for error mapping based on exit code
                error_mappings = self.get_config_value('error_mappings', {})
                if str(process.returncode) in error_mappings:
                    mapped_error = error_mappings[str(process.returncode)]
                    logger.info(f"Mapping exit code {process.returncode} to event: {mapped_error}")
                    
                    # For specific error types, don't auto-remove job
                    # Let the state machine handle it through proper transitions
                    recoverable_errors = self.get_config_value('recoverable_errors', ['validation_failed', 'retry_needed'])
                    if mapped_error in recoverable_errors:
                        return mapped_error
                
                # For unmapped errors, remove failed job from queue to prevent infinite retries
                if job and 'queue' in context and hasattr(context['queue'], 'complete_job'):
                    context['queue'].complete_job(job['id'])
                    logger.info(f"Removed failed job {job_id} from queue")
                
                # Clear current job on error to prevent infinite loops
                context.pop('current_job', None)
                
                # Return mapped error event if available, otherwise default 'error'
                return error_mappings.get(str(process.returncode), 'error')
                
        except asyncio.TimeoutError:
            logger.error(f"Command timed out after {timeout} seconds for job {job_id}")
            
            # Remove timed-out job from queue
            if job and 'queue' in context and hasattr(context['queue'], 'complete_job'):
                context['queue'].complete_job(job['id'])
                logger.info(f"Removed timed-out job {job_id} from queue")
            
            # Clear current job on timeout to prevent infinite loops
            context.pop('current_job', None)
            return 'error'
            
        except Exception as e:
            logger.error(f"Command execution failed for job {job_id}: {e}")
            
            # Remove failed job from queue
            if job and 'queue' in context and hasattr(context['queue'], 'complete_job'):
                context['queue'].complete_job(job['id'])
                logger.info(f"Removed failed job {job_id} from queue")
                
            # Clear current job on exception to prevent infinite loops
            context.pop('current_job', None)
            return 'error'