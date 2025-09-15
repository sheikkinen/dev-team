# Todo for Dev Team

Project has following parts:
- Process
- Database 
- Sample Product

# The Process

The idea for the process is to have a state machine that runs ecah step of the process. Building of the state machine is excluded from the project scope. 

Initial Steps:
- Research of the Sample Product domain - Deep Research, Website Analysis, Competitor Analysis
- Initial Product Design - analysis of the requirements, user stories, use cases, and domain model

The Development Loop / Kanban:
- Product Owner: Backlog
- Architect: Update System Architecture
- Tester: Test Planning
- Developer: Updating Module and Function Descriptions
- Developer: Updating Function Implementations
- UX Designer: UI/UX Design
- Frontend Developer: Updating Frontend Implementations
- Tester: Testing
- Team: Demo
- Product Owner: Review and Accept

Tasks:
- [ ] Create the process.md file, describing the process - Mermaid diagram

# The Database

All operations of software development are stored in a database. The database is a relational database, implemented in SQLite. Software is created first in the database allowing easy way to manipulate the data.

Runnable code is generated from the database.

Tasks:
- [ ] Create the database.md file, describing the key entities and their relationships - Mermaid diagram

# The Sample Product

Sample Product is a web application with a backend and a frontend. The backend is a REST API, the frontend is a web application that consumes the REST API.

Sample Product is a game of Mastermind.

Tasks:
- [ ] Create the mastermind.md file - a Game Design Document

# Setup

## State Machine Engine

Check ../face-changer/src for statemachine engine implementation and config folder for state definitions. Overview in  ../face-changer/CLAUDE.md 

Copy code needed for process.md implementation, 1 sec sleep as the demo action.

Check ../face-changer/src for statemachine engine implementation for Dynamic import of actions and bash_action. Implement bash action: sample echo command.

## Run the demo
python run_process.py --config config/development_process_demo.yaml

## Full workflow (requires manual review acceptance)
python run_process.py --config config/development_process.yaml

## Database

Check ../face-changer/src for database implementation and config folder for state definitions. State Machine Engine has already been copied. Overview in ../face-changer/CLAUDE.md 

Copy code needed for database.md implementation. 

Run the demo
python run_process.py --config config/development_process_demo.yaml

Add filling the demo data to the database.

Add a demo script outputting the data from the database in a readable format.

## LLM Usage

Check /Volumes/Backup-2021/deviant-working/loop.sh for LLM usage example: delegating work to claude.

Create scripts/llm_claude.sh and use it as bash_action - start with hello world task.

