# Module-Specific Coverage Reports

This document explains how to generate separate coverage reports for each module (algorithm and statistics) without modifying the CMake build system.

## Overview

The module coverage system provides:
- **Separate reports** for each module (algorithm, statistics)
- **C files only** coverage (excludes C++ CLI code)
- **No CMake modifications** required
- **Compatible** with existing coverage workflow

## Quick Start

### Generate Reports for All Modules
```bash
python3 coverage_tools/scripts/coverage_modules.py full
```

### Generate Report for Specific Module
```bash
python3 coverage_tools/scripts/coverage_modules.py full algorithm
python3 coverage_tools/scripts/coverage_modules.py full statistics
```

## Available Commands

### Complete Workflow
```bash
# Full workflow for all modules
python3 coverage_tools/scripts/coverage_modules.py full

# Full workflow for specific module
python3 coverage_tools/scripts/coverage_modules.py full algorithm
python3 coverage_tools/scripts/coverage_modules.py full statistics
```

### Individual Steps
```bash
# Build with coverage instrumentation
python3 coverage_tools/scripts/coverage_modules.py build

# Run tests with coverage collection
python3 coverage_tools/scripts/coverage_modules.py test

# Generate module reports (after build + test)
python3 coverage_tools/scripts/coverage_modules.py generate
python3 coverage_tools/scripts/coverage_modules.py generate algorithm
python3 coverage_tools/scripts/coverage_modules.py generate statistics

# Clean coverage data
python3 coverage_tools/scripts/coverage_modules.py clean
```

## Output Structure

After running the coverage workflow, you'll find module-specific reports at:

```
build/coverage/
├── algorithm/
│   ├── html/
│   │   └── index.html          # Algorithm module HTML report
│   ├── coverage.info           # Algorithm module LCOV data (all files)
│   ├── coverage_c_only.info    # Algorithm module LCOV data (C files only)
│   └── summary.txt             # Algorithm module text summary
├── statistics/
│   ├── html/
│   │   └── index.html          # Statistics module HTML report
│   ├── coverage.info           # Statistics module LCOV data (all files)
│   ├── coverage_c_only.info    # Statistics module LCOV data (C files only)
│   └── summary.txt             # Statistics module text summary
└── [original combined reports]
```

## Coverage Results

### Algorithm Module
- **Source Files**: `algorithm/src/algorithm.c`
- **Coverage**: ~94% line coverage for C files
- **Excludes**: `algorithm/app/main.cpp` (C++ CLI code)

### Statistics Module  
- **Source Files**: `statistics/src/statistics.c` + `algorithm/src/algorithm.c` (dependency)
- **Coverage**: ~80% line coverage for C files
- **Excludes**: `statistics/app/main.cpp` (C++ CLI code)

## Features

### 1. Module Separation
Each module gets its own coverage report showing only relevant source files:
- Algorithm module: Shows coverage for algorithm library code
- Statistics module: Shows coverage for statistics library code + algorithm dependency

### 2. C Files Only
The `coverage_c_only.info` files contain filtered LCOV data that includes only `.c` files, excluding all C++ CLI application code.

### 3. No Build System Changes
The system works as a post-processing step on existing coverage data, requiring no modifications to:
- `cmake/coverage.cmake`
- Module CMakeLists.txt files
- Build configuration

### 4. Compatible with Existing Workflow
You can still use the original coverage commands:
```bash
python3 coverage_tools/scripts/coverage.py full tests/      # Original combined coverage
python3 coverage_tools/scripts/coverage_modules.py full  # New module-specific coverage
```

## Implementation Details

### Scripts
- `coverage_tools/scripts/coverage_modules.py`: Main workflow script (Python)
- Enhanced Python implementation with better error handling and logging

### Process
1. **Build**: Uses existing `python3 coverage_tools/scripts/coverage.py build`
2. **Test**: Uses existing `python3 coverage_tools/scripts/coverage.py test tests/` 
3. **Merge**: Combines all `.profraw` files into `module_coverage.profdata`
4. **Generate**: Creates separate reports for each module using `llvm-cov`
5. **Filter**: Extracts C-only coverage data from LCOV files

### Module Detection
The system automatically detects modules by:
- Looking for `*/src/*.c` files in the project
- Mapping to corresponding `*_cli` executables
- Currently supports: `algorithm`, `statistics`

## Troubleshooting

### Prerequisites
Ensure you have:
- LLVM tools installed (`llvm-profdata`, `llvm-cov`)
- Project built with coverage instrumentation
- Test suite executed with coverage data collection

### Common Issues

**"No .profraw files found"**
```bash
# Run tests first to generate coverage data
python3 coverage_tools/scripts/coverage.py test tests/
```

**"Executable not found"**
```bash
# Build the project first
python3 coverage_tools/scripts/coverage.py build
```

**"LLVM tools not found"**
```bash
# Install LLVM or update LLVM_TOOLS_PATHS in the script
brew install llvm
```

## Examples

### Daily Development Workflow
```bash
# Make code changes
vim algorithm/src/algorithm.c

# Generate coverage for algorithm module only
python3 coverage_tools/scripts/coverage_modules.py full algorithm

# View results
open build/coverage/algorithm/html/index.html
```

### CI/CD Integration
```bash
# Full coverage analysis for all modules
python3 coverage_tools/scripts/coverage_modules.py full

# Archive coverage reports
tar -czf coverage-reports.tar.gz build/coverage/
```

### Coverage Analysis
```bash
# Compare C-only vs full coverage
python3 coverage_tools/scripts/coverage_modules.py generate
diff build/coverage/algorithm/coverage.info build/coverage/algorithm/coverage_c_only.info
```

This system provides focused, module-specific coverage analysis while maintaining compatibility with the existing build infrastructure.
