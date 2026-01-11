#!/usr/bin/env python3
"""
Comprehensive test for the specific nested build directory scenario
that was causing the original CMake error.

This test simulates real-world project structures and verifies that
the PathManager and CMakeHelper work correctly with nested builds.
"""

import pytest
import tempfile
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock

from pydcov.utils.path_utils import PathManager
from pydcov.utils.cmake_integration import CMakeHelper
from pydcov.core.incremental_coverage import IncrementalCoverageManager


class TestNestedBuildDirectoryScenario:
    """Test the specific nested build directory scenario that was problematic."""

    def test_original_cmake_error_scenario(self):
        """
        Test the specific scenario that was causing the original CMake error.

        This simulates a project structure like:
        my_project/
        ├── CMakeLists.txt
        ├── src/
        └── build/
            └── Debug/
                ├── CMakeCache.txt
                ├── Makefile
                └── coverage/
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the project structure
            project_dir = Path(temp_dir) / "my_project"
            src_dir = project_dir / "src"
            build_dir = project_dir / "build" / "Debug"

            # Create directories
            src_dir.mkdir(parents=True)
            build_dir.mkdir(parents=True)

            # Create project files
            (project_dir / "CMakeLists.txt").write_text(
                """
cmake_minimum_required(VERSION 3.10)
project(MyProject)

set(CMAKE_CXX_STANDARD 17)

# Enable coverage if requested
if(ENABLE_COVERAGE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --coverage")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} --coverage")
endif()

add_executable(my_app src/main.cpp)
"""
            )

            (src_dir / "main.cpp").write_text(
                """
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""
            )

            # Create CMakeCache.txt with coverage enabled
            cmake_cache = build_dir / "CMakeCache.txt"
            cmake_cache.write_text(
                """
CMAKE_BUILD_TYPE:STRING=Debug
CMAKE_CXX_COMPILER:FILEPATH=/usr/bin/g++
CMAKE_C_COMPILER:FILEPATH=/usr/bin/gcc
PYDCOV_COVERAGE_ENABLED:BOOL=ON
CMAKE_SOURCE_DIR:STATIC={project_dir}
CMAKE_BINARY_DIR:STATIC={build_dir}
""".format(
                    project_dir=project_dir, build_dir=build_dir
                )
            )

            # Create a basic Makefile
            makefile = build_dir / "Makefile"
            makefile.write_text(
                """
all: my_app

my_app:
\t@echo "Building my_app"

clean:
\t@echo "Cleaning"

.PHONY: all clean
"""
            )

            # Test PathManager initialization with nested build directory
            path_manager = PathManager(build_root=build_dir)

            # Verify PathManager works correctly
            assert path_manager.build_root == build_dir.resolve()
            assert (
                path_manager.build_dir == build_dir.resolve()
            )  # Backward compatibility
            assert path_manager.coverage_dir == build_dir.resolve() / "coverage"

            # Verify build directory validation
            assert path_manager.validate_build_dir() is True
            assert path_manager.validate_coverage_build() is True

            # Test CMakeHelper with this structure
            cmake_helper = CMakeHelper(path_manager)

            # Test that CMakeHelper can work with nested structure
            assert cmake_helper.ensure_build_configured() is True

            # Test running targets in nested structure
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=0, stdout="Build successful", stderr=""
                )

                result = cmake_helper.run_target("all")
                assert result is True

                # Verify the command was called with correct working directory
                mock_run.assert_called_with(
                    ["make", "all"],
                    cwd=build_dir.resolve(),
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

    def test_incremental_coverage_with_nested_build(self):
        """Test IncrementalCoverageManager with nested build directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested build structure
            project_dir = Path(temp_dir) / "complex_project"
            build_dir = project_dir / "cmake-build-debug"

            build_dir.mkdir(parents=True)

            # Create CMakeCache.txt with coverage enabled
            cmake_cache = build_dir / "CMakeCache.txt"
            cmake_cache.write_text("PYDCOV_COVERAGE_ENABLED:BOOL=ON\n")

            # Test IncrementalCoverageManager initialization
            # Use is_init_command=True to force using provided build_root
            manager = IncrementalCoverageManager(
                build_root=build_dir, is_init_command=True
            )

            assert manager.path_manager.build_root == build_dir.resolve()
            assert manager.path_manager.validate_build_dir() is True
            assert manager.path_manager.validate_coverage_build() is True

            # Test coverage directory creation
            coverage_dir = manager.path_manager.ensure_coverage_dir()
            assert coverage_dir.exists()
            assert coverage_dir == build_dir.resolve() / "coverage"

            incremental_dir = manager.path_manager.ensure_incremental_dir()
            assert incremental_dir.exists()
            assert incremental_dir == build_dir.resolve() / "coverage" / "incremental"

    def test_auto_detection_in_nested_structure(self):
        """Test auto-detection when running from nested build directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create deeply nested structure
            project_dir = Path(temp_dir) / "project"
            build_dir = project_dir / "out" / "build" / "x64-Debug"

            build_dir.mkdir(parents=True)
            (build_dir / "CMakeCache.txt").write_text(
                "PYDCOV_COVERAGE_ENABLED:BOOL=ON\n"
            )

            original_cwd = os.getcwd()
            try:
                # Change to the nested build directory
                os.chdir(build_dir)

                # PathManager should auto-detect even in deeply nested structure
                path_manager = PathManager(build_root=None)

                assert path_manager.build_root == build_dir.resolve()
                assert path_manager.validate_build_dir() is True
                assert path_manager.validate_coverage_build() is True

                # Test CMakeHelper works with auto-detected path
                cmake_helper = CMakeHelper(path_manager)
                assert cmake_helper.ensure_build_configured() is True

            finally:
                os.chdir(original_cwd)

    def test_multiple_build_configurations(self):
        """Test handling multiple build configurations in the same project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "multi_config_project"

            # Create multiple build configurations
            configs = ["Debug", "Release", "RelWithDebInfo"]

            for config in configs:
                build_dir = project_dir / "build" / config
                build_dir.mkdir(parents=True)

                # Create CMakeCache.txt for each configuration
                cmake_cache = build_dir / "CMakeCache.txt"
                cmake_cache.write_text(
                    f"""
CMAKE_BUILD_TYPE:STRING={config}
PYDCOV_COVERAGE_ENABLED:BOOL=ON
"""
                )

                # Test each configuration independently
                path_manager = PathManager(build_root=build_dir)
                cmake_helper = CMakeHelper(path_manager)

                assert path_manager.validate_build_dir() is True
                assert path_manager.validate_coverage_build() is True
                assert cmake_helper.ensure_build_configured() is True

                # Verify coverage directory is configuration-specific
                coverage_dir = path_manager.ensure_coverage_dir()
                assert coverage_dir == build_dir.resolve() / "coverage"

    def test_error_recovery_scenarios(self):
        """Test error recovery in various problematic scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "error_test_project"

            # Scenario 1: Build directory exists but no CMakeCache.txt
            build_dir_no_cache = project_dir / "build_no_cache"
            build_dir_no_cache.mkdir(parents=True)

            path_manager = PathManager(build_root=build_dir_no_cache)
            assert path_manager.validate_build_dir() is False

            cmake_helper = CMakeHelper(path_manager)
            assert cmake_helper.ensure_build_configured() is False
            assert cmake_helper.run_target("any_target") is False

            # Scenario 2: CMakeCache.txt exists but coverage not enabled
            build_dir_no_coverage = project_dir / "build_no_coverage"
            build_dir_no_coverage.mkdir(parents=True)
            (build_dir_no_coverage / "CMakeCache.txt").write_text(
                "ENABLE_COVERAGE:BOOL=OFF\n"
            )

            path_manager = PathManager(build_root=build_dir_no_coverage)
            assert path_manager.validate_build_dir() is True
            assert path_manager.validate_coverage_build() is False

            cmake_helper = CMakeHelper(path_manager)
            assert cmake_helper.ensure_build_configured() is False

            # Scenario 3: Completely invalid build directory
            invalid_build_dir = project_dir / "nonexistent"

            path_manager = PathManager(build_root=invalid_build_dir)
            assert path_manager.validate_build_dir() is False

            cmake_helper = CMakeHelper(path_manager)
            assert cmake_helper.run_target("any_target") is False


if __name__ == "__main__":
    pytest.main([__file__])
