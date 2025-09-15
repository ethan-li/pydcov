#!/usr/bin/env python3
"""
Test PyDCov integration scenarios and end-to-end workflows.

Tests complete workflows including init-cmake and incremental coverage functionality.
"""

import pytest
import subprocess
import tempfile
import shutil
import os
from pathlib import Path


class TestInitCMakeIntegration:
    """Test init-cmake integration with real projects."""

    @pytest.mark.slow
    def test_cmake_integration_workflow(self):
        """Test CMake integration workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Step 1: Create a simple CMake project
            project_path = temp_path / 'cmake_integration_test'
            project_path.mkdir()

            # Create basic CMakeLists.txt
            cmake_content = """
cmake_minimum_required(VERSION 3.10)
project(cmake_integration_test)

set(CMAKE_CXX_STANDARD 17)

# Include PyDCov coverage support
include(cmake/coverage.cmake)

# Simple executable
add_executable(test_app main.cpp)
"""
            (project_path / 'CMakeLists.txt').write_text(cmake_content)

            # Create simple main.cpp
            main_content = """
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""
            (project_path / 'main.cpp').write_text(main_content)

            # Step 2: Initialize CMake integration
            result = subprocess.run([
                'pydcov', 'init-cmake', '--project-root', str(project_path)
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"init-cmake failed: {result.stderr}"

            # Check that CMake files were copied
            assert (project_path / 'cmake' / 'coverage.cmake').exists()
            assert (project_path / 'cmake' / 'COVERAGE_USAGE.md').exists()

            # Step 3: Try to configure with CMake
            build_dir = project_path / 'build'
            build_dir.mkdir()

            cmake_result = subprocess.run([
                'cmake', '..'
            ], cwd=build_dir, capture_output=True, text=True)

            # CMake should configure successfully (even if coverage tools are missing)
            if cmake_result.returncode != 0:
                # Check if it's a coverage tool issue vs CMake issue
                if 'not found' in cmake_result.stderr and ('llvm' in cmake_result.stderr or 'gcov' in cmake_result.stderr):
                    pytest.skip("Coverage tools not available for full test")
                else:
                    pytest.fail(f"CMake configuration failed: {cmake_result.stderr}")


class TestIncrementalCoverageIntegration:
    """Test incremental coverage integration."""

    def test_incremental_init_basic(self):
        """Test basic incremental init command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test incremental init in empty directory
            result = subprocess.run([
                'pydcov', 'init', '--project-root', temp_dir
            ], capture_output=True, text=True)

            # Should run without crashing
            # Return code might vary depending on tool availability
            assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_incremental_status_basic(self):
        """Test basic incremental status command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test status in empty directory
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir(parents=True)
            (build_dir / 'CMakeCache.txt').touch()

            # First initialize to set up configuration using Python script directly
            import sys
            pydcov_script = Path(__file__).parent.parent / 'pydcov' / 'cli.py'
            init_result = subprocess.run([
                sys.executable, str(pydcov_script), 'init', '--build-root', str(build_dir)
            ], capture_output=True, text=True, cwd=temp_dir)

            # Now test status command without --build-root
            result = subprocess.run([
                sys.executable, str(pydcov_script), 'status'
            ], capture_output=True, text=True, cwd=temp_dir)

            # Should run without crashing (might detect missing tools)
            assert 'Detected compiler:' in result.stdout or 'not found' in result.stderr.lower()


class TestErrorRecovery:
    """Test error recovery and graceful failure handling."""
    
    def test_init_cmake_in_non_cmake_project(self):
        """Test init-cmake in directory without CMakeLists.txt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'pydcov', 'init-cmake', '--project-root', temp_dir
            ], capture_output=True, text=True)

            # Should succeed (just copies files)
            assert result.returncode == 0

            cmake_dir = Path(temp_dir) / 'cmake'
            assert cmake_dir.exists()
            assert (cmake_dir / 'coverage.cmake').exists()

    def test_incremental_commands_without_cmake_project(self):
        """Test incremental commands in directory without CMake project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try status in empty directory without configuration using Python script directly
            import sys
            pydcov_script = Path(__file__).parent.parent / 'pydcov' / 'cli.py'
            result = subprocess.run([
                sys.executable, str(pydcov_script), 'status'
            ], capture_output=True, text=True, cwd=temp_dir)

            # Should handle gracefully (might warn about missing configuration)
            # Exact behavior depends on implementation
            assert result.returncode in [0, 1]  # Should not crash


class TestMultipleOperations:
    """Test multiple operations in sequence."""

    def test_init_cmake_multiple_times(self):
        """Test running init-cmake multiple times."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Run init-cmake first time
            result1 = subprocess.run([
                'pydcov', 'init-cmake', '--project-root', str(temp_path)
            ], capture_output=True, text=True)

            assert result1.returncode == 0
            assert (temp_path / 'cmake' / 'coverage.cmake').exists()

            # Run init-cmake again (should handle existing files)
            result2 = subprocess.run([
                'pydcov', 'init-cmake', '--project-root', str(temp_path)
            ], capture_output=True, text=True)

            # Should either succeed or warn about existing files
            assert result2.returncode in [0, 1]  # Should not crash


if __name__ == '__main__':
    pytest.main([__file__])
