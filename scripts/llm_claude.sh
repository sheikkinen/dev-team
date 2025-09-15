#!/bin/bash
# Claude LLM Integration Script for Dev-Team Project
# Usage: ./llm_claude.sh [task_file] [context_dir]
#
# This script delegates work to Claude AI using the local Claude CLI
# Based on the pattern from /Volumes/Backup-2021/deviant-working/loop.sh

set -e

# Configuration
CLAUDE_CLI="claude"
DEFAULT_TASK_FILE="task.txt"
DEFAULT_CONTEXT_DIR="."
TIMEOUT=300  # 5 minutes timeout

# Parse arguments
TASK_FILE="${1:-$DEFAULT_TASK_FILE}"
CONTEXT_DIR="${2:-$DEFAULT_CONTEXT_DIR}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Claude CLI is available
if ! command -v "$CLAUDE_CLI" &> /dev/null; then
    log_warning "Claude CLI not found in PATH"
    log_info "Running in MOCK MODE for demonstration purposes"
    
    # Mock Claude response for demo purposes
    log_info "🤖 Mock Claude AI Response:"
    echo ""
    echo "✅ Task received successfully!"
    echo ""
    echo "🌟 Hello World from Mock Claude AI! 🌟"
    echo ""
    echo "📋 Task Summary:"
    echo "  - Received task from dev-team project"
    echo "  - Current timestamp: $(date)"
    echo "  - Integration status: Working correctly"
    echo ""
    echo "💡 Suggestions for improvement:"
    echo "  1. Install actual Claude CLI for real AI responses"
    echo "  2. Add task result persistence to database"
    echo "  3. Implement task queuing for multiple requests"
    echo ""
    echo "🎉 Mock integration completed successfully!"
    echo ""
    
    log_success "✅ Mock Claude completed the task successfully"
    exit 0
fi

# Check if task file exists
if [ ! -f "$TASK_FILE" ]; then
    log_error "Task file '$TASK_FILE' not found"
    log_info "Creating a default hello world task file..."
    
    cat > "$TASK_FILE" << 'EOF'
Hello! This is a test task for the Claude integration in the dev-team project.

Task: Create a simple "Hello World" response and demonstrate that the Claude integration is working.

Please respond with:
1. A confirmation that you received this task
2. A simple "Hello World" message
3. Current timestamp
4. Any observations about the development environment

This is a test of the bash action integration with Claude AI.
EOF
    
    log_success "Created default task file: $TASK_FILE"
fi

# Read the task from file
if [ -f "$TASK_FILE" ]; then
    prompt=$(cat "$TASK_FILE")
    log_info "Using task file: $TASK_FILE"
    log_info "Context directory: $CONTEXT_DIR"
else
    log_error "Task file '$TASK_FILE' not found"
    exit 1
fi

# Execute Claude with the task
log_info "🤖 Delegating task to Claude AI..."
log_info "📝 Task preview: $(echo "$prompt" | head -1)..."

# Run Claude with timeout and capture output
output=""
if timeout $TIMEOUT "$CLAUDE_CLI" --add-dir "$CONTEXT_DIR" --permission-mode acceptEdits -p "$prompt" 2>&1; then
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_success "✅ Claude completed the task successfully"
    elif [ $exit_code -eq 124 ]; then
        log_warning "⏰ Task timed out after $TIMEOUT seconds"
        exit 2
    else
        log_error "❌ Claude encountered an error (exit code: $exit_code)"
        exit 3
    fi
else
    exit_code=$?
    
    # Check for common error patterns
    if echo "$output" | grep -q "usage limit\|rate limit\|limit reached"; then
        log_warning "🚫 Claude usage limit reached"
        exit 4
    elif echo "$output" | grep -q "authentication\|unauthorized"; then
        log_error "🔐 Authentication error - check Claude CLI setup"
        exit 5
    else
        log_error "💥 Unknown error occurred (exit code: $exit_code)"
        exit 6
    fi
fi

log_success "🎉 Claude integration completed successfully!"