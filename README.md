# Development Team State Machine

This project implements a state machine-based workflow for software development processes with database tracking and bash command execution capabilities. Each step in the development lifecycle is represented as a state with associated actions, providing a structured and trackable approach to team development workflows.

## Overview

The state machine implements a complete development process with database persistence and extensible action system including:

### Core Features
- **Event-driven workflow**: State transitions triggered by events
- **Database integration**: SQLite-based job tracking and pipeline results
- **Bash action support**: Execute shell commands with parameter substitution
- **Dynamic action loading**: Pluggable action system for extensibility
- **Configuration as code**: Complete workflows defined in YAML

### Development Process States
1. **Research**: Deep research, website analysis, competitor analysis
2. **Product Design**: Requirements analysis, user stories, use cases, domain model
3. **Development Loop** (Kanban-style):
   - Backlog → Architecture → Test Planning → Module Design
   - Implementation → UI/UX Design → Frontend Development
   - Testing → Demo → Review

## Project Structure

```
dev-team/
├── src/                      # Source code
│   ├── state_machine/        # State machine engine
│   │   ├── __init__.py
│   │   └── engine.py         # Core state machine engine with dynamic imports
│   ├── actions/              # Pluggable actions
│   │   ├── __init__.py
│   │   ├── base.py           # Base action interface
│   │   ├── bash_action.py    # Execute bash commands with parameters
│   │   ├── sleep_action.py   # Demo action (1-second sleep)
│   │   ├── accepted_action.py # Auto-acceptance for demo
│   │   ├── database_record_action.py # Database recording
│   │   └── check_database_queue_action.py # Queue checking
│   ├── database/             # Database models and CLI
│   │   ├── __init__.py
│   │   ├── models.py         # Database models and schema
│   │   └── cli.py            # Database command-line interface
│   └── queue/                # Queue implementation
│       ├── __init__.py
│       └── database_queue.py # Database-backed queue
├── config/                   # Configuration files
│   ├── development_process.yaml       # Full process configuration
│   ├── development_process_demo.yaml  # Demo version (auto-completes)
│   ├── development_process_demo_db.yaml # Demo with database tracking
│   └── bash_demo.yaml        # Bash action demonstration config
├── scripts/                  # Executable scripts
│   └── run_process.py        # CLI to run the state machine
├── demos/                    # Demo and example scripts
│   ├── demo_database.py      # Complete database demo
│   ├── demo_database_reader.py # Database content viewer
│   ├── bash_direct_test.py   # Direct bash action test
│   └── bash_demo_fixed.py    # Bash action with state machine
├── docs/                     # Documentation
│   ├── database.md           # Database implementation docs
│   ├── process.md            # Original process specification
│   └── todo.md               # Development tasks and notes
├── data/                     # Data storage
│   └── pipeline.db           # SQLite database (created automatically)
├── dev.py                    # Convenient launcher script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

## Quick Start

Use the convenient launcher script for common tasks:

```bash
# Run complete database demo
python dev.py demo

# View database contents
python dev.py database

# Run development process
python dev.py process

# Test bash action functionality
python dev.py bash-test

# Run bash action demo with state machine
python dev.py bash-demo

# Database CLI operations
python dev.py cli status
python dev.py cli list

# Show help
python dev.py help
```

## Detailed Usage

### Run the Development Process

```bash
# Run the demo version (auto-completes)
python scripts/run_process.py --config config/development_process_demo.yaml

# Run with debug logging
python scripts/run_process.py --config config/development_process_demo.yaml --debug

# Run the full interactive version (requires manual acceptance)
python scripts/run_process.py --config config/development_process.yaml

# Run with database tracking
python scripts/run_process.py --config config/development_process_demo_db.yaml
```

### Database Demos

```bash
# Run complete database demo (creates jobs + runs process + shows results)
python demos/demo_database.py

# View current database contents
python demos/demo_database_reader.py

# Database CLI operations
python src/database/cli.py status
python src/database/cli.py list
python src/database/cli.py add-job <job_id> <project_path>
```

### Bash Action Testing

```bash
# Test bash action directly (parameter substitution demo)
python demos/bash_direct_test.py

# Test bash action with state machine integration
python demos/bash_demo_fixed.py
```

### Example Output

**Development Process:**
```
🚀 Development process starting...
🛠️  Conducting deep research, website analysis, and competitor analysis
💤 Sleeping for 1 second(s) to simulate work...
✅ Work completed: Deep Research Phase
🛠️  Creating requirements analysis, user stories, use cases, and domain model
💤 Sleeping for 1 second(s) to simulate work...
✅ Work completed: Product Design Phase
...
🎯 Review complete - work accepted!
✅ Work automatically accepted for demo
🎉 Development process completed successfully!
```

**Bash Action Example:**
```
🚀 Direct Bash Action Test
==================================================
Executing bash action...
Command template: echo 'Hello {name}! Processing file: {filename} at $(date)'
Job data: {'name': 'Alice', 'filename': '/tmp/sample.txt'}
2025-09-15 06:10:13,893 - actions.bash_action - INFO - 🔧 Sample echo command with parameter substitution (job test_job_123)
2025-09-15 06:10:13,899 - actions.bash_action - INFO - Command stdout: Hello Alice! Processing file: "/tmp/sample.txt" at $(date)
2025-09-15 06:10:13,899 - actions.bash_action - INFO - Command completed successfully for job test_job_123

✅ Bash action completed!
Result event: job_done
```

## Configuration

The state machine is configured via YAML files that define:

- **States**: All possible workflow states
- **Events**: Triggers for state transitions  
- **Transitions**: Valid state changes based on events
- **Actions**: Work to be performed in each state

### Sample Configuration

```yaml
states:
  - waiting
  - research
  - implementation
  - completed

events:
  - start
  - work_done
  - accepted

transitions:
  - from: waiting
    to: research
    event: start

actions:
  research:
    - type: sleep_action
      description: "Deep Research Phase"
      duration: 1
    - type: bash
      description: "Execute research script"
      command: "echo 'Researching {topic} for project {project_name}'"
      timeout: 30
      success: "research_completed"
      error_mappings:
        "1": "research_failed"
```

## Implementation Details

### State Machine Engine

The core engine (`src/state_machine/engine.py`) provides:
- YAML configuration loading
- Event-driven state transitions
- Pluggable action system
- Error handling and recovery

### Actions

Actions are pluggable components that perform work in each state:

- **BashAction**: Execute shell commands with parameter substitution and error mapping
- **SleepAction**: Demo implementation that sleeps for N seconds  
- **AcceptedAction**: Auto-triggers acceptance for demo completion
- **DatabaseRecordAction**: Records pipeline steps to database
- **CheckDatabaseQueueAction**: Monitors database job queue
- **BaseAction**: Abstract base class for all actions

#### Bash Action Features

The bash action provides powerful command execution capabilities:

- **Parameter Substitution**: Replace `{param_name}` placeholders with job data
- **Error Mapping**: Map exit codes to specific events (e.g., exit code 1 → 'validation_failed')
- **Timeout Support**: Configurable command timeout (default 30s)
- **Success Events**: Custom success event names instead of default 'job_done'
- **Proper Quoting**: Automatically handles file paths and strings with spaces

Example bash action configuration:
```yaml
- type: bash
  description: "Process image file"
  command: "convert {input_file} -resize 50% {output_file}"
  timeout: 60
  success: "image_processed"
  error_mappings:
    "1": "conversion_failed"
    "2": "file_not_found"
  recoverable_errors: ["conversion_failed"]
```

### Demo vs Production

- **Demo Version**: Automatically completes the entire workflow
- **Full Version**: Requires external triggers for review acceptance
- Both versions simulate 1-second work for each development phase

## Extending the System

### Adding New Actions

1. Create a new action class extending `BaseAction` in `src/actions/`
2. Implement the `execute()` method to return an event name
3. Add the action type to the engine's `_execute_pluggable_action()` method
4. Configure the action in your YAML file

Example action implementation:
```python
from .base import BaseAction

class CustomAction(BaseAction):
    async def execute(self, context):
        # Your custom logic here
        return 'success_event'
```

### Modifying the Workflow

1. Edit the YAML configuration file
2. Add/remove states, events, and transitions as needed
3. Configure appropriate actions for each state
4. Test with the demo modes before production use

## Architecture

This implementation demonstrates advanced state machine patterns:

- **Event-driven design**: All state changes triggered by events
- **Configuration as code**: Complete workflow defined in YAML
- **Pluggable actions**: Extensible action system with dynamic imports
- **Database persistence**: SQLite-based job tracking and pipeline results
- **Command execution**: Bash action with parameter substitution and error handling
- **Separation of concerns**: Engine, actions, and configuration are decoupled
- **Queue management**: Database-backed job queue for workflow coordination

The architecture is based on the battle-tested state machine implementation from the face-changer project, providing enterprise-grade reliability and extensibility.

## Original Specification

The state machine implements the development process defined in `process.md`, providing a concrete, executable representation of the team workflow described in that document.