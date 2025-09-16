#!/bin/bash

# End-to-End Test Script
# Tests the complete workflow: research -> backlog -> architecture
# Generates organized output files

set -e

TEST_TOPIC="Mastermind game"
TEST_ID="mastermind_e2e_test"
RESULTS_DIR="test_results"

echo "🧪 Starting End-to-End Test"
echo "Topic: '$TEST_TOPIC'"
echo "Test ID: '$TEST_ID'"
echo "Results: $RESULTS_DIR/"
echo "=================================="

# Clean up previous test files and database entries
echo "🧹 Cleaning up previous test files and database entries..."
rm -f mastermind_e2e_test_*
rm -rf "$RESULTS_DIR"
mkdir -p "$RESULTS_DIR"

# Also clean up any previous test_results files
rm -f test_results/*

# Remove previous test data from database
echo "🗑️ Removing previous test data from database..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from database.models import get_database
db = get_database()
with db._get_connection() as conn:
    # Remove architecture versions
    conn.execute('DELETE FROM architecture_versions WHERE research_id = ?', ('$TEST_ID',))
    # Remove user stories
    conn.execute('DELETE FROM user_stories WHERE research_id = ?', ('$TEST_ID',))
    # Remove research results
    conn.execute('DELETE FROM research_results WHERE job_id = ?', ('$TEST_ID',))
    conn.commit()
    print('✅ Previous test data removed from database')
"

# Step 1: Research
echo ""
echo "📖 Step 1: Research Phase"
echo "--------------------------"
./scripts/research.sh "$TEST_TOPIC" "prompts/research_prompt.md" "$TEST_ID"

# Export research result
echo "📝 Exporting research result..."
python scripts/view_results.py research --id "$TEST_ID" > "$RESULTS_DIR/1_research_result.txt"

# Step 2: Backlog Processing  
echo ""
echo "📋 Step 2: Backlog Processing"
echo "-----------------------------"
./scripts/backlog.sh "$TEST_ID" "prompts/backlog_prompt.md" "${TEST_ID}_backlog"

# Export stories
echo "📝 Exporting user stories..."
python scripts/view_results.py stories --research-id "$TEST_ID" -v > "$RESULTS_DIR/2_user_stories.txt"

# Step 3: Architecture Planning (first story)
FIRST_STORY="${TEST_ID}_story_1"
echo ""
echo "🏗️ Step 3: Architecture Planning"
echo "--------------------------------"
echo "Planning architecture for: $FIRST_STORY"
./scripts/architecture.sh "$FIRST_STORY" "prompts/architecture_prompt.md" "${TEST_ID}_arch"

# Export architecture
echo "📝 Exporting architecture..."
python scripts/view_results.py architecture --research-id "$TEST_ID" > "$RESULTS_DIR/3_architecture.txt"

# Step 4: Generate comprehensive exports
echo ""
echo "📤 Step 4: Comprehensive Exports"
echo "--------------------------------"
python scripts/export_results.py "$TEST_ID" --format json --output "$RESULTS_DIR/full_export.json"
python scripts/export_results.py "$TEST_ID" --format markdown --output "$RESULTS_DIR/documentation.md"
python scripts/export_results.py "$TEST_ID" --format csv --output "$RESULTS_DIR/stories.csv"

# Summary
echo ""
echo "✅ End-to-End Test Completed!"
echo "=============================="
echo "Results in: $RESULTS_DIR/"
echo ""
echo "Generated files:"
ls -la "$RESULTS_DIR/"

echo ""
echo "🔍 Test Summary:"
echo "Research ID: $TEST_ID"
echo "Stories generated: $(python scripts/view_results.py stories --research-id "$TEST_ID" | grep -c '_story_')"
echo "Architecture components: $(python scripts/view_results.py architecture --research-id "$TEST_ID" | grep -c '^  - ')"