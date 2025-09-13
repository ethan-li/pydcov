# Build-Only Coverage System Usage Guide

> **✅ MIGRATION COMPLETE**: CMake coverage targets have been removed in favor of PyDCov's pure Python implementation.
>
> **Use PyDCov Commands**:
> - `pydcov coverage clean` (replaces make coverage-clean)
> - `pydcov coverage report` (replaces make coverage-report)
> - `pydcov coverage full "test_cmd"` (complete workflow)
>
> The Python implementation provides better error handling, cross-platform compatibility, and automatic executable detection.

## Overview

The `coverage.cmake` module now provides build configuration only for C/C++ projects with coverage support. Coverage file operations have been moved to PyDCov's pure Python implementation.

**Note**: CMake coverage targets have been removed. Use PyDCov commands for coverage operations.

## Key Features

### ✅ **Build Configuration**
- Sets up compiler flags for coverage instrumentation
- Configures coverage libraries for linking
- Creates coverage output directory structure

### ✅ **Executable Registration (Compatibility)**
- Preserves coverage_add_executable() for legacy code
- Automatic executable detection (for compatibility)
- No longer used by Python tools (automatic detection instead)

### ✅ **Cross-Compiler Support**
- GCC/gcov toolchain support
- Clang/llvm-cov toolchain support
- Automatic compiler detection and flag configuration

### ✅ **Python Integration**
- Seamless integration with PyDCov commands
- Automatic PyDCov detection and status reporting
- Migration guidance and compatibility warnings

## Usage Examples

### 1. Basic Build Configuration

```cmake
# In your root CMakeLists.txt
include(cmake/coverage.cmake)

# Build your project normally
add_executable(my_app src/main.cpp)
add_executable(my_tool src/tool.cpp)

# Coverage flags are automatically applied when ENABLE_COVERAGE=ON
```

### 2. Legacy Executable Registration (Optional)

```cmake
# Include coverage system
include(cmake/coverage.cmake)

# Build executables
add_executable(my_app src/main.cpp)
add_executable(my_tool src/tool.cpp)

# Optional: Register executables for compatibility (not used by Python tools)
coverage_add_executable(my_app)
coverage_add_executable(my_tool)
```

### 3. Coverage Library Linking

```cmake
# Include coverage system
include(cmake/coverage.cmake)

# Build executable
add_executable(my_app src/main.cpp)

# Link coverage libraries (for GCC projects)
target_link_coverage_libraries(my_app)
```

## Build and Coverage Workflow

```bash
# Configure with coverage enabled
cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug

# Build the project
make

# Use PyDCov for coverage operations
pydcov coverage clean                    # Clean coverage data
pydcov coverage test "make test"         # Run tests with coverage
pydcov coverage report                   # Generate coverage reports

# Or use the complete workflow
pydcov coverage full "make test"         # Clean, build, test, and report
```

## Output Files

- `build/coverage/html/index.html` - Interactive HTML coverage report
- `build/coverage/coverage.info` - LCOV format for CI/CD tools
- `build/coverage/coverage.profdata` - Raw coverage data (Clang only)

## Migration from CMake Targets

### Before (CMake Targets)
```bash
# Old CMake approach
make coverage-clean
make coverage-report
```

### After (PyDCov Commands)
```bash
# New PyDCov approach
pydcov coverage clean
pydcov coverage report
# Automatic executable detection included!
```

## Advanced Configuration

### Custom Build Configuration
```cmake
# Custom compiler flags (if needed)
if(ENABLE_COVERAGE)
    if(CMAKE_C_COMPILER_ID MATCHES "GNU")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} --coverage -fprofile-arcs -ftest-coverage")
    elseif(CMAKE_C_COMPILER_ID MATCHES "Clang")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fprofile-instr-generate -fcoverage-mapping")
    endif()
endif()
```

### Legacy Executable Registration (Compatibility)
```cmake
# For compatibility with legacy code that expects executable registration
include(cmake/coverage.cmake)

# Manual registration (not used by Python tools)
coverage_add_executable(my_specific_app)
```

## Troubleshooting

### PyDCov Not Found
```
Warning: PyDCov: NOT INSTALLED
```
**Solution**: Install PyDCov:
```bash
pip install pydcov
```

### LLVM Tools Not Found
```
Error: llvm-profdata not found
```
**Solution**: Install LLVM tools or add them to PATH:
```bash
export PATH="/opt/homebrew/Cellar/llvm/21.1.0/bin:$PATH"
```

### Coverage Data Not Generated
**Solution**: Ensure you build with coverage enabled and run tests:
```bash
cmake .. -DENABLE_COVERAGE=ON
make
pydcov coverage test "make test"
```

## Benefits of the Python-Only System

1. **Better Error Handling**: Comprehensive error reporting and validation
2. **Cross-Platform**: Works consistently across Linux, macOS, and Windows
3. **Automatic Detection**: No manual executable registration required
4. **Library Support**: Works with library-only projects without executables
5. **Incremental Coverage**: Advanced incremental coverage tracking capabilities
6. **Unified Workflows**: Single interface for both GCC and Clang toolchains
