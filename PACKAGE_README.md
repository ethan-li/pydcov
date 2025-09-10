# PyDCov - C Code Coverage Tools Package

This package contains the PyDCov coverage tools and utilities for measuring C code coverage in Python-driven test environments.

## Package Contents

### Core Deliverable Components

- **`coverage_tools/`** - Main Python coverage tools package
  - Core coverage management utilities
  - Incremental coverage collection
  - Module-specific coverage analysis
  - Framework-agnostic test execution

- **`cmake/`** - CMake coverage integration utilities
  - Coverage configuration for CMake projects
  - Cross-platform compiler support (GCC/Clang)
  - Automated coverage target generation

- **`docs/`** - Documentation
  - Usage guides and technical documentation
  - Coverage workflow examples
  - Integration instructions

- **`scripts/`** - Build and deployment scripts
  - Dependency installation scripts
  - Coverage verification utilities
  - Deployment helpers

### Configuration Files

- **`CMakeLists.txt`** - Root CMake configuration
- **`requirements.txt`** - Python dependencies
- **`pytest.ini`** - Test configuration
- **`README.md`** - Main project documentation
- **`LICENSE`** - MIT license
- **`EXAMPLES.md`** - Detailed usage examples
- **`CMAKE_TECHNICAL_DOCUMENTATION.md`** - CMake technical details

### Example Modules

- **`examples/algorithm/`** - Dynamic array C library example
- **`examples/statistics/`** - Statistical analysis C library example

These example modules demonstrate how to use the coverage tools with real C projects.

## Quick Start

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Basic coverage workflow:**
   ```bash
   python3 coverage_tools/scripts/coverage.py full tests/
   ```

3. **Incremental coverage workflow:**
   ```bash
   python3 coverage_tools/scripts/incremental_coverage.py init
   python3 coverage_tools/scripts/incremental_coverage.py add tests/
   python3 coverage_tools/scripts/incremental_coverage.py report
   ```

4. **Module-specific coverage:**
   ```bash
   python3 coverage_tools/scripts/coverage_modules.py full algorithm
   ```

## Integration

The coverage tools can be integrated into existing C/C++ projects by:

1. Including the `cmake/coverage.cmake` module in your CMakeLists.txt
2. Using the Python scripts in `coverage_tools/` for test execution
3. Following the patterns shown in the example modules

## Documentation

- See `README.md` for comprehensive documentation
- See `EXAMPLES.md` for detailed usage examples
- See `docs/` directory for technical guides
- See `CMAKE_TECHNICAL_DOCUMENTATION.md` for CMake integration details

## Support

This package provides cross-platform C code coverage collection for:
- Linux and macOS
- GCC and Clang compilers
- Various testing frameworks (pytest, unittest, custom executables)
- CI/CD integration (GitHub Actions, etc.)

The tools are framework-agnostic and can work with any testing approach that executes C code via command-line interfaces.
