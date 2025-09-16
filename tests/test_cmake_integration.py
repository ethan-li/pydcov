#!/usr/bin/env python3
"""
Comprehensive tests for CMake integration utilities.

Tests the CMakeHelper class and its integration with PathManager,
including normal use cases, edge cases, and error handling.
"""

import pytest
import tempfile
import subprocess
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pydcov.utils.cmake_integration import CMakeHelper
from pydcov.utils.path_utils import PathManager


class TestCMakeHelperInitialization:
    """Test CMakeHelper initialization with different PathManager configurations."""
    
    def test_init_with_valid_path_manager(self):
        """Test initialization with a valid PathManager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            assert cmake_helper.path_manager == path_manager
            assert hasattr(cmake_helper, 'logger')
    
    def test_init_with_nested_build_directory(self):
        """Test initialization with nested build directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure: project/build/Debug
            project_dir = Path(temp_dir) / 'project'
            build_dir = project_dir / 'build' / 'Debug'
            build_dir.mkdir(parents=True)
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            assert cmake_helper.path_manager.build_root == build_dir.resolve()


class TestCMakeHelperRunTarget:
    """Test CMakeHelper target execution functionality."""
    
    def test_run_target_success(self):
        """Test successful target execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()

            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)

            # Mock successful subprocess run
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="Target completed successfully",
                    stderr=""
                )

                result = cmake_helper.run_target('test_target')

                assert result is True
                # Use resolve() to handle path symlinks consistently
                mock_run.assert_called_once_with(
                    ['make', 'test_target'],
                    cwd=build_dir.resolve(),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
    
    def test_run_target_with_custom_cwd(self):
        """Test target execution with custom working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            custom_dir = Path(temp_dir) / 'custom'
            build_dir.mkdir()
            custom_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                
                result = cmake_helper.run_target('test_target', cwd=custom_dir)
                
                assert result is True
                mock_run.assert_called_once_with(
                    ['make', 'test_target'],
                    cwd=custom_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
    
    def test_run_target_failure(self):
        """Test target execution failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stdout="",
                    stderr="Make target failed"
                )
                
                result = cmake_helper.run_target('failing_target')
                
                assert result is False
    
    def test_run_target_timeout(self):
        """Test target execution timeout."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired(['make', 'target'], 300)
                
                result = cmake_helper.run_target('slow_target')
                
                assert result is False
    
    def test_run_target_make_not_found(self):
        """Test target execution when make is not available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = FileNotFoundError("make not found")
                
                result = cmake_helper.run_target('target')
                
                assert result is False
    
    def test_run_target_invalid_build_dir(self):
        """Test target execution with invalid build directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'nonexistent'
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            result = cmake_helper.run_target('target')
            
            assert result is False


class TestCMakeHelperBuildProject:
    """Test CMakeHelper build project functionality."""
    
    def test_build_project_success(self):
        """Test successful project build."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            with patch.object(cmake_helper, 'run_target') as mock_run_target:
                mock_run_target.return_value = True
                
                result = cmake_helper.build_project()
                
                assert result is True
                mock_run_target.assert_called_once_with('all')
    
    def test_build_project_failure(self):
        """Test project build failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            with patch.object(cmake_helper, 'run_target') as mock_run_target:
                mock_run_target.return_value = False
                
                result = cmake_helper.build_project()
                
                assert result is False


class TestCMakeHelperEnsureBuildConfigured:
    """Test CMakeHelper build configuration functionality."""
    
    def test_ensure_build_configured_already_configured(self):
        """Test when build is already configured with coverage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            
            # Create CMakeCache.txt with coverage enabled
            cmake_cache = build_dir / 'CMakeCache.txt'
            cmake_cache.write_text('PYDCOV_COVERAGE_ENABLED:BOOL=ON\nOTHER_VAR:STRING=value\n')
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            result = cmake_helper.ensure_build_configured()
            
            assert result is True
    
    def test_ensure_build_configured_not_configured(self):
        """Test when build is not configured with coverage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            
            # Create CMakeCache.txt without coverage enabled
            cmake_cache = build_dir / 'CMakeCache.txt'
            cmake_cache.write_text('OTHER_VAR:STRING=value\n')
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            result = cmake_helper.ensure_build_configured()
            
            assert result is False
    
    def test_ensure_build_configured_creates_build_dir(self):
        """Test that build directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            # This should create the build directory but return False since no CMakeCache.txt
            result = cmake_helper.ensure_build_configured()
            
            assert build_dir.exists()
            assert result is False


class TestCMakeHelperGetAvailableTargets:
    """Test CMakeHelper target discovery functionality."""
    
    def test_get_available_targets_success(self):
        """Test successful target discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()

            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)

            # Fix the mock output format to match what the parser expects
            mock_output = """The following are some of the valid targets for this Makefile:
all... (the default if no target is provided)
clean...
depend...
test_target...
coverage_target...
install..."""

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=mock_output,
                    stderr=""
                )

                targets = cmake_helper.get_available_targets()

                expected_targets = ['all', 'clean', 'depend', 'test_target', 'coverage_target', 'install']
                assert targets == expected_targets
    
    def test_get_available_targets_failure(self):
        """Test target discovery failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stdout="",
                    stderr="Make help failed"
                )
                
                targets = cmake_helper.get_available_targets()
                
                assert targets == []
    
    def test_get_available_targets_exception(self):
        """Test target discovery with exception."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)
            
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = Exception("Unexpected error")
                
                targets = cmake_helper.get_available_targets()
                
                assert targets == []


class TestCMakeHelperIntegrationScenarios:
    """Test CMakeHelper integration with real-world scenarios."""

    def test_nested_build_directory_structure(self):
        """Test the specific scenario that was causing the original CMake error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a nested build structure like: project/build/Debug/
            project_dir = Path(temp_dir) / 'my_project'
            build_dir = project_dir / 'build' / 'Debug'
            build_dir.mkdir(parents=True)

            # Create CMakeCache.txt in the nested build directory
            cmake_cache = build_dir / 'CMakeCache.txt'
            cmake_cache.write_text(
                'CMAKE_BUILD_TYPE:STRING=Debug\n'
                'PYDCOV_COVERAGE_ENABLED:BOOL=ON\n'
                'CMAKE_CXX_COMPILER:FILEPATH=/usr/bin/g++\n'
            )

            # Create a Makefile to simulate a configured build
            makefile = build_dir / 'Makefile'
            makefile.write_text('all:\n\t@echo "Building project"\n')

            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)

            # Test that PathManager correctly identifies the build directory
            assert path_manager.validate_build_dir() is True
            assert path_manager.validate_coverage_build() is True

            # Test that CMakeHelper can work with this structure
            assert cmake_helper.ensure_build_configured() is True

            # Test running a target in this nested structure
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
                result = cmake_helper.run_target('all')
                assert result is True
                mock_run.assert_called_with(
                    ['make', 'all'],
                    cwd=build_dir.resolve(),
                    capture_output=True,
                    text=True,
                    timeout=300
                )

    def test_backward_compatibility_with_existing_structures(self):
        """Test backward compatibility with existing directory structures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test various common build directory structures
            structures = [
                'build',  # Standard structure
                'cmake-build-debug',  # CLion default
                'cmake-build-release',  # CLion release
                'out/build',  # Visual Studio default
                'build/Debug',  # Multi-config generator
                'build/Release',  # Multi-config generator
            ]

            for structure in structures:
                build_dir = Path(temp_dir) / structure
                build_dir.mkdir(parents=True, exist_ok=True)

                # Create CMakeCache.txt
                cmake_cache = build_dir / 'CMakeCache.txt'
                cmake_cache.write_text('PYDCOV_COVERAGE_ENABLED:BOOL=ON\n')

                path_manager = PathManager(build_root=build_dir)
                cmake_helper = CMakeHelper(path_manager)

                # All structures should work
                assert path_manager.validate_build_dir() is True
                assert cmake_helper.ensure_build_configured() is True

    def test_error_handling_cmake_cache_not_found(self):
        """Test error handling when CMakeLists.txt cannot be found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory that looks like a build directory but isn't
            fake_build_dir = Path(temp_dir) / 'fake_build'
            fake_build_dir.mkdir()

            path_manager = PathManager(build_root=fake_build_dir)
            cmake_helper = CMakeHelper(path_manager)

            # Should fail validation
            assert path_manager.validate_build_dir() is False
            assert cmake_helper.ensure_build_configured() is False

            # Should fail to run targets
            result = cmake_helper.run_target('any_target')
            assert result is False

    def test_auto_detection_from_current_directory(self):
        """Test auto-detection when running from a CMake build directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').write_text('PYDCOV_COVERAGE_ENABLED:BOOL=ON\n')

            original_cwd = os.getcwd()
            try:
                # Change to the build directory
                os.chdir(build_dir)

                # PathManager should auto-detect the build directory
                path_manager = PathManager(build_root=None)
                cmake_helper = CMakeHelper(path_manager)

                assert path_manager.build_root == build_dir.resolve()
                assert cmake_helper.ensure_build_configured() is True

            finally:
                os.chdir(original_cwd)

    def test_auto_detection_failure_scenarios(self):
        """Test auto-detection failure scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / 'project'
            project_dir.mkdir()

            original_cwd = os.getcwd()
            try:
                # Change to a directory without CMakeCache.txt
                os.chdir(project_dir)

                # Should raise ValueError
                with pytest.raises(ValueError, match="Could not auto-detect CMake build directory"):
                    PathManager(build_root=None)

            finally:
                os.chdir(original_cwd)


class TestCMakeHelperEdgeCases:
    """Test CMakeHelper edge cases and error conditions."""

    def test_run_target_with_output_logging(self):
        """Test that target output is properly logged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()

            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="Build output with details",
                    stderr=""
                )

                with patch.object(cmake_helper.logger, 'debug') as mock_debug:
                    result = cmake_helper.run_target('verbose_target')

                    assert result is True
                    # Check that output was logged
                    mock_debug.assert_any_call("Output: Build output with details")

    def test_run_target_with_error_logging(self):
        """Test that target errors are properly logged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()

            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stdout="",
                    stderr="Compilation failed with errors"
                )

                with patch.object(cmake_helper.logger, 'error') as mock_error:
                    result = cmake_helper.run_target('failing_target')

                    assert result is False
                    # Check that error was logged
                    mock_error.assert_any_call("Error: Compilation failed with errors")

    def test_get_available_targets_empty_output(self):
        """Test target discovery with empty output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()

            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="",
                    stderr=""
                )

                targets = cmake_helper.get_available_targets()

                assert targets == []

    def test_get_available_targets_malformed_output(self):
        """Test target discovery with malformed output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()

            path_manager = PathManager(build_root=build_dir)
            cmake_helper = CMakeHelper(path_manager)

            # Fix the malformed output to match the actual parsing logic
            # The parser looks for lines with '...' that don't start with "The following"
            # and extracts everything before the first '...'
            malformed_output = """Some random text
            No proper target format
            target_without_dots
            proper_target... with description
            """

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=malformed_output,
                    stderr=""
                )

                targets = cmake_helper.get_available_targets()

                # Should only extract the properly formatted target
                assert targets == ['proper_target']


if __name__ == '__main__':
    pytest.main([__file__])
