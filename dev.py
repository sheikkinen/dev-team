#!/usr/bin/env python3
"""
Dev-Team Project Launcher

Simple launcher script for common development tasks.

Usage:
    python dev.py <command>

Commands:
    demo         - Run complete database demo
    process      - Run development process state machine
    database     - View database contents
    bash-test    - Test bash action functionality
    bash-demo    - Run bash action demo with state machine
    cli          - Launch database CLI
    help         - Show this help message
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🚀 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=Path(__file__).parent)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        return 1

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "demo":
        return run_command(
            "python demos/demo_database.py",
            "Running complete database demo"
        )
    
    elif command == "process":
        config = "config/development_process_demo_db.yaml"
        if len(sys.argv) > 2:
            config = sys.argv[2]
        return run_command(
            f"python scripts/run_process.py --config {config}",
            f"Running development process with {config}"
        )
    
    elif command == "database":
        return run_command(
            "python demos/demo_database_reader.py",
            "Showing database contents"
        )
    
    elif command == "bash-test":
        return run_command(
            "python demos/bash_direct_test.py",
            "Running bash action test"
        )
        
    elif command == "bash-demo":
        return run_command(
            "python demos/bash_demo_fixed.py",
            "Running bash action demo"
        )
    
    elif command == "cli":
        args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "status"
        return run_command(
            f"python src/database/cli.py {args}",
            f"Running database CLI: {args}"
        )
    
    elif command in ["help", "-h", "--help"]:
        print(__doc__)
        return 0
    
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main())