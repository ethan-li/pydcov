# PyDCov CMake Integration Usage

This document explains how to use the PyDCov CMake integration files in your C/C++ project.

## Quick Setup

1. **Copy integration files** to your project:
   ```bash
   pydcov init-cmake
   ```

2. **Include in CMakeLists.txt**:
   ```cmake
   include(cmake/coverage.cmake)
   ```

3. **Build with coverage**:
   ```bash
   mkdir build && cd build
   cmake ..
   make
   ```

4. **Run incremental coverage**:
   ```bash
   pydcov init
   pydcov add make test
   pydcov report
   ```

## What's Included

### coverage.cmake

The main CMake module that provides:

- **Automatic compiler detection** (GCC/Clang)
- **Coverage flag configuration** for C/C++ targets
- **Cross-platform support** (Linux, macOS, Windows)
- **Integration with PyDCov** incremental coverage system

### Automatic Features

When you include `coverage.cmake`, it automatically:

1. **Detects your compiler** and sets appropriate coverage flags
2. **Configures build targets** with coverage instrumentation
3. **Sets up environment** for PyDCov coverage collection
4. **Provides compatibility** with both GCC/gcov and Clang/llvm-cov

## Usage Patterns

### Basic Usage

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

# Include PyDCov coverage support
include(cmake/coverage.cmake)

# Your targets will automatically get coverage flags
add_executable(my_app src/main.cpp)
add_library(my_lib src/library.cpp)
```

### With Testing

```cmake
# Enable testing
enable_testing()

# Add test executable
add_executable(my_tests tests/test_main.cpp)
target_link_libraries(my_tests my_lib)

# Add test
add_test(NAME my_tests COMMAND my_tests)
```

### Coverage Workflow

```bash
# Build with coverage
mkdir build && cd build
cmake ..
make

# Run incremental coverage collection
pydcov init                    # Initialize tracking
pydcov add make test           # Run tests and collect coverage
pydcov report                  # Generate HTML report
```

## Advanced Configuration

### Custom Compiler Flags

The coverage.cmake module automatically sets appropriate flags, but you can customize:

```cmake
# Before including coverage.cmake
set(COVERAGE_COMPILE_FLAGS "--coverage -fprofile-arcs -ftest-coverage")
set(COVERAGE_LINK_FLAGS "--coverage")

include(cmake/coverage.cmake)
```

### Selective Coverage

To enable coverage only for specific targets:

```cmake
include(cmake/coverage.cmake)

# Only enable coverage for library, not main executable
add_library(my_lib src/library.cpp)
# my_lib automatically gets coverage flags

add_executable(my_app src/main.cpp)
# Remove coverage flags from main app if needed
target_compile_options(my_app PRIVATE -fno-profile-arcs -fno-test-coverage)
```

## Troubleshooting

### "Coverage tools not found"

Ensure you have the required tools installed:

**For GCC:**
```bash
# Ubuntu/Debian
sudo apt-get install gcc gcov lcov

# macOS
brew install gcc lcov
```

**For Clang:**
```bash
# Ubuntu/Debian
sudo apt-get install clang llvm

# macOS
brew install llvm
```

### "No coverage data generated"

1. Verify coverage flags are applied: `make VERBOSE=1`
2. Check that tests actually run: `make test`
3. Ensure executables are built with coverage: check for `.gcno` or `.profraw` files

### "CMake configuration failed"

1. Verify CMake version: `cmake --version` (requires 3.10+)
2. Check include path: ensure `include(cmake/coverage.cmake)` is correct
3. Verify file exists: `ls cmake/coverage.cmake`

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Setup coverage
  run: pydcov init-cmake

- name: Build with coverage
  run: |
    mkdir build && cd build
    cmake ..
    make

- name: Run coverage
  run: |
    pydcov init
    pydcov add make test
    pydcov merge
    pydcov report
```

### GitLab CI

```yaml
coverage:
  script:
    - pydcov init-cmake
    - mkdir build && cd build
    - cmake ..
    - make
    - pydcov init
    - pydcov add make test
    - pydcov merge
    - pydcov report
```

## Support

For more information:
- [PyDCov Documentation](https://github.com/ethan-li/pydcov)
- [Issue Tracker](https://github.com/ethan-li/pydcov/issues)
