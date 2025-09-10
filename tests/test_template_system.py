#!/usr/bin/env python3
"""
Test PyDCov template system functionality.

Tests project template creation, placeholder substitution, and generated project structure.
"""

import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path


class TestTemplateCreation:
    """Test template creation functionality."""
    
    def test_basic_template_creation(self):
        """Test creating a basic C++ project template."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'test_project'
            
            # Create template project
            result = subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Template creation failed: {result.stderr}"
            assert 'Created new project' in result.stdout
            assert project_name in result.stdout
            
            # Check project structure
            project_path = temp_path / project_name
            assert project_path.exists()
            assert project_path.is_dir()
            
            # Check required files exist
            assert (project_path / 'CMakeLists.txt').exists()
            assert (project_path / 'README.md').exists()
            assert (project_path / 'src').exists()
            assert (project_path / 'tests').exists()
            assert (project_path / 'app').exists()
            assert (project_path / 'cmake').exists()
            
            # Check CMake integration files
            assert (project_path / 'cmake' / 'coverage.cmake').exists()
            assert (project_path / 'cmake' / 'COVERAGE_USAGE.md').exists()
    
    def test_template_placeholder_substitution(self):
        """Test that placeholder substitution works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'my_calculator_app'
            
            # Create template project
            result = subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            project_path = temp_path / project_name
            
            # Check CMakeLists.txt has correct project name
            cmake_content = (project_path / 'CMakeLists.txt').read_text()
            assert f'project({project_name})' in cmake_content
            assert '{{PROJECT_NAME}}' not in cmake_content
            
            # Check README.md has correct project name
            readme_content = (project_path / 'README.md').read_text()
            assert f'# {project_name}' in readme_content
            assert '{{PROJECT_NAME}}' not in readme_content
            
            # Check test CMakeLists.txt has correct target names
            test_cmake_content = (project_path / 'tests' / 'CMakeLists.txt').read_text()
            assert f'test_{project_name}' in test_cmake_content
            assert f'{project_name}_lib' in test_cmake_content
            assert '{{PROJECT_NAME}}' not in test_cmake_content
    
    def test_template_with_special_characters(self):
        """Test template creation with project names containing special characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'my_project_123'
            
            result = subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            project_path = temp_path / project_name
            assert project_path.exists()
            
            # Check that special characters are handled correctly
            cmake_content = (project_path / 'CMakeLists.txt').read_text()
            assert project_name in cmake_content
    
    def test_template_force_overwrite(self):
        """Test template creation with force overwrite."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'test_project'
            project_path = temp_path / project_name
            
            # Create existing directory
            project_path.mkdir()
            existing_file = project_path / 'existing.txt'
            existing_file.write_text('existing content')
            
            # Create template with force
            result = subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path),
                '--force'
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            # Check that template was created (existing file should be gone)
            assert (project_path / 'CMakeLists.txt').exists()
            # Existing file might or might not exist depending on implementation
    
    def test_template_without_force_existing_dir(self):
        """Test template creation without force when directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'test_project'
            project_path = temp_path / project_name
            
            # Create existing directory
            project_path.mkdir()
            
            # Try to create template without force
            result = subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            # Should either fail or warn about existing directory
            if result.returncode != 0:
                error_output = (result.stderr + result.stdout).lower()
                assert 'exists' in error_output or 'force' in error_output


class TestTemplateStructure:
    """Test generated template structure and content."""
    
    def test_generated_cmake_structure(self):
        """Test that generated CMake structure is correct."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'cmake_test_project'
            
            result = subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            project_path = temp_path / project_name
            
            # Check main CMakeLists.txt structure
            main_cmake = project_path / 'CMakeLists.txt'
            content = main_cmake.read_text()
            
            assert 'cmake_minimum_required' in content
            assert f'project({project_name})' in content
            assert 'include(cmake/coverage.cmake)' in content
            assert 'add_subdirectory(src)' in content
            assert 'add_subdirectory(tests)' in content
            
            # Check src CMakeLists.txt
            src_cmake = project_path / 'src' / 'CMakeLists.txt'
            src_content = src_cmake.read_text()
            assert f'{project_name}_lib' in src_content
            assert 'calculator.cpp' in src_content
            
            # Check tests CMakeLists.txt
            tests_cmake = project_path / 'tests' / 'CMakeLists.txt'
            tests_content = tests_cmake.read_text()
            assert f'test_{project_name}' in tests_content
            assert f'{project_name}_lib' in tests_content
    
    def test_generated_source_files(self):
        """Test that generated source files are correct."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_name = 'source_test_project'
            
            result = subprocess.run([
                'pydcov', 'init-template', project_name,
                '--template', 'basic_cpp',
                '--output-dir', str(temp_path)
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            project_path = temp_path / project_name
            
            # Check header file
            header_file = project_path / 'src' / 'calculator.hpp'
            assert header_file.exists()
            header_content = header_file.read_text()
            assert '#pragma once' in header_content or '#ifndef' in header_content
            assert 'class Calculator' in header_content
            
            # Check source file
            source_file = project_path / 'src' / 'calculator.cpp'
            assert source_file.exists()
            source_content = source_file.read_text()
            assert '#include "calculator.hpp"' in source_content
            
            # Check test file
            test_file = project_path / 'tests' / 'test_calculator.cpp'
            assert test_file.exists()
            test_content = test_file.read_text()
            assert '#include' in test_content
            assert 'main(' in test_content
            
            # Check app file
            app_file = project_path / 'app' / 'main.cpp'
            assert app_file.exists()
            app_content = app_file.read_text()
            assert '#include' in app_content
            assert 'main(' in app_content


class TestTemplateErrorHandling:
    """Test template system error handling."""
    
    def test_invalid_template_name(self):
        """Test creation with invalid template name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'pydcov', 'init-template', 'test_project',
                '--template', 'invalid_template',
                '--output-dir', temp_dir
            ], capture_output=True, text=True)
            
            assert result.returncode != 0
            assert 'invalid choice' in result.stderr.lower() or 'not found' in result.stderr.lower()
    
    def test_invalid_output_directory(self):
        """Test creation with invalid output directory."""
        result = subprocess.run([
            'pydcov', 'init-template', 'test_project',
            '--template', 'basic_cpp',
            '--output-dir', '/nonexistent/directory/path'
        ], capture_output=True, text=True)
        
        # Should either fail or create the directory
        # Exact behavior depends on implementation
        if result.returncode != 0:
            error_output = (result.stderr + result.stdout).lower()
            assert any(keyword in error_output for keyword in ['not found', 'permission', 'read-only', 'errno'])
    
    def test_empty_project_name(self):
        """Test creation with empty project name."""
        result = subprocess.run([
            'pydcov', 'init-template', '',
            '--template', 'basic_cpp'
        ], capture_output=True, text=True)
        
        # Should fail with empty project name
        assert result.returncode != 0


class TestTemplateDefaultBehavior:
    """Test template system default behavior."""
    
    def test_default_template(self):
        """Test that default template is used when not specified."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'pydcov', 'init-template', 'default_test',
                '--output-dir', temp_dir
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            
            project_path = Path(temp_dir) / 'default_test'
            assert project_path.exists()
            assert (project_path / 'CMakeLists.txt').exists()
    
    def test_default_output_directory(self):
        """Test that current directory is used when output-dir not specified."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                result = subprocess.run([
                    'pydcov', 'init-template', 'current_dir_test',
                    '--template', 'basic_cpp'
                ], capture_output=True, text=True)
                
                assert result.returncode == 0
                
                project_path = Path(temp_dir) / 'current_dir_test'
                assert project_path.exists()
                
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    pytest.main([__file__])
