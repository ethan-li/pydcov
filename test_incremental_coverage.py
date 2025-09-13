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
