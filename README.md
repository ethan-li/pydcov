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
- **📊 Modern Python API**: Clean, well-documented Python interface

## 🚀 Quick Start

### Installation

### Option 1: Python Package (Recommended)

```bash
pip install pydcov
```

### Option 2: Standalone Executable

Download pre-built standalone executables from the [GitHub Releases](https://github.com/ethan-li/pydcov/releases) page:

- **Linux (x64)**: `pydcov-linux-x64`
- **macOS (ARM64)**: `pydcov-macos-arm64`

No Python installation required! Simply download, make executable, and run:

```bash
# Linux/macOS
chmod +x pydcov-linux-x64  # or pydcov-macos-arm64
./pydcov-linux-x64 --version
```

### Option 3: Build Your Own Executable

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

## ✨ Features

- **🔧 Easy Installation**: Simple `pip install pydcov`
- **🐍 Pure Python**: No CMake dependencies for coverage operations
- **🔄 Cross-Platform**: Linux, macOS, Windows support
- **⚙️ Multiple Compilers**: GCC/gcov and Clang/llvm-cov
- **📊 Incremental Coverage**: Efficient incremental collection and reporting
- **🧪 Framework-Agnostic**: Works with any testing framework
- **🎯 CMake Integration**: Optional CMake build system support
- **📈 Rich Reporting**: HTML, XML, and LCOV format reports
- **🚀 Better Error Handling**: Comprehensive error reporting and validation

## 🎯 Incremental Coverage Approach

PyDCov focuses on **incremental coverage collection** for optimal performance and flexibility:

- **Cumulative Collection**: Multiple test runs automatically accumulate coverage data
- **Optimal Performance**: Efficient data collection and merging for large projects
- **Flexible Workflow**: Add coverage data from different test runs as needed
- **Clean Separation**: Clear commands for initialization, collection, and reporting

### How It Works

1. **Initialize**: Set up incremental coverage tracking with `pydcov init`
2. **Collect**: Add coverage data from test runs with `pydcov add test_command`
3. **Merge**: Combine coverage data with `pydcov merge`
4. **Report**: Generate reports at any time with `pydcov report`
5. **Clean**: Reset for fresh collection with `pydcov clean`

## 📋 Command Reference

### Incremental Coverage Commands

```bash
pydcov init                              # Initialize incremental tracking
pydcov add python -m pytest tests/      # Add coverage data from test run
pydcov merge                             # Merge coverage data
pydcov report                            # Generate incremental report
pydcov status                            # Show incremental status
pydcov clean                             # Clean incremental data
```

### Project Setup Commands

```bash
pydcov init-cmake              # Copy CMake integration files
pydcov --version               # Show version
pydcov --help                  # Show help
```
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
open build/coverage/incremental_report/index.html
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
          file: ./build/coverage/incremental_merged.info
```

## 🔍 Advanced Features

### Incremental Coverage Collection

PyDCov provides efficient incremental coverage collection for optimal performance:

```bash
# Initialize tracking (specify build directory once)
pydcov init --build-root build

# Add coverage from multiple test runs (no --build-root needed)
pydcov add python -m pytest tests/module1/
pydcov add python -m pytest tests/module2/

# Merge and generate report
pydcov merge
```

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
# - build/coverage/incremental_report/index.html  (Interactive HTML)
# - build/coverage/incremental_merged.profdata    (Clang format)
# - build/coverage/incremental_merged.info        (LCOV format)
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
