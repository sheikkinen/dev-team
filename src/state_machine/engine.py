"""
StateMachineEngine - YAML-driven finite state machine for event-based workflow processing

IMPORTANT: Changes via Change Management, see CLAUDE.md

The engine loads YAML configuration defining states, events, transitions, and actions, then executes 
an async event loop processing state transitions. Actions are executed for each state using either 
built-in handlers (log, sleep) or pluggable action classes loaded dynamically from src/actions/. 
The system maintains execution context across state changes and supports error recovery via wildcard transitions.

KEY FILES:
- config/walking_skeleton.yaml, config/face_changer.yaml - YAML state machine definitions
- src/actions/check_queue_action.py - Queue checking action
- src/actions/bash_action.py - Shell command execution action
- src/queue/persistent_queue.py - Persistent job queue integration

KEY FUNCTIONS:
- load_config(yaml_path) - Load and validate YAML state machine configuration
- execute_state_machine(context) - Run async event loop with state transitions
- process_event(event, context) - Handle event and trigger state transition
- _execute_action(action_config) - Execute action defined in YAML configuration
- _execute_pluggable_action(type, config) - Load and execute pluggable action class
"""

import asyncio
import logging
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class StateMachineEngine:
    """
    Core state machine engine that loads YAML configuration and executes
    state-based workflows with event processing
    
    """
    
    def __init__(self):
        self.config = None
        self.current_state = None
        self.context = {}
        self.actions = {}
        
    async def load_config(self, yaml_path: str) -> None:
        """Load state machine configuration from YAML file"""
        config_path = Path(yaml_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")
            
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Set initial state
        self.current_state = self.config.get('initial_state', 'waiting')
        
        # Register actions
        await self._register_actions()
        
        logger.info(f"Loaded state machine config: {self.config.get('metadata', {}).get('name', 'Unknown')}")
        logger.info(f"Initial state: {self.current_state}")
    
    async def _register_actions(self) -> None:
        """Register action handlers"""
        # For simplified version, we don't need action registry
        # Actions are loaded dynamically in _execute_pluggable_action
        pass
    
    async def execute_state_machine(self, initial_context: Dict[str, Any] = None) -> None:
        """Execute the state machine with given initial context"""
        if not self.config:
            raise RuntimeError("No configuration loaded. Call load_config() first.")
            
        self.context = initial_context or {}
        
        logger.info(f"Starting state machine execution from state: {self.current_state}")
        
        # Start with initial event
        await self.process_event("start", self.context)
        
        # Main event loop
        while True:
            # Check if we're in a final state (completed) with no outgoing transitions
            if self.current_state == 'completed' and not self._has_outgoing_transitions(self.current_state):
                logger.info(f"🏁 State machine completed in final state: {self.current_state}")
                break
                
            # Execute actions for current state
            await self._execute_state_actions()

            # Wait for next event (for now, we'll use a simple loop)
            # In a real implementation, this would listen to an event queue
            await asyncio.sleep(0.1)  # Prevent busy waiting
    
    async def process_event(self, event: str, context: Dict[str, Any] = None) -> bool:
        """Process an event and potentially transition to a new state"""
        if context:
            self.context.update(context)
            
        logger.debug(f"Processing event '{event}' in state '{self.current_state}'")
        
        # Find valid transition
        new_state = await self._find_transition(self.current_state, event)
        if new_state:            
            # Only log state transitions for important events, skip idle cycles
            if event not in ['wake_up', 'no_jobs'] or new_state != '😴 sleeping':
                # Get actions for the new state to show what will be executed
                next_actions = self.config.get('actions', {}).get(new_state, [])
                action_descriptions = []
                for action in next_actions:
                    action_type = action.get('type', 'unknown')
                    if action_type == 'bash':
                        desc = action.get('description', action.get('command', 'bash'))[:30]
                    elif action_type == 'check_database_queue':
                        desc = 'check queue'
                    elif action_type == 'sleep':
                        duration = action.get('duration', 1)
                        desc = f'sleep {duration}s'
                    elif action_type == 'log':
                        desc = 'log'
                    else:
                        desc = action_type
                    action_descriptions.append(desc)
                
                actions_text = " / ".join(action_descriptions) if action_descriptions else "no actions"
                logger.info(f"{self.current_state} --{event}--> {new_state}: {actions_text}")
            
            self.current_state = new_state
            return True
        else:
            # Only log missing transitions for non-idle events
            if event not in ['cleanup_done']:
                logger.debug(f"No transition found for event '{event}' in state '{self.current_state}'")
            return False
    
    async def _find_transition(self, current_state: str, event: str) -> Optional[str]:
        """Find valid transition for current state and event"""
        transitions = self.config.get('transitions', [])
        
        for transition in transitions:
            from_state = transition.get('from')
            to_state = transition.get('to')
            on_event = transition.get('event')
            
            # Check if transition matches (support wildcard '*' for from state)
            if (from_state == current_state or from_state == '*') and on_event == event:
                return to_state
                
        return None
    
    def _has_outgoing_transitions(self, state: str) -> bool:
        """Check if a state has any outgoing transitions"""
        transitions = self.config.get('transitions', [])
        for transition in transitions:
            if transition.get('from') == state:
                return True
        return False
    
    async def _execute_state_actions(self) -> None:
        """Execute actions defined for current state"""
        state_actions = self.config.get('actions', {}).get(self.current_state, [])
        
        for action_config in state_actions:
            await self._execute_action(action_config)
    
    async def _execute_action(self, action_config: Dict[str, Any]) -> None:
        """Execute a single action"""
        action_type = action_config.get('type')
        
        if not action_type:
            logger.error(f"Action missing 'type' field: {action_config}")
            return
            
        # For now, implement basic actions directly
        # Later this will delegate to action registry
        if action_type == 'log':
            message = action_config.get('message', 'No message')
            logger.info(f"Action log: {message}")
            
        elif action_type == 'sleep':
            duration = action_config.get('duration', 1)
            # Reduce verbosity for idle cycles - only log on first sleep or long sleeps
            if duration > 10 or not hasattr(self, '_last_sleep_logged'):
                logger.info(f"💤 Sleeping for {duration} seconds")
                self._last_sleep_logged = True
            await asyncio.sleep(duration)
            # Generate wake_up event after sleeping
            await self.process_event('wake_up')
            
            
        elif action_type == 'check_database_queue':
            # Execute database queue check using new action system
            await self._execute_pluggable_action('check_database_queue', action_config)
            
        elif action_type == 'check_pony_flux_queue':
            # Execute pony-flux queue check using new action system
            await self._execute_pluggable_action('check_pony_flux_queue', action_config)
            
        elif action_type == 'bash':
            # Execute bash command using new action system
            await self._execute_pluggable_action('bash', action_config)
            
        elif action_type == 'sleep_action':
            # Execute sleep action using new action system
            await self._execute_pluggable_action('sleep_action', action_config)
            
        elif action_type == 'accepted_action':
            # Execute accepted action using new action system
            await self._execute_pluggable_action('accepted_action', action_config)
            
        elif action_type == 'database_record_action':
            # Execute database record action using new action system
            await self._execute_pluggable_action('database_record_action', action_config)
            
        else:
            logger.warning(f"Unknown action type: {action_type}")
    
    
    async def _execute_pluggable_action(self, action_type: str, action_config: Dict[str, Any]) -> None:
        """Execute pluggable action from actions module"""
        try:
            # Import actions dynamically
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            # Add queue to context for actions to use
            if hasattr(self, '_queue'):
                self.context['queue'] = self._queue
            
            # Add global config to context so actions can access configuration parameters
            self.context['config'] = self.config
            
            if action_type == 'bash':
                from actions.bash_action import BashAction
                action = BashAction(action_config)
                event = await action.execute(self.context)
                await self.process_event(event)
            elif action_type == 'check_database_queue':
                from actions.check_database_queue_action import CheckDatabaseQueueAction
                action = CheckDatabaseQueueAction(action_config)
                event = await action.execute(self.context)
                await self.process_event(event)
            elif action_type == 'check_pony_flux_queue':
                from actions.check_pony_flux_queue_action import CheckPonyFluxQueueAction
                action = CheckPonyFluxQueueAction(action_config)
                event = await action.execute(self.context)
                await self.process_event(event)
            elif action_type == 'sleep_action':
                from actions.sleep_action import SleepAction
                action = SleepAction(action_config)
                event = await action.execute(self.context)
                await self.process_event(event)
            elif action_type == 'accepted_action':
                from actions.accepted_action import AcceptedAction
                action = AcceptedAction(action_config)
                event = await action.execute(self.context)
                await self.process_event(event)
            elif action_type == 'database_record_action':
                from actions.database_record_action import DatabaseRecordAction
                action = DatabaseRecordAction(action_config)
                event = await action.execute(self.context)
                await self.process_event(event)
            else:
                logger.error(f"Unsupported pluggable action type: {action_type}")
                await self.process_event('error')
                
        except Exception as e:
            logger.error(f"Error executing pluggable action {action_type}: {e}")
            await self.process_event('error')
