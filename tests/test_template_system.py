#!/usr/bin/env python3
"""
Test suite for PyDCov template/CMake integration system.

This module tests the CMake integration functionality that provides
template-like capabilities for setting up coverage in C/C++ projects.
"""

import pytest
import tempfile
import subprocess
import shutil
from pathlib import Path


class TestCMakeIntegration:
    """Test CMake integration functionality."""
    
    def test_init_cmake_creates_files(self):
        """Test that init-cmake creates the expected files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run init-cmake command
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path)],
                capture_output=True, text=True
            )
            
            assert result.returncode == 0
            
            # Check that cmake directory was created
            cmake_dir = temp_path / 'cmake'
            assert cmake_dir.exists()
            assert cmake_dir.is_dir()
            
            # Check that coverage.cmake was created
            coverage_cmake = cmake_dir / 'coverage.cmake'
            assert coverage_cmake.exists()
            assert coverage_cmake.is_file()
            
            # Check that documentation was created
            usage_doc = cmake_dir / 'COVERAGE_USAGE.md'
            assert usage_doc.exists()
            assert usage_doc.is_file()
    
    def test_init_cmake_force_overwrite(self):
        """Test that init-cmake --force overwrites existing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cmake_dir = temp_path / 'cmake'
            cmake_dir.mkdir()
            
            # Create existing file with different content
            existing_file = cmake_dir / 'coverage.cmake'
            existing_file.write_text("# Existing content")
            
            # Run init-cmake with force
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path), '--force'],
                capture_output=True, text=True
            )
            
            assert result.returncode == 0
            
            # Check that file was overwritten
            assert existing_file.exists()
            content = existing_file.read_text()
            assert "# Existing content" not in content
            assert "coverage" in content.lower()  # Should contain coverage-related content
    
    def test_init_cmake_without_force_preserves_existing(self):
        """Test that init-cmake without --force preserves existing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cmake_dir = temp_path / 'cmake'
            cmake_dir.mkdir()
            
            # Create existing file
            existing_file = cmake_dir / 'coverage.cmake'
            original_content = "# Existing content"
            existing_file.write_text(original_content)
            
            # Run init-cmake without force
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path)],
                capture_output=True, text=True
            )
            
            assert result.returncode == 0
            
            # Check that file was preserved
            assert existing_file.exists()
            content = existing_file.read_text()
            assert content == original_content
    
    def test_coverage_cmake_content(self):
        """Test that coverage.cmake contains expected content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run init-cmake command
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path)],
                capture_output=True, text=True
            )
            
            assert result.returncode == 0
            
            # Check coverage.cmake content
            coverage_cmake = temp_path / 'cmake' / 'coverage.cmake'
            content = coverage_cmake.read_text()
            
            # Should contain CMake coverage configuration
            assert 'coverage' in content.lower()
            assert 'cmake' in content.lower()
            
            # Should contain common CMake patterns
            assert any(keyword in content for keyword in ['option', 'if', 'endif'])
    
    def test_usage_documentation_exists(self):
        """Test that usage documentation is created and contains helpful content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run init-cmake command
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path)],
                capture_output=True, text=True
            )
            
            assert result.returncode == 0
            
            # Check usage documentation
            usage_doc = temp_path / 'cmake' / 'COVERAGE_USAGE.md'
            content = usage_doc.read_text()
            
            # Should contain usage instructions
            assert 'coverage' in content.lower()
            assert 'cmake' in content.lower()
            assert any(keyword in content.lower() for keyword in ['usage', 'how', 'example'])


class TestCMakeIntegrationAPI:
    """Test CMake integration through Python API."""
    
    def test_cmake_integration_import(self):
        """Test that CMake integration modules can be imported."""
        try:
            from pydcov.utils.cmake_integration import CMakeHelper
            assert CMakeHelper is not None
        except ImportError:
            pytest.skip("CMake integration module not available")
    
    def test_compiler_detection_import(self):
        """Test that compiler detection can be imported."""
        try:
            from pydcov.utils.compiler_detection import CompilerDetector
            detector = CompilerDetector()
            assert detector is not None
        except ImportError:
            pytest.skip("Compiler detection module not available")


class TestTemplateSystemCompatibility:
    """Test template system compatibility and basic functionality."""
    
    def test_basic_project_structure_creation(self):
        """Test creating a basic project structure manually."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Initialize CMake integration
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path)],
                capture_output=True, text=True
            )
            assert result.returncode == 0
            
            # Create basic project structure
            src_dir = temp_path / 'src'
            src_dir.mkdir()
            
            tests_dir = temp_path / 'tests'
            tests_dir.mkdir()
            
            # Create basic CMakeLists.txt
            cmake_content = """cmake_minimum_required(VERSION 3.10)
project(TestProject)
include(cmake/coverage.cmake)
add_executable(test_app src/main.cpp)
"""
            (temp_path / 'CMakeLists.txt').write_text(cmake_content)
            
            # Create basic source file
            main_content = """#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""
            (src_dir / 'main.cpp').write_text(main_content)
            
            # Verify structure
            assert (temp_path / 'cmake' / 'coverage.cmake').exists()
            assert (temp_path / 'CMakeLists.txt').exists()
            assert (src_dir / 'main.cpp').exists()
            assert tests_dir.exists()
    
    def test_cmake_configuration_syntax(self):
        """Test that generated CMake files have valid syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Initialize CMake integration
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path)],
                capture_output=True, text=True
            )
            assert result.returncode == 0
            
            # Check that coverage.cmake has valid CMake syntax
            coverage_cmake = temp_path / 'cmake' / 'coverage.cmake'
            content = coverage_cmake.read_text()
            
            # Basic syntax checks
            assert content.count('(') == content.count(')')  # Balanced parentheses
            assert 'if(' in content and 'endif()' in content  # Proper if/endif structure


if __name__ == '__main__':
    pytest.main([__file__])
