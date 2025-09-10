# Incremental Coverage Collection

This document describes the incremental coverage collection system that allows you to accumulate coverage data across multiple pytest executions and generate comprehensive coverage reports.

## Overview

The incremental coverage system enables you to:

- **Preserve coverage data** between multiple pytest runs instead of overwriting it
- **Accumulate coverage** from successive test executions
- **Generate comprehensive reports** that combine all incremental coverage data
- **Run targeted tests** and build up coverage incrementally
- **Support both GCC/gcov and Clang/llvm-cov** toolchains

## Quick Start

### 1. Build with Coverage

First, build your project with coverage instrumentation:

```bash
python3 coverage_tools/scripts/coverage.py build
```

### 2. Initialize Incremental Coverage

```bash
python3 coverage_tools/scripts/incremental_coverage.py init
```

### 3. Run Tests Incrementally

Run different test suites or specific tests, accumulating coverage:

```bash
# Run basic tests
python3 coverage_tools/scripts/incremental_coverage.py add tests/test_basic.py

# Run advanced tests
python3 coverage_tools/scripts/incremental_coverage.py add tests/test_advanced.py -v

# Run specific test methods
python3 coverage_tools/scripts/incremental_coverage.py add algorithm/tests/test_dynarray.py::test_create
```

### 4. Generate Final Report

Merge all accumulated data and generate the comprehensive report:

```bash
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report
```

### 5. View Results

Open the comprehensive coverage report:

```bash
open build/coverage/incremental_report/index.html
```

## Complete Workflow Example

### Option 1: Step-by-Step

```bash
# 1. Build with coverage
python3 coverage_tools/scripts/coverage.py build

# 2. Initialize incremental coverage
python3 coverage_tools/scripts/incremental_coverage.py init

# 3. Run different test suites incrementally
python3 coverage_tools/scripts/incremental_coverage.py add algorithm/tests/
python3 coverage_tools/scripts/incremental_coverage.py add statistics/tests/
python3 coverage_tools/scripts/incremental_coverage.py add tests/integration/

# 4. Merge and generate final report
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report

# 5. Check status
python3 coverage_tools/scripts/incremental_coverage.py status
```

### Option 2: All-in-One

```bash
# Build with coverage
python3 coverage_tools/scripts/coverage.py build

# Run complete incremental workflow
python3 coverage_tools/scripts/incremental_coverage.py full tests/
```

## Commands Reference

### `python3 coverage_tools/scripts/incremental_coverage.py [command] [options]`

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize incremental coverage collection | `python3 coverage_tools/scripts/incremental_coverage.py init` |
| `add [pytest_args]` | Run pytest and add coverage data | `python3 coverage_tools/scripts/incremental_coverage.py add tests/test_basic.py` |
| `merge` | Merge all accumulated coverage data | `python3 coverage_tools/scripts/incremental_coverage.py merge` |
| `report` | Generate final comprehensive coverage report | `python3 coverage_tools/scripts/incremental_coverage.py report` |
| `full [pytest_args]` | Complete workflow: init, add, merge, report | `python3 coverage_tools/scripts/incremental_coverage.py full tests/` |
| `clean` | Clean all incremental coverage data | `python3 coverage_tools/scripts/incremental_coverage.py clean` |
| `status` | Show current incremental coverage status | `python3 coverage_tools/scripts/incremental_coverage.py status` |
| `help` | Show help message | `python3 coverage_tools/scripts/incremental_coverage.py help` |

## Advanced Usage

### Running Specific Test Patterns

```bash
# Run tests matching a pattern
python3 coverage_tools/scripts/incremental_coverage.py add -k "test_create"

# Run tests with specific markers
python3 coverage_tools/scripts/incremental_coverage.py add -m "not slow"

# Run tests with verbose output
python3 coverage_tools/scripts/incremental_coverage.py add tests/ -v --tb=short
```

### Multiple Module Testing

```bash
# Initialize
python3 coverage_tools/scripts/incremental_coverage.py init

# Test each module separately
python3 coverage_tools/scripts/incremental_coverage.py add algorithm/tests/
python3 coverage_tools/scripts/incremental_coverage.py add statistics/tests/

# Generate combined report
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report
```

### Continuous Integration Workflow

```bash
#!/bin/bash
# CI script for incremental coverage

# Build with coverage
python3 coverage_tools/scripts/coverage.py build

# Initialize incremental coverage
python3 coverage_tools/scripts/incremental_coverage.py init

# Run test suites in parallel (if supported)
python3 coverage_tools/scripts/incremental_coverage.py add algorithm/tests/ &
python3 coverage_tools/scripts/incremental_coverage.py add statistics/tests/ &
wait

# Generate final report
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report

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

### CMake Integration

The system adds new CMake targets:

- `coverage-incremental-init`: Initialize incremental coverage
- `coverage-incremental-add`: Add current coverage data
- `coverage-incremental-merge`: Merge accumulated data
- `coverage-incremental-report`: Generate final report

## Troubleshooting

### Common Issues

#### No Coverage Data Generated

**Problem**: No `.profraw` or `.gcda` files are created during test runs.

**Solution**:
1. Ensure the project was built with coverage: `python3 coverage_tools/scripts/coverage.py build`
2. Check that `ENABLE_COVERAGE=ON` in `build/CMakeCache.txt`
3. Verify executables are linked with coverage libraries

#### Merge Fails

**Problem**: `coverage-incremental-merge` fails with "No files found".

**Solution**:
1. Check that tests actually ran: `python3 coverage_tools/scripts/incremental_coverage.py status`
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
python3 coverage_tools/scripts/incremental_coverage.py status

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
python3 coverage_tools/scripts/incremental_coverage.py add tests/unit/
python3 coverage_tools/scripts/incremental_coverage.py add tests/integration/
python3 coverage_tools/scripts/incremental_coverage.py add tests/performance/
```

### 2. Use Descriptive Test Selection

Use pytest's selection features to run meaningful test subsets:

```bash
# Run only fast tests first
python3 coverage_tools/scripts/incremental_coverage.py add -m "not slow"

# Then run comprehensive tests
python3 coverage_tools/scripts/incremental_coverage.py add -m "slow"
```

### 3. Monitor Coverage Progress

Check status between runs to monitor progress:

```bash
python3 coverage_tools/scripts/incremental_coverage.py add tests/basic/
python3 coverage_tools/scripts/incremental_coverage.py status
python3 coverage_tools/scripts/incremental_coverage.py add tests/advanced/
python3 coverage_tools/scripts/incremental_coverage.py status
```

### 4. Clean Between Major Changes

Clean incremental data when making significant code changes:

```bash
python3 coverage_tools/scripts/incremental_coverage.py clean
python3 coverage_tools/scripts/incremental_coverage.py init
# ... run tests again ...
```

## Integration with Existing Workflows

The incremental coverage system is designed to work alongside existing coverage workflows:

- **Standard coverage**: `python3 coverage_tools/scripts/coverage.py full tests/` continues to work as before
- **Module coverage**: `python3 coverage_tools/scripts/coverage_modules.py` provides enhanced module coverage
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
