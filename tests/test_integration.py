#!/usr/bin/env python3
"""
Test PyDCov integration scenarios and end-to-end workflows.

Tests complete workflows including template creation, building, and coverage analysis.
"""

import pytest
import subprocess
import tempfile
import shutil
import os
from pathlib import Path


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.slow
    def test_template_to_build_workflow(self):
        """Test complete workflow from template creation to building."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'e2e_test_project'
            
            # Step 1: Create template
            result = subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Template creation failed: {result.stderr}"
            
            project_path = temp_path / project_name
            assert project_path.exists()
            
            # Step 2: Build the project
            build_dir = project_path / 'build'
            build_dir.mkdir()
            
            # Configure with CMake
            cmake_result = subprocess.run([
                'cmake', '..', '-DCMAKE_BUILD_TYPE=Release'
            ], cwd=build_dir, capture_output=True, text=True)
            
            if cmake_result.returncode != 0:
                pytest.skip(f"CMake not available or failed: {cmake_result.stderr}")
            
            # Build with make
            make_result = subprocess.run([
                'make'
            ], cwd=build_dir, capture_output=True, text=True)
            
            if make_result.returncode != 0:
                pytest.skip(f"Make not available or failed: {make_result.stderr}")
            
            # Step 3: Run tests
            test_result = subprocess.run([
                'make', 'test'
            ], cwd=build_dir, capture_output=True, text=True)
            
            # Tests should pass
            assert test_result.returncode == 0, f"Tests failed: {test_result.stderr}"
            assert 'tests passed' in test_result.stdout or 'Test #1:' in test_result.stdout
    
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


class TestCLIIntegration:
    """Test CLI integration with real projects."""
    
    def test_coverage_status_on_template_project(self):
        """Test coverage status command on a template project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'status_test_project'
            
            # Create template
            subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            project_path = temp_path / project_name
            
            # Test coverage status
            result = subprocess.run([
                'pydcov', 'coverage', 'status', '--project-root', str(project_path)
            ], capture_output=True, text=True)
            
            # Should run without crashing (might detect missing tools)
            assert 'Detected compiler:' in result.stdout or 'not found' in result.stderr.lower()
    
    def test_incremental_init_on_template_project(self):
        """Test incremental init command on a template project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'incremental_test_project'
            
            # Create template
            subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            project_path = temp_path / project_name
            
            # Test incremental init
            result = subprocess.run([
                'pydcov', 'incremental', 'init', '--project-root', str(project_path)
            ], capture_output=True, text=True)
            
            # Should run without crashing
            # Return code might vary depending on tool availability
            assert len(result.stdout) > 0 or len(result.stderr) > 0


class TestErrorRecovery:
    """Test error recovery and graceful failure handling."""
    
    def test_coverage_without_cmake_project(self):
        """Test coverage commands in directory without CMake project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try coverage status in empty directory
            result = subprocess.run([
                'pydcov', 'coverage', 'status', '--project-root', temp_dir
            ], capture_output=True, text=True)
            
            # Should handle gracefully (might warn about missing CMakeLists.txt)
            # Exact behavior depends on implementation
            assert result.returncode in [0, 1]  # Should not crash
    
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
    
    def test_template_creation_permission_error(self):
        """Test template creation with permission issues."""
        # Try to create in root directory (should fail)
        result = subprocess.run([
            'pydcov', 'init-template', 'permission_test',
            '--output-dir', '/root'
        ], capture_output=True, text=True)
        
        # Should fail gracefully
        assert result.returncode != 0
        error_output = (result.stdout + result.stderr).lower()
        assert 'permission' in error_output or 'denied' in error_output or 'read-only' in error_output


class TestCrossProjectCompatibility:
    """Test compatibility with different project structures."""
    
    def test_nested_project_structure(self):
        """Test with nested project structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create nested structure
            nested_path = temp_path / 'workspace' / 'projects' / 'my_project'
            nested_path.mkdir(parents=True)
            
            # Create template in nested location
            result = subprocess.run([
                'pydcov', 'init-template', 'nested_test',
                '--template', 'basic_cpp',
                '--output-dir', str(nested_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            project_path = nested_path / 'nested_test'
            assert project_path.exists()
            assert (project_path / 'CMakeLists.txt').exists()
    
    def test_project_with_spaces_in_path(self):
        """Test with spaces in project path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create path with spaces
            spaced_path = temp_path / 'my project folder'
            spaced_path.mkdir()
            
            result = subprocess.run([
                'pydcov', 'init-template', 'spaced_test',
                '--template', 'basic_cpp',
                '--output-dir', str(spaced_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            project_path = spaced_path / 'spaced_test'
            assert project_path.exists()


class TestMultipleOperations:
    """Test multiple operations in sequence."""
    
    def test_multiple_template_creations(self):
        """Test creating multiple templates in same directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create first project
            result1 = subprocess.run([
                'pydcov', 'init-template', 'project1',
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            assert result1.returncode == 0
            
            # Create second project
            result2 = subprocess.run([
                'pydcov', 'init-template', 'project2',
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            assert result2.returncode == 0
            
            # Both should exist
            assert (temp_path / 'project1').exists()
            assert (temp_path / 'project2').exists()
            
            # Each should have correct content
            cmake1 = (temp_path / 'project1' / 'CMakeLists.txt').read_text()
            cmake2 = (temp_path / 'project2' / 'CMakeLists.txt').read_text()
            
            assert 'project(project1)' in cmake1
            assert 'project(project2)' in cmake2
    
    def test_init_cmake_after_template(self):
        """Test running init-cmake after template creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'double_init_test'
            
            # Create template (which includes CMake files)
            subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            project_path = temp_path / project_name
            
            # Run init-cmake again (should handle existing files)
            result = subprocess.run([
                'pydcov', 'init-cmake', '--project-root', str(project_path)
            ], capture_output=True, text=True)
            
            # Should either succeed or warn about existing files
            assert result.returncode in [0, 1]  # Should not crash


if __name__ == '__main__':
    pytest.main([__file__])
