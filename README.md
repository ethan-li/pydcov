# PyDCov - Python-based C/C++ Code Coverage Tools

[![PyPI version](https://badge.fury.io/py/pydcov.svg)](https://badge.fury.io/py/pydcov)
[![Python Support](https://img.shields.io/pypi/pyversions/pydcov.svg)](https://pypi.org/project/pydcov/)
[![CI](https://github.com/ethan-li/pydcov/actions/workflows/ci.yml/badge.svg)](https://github.com/ethan-li/pydcov/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive **pure Python** coverage management system for C/C++ projects. PyDCov provides modern Python tools for coverage collection, incremental coverage tracking, and reporting with support for both GCC/gcov and Clang/llvm-cov toolchains. **No CMake dependencies required** for coverage operations.

## 🚀 Quick Start

### Installation

```bash
pip install pydcov
```

### Create a New Project

```bash
# Create a new C++ project with coverage support
pydcov init-template my_project

# Navigate to project and build
cd my_project
mkdir build && cd build
cmake ..
make

# Run coverage analysis
pydcov coverage full "make test"
```

### Add to Existing Project

```bash
# Add PyDCov to existing CMake project
pydcov init-cmake

# Add to your CMakeLists.txt:
# include(cmake/coverage.cmake)

# Run coverage
pydcov coverage full "python -m pytest tests/"
```

## ✨ Features

- **🔧 Easy Installation**: Simple `pip install pydcov`
- **🐍 Pure Python**: No CMake dependencies for coverage operations
- **🏗️ Project Templates**: Bootstrap new projects with `init-template`
- **🔄 Cross-Platform**: Linux, macOS, Windows support
- **⚙️ Multiple Compilers**: GCC/gcov and Clang/llvm-cov
- **📊 Incremental Coverage**: Track coverage changes over time
- **🧪 Framework-Agnostic**: Works with any testing framework
- **🎯 CMake Integration**: Optional CMake build system support
- **📈 Rich Reporting**: HTML, XML, and LCOV format reports
- **🚀 Better Error Handling**: Comprehensive error reporting and validation

## 📋 Command Reference

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

### Project Setup Commands

```bash
pydcov init-cmake              # Copy CMake integration files
pydcov init-template name      # Create new project from template
pydcov --version               # Show version
pydcov --help                  # Show help
```

## 🏗️ Project Templates

PyDCov includes project templates to quickly bootstrap new C/C++ projects:

### Basic C++ Template

```bash
pydcov init-template my_project --template basic_cpp
```

Creates a complete C++ project with:
- ✅ CMake configuration with coverage support
- ✅ Example library with calculator functions
- ✅ Unit tests with assertions
- ✅ Application executable
- ✅ Complete documentation
## 💻 Python API

PyDCov can also be used programmatically:

```python
from pydcov import CoverageManager, IncrementalCoverageManager

# Standard coverage workflow
manager = CoverageManager()
success = manager.full_workflow(["python", "-m", "pytest", "tests/"])

# Incremental coverage
incremental = IncrementalCoverageManager()
incremental.init()
incremental.add(["python", "-m", "pytest", "tests/module1/"])
incremental.add(["python", "-m", "pytest", "tests/module2/"])
incremental.report()
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
- ✅ Provides incremental coverage capabilities

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

### Basic C++ Project Example

```bash
# Create a new project
pydcov init-template calculator_app

# Build and test
cd calculator_app
mkdir build && cd build
cmake ..
make

# Run coverage analysis
pydcov coverage full "make test"

# View results
open coverage_html/index.html
```

### Integration with Existing Projects

```bash
# Add PyDCov to existing project
cd my_existing_project
pydcov init-cmake

# Update CMakeLists.txt to include:
# include(cmake/coverage.cmake)

# Run coverage on your existing tests
pydcov coverage full "python -m pytest tests/"
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
      - name: Run coverage
        run: pydcov coverage full "python -m pytest tests/"
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## 🔍 Advanced Features

### Incremental Coverage Tracking

Track coverage changes across multiple test runs:

```bash
# Initialize incremental tracking
pydcov incremental init

# Add coverage from different test suites
pydcov incremental add "python -m pytest tests/unit/"
pydcov incremental add "python -m pytest tests/integration/"
pydcov incremental add "python -m pytest tests/e2e/"

# Generate combined report
pydcov incremental report

# Check status
pydcov incremental status
```

### Custom Test Commands

PyDCov works with any test framework or executable:

```bash
# With pytest
pydcov coverage full "python -m pytest tests/"

# With CTest
pydcov coverage full "make test"

# With custom test executable
pydcov coverage full "./my_test_runner --verbose"

# With shell scripts
pydcov coverage full "bash run_all_tests.sh"
```

### Multiple Output Formats

```bash
# Generate coverage report (creates multiple formats)
pydcov coverage report

# Output includes:
# - coverage_html/index.html    (Interactive HTML)
# - coverage.xml                (XML for CI tools)
# - coverage.lcov               (LCOV format)
# - coverage.json               (JSON format)
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
pydcov coverage full "python -m pytest examples/"
```

### Project Structure

```
pydcov/
├── pydcov/                 # PyPI package source
│   ├── core/              # Coverage managers
│   ├── utils/             # Utilities and helpers
│   ├── cmake/             # CMake integration files
│   ├── templates/         # Project templates
│   └── cli.py             # Command-line interface
├── examples/              # Example C/C++ projects
│   ├── algorithm/         # Dynamic array example
│   └── statistics/        # Statistics example
├── cmake/                 # CMake utilities (for examples)
├── docs/                  # Documentation
├── tests/                 # Package tests
└── pyproject.toml         # Package configuration
```

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
pydcov coverage full "python -m pytest examples/"
```

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Ensure all tests pass**: `python -m pytest tests/ -v`
5. **Test with examples**: `pydcov coverage full "python -m pytest examples/"`
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
pydcov coverage test "echo 'test command here'"

# Check that executables are built with coverage
pydcov coverage build
```

**"Permission denied"**:
```bash
# Make sure PyDCov is properly installed
pip install --upgrade pydcov
```

## 🔄 Migration from CMake Targets

PyDCov has transitioned to a **pure Python implementation** for better cross-platform support and error handling. If you're currently using CMake targets, here's how to migrate:

### CMake Target Migration

| **Old CMake Target** | **New Python Command** | **Benefits** |
|---------------------|------------------------|--------------|
| `make coverage-clean` | `pydcov coverage clean` | Better error handling, cross-platform |
| `make coverage-report` | `pydcov coverage report` | Automatic executable detection, library support |
| `coverage_add_executable()` | Automatic detection | No manual registration needed |

### Migration Steps

1. **Replace CMake target calls**:
   ```bash
   # Before
   make coverage-clean
   make coverage-report

   # After
   pydcov coverage clean
   pydcov coverage report
   ```

2. **Remove manual executable registration**:
   ```cmake
   # Before (manual registration)
   coverage_add_executable(my_app)

   # After (automatic detection)
   # No action needed - PyDCov automatically detects executables
   ```

3. **Update CI/CD pipelines**:
   ```yaml
   # Before
   - run: make coverage-report

   # After
   - run: pydcov coverage report
   ```

### Backward Compatibility

- **CMake targets still work** but show deprecation warnings
- **Gradual migration** is supported - you can migrate one command at a time
- **No breaking changes** to existing workflows

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
