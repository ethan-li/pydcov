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
├── src/                    # C source code
│   ├── algorithm.h         # Header file with dynamic array declarations
│   ├── algorithm.c         # C90-compliant dynamic array implementation (70 lines)
│   └── main.cpp            # C++ command-line wrapper (237 lines)
├── tests/                  # Python test suite
│   ├── conftest.py         # Pytest configuration and fixtures (135 lines)
│   ├── test_utils.py       # Test utilities and helpers (156 lines)
│   └── test_dynarray.py    # Dynamic array tests - 16 test cases (251 lines)
├── scripts/                # Build and coverage scripts
│   ├── coverage.sh         # Coverage collection script (263 lines)
│   ├── install_deps.sh     # Dependency installation script (290 lines)
│   ├── test_coverage_fix.sh # Coverage verification script (217 lines)
│   └── verify_deployment.sh # Pre-deployment verification (271 lines)
├── .github/workflows/      # CI/CD configuration
│   └── ci.yml              # GitHub Actions workflow (217 lines)
├── CMakeLists.txt          # CMake build configuration (138 lines)
├── requirements.txt        # Python dependencies (5 lines)
├── EXAMPLES.md             # Detailed usage examples (251 lines)
└── LICENSE                 # MIT license
```

**Total Project Size**: ~2,900 lines across 16 files

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

### Using the Coverage Script

The project includes a comprehensive coverage script that handles the entire workflow:

```bash
# Full coverage workflow (clean, build, test, report)
./scripts/coverage.sh

# Individual steps
./scripts/coverage.sh clean    # Clean coverage data
./scripts/coverage.sh build    # Build with coverage
./scripts/coverage.sh test     # Run tests
./scripts/coverage.sh report   # Generate report

# Specify compiler
./scripts/coverage.sh full gcc    # Use GCC
./scripts/coverage.sh full clang  # Use Clang
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

# Run specific test file
python3 -m pytest tests/test_dynarray.py -v

# Run with coverage (Python-level)
python3 -m pytest tests/ --cov=tests --cov-report=html

# Run in parallel
python3 -m pytest tests/ -n auto

# Generate HTML test report
python3 -m pytest tests/ --html=report.html --self-contained-html
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python3 -m pytest tests/ -v`
6. Check coverage: `./scripts/coverage.sh`
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
