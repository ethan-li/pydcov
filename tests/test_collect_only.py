"""
Test --collect-only functionality for incremental coverage collection.
"""

import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from pydcov.core.incremental_coverage import IncrementalCoverageManager
from pydcov.utils.config import PyDCovConfig


def test_collect_only_without_test_command(tmp_path):
    """Test that collect_only works without test_command argument."""
    build_dir = tmp_path / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    pydcov_dir = tmp_path / "pydcov_data"

    manager = IncrementalCoverageManager(
        build_root=build_dir, pydcov_dir=pydcov_dir, is_init_command=False
    )

    # Test that collect_only=True works with test_command=None
    # Note: This will fail due to missing coverage files, but should not
    # fail due to missing test_command argument
    try:
        result = manager.add(test_command=None, collect_only=True)
        # If we get here, the function accepted the arguments (likely failed on collection)
        assert True
    except TypeError as e:
        if "required positional argument" in str(e) or "test_command" in str(e):
            assert (
                False
            ), f"collect_only should work with test_command=None, but got: {e}"
        else:
            raise


def test_collect_only_timestamp_filtering():
    """Test that collect_only filters files by modification time."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        build_dir = tmp_path / "build"
        build_dir.mkdir(parents=True, exist_ok=True)

        # Create a minimal CMakeCache.txt to satisfy validation
        cmake_cache = build_dir / "CMakeCache.txt"
        cmake_cache.write_text(
            "CMAKE_BUILD_TYPE=Debug\nPYDCOV_COVERAGE_ENABLED:BOOL=ON\n"
        )

        pydcov_dir = tmp_path / "pydcov_data"

        manager = IncrementalCoverageManager(
            build_root=build_dir, pydcov_dir=pydcov_dir, is_init_command=False
        )

        # Initialize
        assert manager.init()

        # Create a fake .profraw file
        profraw_file = build_dir / "test.profraw"
        profraw_file.write_text("fake coverage data")

        # First collection should collect file
        success = manager.add(test_command=None, collect_only=True)
        assert success

        # Check that file was collected
        add_subdirs = [d for d in pydcov_dir.iterdir() if d.name.startswith("add_")]
        assert len(add_subdirs) == 1

        collected_files = list(add_subdirs[0].glob("*.profraw"))
        assert len(collected_files) == 1

        # Wait a bit
        time.sleep(0.1)

        # Create another .profraw file
        profraw_file2 = build_dir / "test2.profraw"
        profraw_file2.write_text("fake coverage data 2")

        # Second collection should only collect new file
        success = manager.add(test_command=None, collect_only=True)
        assert success

        # Check that we now have two add subdirectories
        add_subdirs = sorted(
            [d for d in pydcov_dir.iterdir() if d.name.startswith("add_")]
        )
        assert len(add_subdirs) == 2

        # The second subdirectory should only have the new file
        second_subdir_files = list(add_subdirs[1].glob("*.profraw"))
        assert len(second_subdir_files) == 1
        assert second_subdir_files[0].name == "test2.profraw"


def test_collect_only_updates_config_timestamp():
    """Test that collect_only updates last_collect_time in config."""
    import os

    # Save original working directory
    orig_cwd = Path.cwd()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a separate project root to avoid config conflicts
        project_root = tmp_path / "project"
        project_root.mkdir(parents=True, exist_ok=True)

        build_dir = project_root / "build"
        build_dir.mkdir(parents=True, exist_ok=True)

        # Create a minimal CMakeCache.txt to satisfy validation
        cmake_cache = build_dir / "CMakeCache.txt"
        cmake_cache.write_text(
            "CMAKE_BUILD_TYPE=Debug\nPYDCOV_COVERAGE_ENABLED:BOOL=ON\n"
        )

        pydcov_dir = project_root / "pydcov_data"

        # Change to project root so PyDCovConfig uses it
        os.chdir(project_root)

        try:
            manager = IncrementalCoverageManager(
                build_root=build_dir, pydcov_dir=pydcov_dir, is_init_command=False
            )

            # Initialize
            assert manager.init()

            # Create a fake .profraw file
            profraw_file = build_dir / "test.profraw"
            profraw_file.write_text("fake coverage data")

            # Get config manager with project root
            config_manager = PyDCovConfig(project_root=project_root)

            # Check that last_collect_time is None initially
            assert config_manager.get_last_collect_time() is None

            # Collect
            success = manager.add(test_command=None, collect_only=True)
            assert success

            # Check that last_collect_time is now set
            last_time = config_manager.get_last_collect_time()
            assert last_time is not None
            assert isinstance(last_time, float)
            assert last_time > 0
        finally:
            # Restore original working directory
            os.chdir(orig_cwd)


def test_cli_collect_only_flag():
    """Test that the --collect-only flag works from CLI."""
    # This is a basic smoke test to ensure the flag is accepted
    result = subprocess.run(
        ["python", "-m", "pydcov.cli", "add", "--collect-only", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--collect-only" in result.stdout


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
