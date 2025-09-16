# Product Backlog Processing Tasks

Aim for simple, skeleton implementations to demonstrate the workflow.

## ✅ 1. Create Backlog Prompt Template
Create `prompts/backlog_prompt.md` template to split product concepts into user stories and components. Focus on brief, structured output.

## ✅ 2. Update Config YAML
Add backlog states to `config/development_process.yaml`: waiting_for_backlog -> splitting_stories -> components_analysis -> completed

## ✅ 3. Modify LangChain Integration
Update `src/langchain_integration/client.py` to add `split_into_array()` method returning structured JSON responses.

## ✅ 4. Create Backlog Script
Create `scripts/backlog.sh` processing script similar to research.sh but handling array outputs.

## ✅ 5. Add Backlog CLI
Update `scripts/langchain_cli.py` to support `--format json` for structured responses.

## ✅ 6. Database Schema Updates
Add backlog processing tables to handle user stories and components separately.

## ✅ 7. Update State Machine Processing
Modify YAML processor to handle single story processing with array iteration.

# Architecture Planning Tasks

## ✅ 8. Create Architecture Prompt Template
Create `prompts/architecture_prompt.md` template to generate system architecture from user stories. Focus on components, data flow, APIs.

## ✅ 9. Update Config YAML for Architecture
Add architecture states: waiting_for_architecture -> planning_components -> defining_interfaces -> technical_design -> completed

## ✅ 10. Extend LangChain for Architecture
Add `plan_architecture()` method to return structured JSON with components, interfaces, dependencies.

## ✅ 11. Create Architecture Script
Create `scripts/architecture.sh` processing user stories into technical architecture plans.

## ✅ 12. Architecture CLI Support
Extend CLI with `--type architecture` for technical planning responses.

## ✅ 13. Database Architecture Schema
Add tables for components, interfaces, dependencies, technical specifications.

## ✅ 14. Architecture Processing
Handle architecture JSON arrays with component-level processing and dependency mapping.

# Database Flow Notes

## Story Splitting Input
- Takes research result as input from database
- Splits into user stories and components
- Stores each story separately for individual processing

## Architecture Planning Input  
- Takes current architecture (if exists) from database
- Takes research result from database
- Takes current story being processed
- Revises architecture incrementally - simple at each step
- Stores new architecture version

## Processing Flow
1. Research → Database
2. Story Splitting (input: research) → Stories in Database  
3. For each story: Architecture Planning (input: current_arch + research + story) → Updated Architecture
4. Simple, incremental architecture evolution

## End to End test

Test the full workflow: with prompt "Mastermind game", run through research, backlog splitting, and architecture planning. Verify database entries at each stage. Provide CLI commands to view and export results.

## ✅ CLI Tools Created

**View Results:**
```bash
python scripts/view_results.py research                    # List all research
python scripts/view_results.py research --id <research_id> # View specific research
python scripts/view_results.py stories --research-id <id>  # View stories for research
python scripts/view_results.py architecture --research-id <id> # View architecture
```

**Export Results:**
```bash
python scripts/export_results.py <research_id> --format json      # Export as JSON
python scripts/export_results.py <research_id> --format markdown  # Export as docs
python scripts/export_results.py <research_id> --format csv       # Export stories CSV
```

## Clean Test Results and Rerun

1. Clear current mastermind_test result files
2. Create test_results folder
3. Create separate result files for research results, all user stories and architecture
4. Rerun end to end test with organized output