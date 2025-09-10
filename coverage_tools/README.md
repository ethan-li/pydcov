# Python Coverage Tools for PyDCov

Modern Python-based coverage management system for the pydcov project. This package provides maintainable Python implementations for comprehensive coverage analysis and reporting.

## Features

- **🐍 Python-based**: Modern, maintainable Python code with enhanced error handling
- **🎯 Intuitive Interface**: Clean command-line interface with comprehensive help and status reporting
- **📊 Incremental Coverage**: Accumulate coverage data across multiple test runs
- **🎯 Module-specific Reports**: Generate targeted coverage reports for individual modules
- **🔧 Cross-platform**: Works on Linux and macOS with both GCC and Clang
- **⚡ Enhanced Logging**: Colored output with structured logging levels
- **🛠️ Better Error Handling**: Comprehensive error handling and validation

## Quick Start

### Installation

1. **Python Requirements**: Python 3.6+ is required
2. **Install Dependencies** (optional):
   ```bash
   pip install -r coverage_tools/requirements.txt
   ```

### Basic Usage

```bash
# Standard coverage workflow
python3 coverage_tools/scripts/coverage.py full tests/

# Incremental coverage workflow
python3 coverage_tools/scripts/incremental_coverage.py init
python3 coverage_tools/scripts/incremental_coverage.py add algorithm/tests/
python3 coverage_tools/scripts/incremental_coverage.py add statistics/tests/
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report

# Module-specific coverage
python3 coverage_tools/scripts/coverage_modules.py full algorithm
```

## Available Tools

### 1. Standard Coverage (`coverage.py`)

Provides comprehensive coverage workflow management.

```bash
python3 coverage_tools/scripts/coverage.py [command] [options]

Commands:
  clean                 - Clean all coverage data
  build                 - Build project with coverage instrumentation
  test [test_args]      - Run tests with coverage data collection
  report                - Generate coverage reports
  full [test_args]      - Complete workflow: clean, build, test, report
  status                - Show current coverage status
  help                  - Show help message
```

### 2. Incremental Coverage (`incremental_coverage.py`)

Enables incremental coverage collection across multiple test runs.

```bash
python3 coverage_tools/scripts/incremental_coverage.py [command] [options]

Commands:
  init                  - Initialize incremental coverage collection
  add [test_args]       - Run tests and add coverage data to collection
  merge                 - Merge all accumulated coverage data
  report                - Generate final comprehensive coverage report
  full [test_args]      - Complete workflow: init, add, merge, report
  clean                 - Clean all incremental coverage data
  status                - Show current incremental coverage status
  help                  - Show help message
```

### 3. Module Coverage (`coverage_modules.py`)

Generates module-specific coverage reports for targeted analysis.

```bash
python3 coverage_tools/scripts/coverage_modules.py [command] [module]

Commands:
  full [module]     - Run complete workflow: build, test, generate module reports
  build             - Build project with coverage instrumentation
  test [module]     - Run tests with coverage data collection
  generate [module] - Generate module-specific coverage reports
  clean             - Clean module coverage data
  status [module]   - Show module coverage status
  help              - Show help message

Modules:
  algorithm         - Dynamic array library module
  statistics        - Statistical analysis library module
  (omit module to process all modules)
```

## Testing Framework Support

The coverage tools are framework-agnostic and support various testing approaches:

### Using pytest
```bash
# Basic pytest usage
python3 coverage_tools/scripts/coverage.py test python -m pytest tests/
python3 coverage_tools/scripts/coverage.py test python -m pytest tests/test_basic.py -v
python3 coverage_tools/scripts/coverage.py full python -m pytest tests/ --tb=short

# Incremental coverage with pytest
python3 coverage_tools/scripts/incremental_coverage.py add python -m pytest tests/ -k "test_create"
python3 coverage_tools/scripts/incremental_coverage.py add python -m pytest tests/test_advanced.py -v
```

### Using unittest
```bash
# Standard unittest discovery
python3 coverage_tools/scripts/coverage.py test python -m unittest discover
python3 coverage_tools/scripts/coverage.py full python -m unittest discover tests

# Specific unittest modules
python3 coverage_tools/scripts/incremental_coverage.py add python -m unittest tests.test_basic
python3 coverage_tools/scripts/incremental_coverage.py add python -m unittest tests.test_advanced
```

### Using custom test commands
```bash
# Custom shell scripts
python3 coverage_tools/scripts/coverage.py test ./run_tests.sh
python3 coverage_tools/scripts/coverage.py full make test

# Other testing frameworks
python3 coverage_tools/scripts/coverage.py test green tests/
python3 coverage_tools/scripts/coverage.py test nose2 tests/
```

### Module-specific testing
```bash
# Module-specific testing (uses pytest with module paths)
python3 coverage_tools/scripts/coverage_modules.py test algorithm
python3 coverage_tools/scripts/coverage_modules.py full statistics

# Custom test commands for modules
python3 coverage_tools/scripts/coverage_modules.py test algorithm --test-command python -m unittest discover algorithm/tests
python3 coverage_tools/scripts/coverage_modules.py full statistics --test-command ./test_statistics.sh
```

## Advanced Usage

Additional advanced workflows and customization options:

```bash
# Check detailed status information
python3 coverage_tools/scripts/coverage.py status

# Generate module-specific reports
python3 coverage_tools/scripts/coverage_modules.py generate algorithm

# Clean specific coverage data
python3 coverage_tools/scripts/incremental_coverage.py clean
```

## CMake Integration

The Python tools integrate seamlessly with the existing CMake coverage system:

```bash
# Enable Python tools in CMake (default: ON)
cmake .. -DENABLE_COVERAGE=ON -DUSE_PYTHON_COVERAGE_TOOLS=ON

# The CMake targets continue to work as before
make coverage-clean
make coverage-report
make coverage-incremental-init
make coverage-incremental-add
make coverage-incremental-merge
make coverage-incremental-report
```

## Architecture

```
coverage_tools/
├── __init__.py                 # Package initialization
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── core/                       # Core coverage management classes
│   ├── __init__.py
│   ├── coverage_manager.py     # Standard coverage workflows
│   ├── incremental_coverage.py # Incremental coverage workflows
│   └── module_coverage.py      # Module-specific coverage workflows
├── utils/                      # Shared utilities
│   ├── __init__.py
│   ├── compiler_detection.py   # Compiler and tool detection
│   ├── logging_config.py       # Colored logging setup
│   ├── path_utils.py           # Path management utilities
│   └── cmake_integration.py    # CMake integration helpers
└── scripts/                    # Command-line scripts
    ├── coverage.py             # Main coverage script
    ├── incremental_coverage.py # Incremental coverage script
    └── coverage_modules.py     # Module coverage script
```

## Key Features

### Enhanced User Experience

1. **Better Error Messages**: More descriptive error messages with suggestions
2. **Structured Logging**: Color-coded log levels (INFO, WARNING, ERROR, SUCCESS)
3. **Input Validation**: Comprehensive validation of arguments and environment
4. **Cross-platform Paths**: Proper path handling across different operating systems
5. **Type Safety**: Python type hints for better code maintainability

### Comprehensive Coverage Analysis

- **Standard Coverage**: Single-run coverage analysis with detailed reporting
- **Incremental Coverage**: Accumulate coverage data across multiple test sessions
- **Module-specific Reports**: Targeted analysis for individual project modules
- **Multiple Formats**: HTML reports and LCOV data for CI/CD integration

## Development

### Running Tests

```bash
# Test the Python tools
python3 -m pytest coverage_tools/tests/

# Test with the actual project
python3 coverage_tools/scripts/coverage.py full tests/ -v
```

### Code Style

```bash
# Format code
black coverage_tools/

# Lint code
flake8 coverage_tools/

# Type checking
mypy coverage_tools/
```

## Troubleshooting

### Common Issues

1. **Python 3 not found**: Install Python 3.6 or later
2. **Coverage tools missing**: Install GCC/gcov or Clang/llvm-cov
3. **CMake not configured**: Run `cmake .. -DENABLE_COVERAGE=ON`
4. **Permission denied**: Make scripts executable with `chmod +x`

### Getting Help

```bash
# Get help for any script
python3 coverage_tools/scripts/coverage.py help
python3 coverage_tools/scripts/incremental_coverage.py help
python3 coverage_tools/scripts/coverage_modules.py help

# Check status
python3 coverage_tools/scripts/coverage.py status
```
