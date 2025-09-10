# PyDCov Examples and Usage Guide

This document provides comprehensive examples of how to use PyDCov for C/C++ code coverage measurement in various scenarios.

## 🚀 Quick Start Examples

### Installation and Basic Usage

```bash
# Install PyDCov
pip install pydcov

# Create a new project
pydcov init-template my_project
cd my_project

# Build and test
mkdir build && cd build
cmake ..
make

# Generate coverage report
pydcov coverage full "make test"
```

### Adding to Existing Project

```bash
# Add PyDCov to existing CMake project
cd my_existing_project
pydcov init-cmake

# Update CMakeLists.txt to include:
# include(cmake/coverage.cmake)

# Run coverage analysis
pydcov coverage full "python -m pytest tests/"
```

## 📋 Command Examples

### Coverage Commands

```bash
# Complete coverage workflow
pydcov coverage full "python -m pytest tests/"

# Step-by-step coverage
pydcov coverage clean          # Clean previous coverage data
pydcov coverage build          # Build with coverage instrumentation
pydcov coverage test "make test"  # Run tests with coverage collection
pydcov coverage report         # Generate coverage reports

# Check coverage status
pydcov coverage status
```

### Incremental Coverage

```bash
# Initialize incremental tracking
pydcov incremental init

# Add coverage from different test runs
pydcov incremental add "python -m pytest tests/unit/"
pydcov incremental add "python -m pytest tests/integration/"
pydcov incremental add "python -m pytest tests/e2e/"

# Generate combined report
pydcov incremental report

# Check incremental status
pydcov incremental status

# Clean incremental data
pydcov incremental clean
```

## 🧪 Testing Framework Examples

PyDCov works with any testing framework or executable:

### With pytest

```bash
# Basic pytest usage
pydcov coverage full "python -m pytest tests/"

# With specific options
pydcov coverage full "python -m pytest tests/ -v --tb=short"

# Test specific modules
pydcov incremental add "python -m pytest tests/unit/"
pydcov incremental add "python -m pytest tests/integration/"
```

### With unittest

```bash
# Standard unittest discovery
pydcov coverage full "python -m unittest discover tests/"

# Specific test modules
pydcov coverage full "python -m unittest tests.test_calculator"

# Incremental with unittest
pydcov incremental init
pydcov incremental add "python -m unittest tests.test_basic"
pydcov incremental add "python -m unittest tests.test_advanced"
pydcov incremental report
```

### With CMake/CTest

```bash
# Using make test
pydcov coverage full "make test"

# Using ctest directly
pydcov coverage full "ctest --verbose"

# With specific test patterns
pydcov coverage full "ctest -R unit_tests"
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
pydcov coverage full "./run_tests.sh"
```

### With Other Testing Tools

```bash
# Using Google Test
pydcov coverage full "./build/my_gtest_executable"

# Using Catch2
pydcov coverage full "./build/my_catch2_tests"

# Using custom executables
pydcov coverage full "./build/my_custom_test_runner --all"
```

## 🏗️ Project Template Examples

### Creating New Projects

```bash
# Create basic C++ project
pydcov init-template calculator --template basic_cpp

# Navigate and build
cd calculator
mkdir build && cd build
cmake ..
make

# Run tests and coverage
pydcov coverage full "make test"
```

### Template Structure

The generated project includes:

```
calculator/
├── CMakeLists.txt          # Main CMake configuration
├── cmake/
│   ├── coverage.cmake      # PyDCov integration
│   └── COVERAGE_USAGE.md   # Usage documentation
├── src/                    # Library source code
│   ├── calculator.hpp
│   ├── calculator.cpp
│   └── CMakeLists.txt
├── app/                    # Application executable
│   └── main.cpp
├── tests/                  # Test source code
│   ├── test_calculator.cpp
│   └── CMakeLists.txt
└── README.md               # Project documentation
```

## 💻 Python API Examples

### Using PyDCov Programmatically

```python
from pydcov import CoverageManager, IncrementalCoverageManager

# Basic coverage workflow
def run_coverage_analysis():
    manager = CoverageManager()

    # Clean previous data
    manager.clean()

    # Build with coverage
    success = manager.build()
    if not success:
        print("Build failed!")
        return False

    # Run tests
    success = manager.test(["python", "-m", "pytest", "tests/"])
    if not success:
        print("Tests failed!")
        return False

    # Generate report
    success = manager.report()
    if not success:
        print("Report generation failed!")
        return False

    print("Coverage analysis completed successfully!")
    return True

# Incremental coverage workflow
def run_incremental_coverage():
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

    # Generate combined report
    success = manager.report()
    if not success:
        print("Failed to generate incremental report!")
        return False

    print("Incremental coverage analysis completed!")
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

# Run the examples
if __name__ == "__main__":
    run_coverage_analysis()
    run_incremental_coverage()
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
pydcov coverage full "python -m pytest tests/"
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
        run: pydcov coverage full "python -m pytest tests/"

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
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
    - pydcov coverage full "python -m pytest tests/"
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - coverage_html/
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
                sh 'pydcov coverage full "python -m pytest tests/"'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'coverage_html',
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

This shows how to use PyDCov with a real calculator project:

```bash
# Create the project
pydcov init-template calculator_lib

# Navigate to project
cd calculator_lib

# Examine the generated structure
tree .
# calculator_lib/
# ├── CMakeLists.txt
# ├── cmake/
# │   ├── coverage.cmake
# │   └── COVERAGE_USAGE.md
# ├── src/
# │   ├── calculator.hpp
# │   ├── calculator.cpp
# │   └── CMakeLists.txt
# ├── app/
# │   └── main.cpp
# ├── tests/
# │   ├── test_calculator.cpp
# │   └── CMakeLists.txt
# └── README.md

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

# Generate coverage report
cd ..
pydcov coverage full "make test"

# View coverage results
open coverage_html/index.html
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

# Run your existing tests with coverage
cd ..
pydcov coverage full "python -m pytest tests/"
# or
pydcov coverage full "make test"
# or
pydcov coverage full "./my_custom_test_runner"

# View results
open coverage_html/index.html
```

This comprehensive guide demonstrates PyDCov's flexibility and ease of use across different scenarios, from simple projects to complex CI/CD integrations.
