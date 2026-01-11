#!/usr/bin/env python3
"""
Utility functions for testing the C algorithm library.
"""

import subprocess
import os
import sys
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    # This file is in examples/algorithm/tests/, so project root is three levels up
    return Path(__file__).parent.parent.parent.parent


def get_executable_path():
    """Get the path to the compiled algorithm CLI executable."""
    project_root = get_project_root()

    # Try different possible locations for the new examples structure
    possible_paths = [
        # New examples structure paths
        project_root / "build" / "examples" / "algorithm" / "app" / "algorithm_cli",
        project_root / "examples" / "algorithm" / "app" / "algorithm_cli",
        project_root
        / "build"
        / "Debug"
        / "examples"
        / "algorithm"
        / "app"
        / "algorithm_cli",
        project_root
        / "build"
        / "Release"
        / "examples"
        / "algorithm"
        / "app"
        / "algorithm_cli",
        # Legacy modular structure paths
        project_root / "build" / "algorithm" / "app" / "algorithm_cli",
        project_root / "algorithm" / "app" / "algorithm_cli",
        project_root / "build" / "Debug" / "algorithm" / "app" / "algorithm_cli",
        project_root / "build" / "Release" / "algorithm" / "app" / "algorithm_cli",
        # Legacy paths for backward compatibility
        project_root / "build" / "pydcov",
        project_root / "pydcov",
        project_root / "build" / "Debug" / "pydcov",
        project_root / "build" / "Release" / "pydcov",
    ]

    for path in possible_paths:
        if path.exists() and path.is_file():
            return str(path)

    # If not found, try to find algorithm_cli in PATH
    try:
        result = subprocess.run(
            ["which", "algorithm_cli"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        pass

    # Try legacy pydcov in PATH
    try:
        result = subprocess.run(
            ["which", "pydcov"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        pass

    raise FileNotFoundError(
        f"Could not find algorithm_cli executable. Tried: {[str(p) for p in possible_paths]}\n"
        "Make sure to build the project first with 'cmake --build build' or 'make'"
    )


def run_command(args, check=False, **kwargs):
    """
    Run the pydcov command with the given arguments.

    Args:
        args: List of command arguments (without the executable name)
        check: If True, raise CalledProcessError on non-zero exit
        **kwargs: Additional arguments to pass to subprocess.run

    Returns:
        subprocess.CompletedProcess object
    """
    executable = get_executable_path()
    full_command = [executable] + args

    # Set default values for subprocess.run
    defaults = {"capture_output": True, "text": True, "check": check}
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


def parse_int_list(output_line):
    """Parse a line of space-separated integers."""
    return [int(x) for x in output_line.strip().split()]


def assert_command_success(args, expected_output=None):
    """
    Assert that a command runs successfully and optionally check output.

    Args:
        args: Command arguments
        expected_output: Expected stdout (if provided)

    Returns:
        subprocess.CompletedProcess object
    """
    result = run_command(args)
    assert result.returncode == 0, f"Command failed: {args}\nStderr: {result.stderr}"

    if expected_output is not None:
        actual_output = result.stdout.strip()
        assert actual_output == str(
            expected_output
        ), f"Expected '{expected_output}', got '{actual_output}'"

    return result


def assert_command_failure(args):
    """
    Assert that a command fails (returns non-zero exit code).

    Args:
        args: Command arguments

    Returns:
        subprocess.CompletedProcess object
    """
    result = run_command(args)
    assert result.returncode != 0, f"Command should have failed: {args}"
    return result


def setup_coverage_environment():
    """Set up environment variables for coverage collection."""
    # For Clang coverage - ensure coverage directory exists
    project_root = get_project_root()
    coverage_dir = project_root / "build" / "coverage"
    coverage_dir.mkdir(parents=True, exist_ok=True)

    # Set LLVM_PROFILE_FILE to generate unique files per process
    # Using %p (process ID) and %m (module signature) for uniqueness
    os.environ["LLVM_PROFILE_FILE"] = str(coverage_dir / "coverage-%p-%m.profraw")

    # For GCC coverage (gcov looks for .gcda files in the same directory as .gcno files)
    # No special environment setup needed for GCC

    print(f"Coverage environment set up. Files will be written to: {coverage_dir}")


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


class CoverageContext:
    """Context manager for coverage collection during tests."""

    def __enter__(self):
        setup_coverage_environment()
        cleanup_coverage_files()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Coverage files are left for collection by the build system
        pass
