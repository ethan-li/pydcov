# PyDCov - C Code Coverage for Python-Driven Tests

[![CI](https://github.com/your-username/pydcov/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/pydcov/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/your-username/pydcov/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/pydcov)

A focused sample project demonstrating how to measure code coverage for C code that is executed via command-line interface from Python tests. This project provides a comprehensive solution for cross-platform C code coverage collection, reporting, and CI integration, using a dynamic array data structure as the example C algorithm.

## Features

- **Cross-Platform Support**: Works on both Linux and macOS
- **Multiple Compiler Support**: GCC (gcov) and Clang (llvm-cov)
- **Comprehensive Test Suite**: Python-driven tests using pytest
- **Coverage Reporting**: HTML, XML, and LCOV format reports
- **CI/CD Integration**: Complete GitHub Actions workflow
- **Dynamic Array Implementation**: C90-compliant dynamic array data structure with memory management

## Project Structure

```
pydcov/
├── coverage_tools/         # Main Python coverage tools package (DELIVERABLE)
│   ├── core/              # Core coverage management utilities
│   ├── scripts/           # Command-line coverage tools
│   ├── utils/             # Utility modules and helpers
│   └── requirements.txt   # Python dependencies for coverage tools
├── cmake/                  # CMake coverage utilities (DELIVERABLE)
│   ├── coverage.cmake     # Coverage configuration module
│   └── COVERAGE_USAGE.md  # CMake integration documentation
├── docs/                   # Documentation (DELIVERABLE)
│   ├── INCREMENTAL_COVERAGE.md
│   └── MODULE_COVERAGE.md
├── scripts/                # Build and deployment scripts (DELIVERABLE)
│   ├── install_deps.sh     # Dependency installation script
│   ├── test_coverage_fix.sh # Coverage verification script
│   └── verify_deployment.sh # Pre-deployment verification
├── tests/                  # Unified test suite
│   ├── algorithm/         # Tests for algorithm example module
│   ├── statistics/        # Tests for statistics example module
│   ├── coverage_tools/    # Tests for coverage tools (future)
│   └── conftest.py        # Root pytest configuration
├── algorithm/              # Example C library module
│   ├── src/               # Algorithm library source code
│   ├── app/               # Algorithm CLI application
│   └── CMakeLists.txt     # Module build configuration
├── statistics/             # Example C library module
│   ├── src/               # Statistics library source code
│   ├── app/               # Statistics CLI application
│   └── CMakeLists.txt     # Module build configuration
├── .github/workflows/      # CI/CD configuration
│   └── ci.yml              # GitHub Actions workflow with artifact packaging
├── CMakeLists.txt          # Root CMake build configuration
├── requirements.txt        # Python dependencies
├── pytest.ini             # Pytest configuration
├── EXAMPLES.md             # Detailed usage examples
├── PACKAGE_README.md       # Package distribution documentation
└── LICENSE                 # MIT license
```

### Deliverable vs Example Components

**Deliverable Components** (packaged in CI artifacts):
- `coverage_tools/` - The core Python coverage tools
- `cmake/` - CMake integration utilities
- `docs/` - Documentation
- `scripts/` - Build and deployment scripts
- Root configuration files

**Example/Demo Components** (for testing and demonstration):
- `algorithm/` and `statistics/` - Example C library modules
- `tests/` - Test suite for all components

## Quick Start

### Prerequisites

- **C Compiler**: GCC or Clang
- **Python 3.7+**: For running tests
- **CMake 3.15+**: For building the project

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/pydcov.git
   cd pydcov
   ```

2. **Install dependencies** (optional - uses automated script):
   ```bash
   ./scripts/install_deps.sh
   ```

3. **Or install manually**:

   **On Ubuntu/Debian**:
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential gcc g++ clang llvm cmake lcov python3 python3-pip
   pip3 install pytest pytest-cov pytest-xdist pytest-html coverage
   ```

   **On macOS**:
   ```bash
   brew install llvm lcov cmake
   pip3 install pytest pytest-cov pytest-xdist pytest-html coverage
   ```

### Building and Testing

1. **Build the project**:
   ```bash
   mkdir -p build && cd build
   cmake .. -DCMAKE_BUILD_TYPE=Release
   make
   cd ..
   ```

2. **Run tests**:
   ```bash
   python3 -m pytest tests/ -v
   ```

3. **Generate coverage report**:
   ```bash
   # Clean and build with coverage
   rm -rf build && mkdir -p build && cd build
   cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
   make
   cd ..

   # Run tests with coverage
   export LLVM_PROFILE_FILE="build/coverage-%p.profraw"  # For Clang
   python3 -m pytest tests/ -v

   # Generate coverage report
   cd build && make coverage-report
   ```

4. **View coverage report**:
   ```bash
   open build/coverage/html/index.html  # macOS
   xdg-open build/coverage/html/index.html  # Linux
   ```

## Usage Examples

The project implements a dynamic array data structure with a command-line interface:

```bash
# Dynamic array operations
./build/pydcov dynarray create 10      # Create array with capacity 10
./build/pydcov dynarray push 1 2 3     # Push values to array
./build/pydcov dynarray get 0          # Get value at index 0
./build/pydcov dynarray pop 2          # Pop 2 values from array
./build/pydcov dynarray cleanup        # Clean up array data

# Example workflow
./build/pydcov dynarray create 5       # Create array with capacity 5
./build/pydcov dynarray push 10 20 30  # Push three values
./build/pydcov dynarray get 1          # Returns: 20
./build/pydcov dynarray pop            # Returns: 30 (LIFO order)
./build/pydcov dynarray push 40 50 60  # Push more values (triggers expansion)
./build/pydcov dynarray pop 2          # Returns: 60 50
```

## Coverage Workflow

### Using the Python Coverage Tools

The project uses modern Python-based coverage tools that provide enhanced functionality and better maintainability:

```bash
# Full coverage workflow (clean, build, test, report)
python3 coverage_tools/scripts/coverage.py full tests/

# Individual steps
python3 coverage_tools/scripts/coverage.py clean    # Clean coverage data
python3 coverage_tools/scripts/coverage.py build    # Build with coverage
python3 coverage_tools/scripts/coverage.py test tests/  # Run tests
python3 coverage_tools/scripts/coverage.py report   # Generate report

# Check status
python3 coverage_tools/scripts/coverage.py status
```

### Manual Coverage Workflow

1. **Clean and build with coverage**:
   ```bash
   rm -rf build
   mkdir -p build
   cd build
   cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
   make
   cd ..
   ```

2. **Run tests with coverage**:
   ```bash
   # For Clang
   export LLVM_PROFILE_FILE="build/coverage-%p.profraw"
   python3 -m pytest tests/ -v

   # For GCC (no special environment needed)
   python3 -m pytest tests/ -v
   ```

3. **Generate coverage report**:
   ```bash
   cd build
   make coverage-report
   ```

### Coverage Output

The coverage report includes:
- **HTML Report**: Interactive coverage visualization
- **LCOV Report**: Standard format for CI integration
- **Console Summary**: Quick coverage statistics

Example coverage output:
```
Filename                      Regions    Missed Regions     Cover   Functions  Missed Functions  Executed       Lines      Missed Lines     Cover
algorithm.c                       214                18    91.59%          16                 0   100.00%         162                 3    98.15%
main.cpp                          220                20    90.91%          10                 1    90.00%         356                72    79.78%
TOTAL                             434                38    91.24%          26                 1    96.15%         518                75    85.52%
```

## CI/CD Pipeline

### GitHub Actions Workflow

The project includes a robust CI/CD pipeline with a **3-job matrix** that ensures cross-platform compatibility:

#### **Test Matrix**
```yaml
matrix:
  os: [ubuntu-latest, macos-latest]
  compiler: [gcc, clang]
  exclude:
    - os: macos-latest
      compiler: gcc  # macOS uses Clang by default
```

**Resulting Jobs:**
- ✅ **ubuntu-latest + gcc**: Linux with GCC and gcov coverage
- ✅ **ubuntu-latest + clang**: Linux with Clang and llvm-cov coverage
- ✅ **macos-latest + clang**: macOS with Clang and llvm-cov coverage

#### **Pipeline Features**
- **Cross-platform testing**: Ensures compatibility on both Linux and macOS
- **Multi-compiler support**: Tests with both GCC and Clang compilers
- **Automated dependency installation**: Platform-specific package installation
- **Coverage generation**: Comprehensive coverage reports for each combination
- **Artifact upload**: Coverage reports and build artifacts
- **Codecov integration**: Automatic coverage reporting and badges
- **Error handling**: Robust error handling for coverage tool detection

#### **Recent CI Improvements**
The pipeline includes recent fixes for common CI issues:
- **Linux GCC lcov errors**: Fixed "exclude pattern unused" errors with proper ignore flags
- **Ubuntu Clang LLVM tools**: Automatic detection of versioned LLVM tools (llvm-profdata-14, etc.)
- **Coverage tool detection**: Robust fallback mechanisms for different tool versions
- **Enhanced error handling**: Comprehensive error tolerance for coverage generation

### Setting Up CI

1. **Enable GitHub Actions** in your repository settings

2. **Add Codecov integration** (optional):
   - Sign up at [codecov.io](https://codecov.io)
   - Connect your GitHub repository
   - Public repositories work automatically

3. **Monitor CI runs**:
   - Check the **Actions** tab in your GitHub repository
   - All 3 jobs should complete successfully
   - Coverage reports are uploaded as artifacts
   - Add your repository
   - No additional secrets needed for public repositories

3. **Enable GitHub Pages** (optional):
   - Go to repository Settings → Pages
   - Set source to "GitHub Actions"
   - Coverage reports will be available at `https://your-username.github.io/pydcov/coverage/`

### Customizing CI

The workflow can be customized by modifying `.github/workflows/ci.yml`:

- **Add more platforms**: Add entries to the `matrix.os` array
- **Add more compilers**: Add entries to the `matrix.compiler` array
- **Change Python version**: Modify the `python-version` in setup steps
- **Add deployment targets**: Add steps for deploying to other services

## Build System

The project uses **CMake** as its build system, providing cross-platform compatibility and modern C++ project standards.

### CMake Configuration

**Key Features:**
- **C90 compliance** for algorithm implementation
- **C++11 standard** for CLI wrapper
- **Coverage support** with `ENABLE_COVERAGE` option
- **Cross-platform** compatibility (Linux, macOS, Windows)
- **Automatic tool detection** for GCC/gcov and Clang/llvm-cov

### Build Commands

```bash
# Basic build
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make

# Coverage build
mkdir -p build && cd build
cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
make

# Generate coverage report
cd build && make coverage-report

# Clean build
rm -rf build

# Install (optional)
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make install
```

## Testing

### Test Suite Overview

The project includes a comprehensive test suite with **16 test cases** covering all dynamic array functionality:

- **test_dynarray.py**: 16 comprehensive dynamic array tests (251 lines)
  - Basic operations (create, push, pop, get)
  - Error handling and edge cases
  - Memory management and expansion
  - File persistence and cleanup
- **test_utils.py**: Test utilities and command execution helpers (156 lines)
- **conftest.py**: pytest configuration and fixtures (135 lines)

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run tests for specific modules
python3 -m pytest tests/algorithm/ -v    # Algorithm module tests
python3 -m pytest tests/statistics/ -v   # Statistics module tests

# Run tests with specific markers
python3 -m pytest tests/ -m "algorithm" -v
python3 -m pytest tests/ -m "statistics" -v
python3 -m pytest tests/ -m "not slow" -v

# Run with coverage (Python-level)
python3 -m pytest tests/ --cov=coverage_tools --cov-report=html

# Run in parallel
python3 -m pytest tests/ -n auto

# Generate HTML test report
python3 -m pytest tests/ --html=report.html --self-contained-html
```

### Coverage Analysis

The project includes comprehensive C/C++ code coverage analysis:

#### Standard Coverage (Single Run)
```bash
# Complete coverage workflow
python3 coverage_tools/scripts/coverage.py full tests/

# Step-by-step coverage
python3 coverage_tools/scripts/coverage.py build    # Build with coverage
python3 coverage_tools/scripts/coverage.py test tests/  # Run tests
python3 coverage_tools/scripts/coverage.py report   # Generate report
```

#### Incremental Coverage (Multiple Runs)
```bash
# Step-by-step incremental coverage
python3 coverage_tools/scripts/incremental_coverage.py init
python3 coverage_tools/scripts/incremental_coverage.py add algorithm/tests/
python3 coverage_tools/scripts/incremental_coverage.py add statistics/tests/
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report

# Or complete workflow
python3 coverage_tools/scripts/incremental_coverage.py full tests/
```

#### Module-Specific Coverage
```bash
# Generate reports for all modules
python3 coverage_tools/scripts/coverage_modules.py full

# Generate report for specific module
python3 coverage_tools/scripts/coverage_modules.py generate algorithm
```

**Coverage Features:**
- **🐍 Modern Python Tools**: Enhanced Python-based coverage scripts with better error handling and logging
- **Cross-platform**: Linux and macOS support
- **Multi-compiler**: GCC/gcov and Clang/llvm-cov
- **Incremental collection**: Accumulate coverage across multiple test runs
- **Module separation**: Individual reports for algorithm and statistics modules
- **Multiple formats**: HTML reports and LCOV data for CI/CD integration

> **📖 For detailed information about the Python coverage tools, see [coverage_tools/README.md](coverage_tools/README.md)**

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python3 -m pytest tests/ -v`
6. Check coverage: `python3 coverage_tools/scripts/coverage.py full tests/`
7. Commit your changes: `git commit -am 'Add feature'`
8. Push to the branch: `git push origin feature-name`
9. Create a Pull Request

## Troubleshooting

### Common Issues

**Coverage tools not found**:
```bash
# On macOS, add LLVM tools to PATH
export PATH="/opt/homebrew/opt/llvm/bin:$PATH"

# On Ubuntu, install lcov
sudo apt-get install lcov
```

**Tests failing due to missing executable**:
```bash
# Make sure to build first
rm -rf build && mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make
```

**Permission denied on scripts**:
```bash
chmod +x scripts/*.sh
```

**Python module not found**:
```bash
pip3 install pytest pytest-cov pytest-xdist pytest-html coverage
```

### Platform-Specific Notes

**macOS**:
- Requires Xcode Command Line Tools
- LLVM tools are installed via Homebrew
- Default compiler is Clang

**Linux**:
- Supports both GCC and Clang
- lcov provides better HTML reports with GCC
- May require additional development packages

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- **LLVM Project**: For excellent coverage tools
- **GCC Project**: For gcov and lcov
- **pytest**: For the testing framework
- **GitHub Actions**: For CI/CD infrastructure
# pydcov
