#!/bin/bash
# Test script to verify GCC coverage fix
set -e

echo "🔧 Testing GCC Coverage Fix"
echo "=========================="

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Clean up any existing build
log_info "Cleaning up existing build..."
rm -rf build

# Test 1: Check if we can detect GCC vs Clang
log_info "Testing compiler detection..."

# Try to use GCC if available
if command -v gcc >/dev/null 2>&1; then
    GCC_VERSION=$(gcc --version | head -n1)
    log_info "Found GCC: $GCC_VERSION"
    
    # Check if it's really GCC or Clang masquerading as GCC
    if gcc --version | grep -q "clang"; then
        log_warning "gcc command is actually Clang (common on macOS)"
        USE_CLANG=true
    else
        log_success "Found real GCC"
        USE_CLANG=false
    fi
else
    log_warning "GCC not found, will use Clang"
    USE_CLANG=true
fi

# Test 2: Build with coverage
log_info "Building with coverage..."
mkdir -p build
cd build

if [ "$USE_CLANG" = "true" ]; then
    log_info "Using Clang for coverage build..."
    CC=clang CXX=clang++ cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
else
    log_info "Using GCC for coverage build..."
    CC=gcc CXX=g++ cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
fi

make

if [ $? -eq 0 ]; then
    log_success "Build completed successfully"
else
    log_error "Build failed"
    exit 1
fi

# Test 3: Run a simple test to generate coverage data
log_info "Running tests to generate coverage data..."
cd ..

# Find Python executable
PYTHON=""
for py in /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 python3 python; do
    if command -v "$py" >/dev/null 2>&1 && $py -m pytest --version >/dev/null 2>&1; then
        PYTHON="$py"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    log_error "Python with pytest not found"
    exit 1
fi

# Set up coverage environment for Clang
if [ "$USE_CLANG" = "true" ]; then
    export LLVM_PROFILE_FILE="build/coverage-%p.profraw"
fi

# Run a subset of tests
log_info "Running dynamic array tests..."
$PYTHON -m pytest tests/test_dynarray.py::TestDynamicArrayOperations::test_dynarray_create_basic -v

if [ $? -eq 0 ]; then
    log_success "Tests completed successfully"
else
    log_error "Tests failed"
    exit 1
fi

# Test 4: Generate coverage report
log_info "Generating coverage report..."
cd build

# Check for coverage files
if [ "$USE_CLANG" = "true" ]; then
    log_info "Checking for Clang coverage files..."
    if ls *.profraw 1> /dev/null 2>&1; then
        log_success "Found .profraw files"
        ls -la *.profraw
    else
        log_warning "No .profraw files found"
    fi
else
    log_info "Checking for GCC coverage files..."
    if find . -name "*.gcda" | head -1 | grep -q .; then
        log_success "Found .gcda files"
        find . -name "*.gcda" -o -name "*.gcno" | head -5
    else
        log_warning "No .gcda files found"
    fi
fi

# Try to generate coverage report
log_info "Attempting to generate coverage report..."
if make coverage-report; then
    log_success "Coverage report generated successfully!"
    
    # Check if HTML report was created
    if [ -d "coverage/html" ] && [ -f "coverage/html/index.html" ]; then
        log_success "HTML coverage report created at build/coverage/html/index.html"
    fi
    
    # Check if LCOV report was created
    if [ -f "coverage/coverage.info" ]; then
        log_success "LCOV coverage report created at build/coverage/coverage.info"
        
        # Show a summary
        log_info "Coverage summary:"
        if command -v lcov >/dev/null 2>&1; then
            lcov --summary coverage/coverage.info 2>/dev/null || true
        fi
    fi
else
    log_error "Coverage report generation failed"
    echo "This might be the issue we're trying to fix."
    echo "Check the error messages above for details."
    exit 1
fi

cd ..

log_success "All tests passed! Coverage fix appears to be working."
echo ""
log_info "Summary:"
echo "  - Compiler used: $(if [ "$USE_CLANG" = "true" ]; then echo "Clang"; else echo "GCC"; fi)"
echo "  - Build: ✅ Success"
echo "  - Tests: ✅ Success"  
echo "  - Coverage: ✅ Success"
echo ""
log_info "The coverage fix should now work in CI environments."
