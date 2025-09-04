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
│   ├── algorithm.c         # C90-compliant dynamic array implementation
│   └── main.cpp            # C++ command-line wrapper
├── tests/                  # Python test suite
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── test_utils.py       # Test utilities and helpers
│   └── test_dynarray.py    # Dynamic array tests
├── scripts/                # Build and coverage scripts
│   ├── coverage.sh         # Coverage collection script
│   └── install_deps.sh     # Dependency installation script
├── .github/workflows/      # CI/CD configuration
│   └── ci.yml              # GitHub Actions workflow
├── CMakeLists.txt          # CMake build configuration
├── Makefile                # Make build configuration
└── requirements.txt        # Python dependencies
```

## Quick Start

### Prerequisites

- **C Compiler**: GCC or Clang
- **Python 3.7+**: For running tests
- **Make or CMake**: For building the project

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
   sudo apt-get install build-essential gcc g++ clang cmake lcov python3 python3-pip
   pip3 install pytest pytest-cov pytest-xdist pytest-html coverage
   ```
   
   **On macOS**:
   ```bash
   brew install llvm lcov
   pip3 install pytest pytest-cov pytest-xdist pytest-html coverage
   ```

### Building and Testing

1. **Build the project**:
   ```bash
   make
   ```

2. **Run tests**:
   ```bash
   python3 -m pytest tests/ -v
   ```

3. **Generate coverage report**:
   ```bash
   make coverage
   python3 -m pytest tests/ -v
   make coverage-report
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
   make coverage-clean
   make coverage-build
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

## CI/CD Integration

### GitHub Actions

The project includes a complete GitHub Actions workflow that:

- **Tests on multiple platforms**: Ubuntu and macOS
- **Tests with multiple compilers**: GCC and Clang
- **Generates coverage reports**: For each platform/compiler combination
- **Uploads to Codecov**: Automatic coverage reporting
- **Deploys documentation**: Coverage reports to GitHub Pages
- **Creates releases**: Automated binary releases

### Setting Up CI

1. **Enable GitHub Actions** in your repository settings

2. **Add Codecov integration** (optional):
   - Sign up at [codecov.io](https://codecov.io)
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

## Build Systems

The project supports both Make and CMake:

### Using Make

```bash
# Basic build
make

# Coverage build
make coverage-build

# Generate coverage report
make coverage-report

# Clean
make clean

# Install
make install
```

### Using CMake

```bash
# Configure and build
mkdir build && cd build
cmake .. -DENABLE_COVERAGE=ON
make

# Generate coverage report
make coverage-report
```

## Testing

### Test Structure

The test suite focuses on dynamic array functionality:

- **test_dynarray.py**: Comprehensive dynamic array tests (create, push, pop, get, error handling)
- **test_utils.py**: Test utilities and command execution helpers
- **conftest.py**: pytest configuration and fixtures

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
make clean && make
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
