# {{PROJECT_NAME}}

A C++ project with PyDCov coverage support.

## Building

```bash
mkdir build && cd build
cmake ..
make
```

## Running

```bash
./{{PROJECT_NAME}}
```

## Testing

```bash
# Run tests
make test

# Or run test executable directly
./test_{{PROJECT_NAME}}
```

## Coverage

This project is configured with PyDCov coverage support.

### Generate Coverage Report

```bash
# Full coverage workflow
pydcov coverage full "make test"

# Or step by step
pydcov coverage clean
pydcov coverage build
pydcov coverage test "make test"
pydcov coverage report
```

### Incremental Coverage

```bash
# Initialize incremental tracking
pydcov incremental init

# Add coverage from different test runs
pydcov incremental add "make test"

# Generate report
pydcov incremental report
```

## Project Structure

```
{{PROJECT_NAME}}/
├── CMakeLists.txt          # Main CMake configuration
├── cmake/
│   └── coverage.cmake      # PyDCov coverage integration
├── src/                    # Library source code
│   ├── calculator.hpp
│   ├── calculator.cpp
│   └── CMakeLists.txt
├── app/                    # Application source code
│   └── main.cpp
├── tests/                  # Test source code
│   ├── test_calculator.cpp
│   └── CMakeLists.txt
└── README.md
```

## Dependencies

- CMake 3.10+
- C++17 compatible compiler
- PyDCov (for coverage analysis)

Install PyDCov:
```bash
pip install pydcov
```
