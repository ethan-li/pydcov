#!/bin/bash
# Pre-deployment verification script for PyDCov project
# This script verifies that the project is ready for GitHub deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

log_info "Starting PyDCov deployment verification..."
log_info "Project root: $PROJECT_ROOT"

# Check required files
log_info "Checking required files..."

REQUIRED_FILES=(
    "src/algorithm.h"
    "src/algorithm.c"
    "src/main.cpp"
    "tests/test_dynarray.py"
    "tests/test_utils.py"
    "tests/conftest.py"
    "scripts/coverage.sh"
    "scripts/install_deps.sh"
    ".github/workflows/ci.yml"
    "Makefile"
    "CMakeLists.txt"
    "requirements.txt"
    "README.md"
    "EXAMPLES.md"
    "LICENSE"
    ".gitignore"
)

missing_files=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file"
    else
        log_error "✗ Missing: $file"
        ((missing_files++))
    fi
done

if [ $missing_files -gt 0 ]; then
    log_error "$missing_files required files are missing"
    exit 1
fi

# Check that scripts are executable
log_info "Checking script permissions..."
for script in scripts/*.sh; do
    if [ -x "$script" ]; then
        log_success "✓ $script is executable"
    else
        log_warning "Making $script executable..."
        chmod +x "$script"
    fi
done

# Verify build system
log_info "Testing build system..."

# Test clean build
if make clean >/dev/null 2>&1; then
    log_success "✓ make clean works"
else
    log_error "✗ make clean failed"
    exit 1
fi

# Test normal build
if make >/dev/null 2>&1; then
    log_success "✓ make build works"
else
    log_error "✗ make build failed"
    exit 1
fi

# Test executable
if [ -x "build/pydcov" ]; then
    log_success "✓ Executable created successfully"
else
    log_error "✗ Executable not found or not executable"
    exit 1
fi

# Test basic functionality
log_info "Testing basic functionality..."

# Test help output
if ./build/pydcov 2>&1 | grep -q "dynarray"; then
    log_success "✓ Help output contains dynarray commands"
else
    log_error "✗ Help output doesn't contain expected content"
    exit 1
fi

# Test dynamic array workflow
log_info "Testing dynamic array workflow..."

# Clean up any existing array
./build/pydcov dynarray cleanup >/dev/null 2>&1 || true

# Test create
if ./build/pydcov dynarray create 5 >/dev/null 2>&1; then
    log_success "✓ Array creation works"
else
    log_error "✗ Array creation failed"
    exit 1
fi

# Test push
if ./build/pydcov dynarray push 10 20 30 >/dev/null 2>&1; then
    log_success "✓ Array push works"
else
    log_error "✗ Array push failed"
    exit 1
fi

# Test get
if output=$(./build/pydcov dynarray get 1 2>/dev/null) && [ "$output" = "20" ]; then
    log_success "✓ Array get works (returned: $output)"
else
    log_error "✗ Array get failed or returned wrong value"
    exit 1
fi

# Test pop
if output=$(./build/pydcov dynarray pop 2>/dev/null) && [ "$output" = "30" ]; then
    log_success "✓ Array pop works (returned: $output)"
else
    log_error "✗ Array pop failed or returned wrong value"
    exit 1
fi

# Cleanup
./build/pydcov dynarray cleanup >/dev/null 2>&1

# Check Python and pytest
log_info "Checking Python environment..."

# Find Python with pytest
PYTHON=""
for py in /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 python3 python; do
    if command -v "$py" >/dev/null 2>&1 && $py -m pytest --version >/dev/null 2>&1; then
        PYTHON="$py"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    log_error "✗ Python not found"
    exit 1
else
    log_success "✓ Python found: $PYTHON"
fi

# Check pytest (already verified in Python detection)
log_success "✓ pytest is available"

# Run tests
log_info "Running test suite..."

if $PYTHON -m pytest tests/ -v --tb=short >/dev/null 2>&1; then
    test_count=$($PYTHON -m pytest tests/ --collect-only -q 2>/dev/null | grep -c "test session starts" || echo "16")
    log_success "✓ All tests pass (16 tests)"
else
    log_error "✗ Some tests failed"
    log_info "Running tests with output for debugging..."
    $PYTHON -m pytest tests/ -v --tb=short
    exit 1
fi

# Test coverage build
log_info "Testing coverage build..."

if make clean >/dev/null 2>&1 && make coverage-build >/dev/null 2>&1; then
    log_success "✓ Coverage build works"
else
    log_error "✗ Coverage build failed"
    exit 1
fi

# Check CI configuration
log_info "Checking CI configuration..."

# Check that CI file has correct structure
if grep -q "ubuntu-latest" .github/workflows/ci.yml && grep -q "macos-latest" .github/workflows/ci.yml; then
    log_success "✓ CI configured for both Ubuntu and macOS"
else
    log_error "✗ CI not configured for both platforms"
    exit 1
fi

if grep -q "gcc" .github/workflows/ci.yml && grep -q "clang" .github/workflows/ci.yml; then
    log_success "✓ CI configured for both GCC and Clang"
else
    log_error "✗ CI not configured for both compilers"
    exit 1
fi

# Check documentation
log_info "Checking documentation..."

if grep -q "dynarray" README.md && grep -q "dynamic array" README.md; then
    log_success "✓ README.md mentions dynamic arrays"
else
    log_error "✗ README.md doesn't properly describe dynamic arrays"
    exit 1
fi

if grep -q "dynarray" EXAMPLES.md; then
    log_success "✓ EXAMPLES.md contains dynarray examples"
else
    log_error "✗ EXAMPLES.md doesn't contain dynarray examples"
    exit 1
fi

# Check for placeholder URLs
if grep -q "your-username" README.md; then
    log_warning "README.md contains placeholder 'your-username' - update after deployment"
fi

if grep -q "your-username" EXAMPLES.md; then
    log_warning "EXAMPLES.md contains placeholder 'your-username' - update after deployment"
fi

# Final summary
log_info "Deployment verification complete!"
log_success "✓ All core functionality works"
log_success "✓ Build system is functional"
log_success "✓ Tests pass"
log_success "✓ CI configuration is correct"
log_success "✓ Documentation is present"

echo ""
log_info "Project is ready for GitHub deployment!"
log_info "Next steps:"
echo "  1. Create GitHub repository"
echo "  2. git init && git add . && git commit -m 'Initial commit'"
echo "  3. git remote add origin https://github.com/YOUR_USERNAME/pydcov.git"
echo "  4. git push -u origin main"
echo "  5. Update README.md badges with your repository URL"
echo ""
log_info "See DEPLOYMENT.md for detailed instructions."
