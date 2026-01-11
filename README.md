# PyDCov - Incremental C/C++ Code Coverage Tools

[![PyPI version](https://badge.fury.io/py/pydcov.svg)](https://badge.fury.io/py/pydcov)
[![Python Support](https://img.shields.io/pypi/pyversions/pydcov.svg)](https://pypi.org/project/pydcov/)
[![CI](https://github.com/ethan-li/pydcov/actions/workflows/ci.yml/badge.svg)](https://github.com/ethan-li/pydcov/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A streamlined **pure Python** incremental coverage tracking system for C/C++ projects. PyDCov provides modern Python tools for incremental coverage collection and reporting with support for both GCC/gcov and Clang/llvm-cov toolchains, plus CMake integration setup. **No CMake dependencies required** for coverage operations.

## ✨ Features

- **🐍 Pure Python**: No CMake dependencies for coverage operations
- **📦 Multiple Distribution Options**: Python package, standalone executables, or source
- **🔄 Incremental Coverage**: Efficient incremental collection and reporting
- **🛠️ Framework-Agnostic**: Works with any testing framework (pytest, unittest, custom executables)
- **🌐 Cross-Platform**: Linux, macOS, Windows support
- **⚡ Multiple Compilers**: GCC/gcov and Clang/llvm-cov support
- **🔧 CMake Integration**: Seamless integration with CMake build systems
- **📊 Rich Reporting**: HTML, XML, and LCOV format reports
- **📥 Collect-Only Mode**: Skip test execution and collect existing coverage files

## 🚀 Quick Start

### Installation

#### Option 1: Python Package (Recommended)

```bash
pip install pydcov
```

#### Option 2: Standalone Executable

Download pre-built standalone executables from [GitHub Releases](https://github.com/ethan-li/pydcov/releases) page:

- **Linux (x64)**: `pydcov-linux-x64`
- **macOS (ARM64)**: `pydcov-macos-arm64`

No Python installation required! Simply download, make executable, and run:

```bash
# Linux/macOS
chmod +x pydcov-linux-x64  # or pydcov-macos-arm64
./pydcov-linux-x64 --version
```

#### Option 3: Build Your Own Executable

```bash
git clone https://github.com/ethan-li/pydcov.git
cd pydcov
python build_standalone.py --clean --test
```

### Basic Usage

```bash
# Initialize incremental coverage tracking (specify build directory once)
pydcov init --build-root build

# Add coverage data from test runs (no --build-root needed after init)
pydcov add python -m pytest tests/

# Generate coverage report
pydcov report

# Check coverage status
pydcov status
```

### Add to Existing Project

```bash
# Add PyDCov CMake integration to existing project
pydcov init-cmake

# Add to your CMakeLists.txt:
# include(cmake/coverage.cmake)

# Then use incremental coverage
pydcov init
pydcov add python -m pytest tests/
pydcov report
```

## 📋 Command Reference

### Incremental Coverage Commands

```bash
pydcov init                              # Initialize incremental tracking
pydcov init --pydcov-dir /path/to/data   # Initialize with custom coverage directory
pydcov add python -m pytest tests/      # Add coverage data from test run
pydcov add --collect-only                  # Collect existing coverage files without running tests
pydcov merge                             # Merge coverage data
pydcov report                            # Generate incremental report
pydcov status                            # Show incremental status
pydcov clean                             # Clean all coverage data
pydcov export --format lcov               # Export coverage data (lcov, json, cobertura)
```

### Project Setup Commands

```bash
pydcov init-cmake              # Copy CMake integration files
pydcov --version               # Show version
pydcov --help                  # Show help
```

## 📁 Coverage Directory Management

PyDCov supports flexible coverage directory management:

### Default Behavior
By default, PyDCov creates a `pydcov_dir` directory in your current working directory to store all coverage data.

### Custom Coverage Directory
You can specify a custom location for coverage data:

```bash
# Initialize with custom coverage directory
pydcov init --build-root build --pydcov-dir /path/to/coverage/data

# All subsequent commands will use the configured directory
pydcov add python -m pytest tests/
pydcov merge
pydcov report
```

### Unique Subdirectories for Each Test Run
Each `pydcov add` command creates a unique timestamped subdirectory under `pydcov_dir`, allowing you to:
- Run multiple test suites independently
- Aggregate coverage data from different test runs
- Maintain a complete history of coverage data

### Directory Structure
```
pydcov_dir/
├── add_20240101_120000_123/    # First test run
│   ├── coverage-*.profraw
│   └── *.gcda
├── add_20240101_120030_456/    # Second test run
│   ├── coverage-*.profraw
│   └── *.gcda
├── merged.profdata                  # Merged coverage data (Clang)
├── merged.info                     # Merged coverage data (GCC)
└── report/                        # Generated reports
    └── index.html
```

## 🎯 Incremental Coverage Approach

PyDCov focuses on **incremental coverage collection** for optimal performance and flexibility:

- **Cumulative Collection**: Multiple test runs automatically accumulate coverage data
- **Optimal Performance**: Efficient data collection and merging for large projects
- **Flexible Workflow**: Add coverage data from different test runs as needed
- **Clean Separation**: Clear commands for initialization, collection, and reporting

### How It Works

1. **Initialize**: Set up incremental coverage tracking with `pydcov init`
2. **Collect**: Add coverage data from test runs with `pydcov add test_command` or `pydcov add --collect-only`
3. **Merge**: Combine coverage data with `pydcov merge`
4. **Report**: Generate reports at any time with `pydcov report`
5. **Clean**: Reset for fresh collection with `pydcov clean`

## 📥 Collect-Only Mode

The `--collect-only` option allows you to skip test execution and directly collect existing coverage files. This is particularly useful for:

- Running tests using custom scripts or manually
- Tests have already been completed by other tools
- Need to collect coverage data from multiple test runs in stages
- CI/CD environments with complex test execution workflows

### Usage Examples

#### Collect After Manual Test Execution

```bash
# Build program with coverage enabled
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_ENABLE_COVERAGE=1
cmake --build build

# Manually run test programs
./build/test_program1
./build/test_program2

# Collect existing coverage files
pydcov init --build-root build
pydcov add --collect-only
pydcov merge
pydcov report
```

#### Staged Collection (Clang)

```bash
# Initialize
pydcov init --build-root build

# Run and collect first group of tests
./build/test_group1
pydcov add --collect-only

# Run and collect second group of tests
./build/test_group2
pydcov add --collect-only

# Merge and generate report
pydcov merge
pydcov report
```

#### Mixed Use of Standard Mode and Collect-Only Mode

```bash
pydcov init --build-root build

# Run pytest in standard mode
pydcov add python -m pytest tests/unit/

# Collect after manually running integration tests
./build/integration_tests
pydcov add --collect-only

# Run pytest again in standard mode
pydcov add python -m pytest tests/integration/

# Merge and generate report
pydcov merge
pydcov report
```

### How It Works

#### For Clang (llvm-cov)

- **File Types**: `.profraw`
- **Accumulation**: Each run generates new `.profraw` files (if using `LLVM_PROFILE_FILE` with wildcards)
- **Timestamp Filtering**: Only collects files modified after the last collection
- **Recommended**: Ensure `LLVM_PROFILE_FILE` uses wildcards (e.g., `coverage-%p-%m.profraw`)

#### For GCC (gcov)

- **File Types**: `.gcda`, `.gcno`
- **Accumulation**: `.gcda` files are cumulative; multiple runs of the same program update the same file
- **Collection Behavior**: Always collects all `.gcda` files (because they are cumulative)
- **Recommended**: Run all tests first, then collect only once

### Best Practices

#### For Clang Users

1. **Use Wildcards**: Ensure `LLVM_PROFILE_FILE` uses wildcards (e.g., `%p-%m`)
2. **Collect in Stages**: Call `pydcov add --collect-only` after each new test run
3. **Auto Merge**: All collected data will be merged during the `merge` phase

#### For GCC Users

1. **Run All Tests First**: Run all required tests before collecting
2. **Single Collection**: Call `pydcov add --collect-only` only once
3. **Avoid Duplication**: Do not call collect-only repeatedly for the same tests

## 💻 Python API

PyDCov can also be used programmatically:

```python
from pydcov import IncrementalCoverageManager

# Incremental coverage workflow
manager = IncrementalCoverageManager()
manager.init()
manager.add(["python", "-m", "pytest", "tests/module1/"])
manager.add(["python", "-m", "pytest", "tests/module2/"])
manager.merge()
```

## 🔧 System Requirements

### Required Tools

**Build Tools:**
- CMake 3.9.6 or later
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

### Python Requirements

- **Python 3.11+** (leverages modern Python features for improved performance and reliability)
- No additional Python dependencies (uses standard library)

**Why Python 3.11+?**
- **Enhanced Performance**: Python 3.11 provides significant performance improvements (10-60% faster)
- **Better Error Messages**: More detailed and helpful error messages for debugging
- **Modern Type Hints**: Support for new union syntax (`str | None` instead of `Optional[str]`)
- **Improved Standard Library**: Enhanced `importlib.resources` and other stdlib improvements
- **Better Security**: Latest security patches and improvements

## 🏗️ CMake Integration

PyDCov provides a comprehensive CMake module that automatically:

- ✅ Detects available compilers and coverage tools
- ✅ Configures appropriate coverage flags
- ✅ Creates coverage targets (`coverage-clean`, `coverage-report`)
- ✅ Supports both GCC/gcov and Clang/llvm-cov workflows
- ✅ Automatic incremental coverage collection for all operations

### Example CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.9.6)
project(MyProject)

# Include PyDCov coverage support
include(cmake/coverage.cmake)

# Your project configuration
add_executable(my_app src/main.cpp)
add_library(my_lib src/library.cpp)

# Coverage will be automatically configured
```

## 📊 Examples and Use Cases

### Basic Incremental Coverage Workflow

```bash
# Initialize incremental coverage tracking
pydcov init

# Add coverage from different test runs
pydcov add python -m pytest tests/unit/
pydcov add python -m pytest tests/integration/

# Generate combined coverage report
pydcov report

# View results
open pydcov_dir/report/index.html
```

### Collect-Only Workflow for Manual Testing

```bash
# Initialize
pydcov init

# Run tests manually using your custom workflow
./build/unit_tests
./build/integration_tests

# Collect coverage without running tests
pydcov add --collect-only
pydcov merge
pydcov report
```

### Integration with Existing Projects

```bash
# Add PyDCov to existing project
cd my_existing_project
pydcov init-cmake

# Update CMakeLists.txt to include:
# include(cmake/coverage.cmake)

# Use incremental coverage
pydcov init
pydcov add python -m pytest tests/
pydcov report
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Coverage
on: [push, pull_request]
jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install PyDCov
        run: pip install pydcov
      - name: Setup project
        run: pydcov init-cmake
      - name: Run incremental coverage
        run: |
          pydcov init
          pydcov add python -m pytest tests/
          pydcov report
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./pydcov_dir/merged.info
```

## 🔍 Advanced Features

### Custom Test Commands

PyDCov works with any test framework or executable:

```bash
# With pytest
pydcov add python -m pytest tests/

# With CTest
pydcov add make test

# With custom test executable
pydcov add ./my_test_runner --verbose

# With shell scripts
pydcov add bash run_all_tests.sh

# With custom timeout for long-running tests
pydcov add --timeout 1800 python -m pytest tests/slow/
```

### Multiple Output Formats

```bash
# Generate coverage report (creates multiple formats)
pydcov report

# Output includes:
# - pydcov_dir/report/index.html  (Interactive HTML)
# - pydcov_dir/merged.profdata    (Clang format)
# - pydcov_dir/merged.info        (LCOV format)

# Export to specific formats
pydcov export --format lcov --output coverage.info
pydcov export --format json --output coverage.json
```

## 🛠️ Development and Examples

This repository includes example C/C++ modules that demonstrate PyDCov usage:

### Example Modules

- **`examples/algorithm/`**: Dynamic array implementation with comprehensive tests
- **`examples/statistics/`**: Statistical analysis functions with unit tests

### Running Examples

```bash
# Build examples
mkdir build && cd build
cmake ..
make

# Test algorithm module
python -m pytest examples/algorithm/tests/ -v

# Test statistics module
python -m pytest examples/statistics/tests/ -v

# Generate coverage for examples
pydcov init
pydcov add python -m pytest examples/
pydcov report
```

### Project Structure

```
pydcov/
├── pydcov/                 # PyPI package source
│   ├── core/              # Coverage managers
│   ├── utils/             # Utilities and helpers
│   ├── cmake/             # CMake integration files
│   └── cli.py             # Command-line interface
├── examples/              # Example C/C++ projects
│   ├── algorithm/         # Dynamic array example
│   └── statistics/        # Statistics example
├── cmake/                 # CMake utilities (for examples)
├── docs/                  # Documentation
├── tests/                 # Package tests
└── pyproject.toml         # Package configuration
```

## 🔨 Building Standalone Executables

PyDCov includes a build script for creating standalone executables using PyInstaller:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Build standalone executable
python build_standalone.py --clean --test

# The executable will be created in dist/pydcov
```

### Cross-Platform Building

The GitHub Actions CI automatically builds standalone executables for:
- Linux (x64)
- macOS (ARM64)

These are available as artifacts from CI runs and releases.

📖 **See [Standalone Executables Documentation](docs/STANDALONE_EXECUTABLES.md) for detailed information.**

## 🤝 Contributing

We welcome contributions to PyDCov! Here's how to get started:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ethan-li/pydcov.git
cd pydcov

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/ -v

# Test with examples
pydcov init
pydcov add python -m pytest examples/
pydcov report
```

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Ensure all tests pass**: `python -m pytest tests/ -v`
5. **Test with examples**: `pydcov init && pydcov add python -m pytest examples/ && pydcov report`
6. **Submit a pull request** with a clear description

### Reporting Issues

- **Bug reports**: Include system info, PyDCov version, and reproduction steps
- **Feature requests**: Describe the use case and expected behavior
- **Questions**: Check existing issues and documentation first

## 🔧 Troubleshooting

### Common Issues

**"Coverage tools not found"**:
```bash
# Install required tools
# Ubuntu/Debian:
sudo apt-get install gcc gcov lcov
# or
sudo apt-get install clang llvm

# macOS:
brew install gcc lcov
# or
brew install llvm
```

**"CMake configuration failed"**:
```bash
# Ensure CMake integration is set up
pydcov init-cmake

# Add to CMakeLists.txt:
# include(cmake/coverage.cmake)
```

**"No coverage data found"**:
```bash
# Ensure tests are actually running
pydcov add echo test command here

# Or collect existing files with collect-only
pydcov add --collect-only

# Check incremental coverage status
pydcov status
```

**"Permission denied"**:
```bash
# Make sure PyDCov is properly installed
pip install --upgrade pydcov
```

## 🔄 Migration Guide

PyDCov focuses on **incremental coverage collection** for optimal performance and flexibility. If you're migrating from other coverage tools, here's how to get started:

### Basic Migration Steps

1. **Install PyDCov**:
   ```bash
   pip install pydcov
   ```

2. **Set up CMake integration** (if using CMake):
   ```bash
   pydcov init-cmake
   # Add to CMakeLists.txt: include(cmake/coverage.cmake)
   ```

3. **Use incremental coverage workflow**:
   ```bash
   pydcov init                  # Initialize tracking
   pydcov add your_test_command # Add coverage data
   pydcov report                # Generate report
   ```

### Benefits of Incremental Approach

- **Better Performance**: Efficient data collection and merging
- **Flexible Workflow**: Add coverage from different test runs
- **Cross-Platform**: Works consistently across Linux, macOS, Windows
- **Framework Agnostic**: Works with any testing framework
- **Collect-Only Mode**: Support for existing test execution workflows

### Getting Help

- 📖 **Documentation**: Check this README and `docs/` directory
- 🐛 **Issues**: [GitHub Issues](https://github.com/ethan-li/pydcov/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ethan-li/pydcov/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LLVM Project**: For excellent coverage tools and infrastructure
- **GCC Project**: For gcov and the foundation of C/C++ coverage analysis
- **CMake Community**: For the robust build system that makes cross-platform development possible
- **Python Community**: For the ecosystem that makes this tool possible

---

**Made with ❤️ for the C/C++ development community**
