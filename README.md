# Development Team State Machine

This project implements a state machine-based workflow for software development processes with database tracking and bash command execution capabilities. Each step in the development lifecycle is represented as a state with associated actions, providing a structured and trackable approach to team development workflows.

## 🏛️ Architectural Analysis Summary

**System Classification**: Event-Driven State Machine with Plugin Architecture  
**Domain**: Software Development Workflow Automation  
**Key Patterns**: Finite State Machine, Plugin Architecture, Repository Pattern, Configuration-as-Code

### 🎯 Core Architectural Findings

**Event-Driven Design**: The system implements a finite state machine where all state transitions are triggered by discrete events, providing predictable and traceable workflow execution. This design enables clear audit trails and simplified debugging.

**Pluggable Action System**: A sophisticated plugin architecture allows dynamic loading of action types at runtime. Actions implement a common `BaseAction` interface and are configured via YAML, enabling extensibility without core engine modifications.

**Database-Centric Persistence**: SQLite provides persistent job queuing, pipeline step tracking, and inter-process communication. The three-table design (`jobs`, `pipeline_results`, `pipeline_state`) supports complete workflow lifecycle management.

**Configuration-as-Code**: Complete workflows are defined in YAML files, making them accessible to non-programmers and version-controllable alongside source code. Different configurations support development, demo, and production environments.

**Security by Design**: Parameter substitution using templates prevents injection attacks, while automatic quoting handles file paths safely. Error mapping provides sophisticated error handling with configurable recovery strategies.

> 📚 **Complete Analysis**: See [`archaeology/`](archaeology/) for detailed architectural documentation including visual diagrams, component analysis, and architectural decision records. Start with the [Architecture Index](archaeology/INDEX.md).

## Overview

The state machine implements a complete development process with database persistence and extensible action system including:

### Core Components (Archaeological Analysis)

**🎯 State Machine Engine** (`src/state_machine/engine.py`)
- YAML-driven finite state machine with event processing
- Dynamic action loading with pluggable architecture
- Context management and error recovery mechanisms
- Supports wildcard transitions for robust error handling

**⚡ Action System** (`src/actions/`)
- Plugin architecture with `BaseAction` interface
- `BashAction`: Shell command execution with parameter substitution and error mapping
- `DatabaseAction`: Pipeline step recording and job lifecycle management
- `LangChainAction`: Multi-provider LLM integration (Anthropic Claude, OpenAI GPT)
- Template-based parameter substitution prevents injection attacks

**🗄️ Database Layer** (`src/database/models.py`)
- Three-table SQLite design: `jobs`, `pipeline_results`, `pipeline_state`
- Repository pattern with `JobModel`, `PipelineResultModel`, `PipelineStateModel`
- Database-mediated inter-process communication
- FIFO job queue with atomic operations and orphaned job recovery

**🤖 LangChain Integration** (`src/langchain_integration/client.py`)
- Unified interface for multiple LLM providers
- Sophisticated import path management to prevent module conflicts
- Environment-based API key management with graceful degradation
- Support for both Anthropic Claude and OpenAI GPT models

### Core Features
- **Event-driven workflow**: State transitions triggered by events
- **Database integration**: SQLite-based job tracking and pipeline results
- **Bash action support**: Execute shell commands with parameter substitution
- **Dynamic action loading**: Pluggable action system for extensibility
- **Configuration as code**: Complete workflows defined in YAML

### Current Workflow States
1. **Waiting for Job**: Monitoring database queue for new research topics
2. **Researching**: Executing research script with LLM integration to generate Game Design Documents
3. **Completed**: Research finished and results recorded

### Core Features
- **Event-driven workflow**: State transitions triggered by database events
- **Database integration**: SQLite-based job tracking and research results
- **LLM integration**: Automated research via LangChain (Anthropic Claude, OpenAI GPT)
- **Game-focused research**: All topics generate comprehensive Game Design Documents
- **Template-based prompts**: Consistent research structure and quality

## Project Structure

```
dev-team/
├── archaeology/              # 📚 Complete architectural documentation
│   ├── README.md            # Main architecture overview
│   ├── INDEX.md             # Documentation navigation guide  
│   ├── src/                 # Component-level architecture analysis
│   ├── config/              # Configuration and deployment guide
│   └── docs/                # Visual diagrams and ADRs
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
│   │   └── check_database_queue_action.py # Database queue checking (uses JobModel directly)
│   ├── database/             # Database models and CLI
│   │   ├── __init__.py
│   │   ├── models.py         # Database models and schema
│   │   └── cli.py            # Database command-line interface
│   └── langchain_integration/ # LLM integration
│       ├── __init__.py
│       └── client.py         # Unified LangChain client
├── config/                   # Configuration files
│   └── development_process.yaml       # Research workflow configuration
├── scripts/                  # Executable scripts
│   ├── run_process.py        # CLI to run the state machine
│   ├── research.sh           # Research script with LLM integration
│   ├── llm_langchain.sh      # LangChain wrapper script
│   └── langchain_cli.py      # LangChain Python CLI
├── prompts/                  # LLM prompt templates
│   └── research_prompt.md    # Game Design Document research prompt
├── docs/                     # Documentation
│   ├── database.md           # Database implementation docs
│   ├── process.md            # Original process specification
│   └── todo.md               # Development tasks and notes
├── data/                     # Data storage
│   └── pipeline.db           # SQLite database (created automatically)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Optional: LangChain Integration

For LLM integration features, install additional dependencies:
```bash
pip install langchain-anthropic langchain-core
```

Set up environment variables:
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
# or
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

> 📋 **Detailed Setup**: See [Configuration & Deployment Guide](archaeology/config/README.md) for comprehensive installation and deployment instructions.

## Usage

## Quick Start

### Research Workflow Quick Commands

```bash
# Add a research job for game development
python src/database/cli.py add-research "Your Game Concept"

# Run the research state machine
python scripts/run_process.py --config config/development_process.yaml

# Check status and results
python src/database/cli.py status
python src/database/cli.py list
```

### Database Management

```bash
# Database CLI operations
python src/database/cli.py status
python src/database/cli.py list
python src/database/cli.py details <job_id>

# Show help for all available commands
python src/database/cli.py --help
```

## Detailed Usage

### Research Workflow (Game Design Documents)

The system now provides an automated research workflow for game development topics:

#### Adding Research Jobs

```bash
# Add a research job with a game concept topic
python src/database/cli.py add-research "Retro Arcade Space Shooter Game"

# Add research job with custom job ID
python src/database/cli.py add-research "Puzzle Platformer Adventure" --job-id custom_research_001

# Examples of game research topics
python src/database/cli.py add-research "Medieval Fantasy RPG with Crafting System"
python src/database/cli.py add-research "Multiplayer Tower Defense Strategy"
python src/database/cli.py add-research "VR Horror Escape Room Experience"
```

#### Running the Research State Machine

```bash
# Run the research state machine (monitors database for jobs)
python scripts/run_process.py --config config/development_process.yaml

# Run with debug logging to see detailed workflow
python scripts/run_process.py --config config/development_process.yaml --debug
```

#### Monitoring Research Progress

```bash
# Check database status
python src/database/cli.py status

# List all jobs (shows pending, processing, completed)
python src/database/cli.py list

# List only pending research jobs
python src/database/cli.py list --status pending

# Get details of a specific research job
python src/database/cli.py details <job_id>
```

#### Research Workflow Process

1. **Add Research Job**: Use CLI to add research topic to database
2. **State Machine Detects Job**: Automatically transitions from `waiting_for_job` → `researching`
3. **Research Execution**: Runs `scripts/research.sh` with topic from database
4. **LLM Integration**: Calls LangChain to generate comprehensive Game Design Document
5. **Completion**: Transitions to `completed` state and records results

#### Example Research Output

The system generates comprehensive Game Design Documents including:
- **Executive Summary**: High-level game vision and goals
- **Game Overview**: Core concept, genre, platform, and target audience  
- **Gameplay Mechanics**: Detailed system descriptions and interactions
- **Technical Specifications**: Engine requirements, performance targets
- **Art Bible**: Visual style guide and asset requirements
- **Audio Design**: Sound effects, music, and voice direction
- **Monetization Plan**: Business model and revenue projections
- **Development Timeline**: Milestones and resource requirements
- **Risk Assessment**: Technical and market risks with mitigation strategies

### Run the Development Process

```bash
# Run the full interactive version (requires manual acceptance)
python scripts/run_process.py --config config/development_process.yaml

# Run with debug logging
python scripts/run_process.py --config config/development_process.yaml --debug
```

### Database Operations

### Database Operations

```bash
# Database CLI operations
python src/database/cli.py status
python src/database/cli.py list
python src/database/cli.py details <job_id>

# Add research jobs
python src/database/cli.py add-research "Your Game Concept Here"

# Remove jobs if needed
python src/database/cli.py remove-job <job_id> --reason "Reason for removal"
```

### Testing Research Script Directly

```bash
# Test research script directly with a topic
./scripts/research.sh "Test Game Concept" "prompts/research_prompt.md"

# This will generate a Game Design Document for the specified topic
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

This implementation demonstrates advanced state machine patterns with sophisticated design decisions:

### 🎯 Key Architectural Decisions (from Archaeological Analysis)

**ADR-001: Event-Driven State Machine** - Chosen for predictable workflow execution and clear audit trails. All state transitions are event-triggered, enabling deterministic behavior and simplified debugging.

**ADR-002: Plugin-Based Action Architecture** - Enables extensibility without core engine modifications. Actions are dynamically loaded at runtime, providing clean separation of concerns and easy testing.

**ADR-003: SQLite for Persistence and Queuing** - Selected for zero external dependencies while providing ACID compliance. Three-table design supports complete job lifecycle with atomic queue operations.

**ADR-004: YAML Configuration-as-Code** - Makes workflows accessible to non-programmers and version-controllable. Supports multiple environments (dev/demo/production) through configuration inheritance.

**ADR-005: Database-Mediated Inter-Process Communication** - Uses database tables for coordination between Python components and shell scripts, providing persistence and atomic operations.

### 🏗️ Core Design Patterns

- **Finite State Machine**: Predictable workflow execution with event-driven transitions
- **Plugin Architecture**: Dynamic action loading with consistent interfaces  
- **Repository Pattern**: Clean data access abstraction with model classes
- **Template Method**: Extensible action execution with pluggable implementations
- **Configuration-as-Code**: Declarative workflow definition in YAML

## Original Specification

The state machine implements the development process defined in `process.md`, providing a concrete, executable representation of the team workflow described in that document.