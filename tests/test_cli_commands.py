#!/usr/bin/env python3
"""
Test PyDCov CLI commands and interface.

Tests all CLI commands, subcommands, help text, and error handling.
"""

import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path


class TestCLIBasicCommands:
    """Test basic CLI commands that don't require external tools."""
    
    def test_main_help(self):
        """Test main help command."""
        result = subprocess.run(['pydcov', '--help'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'usage:' in result.stdout
        assert 'PyDCov' in result.stdout
        assert 'coverage' in result.stdout
        assert 'incremental' in result.stdout
        assert 'init-cmake' in result.stdout
        assert 'init-template' in result.stdout
    
    def test_version_command(self):
        """Test version command."""
        result = subprocess.run(['pydcov', '--version'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'PyDCov' in result.stdout
        # Should match semantic versioning pattern
        import re
        version_pattern = r'\d+\.\d+\.\d+'
        assert re.search(version_pattern, result.stdout)
    
    def test_coverage_help(self):
        """Test coverage subcommand help."""
        result = subprocess.run(['pydcov', 'coverage', '--help'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'usage:' in result.stdout
        assert 'clean' in result.stdout
        assert 'build' in result.stdout
        assert 'test' in result.stdout
        assert 'report' in result.stdout
        assert 'full' in result.stdout
        assert 'status' in result.stdout
    
    def test_incremental_help(self):
        """Test incremental subcommand help."""
        result = subprocess.run(['pydcov', 'incremental', '--help'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'usage:' in result.stdout
        assert 'init' in result.stdout
        assert 'add' in result.stdout
        assert 'merge' in result.stdout
        assert 'report' in result.stdout
        assert 'status' in result.stdout
        assert 'clean' in result.stdout
    
    def test_init_cmake_help(self):
        """Test init-cmake subcommand help."""
        result = subprocess.run(['pydcov', 'init-cmake', '--help'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'usage:' in result.stdout
        assert 'CMake integration' in result.stdout
    
    def test_init_template_help(self):
        """Test init-template subcommand help."""
        result = subprocess.run(['pydcov', 'init-template', '--help'], capture_output=True, text=True)
        assert result.returncode == 0
        assert 'usage:' in result.stdout
        assert 'project_name' in result.stdout
        assert 'template' in result.stdout


class TestCLIErrorHandling:
    """Test CLI error handling and validation."""
    
    def test_invalid_command(self):
        """Test invalid command handling."""
        result = subprocess.run(['pydcov', 'invalid-command'], capture_output=True, text=True)
        assert result.returncode != 0
        assert 'invalid choice' in result.stderr.lower() or 'unrecognized' in result.stderr.lower()
    
    def test_coverage_missing_args(self):
        """Test coverage command with missing arguments."""
        # Test 'test' command without test arguments
        result = subprocess.run(['pydcov', 'coverage', 'test'], capture_output=True, text=True)
        assert result.returncode != 0
    
    def test_incremental_missing_args(self):
        """Test incremental command with missing arguments."""
        # Test 'add' command without test arguments
        result = subprocess.run(['pydcov', 'incremental', 'add'], capture_output=True, text=True)
        assert result.returncode != 0
    
    def test_init_template_missing_args(self):
        """Test init-template command with missing arguments."""
        result = subprocess.run(['pydcov', 'init-template'], capture_output=True, text=True)
        assert result.returncode != 0
        assert 'required' in result.stderr.lower() or 'project_name' in result.stderr


class TestInitCMakeCommand:
    """Test init-cmake command functionality."""
    
    def test_init_cmake_basic(self):
        """Test basic init-cmake functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run init-cmake in temporary directory
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path)],
                capture_output=True, text=True
            )
            
            assert result.returncode == 0
            assert 'Copied coverage.cmake' in result.stdout
            assert 'Copied COVERAGE_USAGE.md' in result.stdout
            
            # Check that files were created
            cmake_dir = temp_path / 'cmake'
            assert cmake_dir.exists()
            assert (cmake_dir / 'coverage.cmake').exists()
            assert (cmake_dir / 'COVERAGE_USAGE.md').exists()
    
    def test_init_cmake_force_overwrite(self):
        """Test init-cmake with force overwrite."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cmake_dir = temp_path / 'cmake'
            cmake_dir.mkdir()
            
            # Create existing file
            existing_file = cmake_dir / 'coverage.cmake'
            existing_file.write_text('# Existing content')
            
            # Run init-cmake with force
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path), '--force'],
                capture_output=True, text=True
            )
            
            assert result.returncode == 0
            
            # Check that file was overwritten
            content = existing_file.read_text()
            assert '# Existing content' not in content
            assert 'cmake_minimum_required' in content or 'Coverage' in content
    
    def test_init_cmake_existing_files_no_force(self):
        """Test init-cmake with existing files without force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cmake_dir = temp_path / 'cmake'
            cmake_dir.mkdir()
            
            # Create existing file
            existing_file = cmake_dir / 'coverage.cmake'
            existing_file.write_text('# Existing content')
            
            # Run init-cmake without force
            result = subprocess.run(
                ['pydcov', 'init-cmake', '--project-root', str(temp_path)],
                capture_output=True, text=True
            )
            
            # Should either succeed (if it handles existing files) or warn
            # The exact behavior depends on implementation
            if result.returncode != 0:
                assert 'exists' in result.stderr.lower() or 'force' in result.stderr.lower()


class TestCoverageStatusCommand:
    """Test coverage status command (doesn't require coverage tools)."""
    
    def test_coverage_status_basic(self):
        """Test basic coverage status command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ['pydcov', 'coverage', 'status', '--project-root', temp_dir],
                capture_output=True, text=True
            )
            
            # Status command should run (might detect missing tools)
            # Return code might be 0 or non-zero depending on tool availability
            assert ('Detected compiler' in result.stdout or
                    'not found' in result.stderr.lower() or
                    'Build directory not found' in result.stdout)


class TestIncrementalStatusCommand:
    """Test incremental status command (doesn't require coverage tools)."""
    
    def test_incremental_status_basic(self):
        """Test basic incremental status command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ['pydcov', 'incremental', 'status', '--project-root', temp_dir],
                capture_output=True, text=True
            )
            
            # Status command should run (might detect missing tools)
            # Return code might be 0 or non-zero depending on tool availability
            assert 'Detected compiler:' in result.stdout or 'not found' in result.stderr.lower()


class TestCLIVerboseMode:
    """Test CLI verbose mode functionality."""

    def test_coverage_verbose(self):
        """Test coverage command with verbose flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ['pydcov', 'coverage', 'status', '--verbose', '--project-root', temp_dir],
                capture_output=True, text=True
            )

            # Verbose mode should provide more output
            # Exact content depends on implementation
            assert len(result.stdout) > 0 or len(result.stderr) > 0

    def test_incremental_verbose(self):
        """Test incremental command with verbose flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ['pydcov', 'incremental', 'status', '--verbose', '--project-root', temp_dir],
                capture_output=True, text=True
            )

            # Verbose mode should provide more output
            assert len(result.stdout) > 0 or len(result.stderr) > 0


class TestCLIPathHandling:
    """Test CLI path handling robustness."""

    def test_init_template_without_output_dir(self):
        """Test init-template command without specifying output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory to test current directory handling
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                result = subprocess.run([
                    'pydcov', 'init-template', 'path_test_project',
                    '--template', 'basic_cpp'
                ], capture_output=True, text=True)

                assert result.returncode == 0, f"Command failed: {result.stdout} {result.stderr}"
                assert 'Created new project' in result.stdout

                # Check that project was created in current directory
                project_path = Path(temp_dir) / 'path_test_project'
                assert project_path.exists()
                assert (project_path / 'CMakeLists.txt').exists()

            finally:
                os.chdir(original_cwd)

    def test_init_cmake_without_project_root(self):
        """Test init-cmake command without specifying project root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                result = subprocess.run([
                    'pydcov', 'init-cmake'
                ], capture_output=True, text=True)

                assert result.returncode == 0, f"Command failed: {result.stdout} {result.stderr}"
                assert 'Copied coverage.cmake' in result.stdout

                # Check that cmake files were created in current directory
                cmake_dir = Path(temp_dir) / 'cmake'
                assert cmake_dir.exists()
                assert (cmake_dir / 'coverage.cmake').exists()

            finally:
                os.chdir(original_cwd)

    def test_path_handling_with_none_values(self):
        """Test that path handling gracefully handles None values."""
        # This test simulates the CI environment issue where paths might be None
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with explicit output directory to ensure robustness
            result = subprocess.run([
                'pydcov', 'init-template', 'none_test_project',
                '--template', 'basic_cpp',
                '--output-dir', temp_dir
            ], capture_output=True, text=True)

            assert result.returncode == 0, f"Command failed: {result.stdout} {result.stderr}"

            project_path = Path(temp_dir) / 'none_test_project'
            assert project_path.exists()
            assert (project_path / 'CMakeLists.txt').exists()

    def test_python310_importlib_resources_compatibility(self):
        """Test compatibility with Python 3.10+ importlib.resources behavior."""
        # This test specifically checks for the MultiplexedPath issue in Python 3.10
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                'pydcov', 'init-template', 'python310_test',
                '--template', 'basic_cpp',
                '--output-dir', temp_dir
            ], capture_output=True, text=True)

            # Should not fail with "MultiplexedPath is not a file" error
            assert result.returncode == 0, f"Command failed: {result.stdout} {result.stderr}"
            assert 'MultiplexedPath' not in result.stderr
            assert 'is not a file' not in result.stderr

            # Verify all template files were created correctly
            project_path = Path(temp_dir) / 'python310_test'
            assert project_path.exists()
            assert (project_path / 'CMakeLists.txt').exists()
            assert (project_path / 'src' / 'calculator.cpp').exists()
            assert (project_path / 'src' / 'calculator.hpp').exists()
            assert (project_path / 'tests' / 'test_calculator.cpp').exists()
            assert (project_path / 'app' / 'main.cpp').exists()
            assert (project_path / 'cmake' / 'coverage.cmake').exists()

            # Verify placeholder substitution worked
            cmake_content = (project_path / 'CMakeLists.txt').read_text()
            assert 'project(python310_test)' in cmake_content
            assert '{{PROJECT_NAME}}' not in cmake_content


if __name__ == '__main__':
    pytest.main([__file__])
