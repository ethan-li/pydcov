# Incremental Coverage Implementation Plan

## Overview

This document outlines the implementation plan for fixing incremental coverage collection in PyDCov. The goal is to ensure that coverage data is properly accumulated across multiple pytest test runs without requiring modifications to existing test code.

## Current Problem

The current implementation has several issues:
1. CMake coverage targets are placeholder implementations that don't actually collect coverage files
2. Coverage file paths are inconsistent between test setup and collection logic
3. No automatic accumulation of coverage data from multiple test executions

## Solution Strategy

Use the existing `%p` (process ID) mechanism to generate unique coverage files for each test execution, then collect all files at once after all tests complete. This approach:
- Prevents coverage data overwrites between test runs
- Requires no changes to existing test code
- Provides a clean separation between testing and coverage collection

## Implementation Steps

### Step 1: Fix CMake Coverage Targets

**File**: `cmake/coverage.cmake`

Replace the placeholder implementations with actual file collection logic:

```cmake
# Add current coverage data to incremental collection
add_custom_target(coverage-incremental-add
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/coverage/incremental
    COMMAND ${CMAKE_COMMAND} -E echo "Collecting all coverage files from build directory..."
    # For Clang: Find and copy all .profraw files
    COMMAND find ${CMAKE_BINARY_DIR} -name "*.profraw" -not -path "*/incremental/*" -exec cp {} ${CMAKE_BINARY_DIR}/coverage/incremental/ \; 2>/dev/null || echo "No profraw files found"
    # For GCC: Find and copy all .gcda files  
    COMMAND find ${CMAKE_BINARY_DIR} -name "*.gcda" -not -path "*/incremental/*" -exec cp {} ${CMAKE_BINARY_DIR}/coverage/incremental/ \; 2>/dev/null || echo "No gcda files found"
    COMMAND ${CMAKE_COMMAND} -E echo "Coverage files collected successfully"
    COMMAND find ${CMAKE_BINARY_DIR}/coverage/incremental -name "*.profraw" -o -name "*.gcda" | wc -l | xargs -I {} echo "Total files collected: {}"
    COMMENT "Collecting all generated coverage files"
)

# Merge all incremental coverage data for Clang
add_custom_target(coverage-incremental-merge
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/coverage
    COMMAND ${CMAKE_COMMAND} -E echo "Merging incremental coverage data..."
    # Check if we have profraw files to merge
    COMMAND bash -c 'if ls ${CMAKE_BINARY_DIR}/coverage/incremental/*.profraw 1> /dev/null 2>&1; then ${LLVM_PROFDATA_EXECUTABLE} merge -sparse ${CMAKE_BINARY_DIR}/coverage/incremental/*.profraw -o ${CMAKE_BINARY_DIR}/coverage/incremental_merged.profdata && echo "Clang coverage data merged successfully"; else echo "No profraw files to merge"; fi'
    # For GCC, just copy gcda files to main coverage directory
    COMMAND bash -c 'if ls ${CMAKE_BINARY_DIR}/coverage/incremental/*.gcda 1> /dev/null 2>&1; then cp ${CMAKE_BINARY_DIR}/coverage/incremental/*.gcda ${CMAKE_BINARY_DIR}/coverage/ && echo "GCC coverage data copied successfully"; else echo "No gcda files to copy"; fi'
    COMMENT "Merging all incremental coverage data"
    DEPENDS coverage-incremental-add
)
```

### Step 2: Fix Coverage File Path Configuration

**File**: `examples/algorithm/tests/algorithm_test_utils.py`

Update the `setup_coverage_environment()` function to ensure consistent file paths:

```python
def setup_coverage_environment():
    """Set up environment variables for coverage collection."""
    # For Clang coverage - ensure coverage directory exists
    project_root = get_project_root()
    coverage_dir = project_root / "build" / "coverage"
    coverage_dir.mkdir(parents=True, exist_ok=True)
    
    # Set LLVM_PROFILE_FILE to generate unique files per process
    # Using %p (process ID) and %m (module signature) for uniqueness
    os.environ['LLVM_PROFILE_FILE'] = str(coverage_dir / "coverage-%p-%m.profraw")
    
    # For GCC coverage (gcov looks for .gcda files in the same directory as .gcno files)
    # No special environment setup needed for GCC
    
    print(f"Coverage environment set up. Files will be written to: {coverage_dir}")
```

### Step 3: Improve Python Incremental Coverage Manager

**File**: `pydcov/core/incremental_coverage.py`

Update the `add()` method and add status reporting:

```python
def add(self, test_command: str | List[str]) -> bool:
    """
    Run tests and add coverage data to incremental collection.

    Args:
        test_command: Test command to execute. Must be specified explicitly.
                     Examples:
                     - "python -m pytest tests/"
                     - ["python", "-m", "unittest", "discover"]
                     - "./run_tests.sh"

    Returns:
        True if successful, False otherwise
    """
    self.logger.step("Running tests and collecting coverage data...")

    # Parse and prepare test command
    if isinstance(test_command, list):
        parsed_command = TestExecutor.parse_test_command(test_command)
    else:
        parsed_command = test_command

    # Ensure build is ready
    if not self.path_manager.validate_coverage_build():
        self.logger.error("Coverage build not configured")
        return False

    # Set up environment for coverage
    env = os.environ.copy()
    compiler = self.compiler_detector.detect_compiler()

    if compiler == 'clang':
        # Set LLVM_PROFILE_FILE for Clang coverage
        coverage_dir = self.path_manager.ensure_coverage_dir()
        env['LLVM_PROFILE_FILE'] = str(coverage_dir / 'coverage-%p-%m.profraw')
        self.logger.info(f"Using Clang coverage with LLVM_PROFILE_FILE={env['LLVM_PROFILE_FILE']}")

    # Execute test command using TestExecutor
    if not self.test_executor.execute_test_command(
        parsed_command,
        env=env,
        timeout=600
    ):
        return False
    
    # Collect all coverage files generated during testing
    if not self.cmake_helper.run_incremental_add():
        self.logger.error("Failed to collect coverage data")
        return False

    # Show collection results
    self._show_collection_status()
    return True

def _show_collection_status(self) -> None:
    """Show status of collected coverage files."""
    incremental_dir = self.path_manager.ensure_incremental_dir()
    
    profraw_files = list(incremental_dir.glob('*.profraw'))
    gcda_files = list(incremental_dir.glob('*.gcda'))
    
    if profraw_files:
        self.logger.info(f"Collected {len(profraw_files)} Clang coverage files")
    if gcda_files:
        self.logger.info(f"Collected {len(gcda_files)} GCC coverage files")
    
    if not profraw_files and not gcda_files:
        self.logger.warning("No coverage files were collected")
```

### Step 4: Create Test Script for Validation

**File**: `test_incremental_coverage.py`

Create a comprehensive test script to validate the implementation:

```python
#!/usr/bin/env python3
"""
Test script to verify incremental coverage collection works correctly.
"""

import subprocess
import sys
from pathlib import Path
import shutil
import os

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd, 
                          capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    return result

def main():
    """Test the incremental coverage workflow."""
    project_root = Path(__file__).parent
    build_dir = project_root / "build"
    
    print("=== Testing Incremental Coverage Collection ===")
    
    # Step 1: Clean and build with coverage
    print("\n1. Building project with coverage...")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    build_dir.mkdir()
    run_command(["cmake", "..", "-DENABLE_COVERAGE=ON"], cwd=build_dir)
    run_command(["make"], cwd=build_dir)
    
    # Step 2: Initialize incremental coverage
    print("\n2. Initializing incremental coverage...")
    run_command(["python3", "-m", "pydcov.cli", "incremental", "init"])
    
    # Step 3: Run tests and collect coverage
    print("\n3. Running tests and collecting coverage...")
    
    # Check if algorithm tests exist
    algorithm_tests = project_root / "examples" / "algorithm" / "tests"
    if algorithm_tests.exists():
        print("Running algorithm tests...")
        run_command(["python3", "-m", "pydcov.cli", "incremental", "add", 
                    "python -m pytest examples/algorithm/tests/ -v"])
    else:
        print("Algorithm tests not found, creating a simple test...")
        # Create a simple test that calls the executable
        test_dir = project_root / "test_temp"
        test_dir.mkdir(exist_ok=True)
        
        test_file = test_dir / "test_simple.py"
        test_file.write_text("""
import subprocess
import pytest
from pathlib import Path
import os

def test_executable_runs():
    # Find the executable
    build_dir = Path(__file__).parent.parent / "build"
    executables = list(build_dir.rglob("*algorithm*"))
    if not executables:
        pytest.skip("No algorithm executable found")
    
    executable = executables[0]
    if executable.is_file() and os.access(executable, os.X_OK):
        result = subprocess.run([str(executable), "--help"], 
                              capture_output=True, text=True)
        # Don't require success, just that it runs
        assert result.returncode in [0, 1]  # Help might return 1
""")
        
        run_command(["python3", "-m", "pydcov.cli", "incremental", "add", 
                    f"python -m pytest {test_dir} -v"])
        
        # Cleanup
        shutil.rmtree(test_dir)
    
    # Step 4: Check collection status
    print("\n4. Checking collection status...")
    coverage_dir = build_dir / "coverage"
    incremental_dir = coverage_dir / "incremental"
    
    if incremental_dir.exists():
        profraw_files = list(incremental_dir.glob("*.profraw"))
        gcda_files = list(incremental_dir.glob("*.gcda"))
        
        print(f"Found {len(profraw_files)} .profraw files")
        print(f"Found {len(gcda_files)} .gcda files")
        
        if profraw_files:
            print("Clang coverage files:")
            for f in profraw_files[:5]:  # Show first 5
                print(f"  {f.name}")
        
        if gcda_files:
            print("GCC coverage files:")
            for f in gcda_files[:5]:  # Show first 5
                print(f"  {f.name}")
        
        if not profraw_files and not gcda_files:
            print("WARNING: No coverage files were collected!")
            return False
    else:
        print("ERROR: Incremental directory not found!")
        return False
    
    # Step 5: Generate report
    print("\n5. Generating incremental coverage report...")
    run_command(["python3", "-m", "pydcov.cli", "incremental", "report"])
    
    # Step 6: Check report was generated
    report_dir = coverage_dir / "incremental_report"
    if report_dir.exists() and (report_dir / "index.html").exists():
        print(f"✅ Success! Coverage report generated at: {report_dir / 'index.html'}")
        return True
    else:
        print("❌ Failed: Coverage report not generated")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## Workflow After Implementation

Once implemented, the incremental coverage workflow will be:

```bash
# 1. Build project with coverage
mkdir -p build && cd build
cmake .. -DENABLE_COVERAGE=ON
make
cd ..

# 2. Initialize incremental coverage
python3 -m pydcov.cli incremental init

# 3. Run tests and collect coverage (can be run multiple times)
python3 -m pydcov.cli incremental add "python -m pytest examples/algorithm/tests/ -v"
python3 -m pydcov.cli incremental add "python -m pytest examples/statistics/tests/ -v"

# 4. Generate final comprehensive report
python3 -m pydcov.cli incremental report

# 5. View results
open build/coverage/incremental_report/index.html
```

## Key Benefits

1. **No Test Code Changes**: Existing test code remains unchanged
2. **Automatic Collection**: Coverage files are automatically collected after test runs
3. **Unique Files**: Each test execution generates unique coverage files (no overwrites)
4. **Comprehensive Reports**: Final report includes coverage from all test runs
5. **Error Handling**: Proper error handling and status reporting

## Testing and Validation

1. Run the test script: `python3 test_incremental_coverage.py`
2. Manually test the workflow with existing test suites
3. Verify that coverage files are properly collected and merged
4. Ensure HTML reports are generated correctly

## Files to Modify

1. `cmake/coverage.cmake` - Fix CMake targets
2. `examples/algorithm/tests/algorithm_test_utils.py` - Fix file paths
3. `pydcov/core/incremental_coverage.py` - Improve collection logic
4. `test_incremental_coverage.py` - New test script

This implementation ensures robust incremental coverage collection without requiring changes to existing test code.