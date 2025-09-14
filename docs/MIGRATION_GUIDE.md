# PyDCov Migration Guide: CMake to Pure Python

This guide helps you migrate from CMake-based coverage targets to PyDCov's pure Python implementation.

## 🎯 Why Migrate?

The pure Python implementation provides:

- **Better Error Handling**: Comprehensive error reporting and validation
- **Cross-Platform Compatibility**: Works consistently across Linux, macOS, and Windows
- **Automatic Executable Detection**: No manual registration required
- **Library Project Support**: Works with library-only projects without executables
- **Unified Workflows**: Single interface for both GCC and Clang toolchains
- **Automatic Incremental Coverage**: All operations use incremental collection by default

## 📋 Migration Checklist

### 1. Command Migration

| **Old CMake Target** | **New Python Command** | **Status** |
|---------------------|------------------------|------------|
| `make coverage-clean` | `pydcov coverage clean` | ✅ Ready |
| `make coverage-report` | `pydcov coverage report` | ✅ Ready |
| `make coverage-detect-executables` | Automatic in `pydcov coverage report` | ✅ Ready |

### 2. Code Migration

#### Before (CMake)
```cmake
# CMakeLists.txt
include(cmake/coverage.cmake)
coverage_add_executable(my_app)
coverage_add_executable(my_tool)
```

```bash
# Build and coverage
mkdir build && cd build
cmake .. -DENABLE_COVERAGE=ON
make
make coverage-clean
make coverage-report
```

#### After (Python)
```cmake
# CMakeLists.txt (optional - only for build configuration)
include(cmake/coverage.cmake)
# No need for coverage_add_executable() - automatic detection
```

```bash
# Build and coverage (new environment variable approach)
mkdir build && cd build
PYDCOV_ENABLE_COVERAGE=1 cmake ..
make

# Use Python commands instead
pydcov coverage clean
pydcov coverage report

# Alternative: legacy CMake option (deprecated but still works)
# cmake .. -DENABLE_COVERAGE=ON
```

### 3. CI/CD Pipeline Migration

#### Before (GitHub Actions)
```yaml
- name: Generate Coverage Report
  run: |
    cd build
    make coverage-clean
    make coverage-report
```

#### After (GitHub Actions)
```yaml
- name: Generate Coverage Report
  env:
    PYDCOV_ENABLE_COVERAGE: 1
  run: |
    pydcov coverage clean
    pydcov coverage report
```

#### Before (GitLab CI)
```yaml
coverage:
  script:
    - cd build
    - make coverage-report
```

#### After (GitLab CI)
```yaml
coverage:
  variables:
    PYDCOV_ENABLE_COVERAGE: 1
  script:
    - pydcov coverage report
```

## 🔧 Advanced Migration Scenarios

### Scenario 1: Custom Executable Registration

**Before**: Manual executable registration
```cmake
coverage_add_executable(custom_app)
coverage_add_executable(special_tool)
```

**After**: Automatic detection with patterns
```bash
# PyDCov automatically detects executables matching patterns:
# *_cli, *_app, *_test, and known executables
pydcov coverage report
```

### Scenario 2: Complex Build Workflows

**Before**: Multi-step CMake workflow
```bash
make coverage-clean
make all
make coverage-report
```

**After**: Unified Python workflow
```bash
pydcov coverage full "make test"
# Or step by step:
pydcov coverage clean
pydcov coverage build
pydcov coverage test "make test"
pydcov coverage report
```

### Scenario 3: Automatic Incremental Coverage

**Before**: Not available in CMake
```bash
# No incremental coverage support
```

**After**: Automatic incremental coverage in all operations
```bash
# Simple workflow - incremental collection happens automatically
pydcov coverage full "pytest tests/"

# Step-by-step - each step uses incremental collection
pydcov coverage clean
pydcov coverage test "pytest tests/unit/"
pydcov coverage test "pytest tests/integration/"  # Adds to existing data
pydcov coverage report  # Generates combined report

# Advanced control when needed
pydcov incremental init
pydcov incremental add "pytest tests/unit/"
pydcov incremental add "pytest tests/integration/"
pydcov incremental report
```

## 🛠️ Troubleshooting Migration

### Issue: "No executables found"

**Solution**: PyDCov uses automatic detection. If your executables don't match standard patterns, they'll still be found in the build directory.

```bash
# Check what executables PyDCov finds
pydcov coverage status

# Force report generation (works with library-only projects)
pydcov coverage report
```

### Issue: "CMake targets still show warnings"

**Solution**: This is expected. CMake targets now show deprecation warnings but still work for backward compatibility.

```bash
# Suppress warnings by migrating to Python commands
pydcov coverage clean  # Instead of make coverage-clean
```

### Issue: "Different coverage results"

**Solution**: The Python implementation may find more coverage data due to better file collection algorithms.

```bash
# Compare results
make coverage-report  # Old method
pydcov coverage report  # New method
```

## 📈 Benefits After Migration

### Immediate Benefits
- ✅ Better error messages and debugging information
- ✅ Cross-platform compatibility
- ✅ No need for manual executable registration
- ✅ Support for library-only projects

### Long-term Benefits
- ✅ Automatic incremental coverage for all operations
- ✅ Future enhancements and improvements
- ✅ Better integration with Python-based CI/CD workflows
- ✅ Simplified maintenance and debugging

## 🔄 Gradual Migration Strategy

You can migrate gradually without breaking existing workflows:

### Phase 1: Test Python Commands
```bash
# Keep using CMake targets for production
make coverage-report

# Test Python commands in parallel
pydcov coverage report
```

### Phase 2: Migrate Non-Critical Workflows
```bash
# Use Python for development
pydcov coverage clean
pydcov coverage report

# Keep CMake for CI/CD temporarily
```

### Phase 3: Full Migration
```bash
# Replace all CMake targets with Python commands
pydcov coverage full "pytest tests/"
```

## 📞 Getting Help

If you encounter issues during migration:

1. **Check the logs**: Python implementation provides detailed logging
2. **Compare outputs**: Run both old and new commands to compare results
3. **File an issue**: [GitHub Issues](https://github.com/ethan-li/pydcov/issues)
4. **Ask questions**: [GitHub Discussions](https://github.com/ethan-li/pydcov/discussions)

## 🎉 Migration Complete!

Once migrated, you'll have access to:
- Pure Python coverage workflows
- Better error handling and debugging
- Incremental coverage tracking
- Cross-platform compatibility
- Future enhancements and features

Welcome to the future of C/C++ coverage analysis with PyDCov! 🚀
