# PyDCov - Python-based C/C++ Code Coverage Tools

[![PyPI version](https://badge.fury.io/py/pydcov.svg)](https://badge.fury.io/py/pydcov)
[![Python Support](https://img.shields.io/pypi/pyversions/pydcov.svg)](https://pypi.org/project/pydcov/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive coverage management system for CMake-based C/C++ projects. PyDCov provides modern Python tools for coverage collection, incremental coverage tracking, and reporting with support for both GCC/gcov and Clang/llvm-cov toolchains.

## Features

- **Cross-platform support**: Linux, macOS, Windows
- **Multiple compiler support**: GCC/gcov and Clang/llvm-cov
- **CMake integration**: Seamless integration with CMake build systems
- **Incremental coverage**: Track coverage changes over time
- **Framework-agnostic**: Works with any testing framework (pytest, unittest, custom executables)
- **Modern Python API**: Clean, well-documented Python interface

## Installation

```bash
pip install pydcov
```

### System Requirements

PyDCov requires the following system tools to be installed:

**Build Tools:**
- CMake (3.10 or later)
- Make or Ninja
- GCC or Clang compiler

**Coverage Tools (choose one):**

For GCC:
```bash
# Ubuntu/Debian
sudo apt-get install gcc gcov lcov

# macOS
brew install gcc lcov
```

For Clang:
```bash
# Ubuntu/Debian  
sudo apt-get install clang llvm

# macOS
brew install llvm
```

## Quick Start

### 1. Initialize CMake Integration

In your C/C++ project directory:

```bash
pydcov init-cmake
```

This copies the CMake integration files to your project.

### 2. Update CMakeLists.txt

Add this line to your root CMakeLists.txt:

```cmake
include(cmake/coverage.cmake)
```

### 3. Run Coverage

```bash
# Full coverage workflow
pydcov coverage full "python -m pytest tests/"

# Or step by step
pydcov coverage clean
pydcov coverage build  
pydcov coverage test "python -m pytest tests/"
pydcov coverage report
```

### 4. Incremental Coverage

Track coverage changes over multiple test runs:

```bash
# Initialize incremental tracking
pydcov incremental init

# Add coverage data from test runs
pydcov incremental add "python -m pytest tests/test_module1.py"
pydcov incremental add "python -m pytest tests/test_module2.py"

# Generate combined report
pydcov incremental report
```

## Command Reference

### Coverage Commands

```bash
pydcov coverage clean          # Clean coverage data
pydcov coverage build          # Build with coverage instrumentation
pydcov coverage test "cmd"     # Run tests with coverage collection
pydcov coverage report         # Generate coverage reports
pydcov coverage full "cmd"     # Complete workflow: clean, build, test, report
pydcov coverage status         # Show coverage status
```

### Incremental Coverage Commands

```bash
pydcov incremental init        # Initialize incremental tracking
pydcov incremental add "cmd"   # Add coverage data from test run
pydcov incremental merge       # Merge coverage data
pydcov incremental report      # Generate incremental report
pydcov incremental status      # Show incremental status
pydcov incremental clean       # Clean incremental data
```

### Utility Commands

```bash
pydcov init-cmake              # Copy CMake integration files
pydcov --version               # Show version
pydcov --help                  # Show help
```

## Python API

PyDCov can also be used programmatically:

```python
from pydcov import CoverageManager, IncrementalCoverageManager

# Coverage workflow
manager = CoverageManager()
success = manager.full_workflow(["python", "-m", "pytest", "tests/"])

# Incremental coverage
incremental = IncrementalCoverageManager()
incremental.init()
incremental.add(["python", "-m", "pytest", "tests/module1/"])
incremental.add(["python", "-m", "pytest", "tests/module2/"])
incremental.report()
```

## CMake Integration

PyDCov provides a comprehensive CMake module that automatically:

- Detects available compilers and coverage tools
- Configures appropriate coverage flags
- Creates coverage targets (`coverage-clean`, `coverage-report`)
- Supports both GCC/gcov and Clang/llvm-cov workflows
- Provides incremental coverage capabilities

Example CMakeLists.txt:

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

# Include PyDCov coverage support
include(cmake/coverage.cmake)

# Your project configuration
add_executable(my_app src/main.cpp)

# Coverage will be automatically configured
```

## Examples

### Basic C++ Project

```bash
# Setup
mkdir my-cpp-project && cd my-cpp-project
pydcov init-cmake

# Create CMakeLists.txt with coverage support
echo 'cmake_minimum_required(VERSION 3.10)
project(MyApp)
include(cmake/coverage.cmake)
add_executable(my_app main.cpp)' > CMakeLists.txt

# Run coverage
pydcov coverage full "python -m pytest tests/"
```

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Install PyDCov
  run: pip install pydcov

- name: Setup coverage
  run: pydcov init-cmake

- name: Run coverage
  run: pydcov coverage full "python -m pytest tests/"
```

## Troubleshooting

### Common Issues

**"Coverage tools not found"**
- Install GCC/gcov or Clang/llvm-cov
- Ensure tools are in PATH

**"CMake configuration failed"**
- Verify CMake is installed and accessible
- Check that `include(cmake/coverage.cmake)` is in CMakeLists.txt

**"No coverage data found"**
- Ensure tests are actually running
- Verify executables are built with coverage flags

### Getting Help

- Check the [documentation](https://github.com/ethan-li/pydcov)
- Report issues on [GitHub](https://github.com/ethan-li/pydcov/issues)

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please see the contributing guidelines in the repository.
