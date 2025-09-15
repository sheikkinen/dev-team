#!/usr/bin/env python3
"""
Development Process State Machine CLI

This script runs the development process state machine as defined in process.md.
Each step in the process is implemented as a 1-second sleep action for demonstration.

Usage:
    python run_process.py [--config CONFIG_FILE] [--debug]

Examples:
    python run_process.py
    python run_process.py --debug
    python run_process.py --config config/development_process.yaml --debug
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from state_machine.engine import StateMachineEngine


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger('state_machine.engine').setLevel(level)
    logging.getLogger('actions.sleep_action').setLevel(level)


async def run_development_process(config_file: str, debug: bool = False) -> None:
    """
    Run the development process state machine.
    
    Args:
        config_file: Path to YAML configuration file
        debug: Enable debug logging
    """
    setup_logging(debug)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Development Process State Machine")
    logger.info(f"📋 Configuration: {config_file}")
    
    try:
        # Create and configure state machine
        engine = StateMachineEngine()
        await engine.load_config(config_file)
        
        # Run the state machine with initial context
        initial_context = {
            'process_name': 'Development Process Demo',
            'start_time': asyncio.get_event_loop().time()
        }
        
        await engine.execute_state_machine(initial_context)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Process interrupted by user")
    except FileNotFoundError as e:
        logger.error(f"❌ Configuration file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error running development process: {e}")
        if debug:
            logger.exception("Full error details:")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run the Development Process State Machine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--config',
        default='config/development_process.yaml',
        help='Path to YAML configuration file (default: config/development_process.yaml)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Validate config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Error: Configuration file not found: {args.config}")
        print(f"Current working directory: {Path.cwd()}")
        sys.exit(1)
    
    # Run the state machine
    try:
        asyncio.run(run_development_process(args.config, args.debug))
    except KeyboardInterrupt:
        print("\n⏹️  Process stopped by user")
        sys.exit(0)


if __name__ == '__main__':
    main()