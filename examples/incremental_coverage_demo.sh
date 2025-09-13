#!/bin/bash

# ==============================================================================
# Incremental Coverage Demo Script
# ==============================================================================
# This script demonstrates the incremental coverage collection workflow
# by running different test scenarios and showing how coverage accumulates.
#
# Usage: ./examples/incremental_coverage_demo.sh
# ==============================================================================

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COVERAGE_TOOLS_DIR="${PROJECT_ROOT}/coverage_tools"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log_demo() {
    echo -e "${MAGENTA}[DEMO]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to pause and wait for user input
pause_for_user() {
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r
}

# Function to show a separator
show_separator() {
    echo ""
    echo "=============================================="
    echo "$1"
    echo "=============================================="
    echo ""
}

# Function to run a command and show its output
run_demo_command() {
    local description="$1"
    local command="$2"
    
    log_step "$description"
    echo -e "${CYAN}Command:${NC} $command"
    echo ""
    
    # Run the command
    eval "$command"
    
    echo ""
    log_success "Command completed"
}

# Main demo function
main() {
    cd "${PROJECT_ROOT}"
    
    show_separator "Incremental Coverage Collection Demo"
    
    log_demo "This demo will show you how to use incremental coverage collection"
    log_demo "to accumulate coverage data across multiple pytest executions."
    echo ""
    log_info "We'll demonstrate:"
    log_info "  1. Building the project with coverage"
    log_info "  2. Initializing incremental coverage"
    log_info "  3. Running tests incrementally"
    log_info "  4. Checking status between runs"
    log_info "  5. Generating the final comprehensive report"
    
    pause_for_user
    
    # Step 1: Build with coverage
    show_separator "Step 1: Build Project with Coverage"
    
    log_demo "First, we need to build the project with coverage instrumentation."
    log_demo "This enables the compiler to generate coverage data during test execution."
    
    run_demo_command "Building project with coverage instrumentation" \
                     "pydcov coverage build"
    
    pause_for_user
    
    # Step 2: Initialize incremental coverage
    show_separator "Step 2: Initialize Incremental Coverage"
    
    log_demo "Now we'll initialize the incremental coverage system."
    log_demo "This cleans any existing coverage data and prepares for incremental collection."
    
    run_demo_command "Initializing incremental coverage collection" \
                     "pydcov incremental init"
    
    pause_for_user
    
    # Step 3: Check initial status
    show_separator "Step 3: Check Initial Status"
    
    log_demo "Let's check the status to see the initial state."
    
    run_demo_command "Checking incremental coverage status" \
                     "pydcov incremental status"
    
    pause_for_user
    
    # Step 4: Run first batch of tests
    show_separator "Step 4: Run First Batch of Tests"
    
    log_demo "Now we'll run the algorithm module tests and add their coverage data."
    log_demo "This demonstrates running a specific subset of tests."
    
    if [[ -d "algorithm/tests" ]]; then
        run_demo_command "Running algorithm module tests and adding coverage" \
                         "pydcov incremental add \"python -m pytest algorithm/tests/ -v\""
    else
        log_warning "Algorithm tests directory not found, skipping this step"
    fi
    
    pause_for_user
    
    # Step 5: Check status after first run
    show_separator "Step 5: Check Status After First Run"
    
    log_demo "Let's see how the status has changed after the first test run."
    
    run_demo_command "Checking status after first test run" \
                     "pydcov incremental status"
    
    pause_for_user
    
    # Step 6: Run second batch of tests
    show_separator "Step 6: Run Second Batch of Tests"
    
    log_demo "Now we'll run the statistics module tests and add their coverage data."
    log_demo "This shows how coverage accumulates across multiple test runs."
    
    if [[ -d "statistics/tests" ]]; then
        run_demo_command "Running statistics module tests and adding coverage" \
                         "pydcov incremental add \"python -m pytest statistics/tests/ -v\""
    else
        log_warning "Statistics tests directory not found, skipping this step"
    fi
    
    pause_for_user
    
    # Step 7: Check status after second run
    show_separator "Step 7: Check Status After Second Run"
    
    log_demo "Let's see how the coverage data has accumulated."
    
    run_demo_command "Checking status after second test run" \
                     "pydcov incremental status"
    
    pause_for_user
    
    # Step 8: Run specific tests
    show_separator "Step 8: Run Specific Tests (Optional)"
    
    log_demo "We can also run specific test files or test methods."
    log_demo "This is useful for targeted testing and coverage collection."
    
    # Try to find a specific test file to demonstrate
    if [[ -f "algorithm/tests/test_dynarray.py" ]]; then
        run_demo_command "Running specific test file" \
                         "pydcov incremental add \"python -m pytest algorithm/tests/test_dynarray.py::test_create -v\""
    else
        log_info "Specific test file not found, showing example command:"
        echo -e "${CYAN}Example:${NC} pydcov incremental add \"python -m pytest tests/test_specific.py::test_method\""
    fi
    
    pause_for_user
    
    # Step 9: Merge coverage data
    show_separator "Step 9: Merge All Coverage Data"
    
    log_demo "Now we'll merge all the accumulated coverage data into a single dataset."
    log_demo "This combines coverage from all the test runs we've performed."
    
    run_demo_command "Merging all incremental coverage data" \
                     "pydcov incremental merge"
    
    pause_for_user
    
    # Step 10: Generate final report
    show_separator "Step 10: Generate Final Comprehensive Report"
    
    log_demo "Finally, we'll generate the comprehensive coverage report."
    log_demo "This report shows the combined coverage from all test runs."
    
    run_demo_command "Generating final comprehensive coverage report" \
                     "pydcov incremental report"
    
    pause_for_user
    
    # Step 11: Final status check
    show_separator "Step 11: Final Status Check"
    
    log_demo "Let's check the final status to see all the generated files."
    
    run_demo_command "Checking final status" \
                     "pydcov incremental status"
    
    pause_for_user
    
    # Step 12: Show results
    show_separator "Demo Complete!"
    
    log_success "Incremental coverage collection demo completed successfully!"
    echo ""
    log_info "What we accomplished:"
    log_info "  ✓ Built the project with coverage instrumentation"
    log_info "  ✓ Initialized incremental coverage collection"
    log_info "  ✓ Ran multiple test suites incrementally"
    log_info "  ✓ Accumulated coverage data across runs"
    log_info "  ✓ Merged all coverage data into a comprehensive dataset"
    log_info "  ✓ Generated a final comprehensive coverage report"
    echo ""
    log_success "Your comprehensive coverage report is available at:"
    log_success "  ${PROJECT_ROOT}/build/coverage/incremental_report/index.html"
    echo ""
    log_info "You can now:"
    log_info "  • Open the HTML report in your browser"
    log_info "  • Use the LCOV data for CI/CD integration"
    log_info "  • Run additional tests and add to the coverage"
    log_info "  • Clean and restart the incremental process"
    echo ""
    log_demo "Try these commands to explore further:"
    echo -e "${CYAN}  # Open the coverage report${NC}"
    echo "  open build/coverage/incremental_report/index.html"
    echo ""
    echo -e "${CYAN}  # Add more tests to the coverage${NC}"
    echo "  pydcov incremental add \"python -m pytest tests/additional_tests.py\""
    echo ""
    echo -e "${CYAN}  # Clean and start over${NC}"
    echo "  pydcov incremental clean"
    echo ""
    echo -e "${CYAN}  # Get help${NC}"
    echo "  pydcov incremental --help"
    echo ""
}

# Check if we're in the right directory
if [[ ! -f "CMakeLists.txt" ]]; then
    echo "Error: This script must be run from the project root directory."
    echo "Please cd to the project root and run: ./examples/incremental_coverage_demo.sh"
    exit 1
fi

# Check if required Python tools exist
if [[ ! -f "${COVERAGE_TOOLS_DIR}/scripts/incremental_coverage.py" ]]; then
    echo "Error: Python incremental coverage script not found: ${COVERAGE_TOOLS_DIR}/scripts/incremental_coverage.py"
    exit 1
fi

# Run the demo
main "$@"
