# Setup Guide for Python Coverage Tools

This guide provides detailed setup instructions for the Python-based coverage tools.

## Prerequisites

### Required Software

1. **Python 3.6+**
   ```bash
   # Check Python version
   python3 --version
   
   # Install Python 3 if needed (Ubuntu/Debian)
   sudo apt-get update
   sudo apt-get install python3 python3-pip
   
   # Install Python 3 if needed (macOS with Homebrew)
   brew install python3
   ```

2. **CMake 3.10+**
   ```bash
   # Check CMake version
   cmake --version
   
   # Install CMake if needed
   # Ubuntu/Debian: sudo apt-get install cmake
   # macOS: brew install cmake
   ```

3. **Coverage Tools**
   
   **For GCC/gcov:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install gcc gcov lcov
   
   # macOS
   brew install gcc lcov
   ```
   
   **For Clang/llvm-cov:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install clang llvm
   
   # macOS
   brew install llvm
   ```

### Optional Dependencies

```bash
# Install optional Python packages for development
pip3 install -r coverage_tools/requirements.txt
```

## Installation Steps

### 1. Verify Environment

```bash
# Navigate to project root
cd /path/to/pydcov

# Check that coverage_tools directory exists
ls -la coverage_tools/

# Verify Python tools are executable
ls -la coverage_tools/scripts/*.py
```

### 2. Make Scripts Executable

```bash
# Make all scripts executable
chmod +x coverage_tools/scripts/*.py
chmod +x coverage_tools/scripts/*.sh
```

### 3. Test Basic Functionality

```bash
# Test help commands
python3 coverage_tools/scripts/coverage.py help
python3 coverage_tools/scripts/incremental_coverage.py help
python3 coverage_tools/scripts/coverage_modules.py help
```

### 4. Configure CMake with Python Tools

```bash
# Create build directory
mkdir -p build
cd build

# Configure with Python tools enabled (default)
cmake .. -DENABLE_COVERAGE=ON -DUSE_PYTHON_COVERAGE_TOOLS=ON -DCMAKE_BUILD_TYPE=Debug

# Python tools are enabled by default
# To disable Python tools (not recommended):
# cmake .. -DENABLE_COVERAGE=ON -DUSE_PYTHON_COVERAGE_TOOLS=OFF -DCMAKE_BUILD_TYPE=Debug
```

### 5. Verify Setup

```bash
# Check coverage status
python3 ../coverage_tools/scripts/coverage.py status

# Test basic build
python3 ../coverage_tools/scripts/coverage.py build
```

## Usage Examples

### Standard Coverage Workflow

```bash
# Complete workflow
python3 coverage_tools/scripts/coverage.py full tests/ -v

# Step by step
python3 coverage_tools/scripts/coverage.py clean
python3 coverage_tools/scripts/coverage.py build
python3 coverage_tools/scripts/coverage.py test tests/
python3 coverage_tools/scripts/coverage.py report
```

### Incremental Coverage Workflow

```bash
# Initialize incremental coverage
python3 coverage_tools/scripts/incremental_coverage.py init

# Add coverage from different test runs
python3 coverage_tools/scripts/incremental_coverage.py add algorithm/tests/
python3 coverage_tools/scripts/incremental_coverage.py add statistics/tests/

# Merge and generate final report
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report

# Or do everything at once
python3 coverage_tools/scripts/incremental_coverage.py full tests/
```

### Module-Specific Coverage

```bash
# Generate coverage for specific module
python3 coverage_tools/scripts/coverage_modules.py full algorithm

# Generate coverage for all modules
python3 coverage_tools/scripts/coverage_modules.py full

# Check module status
python3 coverage_tools/scripts/coverage_modules.py status
```

## Integration with Existing Workflows

### Using with Make/CMake

The Python tools work seamlessly with existing CMake targets:

```bash
# CMake targets still work
make coverage-clean
make coverage-report
make coverage-incremental-init
make coverage-incremental-add
make coverage-incremental-merge
make coverage-incremental-report
```

### Advanced Usage

For advanced coverage workflows and customization:

```bash
# Run specific test patterns
python3 coverage_tools/scripts/incremental_coverage.py add tests/ -k "test_create"

# Generate module-specific reports
python3 coverage_tools/scripts/coverage_modules.py generate algorithm

# Check detailed status information
python3 coverage_tools/scripts/coverage.py status
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Coverage
on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install cmake gcc gcov lcov
        pip3 install -r coverage_tools/requirements.txt
    
    - name: Run coverage
      run: |
        python3 coverage_tools/scripts/coverage.py full tests/ -v
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v1
      with:
        file: build/coverage/coverage.info
```

## Troubleshooting

### Common Issues

1. **"python3: command not found"**
   - Install Python 3.6 or later
   - On some systems, use `python` instead of `python3`

2. **"Permission denied" when running scripts**
   ```bash
   chmod +x coverage_tools/scripts/*.py
   ```

3. **"Coverage tools not found"**
   - Install GCC/gcov or Clang/llvm-cov
   - Check that tools are in PATH: `which gcov` or `which llvm-cov`

4. **"CMake configuration failed"**
   ```bash
   # Clean and reconfigure
   rm -rf build/
   mkdir build && cd build
   cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
   ```

5. **"No coverage data found"**
   - Ensure tests are actually running
   - Check that executables are built with coverage flags
   - Verify LLVM_PROFILE_FILE environment variable for Clang

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python3 coverage_tools/scripts/coverage.py -v status
python3 coverage_tools/scripts/coverage.py -v full tests/
```

### Getting Help

```bash
# Show detailed help
python3 coverage_tools/scripts/coverage.py help

# Check current status
python3 coverage_tools/scripts/coverage.py status

# Test with verbose output
python3 coverage_tools/scripts/coverage.py -v build
```

## Advanced Configuration

### Custom Project Root

```bash
python3 coverage_tools/scripts/coverage.py --project-root /custom/path full tests/
```

### Disable Colors

```bash
python3 coverage_tools/scripts/coverage.py --no-colors full tests/
```

### Environment Variables

```bash
# For Clang coverage, you can override the profile file location
export LLVM_PROFILE_FILE="custom_coverage-%p.profraw"
python3 coverage_tools/scripts/coverage.py test tests/
```
