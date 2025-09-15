# Database Implementation

## Overview

The dev-team project uses a SQLite database to track development process execution, job management, and pipeline results. The database implementation is based on the proven architecture from the face-changer project and provides persistent storage for the state machine workflow.

## Current Database Schema

The database consists of three main tables:

### Jobs Table
Stores development process jobs and their lifecycle information.

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT UNIQUE NOT NULL,
    input_image_path TEXT NOT NULL,           -- Input file/project path
    user_prompt TEXT,                         -- Development task description
    padding_factor REAL DEFAULT 1.5,         -- Configuration parameter
    mask_padding_factor REAL DEFAULT 1.2,    -- Configuration parameter
    status TEXT DEFAULT 'pending',           -- pending|processing|completed|failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);
```

### Pipeline Results Table
Records completion of individual development process steps.

```sql
CREATE TABLE pipeline_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    step_name TEXT NOT NULL,                  -- Name of development process step
    step_number INTEGER NOT NULL,            -- Sequential step number
    face_coordinates TEXT,                   -- JSON: Step-specific coordinates data
    crop_dimensions TEXT,                    -- JSON: Step-specific dimensions data
    file_paths TEXT,                        -- JSON: Generated/processed file paths
    metadata TEXT,                          -- JSON: Step metadata and description
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
);
```

### Pipeline State Table
Provides communication between state machine and shell scripts.

```sql
CREATE TABLE pipeline_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    base_filename TEXT NOT NULL,
    current_step INTEGER DEFAULT 1,
    step_name TEXT,
    input_file TEXT,
    output_file TEXT,
    face_coords_raw TEXT,                   -- Raw coordinate data
    crop_geometry TEXT,                     -- Geometric transformations
    extracted_prompt TEXT,                 -- Extracted prompts/requirements
    processing_notes TEXT,                 -- Step-specific notes
    success BOOLEAN DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
);
```

## Database Models

The database is accessed through Python model classes:

### JobModel
- `create_job()` - Create new development process job
- `get_next_job()` - Retrieve next pending job for processing
- `complete_job()` - Mark job as completed
- `fail_job()` - Mark job as failed with error message
- `list_jobs()` - List jobs with optional status filtering
- `count_jobs()` - Count jobs by status

### PipelineResultModel
- `record_step()` - Record completion of a development process step
- `get_job_results()` - Get all pipeline results for a job
- `get_face_coordinates()` - Get coordinates for specific job
- `get_crop_dimensions()` - Get dimensions for specific job

### PipelineStateModel
- `store_coordinates()` - Store coordinates for shell script communication
- `get_coordinates()` - Retrieve coordinates
- `store_crop_geometry()` - Store geometric data
- `get_crop_geometry()` - Retrieve geometric data
- `store_prompt()` - Store extracted prompts
- `get_prompt()` - Retrieve prompts
- `store_step_result()` - Store general step results
- `get_step_result()` - Retrieve step results

## State Machine Integration

The database integrates with the state machine engine through the `database_record_action`:

```yaml
# Example configuration
actions:
  research:
    - type: sleep_action
      description: "Deep Research Phase"
      message: "Conducting deep research, website analysis, and competitor analysis"
      duration: 1
    - type: database_record_action
      step_name: "research"
      step_number: 1
      description: "Deep Research Phase - Market analysis and requirements gathering"
```

Each state can record its completion to the database, providing:
- Step tracking and progress monitoring
- Metadata storage for each development phase
- Process execution history
- Debugging and audit trail

## Usage Examples

### Running Development Process with Database Tracking

```bash
# Run the complete demo with database tracking
python demo_database.py

# Run just the development process state machine
python run_process.py --config config/development_process_demo_db.yaml
```

### Database CLI Operations

```bash
# Show database status
python src/database/cli.py status

# List all jobs
python src/database/cli.py list

# Show specific job details
python src/database/cli.py details <job_id>

# Add a new job
python src/database/cli.py add-job my_job /path/to/project.py --prompt "Create REST API"

# Clean up completed jobs
python src/database/cli.py cleanup --status completed
```

### Reading Database Contents

```bash
# Display readable database summary
python demo_database_reader.py
```

## Demo Scripts

### demo_database.py
Complete demonstration script that:
1. Creates sample development jobs
2. Runs the development process state machine
3. Records all steps to database
4. Displays results

### demo_database_reader.py
Database reader that displays:
- Job summary and statistics
- All jobs with details
- Pipeline execution results
- Recent activity

## Database Features

### Persistent Storage
- SQLite database in `data/pipeline.db`
- Automatic table creation and schema management
- ACID transactions for data integrity

### State Machine Integration
- Records each development process step
- Tracks job lifecycle (pending → processing → completed/failed)
- Stores step metadata and execution context

### CLI Management
- Full command-line interface for database operations
- Job creation, listing, and cleanup
- Status monitoring and reporting

### Process Tracking
- Complete audit trail of development process execution
- Step-by-step progress tracking
- Error handling and failure reporting

## Development Workflow

1. **Job Creation**: Create development jobs with project details and requirements
2. **Process Execution**: State machine executes development process steps
3. **Step Recording**: Each step records completion and metadata to database
4. **Progress Monitoring**: Use CLI or reader scripts to monitor progress
5. **Results Review**: Examine completed jobs and process execution history

The database provides a robust foundation for tracking and managing the complete software development lifecycle within the state machine framework.