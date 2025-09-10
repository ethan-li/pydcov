# Generic Coverage System Usage Guide

## Overview

The refactored `coverage.cmake` module provides a completely generic and reusable code coverage system for C/C++ projects. It automatically detects executable targets and generates coverage reports without requiring hardcoded module names or directory structures.

## Key Features

### ✅ **Automatic Executable Detection**
- Automatically finds all executable targets in your project
- Excludes test executables (patterns: test, tests, testing, gtest, catch, benchmark)
- No manual configuration required for most projects

### ✅ **Manual Registration Support**
- Explicit control over which executables to include in coverage
- Useful for complex projects with specific requirements

### ✅ **Cross-Compiler Support**
- GCC/gcov toolchain support
- Clang/llvm-cov toolchain support
- Automatic tool detection and configuration

### ✅ **Multiple Output Formats**
- HTML reports for interactive viewing
- LCOV format for CI/CD integration
- Comprehensive coverage metrics

## Usage Examples

### 1. Basic Usage (Auto-Detection)

```cmake
# In your root CMakeLists.txt
include(cmake/coverage.cmake)

# Build your project normally
add_executable(my_app src/main.cpp)
add_executable(my_tool src/tool.cpp)

# Coverage will automatically detect and include both executables
```

### 2. Manual Registration

```cmake
# Include coverage system
include(cmake/coverage.cmake)

# Build executables
add_executable(my_app src/main.cpp)
add_executable(my_tool src/tool.cpp)
add_executable(my_test src/test.cpp)  # This would be auto-excluded

# Manually register specific executables for coverage
coverage_add_executable(my_app)
coverage_add_executable(my_tool)
# my_test is intentionally excluded
```

### 3. Automatic Registration via target_link_coverage_libraries

```cmake
# Include coverage system
include(cmake/coverage.cmake)

# Build executable
add_executable(my_app src/main.cpp)

# Link coverage libraries (also auto-registers for coverage)
target_link_coverage_libraries(my_app)
```

## Build Commands

```bash
# Configure with coverage enabled
cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug

# Build the project
make

# Run your executables to generate coverage data
LLVM_PROFILE_FILE="coverage-%p.profraw" ./my_app
LLVM_PROFILE_FILE="coverage-%p.profraw" ./my_tool

# Generate coverage reports
make coverage-report

# Clean coverage data (optional)
make coverage-clean
```

## Output Files

- `build/coverage/html/index.html` - Interactive HTML coverage report
- `build/coverage/coverage.info` - LCOV format for CI/CD tools
- `build/coverage/coverage.profdata` - Raw coverage data (Clang only)

## Migration from Hardcoded Systems

### Before (Hardcoded)
```cmake
# Old hardcoded approach
add_custom_target(coverage-report
    COMMAND llvm-cov show algorithm_cli statistics_cli ...
    DEPENDS algorithm_cli statistics_cli
)
```

### After (Generic)
```cmake
# New generic approach
include(cmake/coverage.cmake)
# Everything else is automatic!
```

## Advanced Configuration

### Custom Executable Detection
```cmake
# Disable auto-detection and use manual registration only
function(coverage_auto_detect_executables)
    # Override with empty implementation
endfunction()

# Then manually register
coverage_add_executable(my_specific_app)
```

### Custom Test Exclusion Patterns
```cmake
# Modify the auto-detection function to use custom patterns
function(coverage_auto_detect_executables)
    get_property(all_targets DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY BUILDSYSTEM_TARGETS)
    
    foreach(target ${all_targets})
        if(TARGET ${target})
            get_target_property(target_type ${target} TYPE)
            if(target_type STREQUAL "EXECUTABLE")
                string(TOLOWER ${target} target_lower)
                # Custom exclusion patterns
                if(NOT target_lower MATCHES "(test|spec|mock|stub)")
                    coverage_add_executable(${target})
                endif()
            endif()
        endif()
    endforeach()
endfunction()
```

## Troubleshooting

### No Executables Found
```
Warning: No executables registered for coverage
```
**Solution**: Ensure your executables are built before coverage configuration, or manually register them.

### LLVM Tools Not Found
```
Error: llvm-profdata not found
```
**Solution**: Install LLVM tools or add them to PATH:
```bash
export PATH="/opt/homebrew/Cellar/llvm/21.1.0/bin:$PATH"
```

### Empty Coverage Reports
**Solution**: Ensure you run your executables with `LLVM_PROFILE_FILE` environment variable set before generating reports.

## Benefits of the Refactored System

1. **Zero Configuration**: Works out of the box for most projects
2. **Maintainable**: No hardcoded module names or paths
3. **Scalable**: Automatically adapts as you add/remove modules
4. **Reusable**: Same coverage.cmake works across different projects
5. **Flexible**: Supports both automatic and manual executable registration
