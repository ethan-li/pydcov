#!/bin/bash
# Coverage collection and reporting script for pydcov project
# Supports both GCC (gcov) and Clang (llvm-cov) on Linux and macOS

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build"
COVERAGE_DIR="${BUILD_DIR}/coverage"
SRC_DIR="${PROJECT_ROOT}/src"

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

# Detect compiler
detect_compiler() {
    if command -v gcc >/dev/null 2>&1; then
        if gcc --version | grep -q "clang"; then
            echo "clang"
        else
            echo "gcc"
        fi
    elif command -v clang >/dev/null 2>&1; then
        echo "clang"
    else
        log_error "No supported compiler found (gcc or clang)"
        exit 1
    fi
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        *)          echo "unknown";;
    esac
}

# Check if required tools are available
check_tools() {
    local compiler="$1"
    
    if [ "$compiler" = "gcc" ]; then
        if ! command -v gcov >/dev/null 2>&1; then
            log_error "gcov not found. Please install gcc development tools."
            exit 1
        fi
        if ! command -v lcov >/dev/null 2>&1; then
            log_warning "lcov not found. HTML reports will not be generated."
            log_warning "Install lcov: apt-get install lcov (Ubuntu) or brew install lcov (macOS)"
        fi
    elif [ "$compiler" = "clang" ]; then
        if ! command -v llvm-profdata >/dev/null 2>&1; then
            log_error "llvm-profdata not found. Please install LLVM tools."
            exit 1
        fi
        if ! command -v llvm-cov >/dev/null 2>&1; then
            log_error "llvm-cov not found. Please install LLVM tools."
            exit 1
        fi
    fi
}

# Clean coverage data
clean_coverage() {
    log_info "Cleaning coverage data..."
    
    # Remove coverage files
    find "${BUILD_DIR}" -name "*.gcda" -delete 2>/dev/null || true
    find "${BUILD_DIR}" -name "*.gcno" -delete 2>/dev/null || true
    find "${BUILD_DIR}" -name "*.profraw" -delete 2>/dev/null || true
    find "${BUILD_DIR}" -name "*.profdata" -delete 2>/dev/null || true
    
    # Remove coverage directory
    rm -rf "${COVERAGE_DIR}"
    
    log_success "Coverage data cleaned"
}

# Build with coverage
build_coverage() {
    local compiler="$1"
    
    log_info "Building with coverage instrumentation using $compiler..."
    
    cd "${PROJECT_ROOT}"
    
    # Create build directory
    mkdir -p "${BUILD_DIR}"
    
    # Build using Makefile with coverage
    if [ "$compiler" = "gcc" ]; then
        CC=gcc CXX=g++ make coverage-build
    elif [ "$compiler" = "clang" ]; then
        CC=clang CXX=clang++ make coverage-build
    fi
    
    log_success "Coverage build completed"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    cd "${PROJECT_ROOT}"
    
    # Set up environment for Clang coverage
    if [ "$(detect_compiler)" = "clang" ]; then
        export LLVM_PROFILE_FILE="${BUILD_DIR}/coverage-%p.profraw"
    fi
    
    # Run pytest
    if command -v python3 >/dev/null 2>&1; then
        python3 -m pytest tests/ -v --tb=short
    elif command -v python >/dev/null 2>&1; then
        python -m pytest tests/ -v --tb=short
    else
        log_error "Python not found. Please install Python 3."
        exit 1
    fi
    
    log_success "Tests completed"
}

# Generate coverage report for GCC
generate_gcc_report() {
    log_info "Generating coverage report using gcov/lcov..."
    
    mkdir -p "${COVERAGE_DIR}"
    
    # Generate gcov files
    cd "${BUILD_DIR}"
    gcov -r "${SRC_DIR}"/*.c
    
    # Generate lcov report if available
    if command -v lcov >/dev/null 2>&1; then
        lcov --capture --directory "${BUILD_DIR}" --output-file "${COVERAGE_DIR}/coverage.info"
        lcov --remove "${COVERAGE_DIR}/coverage.info" '/usr/*' --output-file "${COVERAGE_DIR}/coverage.info"
        lcov --remove "${COVERAGE_DIR}/coverage.info" '*/test/*' --output-file "${COVERAGE_DIR}/coverage.info"
        
        if command -v genhtml >/dev/null 2>&1; then
            genhtml "${COVERAGE_DIR}/coverage.info" --output-directory "${COVERAGE_DIR}/html"
            log_success "HTML coverage report generated: ${COVERAGE_DIR}/html/index.html"
        else
            log_warning "genhtml not found. HTML report not generated."
        fi
        
        # Display summary
        lcov --summary "${COVERAGE_DIR}/coverage.info"
    else
        log_warning "lcov not found. Only basic gcov files generated."
    fi
}

# Generate coverage report for Clang
generate_clang_report() {
    log_info "Generating coverage report using llvm-cov..."
    
    mkdir -p "${COVERAGE_DIR}"
    
    # Merge profile data
    llvm-profdata merge -sparse "${BUILD_DIR}"/*.profraw -o "${COVERAGE_DIR}/coverage.profdata"
    
    # Generate HTML report
    llvm-cov show "${BUILD_DIR}/pydcov" -instr-profile="${COVERAGE_DIR}/coverage.profdata" \
        -format=html -output-dir="${COVERAGE_DIR}/html"
    
    # Generate LCOV format for compatibility
    llvm-cov export "${BUILD_DIR}/pydcov" -instr-profile="${COVERAGE_DIR}/coverage.profdata" \
        -format=lcov > "${COVERAGE_DIR}/coverage.info"
    
    # Display summary
    llvm-cov report "${BUILD_DIR}/pydcov" -instr-profile="${COVERAGE_DIR}/coverage.profdata"
    
    log_success "HTML coverage report generated: ${COVERAGE_DIR}/html/index.html"
}

# Generate coverage report
generate_report() {
    local compiler="$1"
    
    if [ "$compiler" = "gcc" ]; then
        generate_gcc_report
    elif [ "$compiler" = "clang" ]; then
        generate_clang_report
    fi
}

# Main function
main() {
    local action="${1:-full}"
    local compiler="${2:-$(detect_compiler)}"
    local os="$(detect_os)"
    
    log_info "Coverage script for pydcov project"
    log_info "OS: $os, Compiler: $compiler"
    
    # Check tools
    check_tools "$compiler"
    
    case "$action" in
        "clean")
            clean_coverage
            ;;
        "build")
            build_coverage "$compiler"
            ;;
        "test")
            run_tests
            ;;
        "report")
            generate_report "$compiler"
            ;;
        "full")
            clean_coverage
            build_coverage "$compiler"
            run_tests
            generate_report "$compiler"
            ;;
        *)
            echo "Usage: $0 [clean|build|test|report|full] [gcc|clang]"
            echo ""
            echo "Actions:"
            echo "  clean  - Clean coverage data"
            echo "  build  - Build with coverage instrumentation"
            echo "  test   - Run tests"
            echo "  report - Generate coverage report"
            echo "  full   - Run complete coverage workflow (default)"
            echo ""
            echo "Compilers:"
            echo "  gcc    - Use GCC with gcov"
            echo "  clang  - Use Clang with llvm-cov"
            echo "  (auto-detected if not specified)"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
