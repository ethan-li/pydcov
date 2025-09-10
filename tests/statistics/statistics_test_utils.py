#!/usr/bin/env python3
"""
Utility functions for testing the C statistics library.
"""

import subprocess
import os
import sys
import math
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    # This file is in statistics/tests/, so project root is two levels up
    return Path(__file__).parent.parent.parent


def get_statistics_executable_path():
    """Get the path to the compiled statistics CLI executable."""
    project_root = get_project_root()
    
    # Try different possible locations for the new modular structure
    possible_paths = [
        # New modular structure paths
        project_root / "build" / "statistics" / "app" / "statistics_cli",
        project_root / "statistics" / "app" / "statistics_cli",
        project_root / "build" / "Debug" / "statistics" / "app" / "statistics_cli",
        project_root / "build" / "Release" / "statistics" / "app" / "statistics_cli",
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_file():
            return str(path)
    
    # If not found, try to find statistics_cli in PATH
    try:
        result = subprocess.run(["which", "statistics_cli"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        pass
    
    raise FileNotFoundError(
        f"Could not find statistics_cli executable. Tried: {[str(p) for p in possible_paths]}\n"
        "Make sure to build the project first with 'cmake --build build' or 'make'"
    )


def run_statistics_command(args, check=False, **kwargs):
    """
    Run the statistics_cli command with the given arguments.
    
    Args:
        args: List of command arguments (without the executable name)
        check: If True, raise CalledProcessError on non-zero exit
        **kwargs: Additional arguments to pass to subprocess.run
    
    Returns:
        subprocess.CompletedProcess object
    """
    executable = get_statistics_executable_path()
    full_command = [executable] + args
    
    # Set default values for subprocess.run
    defaults = {
        'capture_output': True,
        'text': True,
        'check': check
    }
    defaults.update(kwargs)
    
    try:
        result = subprocess.run(full_command, **defaults)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(full_command)}")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise


def parse_float_list(output_line):
    """Parse a line of space-separated floats."""
    return [float(x) for x in output_line.strip().split()]


def parse_statistics_output(output):
    """
    Parse statistics output and extract values.
    
    Expected format:
    Statistics Summary:
      Count: 5
      Mean: 3.00
      Median: 3.00
      Std Deviation: 1.41
      Min: 1
      Max: 5
    """
    lines = output.strip().split('\n')
    stats = {}
    
    for line in lines:
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            
            # Convert to appropriate type
            if key == 'count':
                stats[key] = int(value)
            elif key in ['mean', 'median', 'std_deviation', 'min', 'max']:
                stats[key] = float(value)
    
    return stats


def assert_statistics_command_success(args, expected_output=None):
    """
    Assert that a statistics command runs successfully and optionally check output.
    
    Args:
        args: Command arguments
        expected_output: Expected stdout (if provided)
    
    Returns:
        subprocess.CompletedProcess object
    """
    result = run_statistics_command(args)
    assert result.returncode == 0, f"Command failed: {args}\nStderr: {result.stderr}"
    
    if expected_output is not None:
        actual_output = result.stdout.strip()
        assert actual_output == str(expected_output), \
            f"Expected '{expected_output}', got '{actual_output}'"
    
    return result


def assert_statistics_command_failure(args):
    """
    Assert that a statistics command fails (returns non-zero exit code).
    
    Args:
        args: Command arguments
    
    Returns:
        subprocess.CompletedProcess object
    """
    result = run_statistics_command(args)
    assert result.returncode != 0, f"Command should have failed: {args}"
    return result


def assert_statistics_close(actual, expected, tolerance=0.01):
    """Assert that statistical values are close within tolerance."""
    assert abs(actual - expected) <= tolerance, \
        f"Expected {expected} ± {tolerance}, got {actual}"


def assert_statistics_dict_close(actual_stats, expected_stats, tolerance=0.01):
    """Assert that statistics dictionaries match within tolerance."""
    for key, expected_value in expected_stats.items():
        assert key in actual_stats, f"Missing statistic: {key}"
        if isinstance(expected_value, (int, float)):
            assert_statistics_close(actual_stats[key], expected_value, tolerance)
        else:
            assert actual_stats[key] == expected_value


def setup_coverage_environment():
    """Set up environment variables for coverage collection."""
    # For Clang coverage
    os.environ['LLVM_PROFILE_FILE'] = str(get_project_root() / "build" / "coverage-%p.profraw")
    
    # For GCC coverage (gcov looks for .gcda files in the same directory as .gcno files)
    # No special environment setup needed for GCC


def cleanup_coverage_files():
    """Clean up coverage files from previous runs."""
    project_root = get_project_root()
    build_dir = project_root / "build"
    
    if build_dir.exists():
        # Remove gcov files
        for gcov_file in build_dir.glob("**/*.gcda"):
            gcov_file.unlink()
        
        # Remove clang coverage files
        for prof_file in build_dir.glob("**/*.profraw"):
            prof_file.unlink()


class StatisticsCoverageContext:
    """Context manager for coverage collection during statistics tests."""
    
    def __enter__(self):
        setup_coverage_environment()
        cleanup_coverage_files()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Coverage files are left for collection by the build system
        pass


# Test data generators
def generate_test_datasets():
    """Generate various test datasets for statistics testing."""
    return {
        'simple': [1, 2, 3, 4, 5],
        'single': [42],
        'negative': [-5, -3, -1, 1, 3, 5],
        'decimal': [1.5, 2.5, 3.5, 4.5, 5.5],
        'large_range': [1, 100, 1000],
        'duplicates': [1, 1, 2, 2, 3, 3],
        'zeros': [0, 0, 0, 1, 2],
        'sorted_asc': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'sorted_desc': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        'random': [7, 2, 9, 1, 5, 8, 3, 6, 4],
    }


def calculate_expected_statistics(data):
    """Calculate expected statistics for a dataset using Python."""
    if not data:
        return None
    
    count = len(data)
    mean_val = sum(data) / count
    sorted_data = sorted(data)
    
    # Median calculation
    if count % 2 == 0:
        median_val = (sorted_data[count // 2 - 1] + sorted_data[count // 2]) / 2
    else:
        median_val = sorted_data[count // 2]
    
    # Standard deviation calculation
    variance = sum((x - mean_val) ** 2 for x in data) / count
    std_dev = math.sqrt(variance)
    
    min_val = min(data)
    max_val = max(data)
    
    return {
        'count': count,
        'mean': mean_val,
        'median': median_val,
        'std_deviation': std_dev,
        'min': min_val,
        'max': max_val
    }
