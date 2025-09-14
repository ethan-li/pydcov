# Coverage Environment Variables

## Overview

PyDCov now supports environment variable-based coverage configuration, making it easier to enable coverage without modifying CMake command lines.

## Environment Variable Configuration

### Primary Method: PYDCOV_ENABLE_COVERAGE

Set the `PYDCOV_ENABLE_COVERAGE` environment variable to enable coverage:

```bash
# Enable coverage
export PYDCOV_ENABLE_COVERAGE=1
cmake ..
make

# Or inline
PYDCOV_ENABLE_COVERAGE=1 cmake ..
```

### Supported Values

The following values enable coverage (case-insensitive):
- `1`
- `ON`
- `TRUE`
- `YES`

Any other value (including `0`, `OFF`, `FALSE`, `NO`) disables coverage.

### Examples

```bash
# Enable coverage - all equivalent
PYDCOV_ENABLE_COVERAGE=1 cmake ..
PYDCOV_ENABLE_COVERAGE=ON cmake ..
PYDCOV_ENABLE_COVERAGE=true cmake ..
PYDCOV_ENABLE_COVERAGE=YES cmake ..

# Disable coverage - all equivalent
PYDCOV_ENABLE_COVERAGE=0 cmake ..
PYDCOV_ENABLE_COVERAGE=OFF cmake ..
PYDCOV_ENABLE_COVERAGE=false cmake ..
cmake ..  # (no environment variable set)
```

## Backward Compatibility

The legacy CMake option `-DENABLE_COVERAGE=ON` is still supported but deprecated:

```bash
# Still works but shows deprecation warning
cmake .. -DENABLE_COVERAGE=ON
```

Output:
```
-- Note: -DENABLE_COVERAGE is deprecated. Use PYDCOV_ENABLE_COVERAGE=1 environment variable instead.
```

## Benefits

1. **Simplified Build Commands**: No need to remember CMake option syntax
2. **Environment Integration**: Works well with CI/CD systems and shell scripts
3. **Consistent Naming**: Uses the `PYDCOV_` prefix for clear identification
4. **Backward Compatible**: Existing scripts continue to work

## Migration Guide

### Before (CMake Option)
```bash
mkdir build && cd build
cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
make
```

### After (Environment Variable)
```bash
mkdir build && cd build
PYDCOV_ENABLE_COVERAGE=1 cmake .. -DCMAKE_BUILD_TYPE=Debug
make
```

### Shell Script Integration
```bash
#!/bin/bash
export PYDCOV_ENABLE_COVERAGE=1
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
make
pydcov init
pydcov add python -m pytest ../tests/
pydcov report
```

### CI/CD Integration
```yaml
# GitHub Actions example
env:
  PYDCOV_ENABLE_COVERAGE: 1
  
steps:
  - name: Configure
    run: cmake .. -DCMAKE_BUILD_TYPE=Debug
  - name: Build
    run: make
  - name: Test with Coverage
    run: |
      pydcov init
      pydcov add python -m pytest tests/
      pydcov report
```

## Implementation Details

The environment variable is checked first, with fallback to the CMake option for backward compatibility:

1. If `PYDCOV_ENABLE_COVERAGE` is set, use its value
2. Otherwise, check for the legacy `ENABLE_COVERAGE` CMake option
3. If neither is set, coverage is disabled

This ensures smooth migration while maintaining full backward compatibility.
