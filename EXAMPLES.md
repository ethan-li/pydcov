# PyDCov Examples and Usage Guide

This document provides comprehensive examples of how to use PyDCov for C/C++ code coverage measurement in various scenarios. PyDCov uses **unified incremental coverage collection** for all operations, providing optimal performance and flexibility without requiring mode selection.

## 🚀 Quick Start Examples

### Installation and Basic Usage

```bash
# Install PyDCov
pip install pydcov

# Set up CMake integration in existing project
pydcov init-cmake

# Add to CMakeLists.txt: include(cmake/coverage.cmake)

# Build and test
mkdir build && cd build
cmake ..
make

# Generate coverage report using incremental workflow
pydcov init
pydcov add make test
pydcov report
```

### Adding to Existing Project

```bash
# Add PyDCov to existing CMake project
cd my_existing_project
pydcov init-cmake

# Update CMakeLists.txt to include:
# include(cmake/coverage.cmake)

# Run incremental coverage analysis
pydcov init
pydcov add python -m pytest tests/
pydcov report
```

## 📋 Command Examples

### Incremental Coverage Commands

```bash
# Complete incremental workflow
pydcov init                          # Initialize tracking
pydcov add python -m pytest tests/  # Add coverage data
pydcov report                        # Generate report

# Step-by-step incremental coverage
pydcov init                    # Initialize incremental tracking
pydcov clean                   # Clean previous coverage data (optional)
pydcov add make test           # Add coverage from test run
pydcov merge                   # Merge coverage data (optional)
pydcov report                  # Generate coverage reports

# Check coverage status
pydcov status
```

### Multiple Test Runs

Incremental coverage allows combining data from multiple test runs:

```bash
# Initialize tracking
pydcov init

# Add coverage from different test suites
pydcov add python -m pytest tests/unit/        # Add unit test coverage
pydcov add python -m pytest tests/integration/ # Add integration test coverage
pydcov add python -m pytest tests/e2e/         # Add end-to-end test coverage

# Generate combined report from all test runs
pydcov report

# Check status and clean when done
pydcov status
pydcov clean  # Reset for next coverage cycle
```

## 🧪 Testing Framework Examples

PyDCov works with any testing framework or executable:

### With pytest

```bash
# Basic pytest usage with incremental coverage
pydcov init
pydcov add python -m pytest tests/
pydcov report

# With specific options
pydcov init
pydcov add python -m pytest tests/ -v --tb=short
pydcov report

# Test specific modules incrementally
pydcov init
pydcov add python -m pytest tests/unit/
pydcov add python -m pytest tests/integration/
pydcov report
```

### With unittest

```bash
# Standard unittest discovery
pydcov init
pydcov add python -m unittest discover tests/
pydcov report

# Specific test modules
pydcov init
pydcov add python -m unittest tests.test_calculator
pydcov report

# Incremental with unittest
pydcov init
pydcov add python -m unittest tests.test_basic
pydcov add python -m unittest tests.test_advanced
pydcov report
```

### With CMake/CTest

```bash
# Using make test
pydcov init
pydcov add make test
pydcov report

# Using ctest directly
pydcov init
pydcov add ctest --verbose
pydcov report

# With specific test patterns
pydcov init
pydcov add ctest -R unit_tests
pydcov report
```

### With Custom Test Scripts

```bash
# Create custom test script
cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "Running unit tests..."
python -m pytest tests/unit/ -v
echo "Running integration tests..."
python -m pytest tests/integration/ -v
echo "Running custom validation..."
./build/my_app --self-test
EOF
chmod +x run_tests.sh

# Use with PyDCov
pydcov init
pydcov add ./run_tests.sh
pydcov report
```

### With Other Testing Tools

```bash
# Using Google Test
pydcov init
pydcov add ./build/my_gtest_executable
pydcov report

# Using Catch2
pydcov init
pydcov add ./build/my_catch2_tests
pydcov report

# Using custom executables
pydcov init
pydcov add ./build/my_custom_test_runner --all
pydcov report
```

## 🏗️ Project Setup Examples

### Setting Up Existing Projects

```bash
# Add PyDCov to existing C++ project
cd my_existing_project
pydcov init-cmake

# This creates:
# cmake/coverage.cmake      # PyDCov integration

# Update your CMakeLists.txt to include:
echo "include(cmake/coverage.cmake)" >> CMakeLists.txt

# Build and test with coverage
mkdir build && cd build
cmake ..
make

# Run incremental coverage
pydcov init
pydcov add make test
pydcov report
```

## 💻 Python API Examples

### Using PyDCov Programmatically

```python
from pydcov import IncrementalCoverageManager

# Basic incremental coverage workflow
def run_incremental_coverage():
    manager = IncrementalCoverageManager()

    # Initialize incremental tracking
    success = manager.init()
    if not success:
        print("Failed to initialize coverage tracking!")
        return False

    # Add coverage from test run
    success = manager.add(["python", "-m", "pytest", "tests/"])
    if not success:
        print("Failed to add coverage data!")
        return False

    # Generate report
    success = manager.report()
    if not success:
        print("Failed to generate report!")
        return False

    print("Incremental coverage analysis completed successfully!")
    return True

# Advanced incremental coverage with multiple test suites
def run_multi_suite_coverage():
    manager = IncrementalCoverageManager()

    # Initialize incremental tracking
    manager.init()

    # Add coverage from different test suites
    test_suites = [
        ["python", "-m", "pytest", "tests/unit/"],
        ["python", "-m", "pytest", "tests/integration/"],
        ["python", "-m", "pytest", "tests/e2e/"]
    ]

    for test_cmd in test_suites:
        success = manager.add(test_cmd)
        if not success:
            print(f"Failed to add coverage for: {' '.join(test_cmd)}")
            return False
        print(f"Added coverage for: {' '.join(test_cmd)}")

    # Merge coverage data
    success = manager.merge()
    if not success:
        print("Failed to merge coverage data!")
        return False

    # Generate combined report
    success = manager.report()
    if not success:
        print("Failed to generate report!")
        return False

    print("Multi-suite coverage analysis completed!")
    return True

# Custom project setup
def setup_project_coverage(project_path):
    import os
    from pathlib import Path

    os.chdir(project_path)

    # Initialize CMake integration
    from pydcov.cli import handle_init_cmake_command
    from argparse import Namespace

    args = Namespace(project_root=Path.cwd(), force=False)
    result = handle_init_cmake_command(args)

    if result == 0:
        print("CMake integration set up successfully!")
        print("Add 'include(cmake/coverage.cmake)' to your CMakeLists.txt")
    else:
        print("Failed to set up CMake integration!")

    return result == 0

# Status checking and cleanup
def check_coverage_status():
    manager = IncrementalCoverageManager()

    # Check current status
    manager.status()

    # Clean coverage data when done
    manager.clean()
    print("Coverage data cleaned!")

# Run the examples
if __name__ == "__main__":
    run_incremental_coverage()
    run_multi_suite_coverage()
    check_coverage_status()
```

## 🔧 Advanced Configuration Examples

### Custom CMake Integration

```cmake
# Advanced CMakeLists.txt with PyDCov
cmake_minimum_required(VERSION 3.10)
project(MyAdvancedProject)

# Include PyDCov coverage support
include(cmake/coverage.cmake)

# Set custom coverage options
set(COVERAGE_EXCLUDES
    "*/tests/*"
    "*/third_party/*"
    "*/build/*"
)

# Create library with coverage
add_library(mylib
    src/core.cpp
    src/utils.cpp
    src/algorithms.cpp
)

# Create executable with coverage
add_executable(myapp
    app/main.cpp
)
target_link_libraries(myapp mylib)

# Create test executable
add_executable(mytests
    tests/test_core.cpp
    tests/test_utils.cpp
    tests/test_algorithms.cpp
)
target_link_libraries(mytests mylib)

# Add test to CTest
enable_testing()
add_test(NAME unit_tests COMMAND mytests)
add_test(NAME integration_tests COMMAND myapp --test)

# Custom coverage targets are automatically created by coverage.cmake
```

### Environment-Specific Configuration

```bash
# Development environment
export PYDCOV_BUILD_TYPE=Debug
export PYDCOV_COVERAGE_FORMAT=html
export PYDCOV_VERBOSE=1

# CI environment
export PYDCOV_BUILD_TYPE=Release
export PYDCOV_COVERAGE_FORMAT=xml
export PYDCOV_PARALLEL_JOBS=4

# Use environment variables
pydcov init
pydcov add python -m pytest tests/
pydcov report
```

## 🚀 CI/CD Integration Examples

### GitHub Actions

```yaml
name: Coverage Analysis
on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        compiler: [gcc, clang]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install PyDCov
        run: pip install pydcov

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y cmake build-essential
          if [ "${{ matrix.compiler }}" = "gcc" ]; then
            sudo apt-get install -y gcc gcov lcov
          else
            sudo apt-get install -y clang llvm
          fi

      - name: Setup project
        run: pydcov init-cmake

      - name: Build project
        run: |
          mkdir build && cd build
          if [ "${{ matrix.compiler }}" = "gcc" ]; then
            CC=gcc CXX=g++ cmake ..
          else
            CC=clang CXX=clang++ cmake ..
          fi
          make

      - name: Run coverage analysis
        run: |
          pydcov init
          pydcov add python -m pytest tests/
          pydcov report

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./build/coverage/incremental_merged.info
          flags: ${{ matrix.compiler }}
          name: codecov-${{ matrix.compiler }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - coverage

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/

coverage:
  stage: coverage
  image: python:3.9
  before_script:
    - apt-get update -qq && apt-get install -y cmake build-essential gcc gcov lcov
    - pip install pydcov
  script:
    - pydcov init-cmake
    - mkdir build && cd build && cmake .. && make && cd ..
    - pydcov init
    - pydcov add python -m pytest tests/
    - pydcov report
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: build/coverage/incremental_merged.info
    paths:
      - build/coverage/incremental_report/
    expire_in: 1 week
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'pip install pydcov'
                sh 'pydcov init-cmake'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    mkdir -p build
                    cd build
                    cmake ..
                    make
                '''
            }
        }

        stage('Coverage') {
            steps {
                sh '''
                    pydcov init
                    pydcov add python -m pytest tests/
                    pydcov report
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'build/coverage/incremental_report',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }
}
```

## 🔍 Real-World Examples

### Example: Calculator Library

This shows how to use PyDCov with an existing calculator project:

```bash
# Navigate to your existing project
cd calculator_lib

# Set up PyDCov integration
pydcov init-cmake

# Update CMakeLists.txt to include coverage support
echo "include(cmake/coverage.cmake)" >> CMakeLists.txt

# Build and test
mkdir build && cd build
cmake ..
make

# Run the application
./calculator_lib
# Output: Calculator Demo with add, subtract, multiply, divide operations

# Run tests
make test
# Output: All tests passed

# Generate coverage report using incremental workflow
cd ..
pydcov init
pydcov add make test
pydcov report

# View coverage results
open build/coverage/incremental_report/index.html
```

### Example: Integration with Existing Project

```bash
# Add PyDCov to existing project
cd my_existing_cpp_project

# Initialize PyDCov
pydcov init-cmake

# Update CMakeLists.txt (add this line)
echo "include(cmake/coverage.cmake)" >> CMakeLists.txt

# Build with coverage
mkdir build && cd build
cmake ..
make

# Run your existing tests with incremental coverage
cd ..
pydcov init
pydcov add python -m pytest tests/
pydcov report
# or
pydcov init
pydcov add make test
pydcov report
# or
pydcov init
pydcov add ./my_custom_test_runner
pydcov report

# View results
open build/coverage/incremental_report/index.html
```

This comprehensive guide demonstrates PyDCov's flexibility and ease of use across different scenarios, from simple projects to complex CI/CD integrations.
