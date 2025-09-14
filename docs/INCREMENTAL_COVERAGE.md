# Incremental Coverage Collection

This document describes PyDCov's incremental coverage system. **All `pydcov coverage` commands automatically use incremental collection**, and this document covers both the automatic behavior and advanced explicit control options for accumulating coverage data across multiple test executions.

## Overview

PyDCov provides two levels of incremental coverage:

### Automatic Incremental Collection (Default)
All `pydcov coverage` commands automatically use incremental collection:
- **Seamless accumulation** across multiple `pydcov coverage test` runs
- **No configuration required** - works out of the box
- **Optimal performance** for most workflows

### Advanced Incremental Control (Explicit)
For complex workflows requiring explicit control:
- **Manual initialization** and data management
- **Fine-grained control** over coverage collection
- **Advanced reporting options**
- **Support both GCC/gcov and Clang/llvm-cov** toolchains
- **Pure Python implementation** with no CMake dependencies for coverage operations

## Quick Start

### Option 1: Automatic Incremental Collection (Recommended)

```bash
# Simple workflow - incremental collection happens automatically
pydcov coverage full "python -m pytest tests/"

# Or step-by-step with automatic incremental collection
pydcov coverage clean
pydcov coverage build
pydcov coverage test "python -m pytest tests/unit/"      # Collects coverage data
pydcov coverage test "python -m pytest tests/integration/"  # Adds to existing data
pydcov coverage report  # Generates combined report from all test runs
```

### Option 2: Advanced Incremental Control

For complex workflows requiring explicit control:

```bash
# 1. Build with coverage instrumentation
pydcov coverage build

# 2. Initialize incremental coverage
pydcov incremental init
```

### 3. Run Tests Incrementally (Advanced Control)

Run different test suites or specific tests, accumulating coverage:

```bash
# Run basic tests
pydcov incremental add "python -m pytest tests/test_basic.py"

# Run advanced tests
pydcov incremental add "python -m pytest tests/test_advanced.py -v"

# Run specific test methods
pydcov incremental add "python -m pytest algorithm/tests/test_dynarray.py::test_create"
```

### 4. Generate Final Report

Generate the comprehensive report. The merge step is automatic, but can be called explicitly:

```bash
# Option 1: Automatic merge (recommended for simple workflows)
pydcov incremental report

# Option 2: Explicit merge (recommended for CI/CD and complex workflows)
pydcov incremental merge
pydcov incremental report
```

### 5. View Results

Open the comprehensive coverage report:

```bash
open build/coverage/incremental_report/index.html
```

## Complete Workflow Examples

### Option 1: Automatic Incremental Collection (Recommended)

```bash
# Simple one-command workflow
pydcov coverage full "python -m pytest tests/"

# Step-by-step with automatic incremental collection
pydcov coverage clean
pydcov coverage build
pydcov coverage test "python -m pytest algorithm/tests/"     # Collects coverage
pydcov coverage test "python -m pytest statistics/tests/"   # Adds to existing data
pydcov coverage test "python -m pytest tests/integration/"  # Adds to existing data
pydcov coverage report  # Generates combined report
pydcov coverage status  # Check status
```

### Option 2: Advanced Incremental Control

```bash
# 1. Build with coverage
pydcov coverage build

# 2. Initialize incremental coverage
pydcov incremental init

# 3. Run different test suites incrementally
pydcov incremental add "python -m pytest algorithm/tests/"
pydcov incremental add "python -m pytest statistics/tests/"
pydcov incremental add "python -m pytest tests/integration/"

# 4. Generate final report (merging is automatic)
pydcov incremental report

# 5. Check status
pydcov incremental status
```

## Commands Reference

### `pydcov incremental [command] [options]`

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize incremental coverage collection | `pydcov incremental init` |
| `add "test_cmd"` | Run test command and add coverage data | `pydcov incremental add "python -m pytest tests/test_basic.py"` |
| `merge` | Merge all accumulated coverage data | `pydcov incremental merge` |
| `report` | Generate final comprehensive coverage report | `pydcov incremental report` |
| `clean` | Clean all incremental coverage data | `pydcov incremental clean` |
| `status` | Show current incremental coverage status | `pydcov incremental status` |

## Advanced Usage

### Running Specific Test Patterns

```bash
# Run tests matching a pattern
pydcov incremental add "python -m pytest -k test_create"

# Run tests with specific markers
pydcov incremental add "python -m pytest -m 'not slow'"

# Run tests with verbose output
pydcov incremental add "python -m pytest tests/ -v --tb=short"
```

### Multiple Module Testing

```bash
# Initialize
pydcov incremental init

# Test each module separately
pydcov incremental add "python -m pytest algorithm/tests/"
pydcov incremental add "python -m pytest statistics/tests/"

# Generate combined report
pydcov incremental report
```

### Continuous Integration Workflow

```bash
#!/bin/bash
# CI script for incremental coverage

# Build with coverage
pydcov coverage build

# Initialize incremental coverage
pydcov incremental init

# Run test suites sequentially (parallel support depends on test framework)
pydcov incremental add "python -m pytest algorithm/tests/"
pydcov incremental add "python -m pytest statistics/tests/"

# Generate final report
pydcov incremental report

# Upload coverage report
# ... upload build/coverage/incremental_report/ ...
```

## Output Files

The incremental coverage system creates the following files:

```
build/coverage/
├── incremental/                    # Temporary incremental data
│   ├── *.profraw                  # Clang coverage data files
│   └── *.info                     # GCC coverage data files
├── incremental_merged.profdata    # Merged Clang coverage data
├── incremental_merged.info        # Merged GCC coverage data
└── incremental_report/            # Final comprehensive report
    ├── index.html                 # Main coverage report
    ├── *.html                     # Per-file coverage reports
    └── style.css                  # Report styling
```

## Technical Details

### How It Works

#### For Clang/LLVM Coverage:
1. **Initialization**: Cleans existing `.profraw` and `.profdata` files
2. **Data Collection**: Each pytest run generates new `.profraw` files with unique process IDs
3. **Accumulation**: `.profraw` files are copied to the incremental directory
4. **Merging**: `llvm-profdata merge` combines all `.profraw` files into a single `.profdata`
5. **Reporting**: `llvm-cov` generates HTML and LCOV reports from merged data

#### For GCC/gcov Coverage:
1. **Initialization**: Cleans existing `.gcda` and `.gcno` files
2. **Data Collection**: Each pytest run updates `.gcda` files
3. **Accumulation**: `lcov --capture` creates `.info` files for each run
4. **Merging**: `lcov --add-tracefile` combines all `.info` files
5. **Reporting**: `genhtml` generates HTML reports from merged data

### Environment Variables

The system automatically sets appropriate environment variables:

- **Clang**: `LLVM_PROFILE_FILE=build/coverage-%p.profraw`
- **GCC**: Uses default gcov behavior

### Python Implementation

The system uses pure Python for all coverage operations:

- **Tool Detection**: Automatically finds `llvm-profdata`, `llvm-cov`, `lcov`, `genhtml`
- **File Management**: Python-based file collection and organization
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **No CMake Dependencies**: Coverage operations don't require CMake targets

## Troubleshooting

### Common Issues

#### No Coverage Data Generated

**Problem**: No `.profraw` or `.gcda` files are created during test runs.

**Solution**:
1. Ensure the project was built with coverage: `pydcov coverage build`
2. Check that `ENABLE_COVERAGE=ON` in `build/CMakeCache.txt`
3. Verify executables are linked with coverage libraries

#### Merge Fails

**Problem**: `pydcov incremental report` fails with "No files found".

**Solution**:
1. Check that tests actually ran: `pydcov incremental status`
2. Ensure pytest found and executed tests
3. Verify coverage data was generated in the incremental directory

#### Permission Errors

**Problem**: Cannot write to coverage directories.

**Solution**:
1. Check write permissions on `build/coverage/` directory
2. Run `chmod -R u+w build/coverage/`

### Debugging

Enable verbose output to debug issues:

```bash
# Check current status
pydcov incremental status

# Manually inspect coverage files
ls -la build/coverage/incremental/
ls -la build/coverage/

# Check CMake cache for coverage settings
grep COVERAGE build/CMakeCache.txt
```

## Best Practices

### 1. Organize Test Runs Logically

Group related tests together for better organization:

```bash
# Group by functionality
pydcov incremental add "python -m pytest tests/unit/"
pydcov incremental add "python -m pytest tests/integration/"
pydcov incremental add "python -m pytest tests/performance/"
```

### 2. Use Descriptive Test Selection

Use pytest's selection features to run meaningful test subsets:

```bash
# Run only fast tests first
pydcov incremental add "python -m pytest -m 'not slow'"

# Then run comprehensive tests
pydcov incremental add "python -m pytest -m slow"
```

### 3. Monitor Coverage Progress

Check status between runs to monitor progress:

```bash
pydcov incremental add "python -m pytest tests/basic/"
pydcov incremental status
pydcov incremental add "python -m pytest tests/advanced/"
pydcov incremental status
```

### 4. Clean Between Major Changes

Clean incremental data when making significant code changes:

```bash
pydcov incremental clean
pydcov incremental init
# ... run tests again ...
```

## Integration with Existing Workflows

The incremental coverage system is designed to work alongside existing coverage workflows:

- **Standard coverage**: `pydcov coverage full tests/` continues to work as before
- **Module coverage**: `pydcov modules` provides enhanced module coverage
- **CI/CD**: Can be integrated into existing CI pipelines

## Performance Considerations

- **Incremental collection** is faster than running all tests at once for large test suites
- **Parallel test execution** can be used with careful coordination
- **Storage requirements** increase with the number of incremental runs (cleaned automatically)

## Compatibility

- **Compilers**: GCC 7+ and Clang 10+
- **Platforms**: Linux and macOS
- **Python**: 3.7+
- **CMake**: 3.15+
