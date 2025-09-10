# PyDCov Examples and Usage Guide

This document provides detailed examples of how to use the PyDCov project for measuring C code coverage with Python-driven tests, focusing on the dynamic array data structure implementation.

## Basic Usage Examples

### Building and Running

```bash
# Clone and setup
git clone https://github.com/your-username/pydcov.git
cd pydcov

# Build the project
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make
cd ..

# Run all tests (using any testing framework)
python3 -m pytest tests/ -v                    # pytest
python3 -m unittest discover tests/            # unittest
green tests/                                   # green test runner

# Generate coverage report using Python tools
python3 coverage_tools/scripts/coverage.py full tests/ -v
```

## Testing Framework Examples

The PyDCov coverage tools support multiple testing frameworks. Here are examples using different approaches:

### Using pytest (Default)

```bash
# Basic coverage workflow with pytest
python3 coverage_tools/scripts/coverage.py clean
python3 coverage_tools/scripts/coverage.py build
python3 coverage_tools/scripts/coverage.py test tests/
python3 coverage_tools/scripts/coverage.py report

# Complete workflow in one command
python3 coverage_tools/scripts/coverage.py full python -m pytest tests/ -v

# Incremental coverage with pytest
python3 coverage_tools/scripts/incremental_coverage.py init
python3 coverage_tools/scripts/incremental_coverage.py add python -m pytest tests/test_dynarray.py -v
python3 coverage_tools/scripts/incremental_coverage.py add python -m pytest tests/test_statistics.py -k "test_mean"
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report
```

### Using unittest

```bash
# Standard unittest discovery
python3 coverage_tools/scripts/coverage.py test python -m unittest discover tests/
python3 coverage_tools/scripts/coverage.py full python -m unittest discover tests/

# Specific unittest modules
python3 coverage_tools/scripts/incremental_coverage.py add python -m unittest tests.test_dynarray
python3 coverage_tools/scripts/incremental_coverage.py add python -m unittest tests.test_statistics

# Module-specific testing with unittest
python3 coverage_tools/scripts/coverage_modules.py test algorithm --test-command python -m unittest discover algorithm/tests/
python3 coverage_tools/scripts/coverage_modules.py full statistics --test-command python -m unittest discover statistics/tests/
```

### Using Custom Test Scripts

```bash
# Create a custom test script
cat > run_custom_tests.sh << 'EOF'
#!/bin/bash
echo "Running custom test suite..."
python3 -m unittest discover tests/ -v
echo "Running additional validation..."
./build/algorithm_cli --test
./build/statistics_cli --test
EOF
chmod +x run_custom_tests.sh

# Use custom script with coverage tools
python3 coverage_tools/scripts/coverage.py test ./run_custom_tests.sh
python3 coverage_tools/scripts/coverage.py full ./run_custom_tests.sh

# Incremental coverage with custom commands
python3 coverage_tools/scripts/incremental_coverage.py init
python3 coverage_tools/scripts/incremental_coverage.py add ./run_custom_tests.sh
python3 coverage_tools/scripts/incremental_coverage.py add make test
python3 coverage_tools/scripts/incremental_coverage.py merge
python3 coverage_tools/scripts/incremental_coverage.py report
```

### Using Other Testing Frameworks

```bash
# Using green test runner
python3 coverage_tools/scripts/coverage.py test green tests/
python3 coverage_tools/scripts/coverage.py full green tests/ -v

# Using nose2
python3 coverage_tools/scripts/coverage.py test nose2 tests/
python3 coverage_tools/scripts/incremental_coverage.py add nose2 tests/ --verbose

# Using make targets
python3 coverage_tools/scripts/coverage.py test make test
python3 coverage_tools/scripts/coverage.py full make check
```

### Command-Line Interface Examples

The project implements a dynamic array data structure accessible via command-line:

#### Dynamic Array Operations

```bash
# Create a dynamic array
./build/pydcov dynarray create 5             # Output: Array created with capacity 5

# Push values to the array
./build/pydcov dynarray push 10 20 30        # Output: Pushed 3 values. Array size: 3
./build/pydcov dynarray push 40 50           # Output: Pushed 2 values. Array size: 5

# Get values from the array
./build/pydcov dynarray get 0                # Output: 10
./build/pydcov dynarray get 2                # Output: 30
./build/pydcov dynarray get 4                # Output: 50

# Pop values from the array
./build/pydcov dynarray pop                  # Output: 50 (pops 1 value by default)
./build/pydcov dynarray pop 2                # Output: 40 30 (pops 2 values)

# Clean up the array
./build/pydcov dynarray cleanup              # Output: Array cleaned up
```

## Coverage Workflow Examples

### Using the Python Coverage Tools

```bash
# Full automated workflow
python3 coverage_tools/scripts/coverage.py full tests/

# Step-by-step workflow
python3 coverage_tools/scripts/coverage.py clean     # Clean previous coverage data
python3 coverage_tools/scripts/coverage.py build     # Build with coverage instrumentation
python3 coverage_tools/scripts/coverage.py test tests/  # Run tests with coverage collection
python3 coverage_tools/scripts/coverage.py report    # Generate coverage reports

# Check status
python3 coverage_tools/scripts/coverage.py status

# Get help for any command
python3 coverage_tools/scripts/coverage.py help
```

### Manual Coverage Workflow

#### Using GCC and gcov

```bash
# Build with GCC coverage
rm -rf build && mkdir -p build && cd build
CC=gcc CXX=g++ cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
make
cd ..

# Run tests (gcov automatically collects data)
python3 -m pytest tests/ -v

# Generate coverage report
make coverage-report

# View the report
open build/coverage/html/index.html
```

#### Using Clang and llvm-cov

```bash
# Ensure LLVM tools are in PATH (macOS)
export PATH="/opt/homebrew/opt/llvm/bin:$PATH"

# Build with Clang coverage
rm -rf build && mkdir -p build && cd build
CC=clang CXX=clang++ cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
make
cd ..

# Set up coverage data collection
export LLVM_PROFILE_FILE="build/coverage-%p.profraw"

# Run tests
python3 -m pytest tests/ -v

# Generate coverage report
make coverage-report

# View the report
open build/coverage/html/index.html
```

## Test Examples

### Running Specific Tests

```bash
# Run the dynamic array tests
python3 -m pytest tests/test_dynarray.py -v

# Run a specific test function
python3 -m pytest tests/test_dynarray.py::TestDynamicArrayOperations::test_dynarray_create_basic -v

# Run tests with specific markers
python3 -m pytest tests/ -m "not slow" -v

# Run tests in parallel
python3 -m pytest tests/ -n auto -v
```

### Test Output Examples

```bash
# Successful test run
$ python3 -m pytest tests/test_dynarray.py::TestDynamicArrayOperations::test_dynarray_create_basic -v
==================================================== test session starts =====================================================
platform darwin -- Python 3.11.9, pytest-8.4.1, pluggy-1.6.0
collecting ... collected 1 item

tests/test_dynarray.py::TestDynamicArrayOperations::test_dynarray_create_basic PASSED                              [100%]

===================================================== 1 passed in 0.05s ======================================================

# Coverage report summary
$ make coverage-report
Filename                      Regions    Missed Regions     Cover   Functions  Missed Functions  Executed       Lines      Missed Lines     Cover
algorithm.c                       214                18    91.59%          16                 0   100.00%         162                 3    98.15%
main.cpp                          220                20    90.91%          10                 1    90.00%         356                72    79.78%
TOTAL                             434                38    91.24%          26                 1    96.15%         518                75    85.52%
```

## Integration Examples

### Extending the Dynamic Array

1. **Add new function to `src/algorithm.h`**:
   ```c
   int array_size(const dynamic_array_t* arr);
   int array_capacity(const dynamic_array_t* arr);
   ```

2. **Implement in `src/algorithm.c`**:
   ```c
   int array_size(const dynamic_array_t* arr) {
       if (arr == NULL) return -1;
       return arr->size;
   }

   int array_capacity(const dynamic_array_t* arr) {
       if (arr == NULL) return -1;
       return arr->capacity;
   }
   ```

3. **Add CLI support in `src/main.cpp`**:
   ```cpp
   else if (operation == "size") {
       dynamic_array_t* arr = load_array_from_file();
       if (arr == nullptr) {
           std::cerr << "Error: No array created. Use 'dynarray create' first\n";
           return 1;
       }
       std::cout << array_size(arr) << std::endl;
       destroy_array(arr);
   }
   ```

4. **Add tests in `tests/test_dynarray.py`**:
   ```python
   def test_dynarray_size(self):
       """Test getting array size."""
       assert_command_success(["dynarray", "create", "10"])
       assert_command_success(["dynarray", "push", "1", "2", "3"])

       result = assert_command_success(["dynarray", "size"])
       size = int(result.stdout.strip())
       assert size == 3
   ```

### Custom Coverage Targets

You can customize coverage collection for specific scenarios:

```bash
# Test only specific functionality
export LLVM_PROFILE_FILE="build/math-coverage-%p.profraw"
python3 -m pytest tests/test_math.py -v

# Generate focused coverage report
llvm-profdata merge -sparse build/math-coverage-*.profraw -o build/math-coverage.profdata
llvm-cov show build/pydcov -instr-profile=build/math-coverage.profdata -format=html -output-dir=build/math-coverage-html
```

## CI/CD Examples

### GitHub Actions Integration

The project includes a complete CI workflow. Here's how to customize it:

```yaml
# Add a new platform to test matrix
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]  # Add Windows
    compiler: [gcc, clang, msvc]  # Add MSVC for Windows
```

### Local CI Simulation

```bash
# Simulate the CI workflow locally
./scripts/install_deps.sh
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make
cd .. && python3 -m pytest tests/ -v
rm -rf build && mkdir -p build && cd build
cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug && make
cd .. && export LLVM_PROFILE_FILE="build/coverage-%p.profraw"
python3 -m pytest tests/ -v
cd build && make coverage-report
```

This comprehensive example set demonstrates how to use PyDCov for various scenarios, from basic usage to advanced integration and customization.
