#!/usr/bin/env python3
"""
Unit tests for PathManager class.

Tests the refactored PathManager with build_root parameter and
generic functionality without module-specific dependencies.
"""

import pytest
import tempfile
import os
from pathlib import Path

from pydcov.utils.path_utils import PathManager


class TestPathManagerInitialization:
    """Test PathManager initialization with different configurations."""
    
    def test_init_with_explicit_build_root(self):
        """Test initialization with explicit build_root parameter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'custom_build'
            build_dir.mkdir()
            
            # Create CMakeCache.txt to make it a valid build directory
            (build_dir / 'CMakeCache.txt').touch()
            
            manager = PathManager(build_root=build_dir)
            
            assert manager.build_root == build_dir.resolve()
            assert manager.build_dir == manager.build_root  # Backward compatibility
            assert manager.coverage_dir == build_dir.resolve() / 'coverage'
    
    def test_init_with_none_auto_detect_current_dir(self):
        """Test auto-detection when current directory is a build directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir)
            (build_dir / 'CMakeCache.txt').touch()
            
            original_cwd = os.getcwd()
            try:
                os.chdir(build_dir)
                manager = PathManager(build_root=None)
                
                assert manager.build_root == build_dir.resolve()
                assert manager.coverage_dir == build_dir.resolve() / 'coverage'
            finally:
                os.chdir(original_cwd)
    
    def test_init_with_none_requires_cmake_cache_in_current_dir(self):
        """Test that auto-detection requires CMakeCache.txt in current directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            build_dir = project_dir / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()

            original_cwd = os.getcwd()
            try:
                # When running from project directory (no CMakeCache.txt), should error
                os.chdir(project_dir)
                with pytest.raises(ValueError, match="Could not auto-detect CMake build directory"):
                    PathManager(build_root=None)

                # When running from build directory (has CMakeCache.txt), should work
                os.chdir(build_dir)
                manager = PathManager(build_root=None)
                assert manager.build_root == build_dir.resolve()
                assert manager.coverage_dir == build_dir.resolve() / 'coverage'
            finally:
                os.chdir(original_cwd)
    
    def test_init_with_none_error_when_no_cmake_cache(self):
        """Test error when no CMakeCache.txt found and no build_root specified."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            original_cwd = os.getcwd()
            try:
                os.chdir(project_dir)
                with pytest.raises(ValueError, match="Could not auto-detect CMake build directory"):
                    PathManager(build_root=None)
            finally:
                os.chdir(original_cwd)
    
    def test_init_with_different_build_directory_names(self):
        """Test with non-standard build directory names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            for build_name in ['cmake-build-debug', 'out', 'Release', 'Debug']:
                build_dir = Path(temp_dir) / build_name
                build_dir.mkdir(exist_ok=True)
                (build_dir / 'CMakeCache.txt').touch()
                
                manager = PathManager(build_root=build_dir)
                
                assert manager.build_root == build_dir.resolve()
                assert manager.coverage_dir == build_dir.resolve() / 'coverage'


class TestPathManagerDirectoryOperations:
    """Test PathManager directory creation and management."""
    
    def test_ensure_coverage_dir(self):
        """Test coverage directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = PathManager(build_root=build_dir)
            
            coverage_dir = manager.ensure_coverage_dir()
            
            assert coverage_dir.exists()
            assert coverage_dir.is_dir()
            assert coverage_dir == manager.coverage_dir
    
    def test_ensure_incremental_dir(self):
        """Test incremental coverage directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = PathManager(build_root=build_dir)
            
            incremental_dir = manager.ensure_incremental_dir()
            
            assert incremental_dir.exists()
            assert incremental_dir.is_dir()
            assert incremental_dir == manager.coverage_dir / 'incremental'
    
    def test_get_module_coverage_dir(self):
        """Test module-specific coverage directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = PathManager(build_root=build_dir)
            
            module_dir = manager.get_module_coverage_dir('test_module')
            
            assert module_dir.exists()
            assert module_dir.is_dir()
            assert module_dir == manager.coverage_dir / 'test_module'


class TestPathManagerValidation:
    """Test PathManager build directory validation."""
    
    def test_validate_build_dir_success(self):
        """Test successful build directory validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()
            
            manager = PathManager(build_root=build_dir)
            
            assert manager.validate_build_dir() is True
    
    def test_validate_build_dir_missing_directory(self):
        """Test validation failure when build directory doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'nonexistent'
            
            manager = PathManager(build_root=build_dir)
            
            assert manager.validate_build_dir() is False
    
    def test_validate_build_dir_missing_cmake_cache(self):
        """Test validation failure when CMakeCache.txt is missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            
            manager = PathManager(build_root=build_dir)
            
            assert manager.validate_build_dir() is False
    
    def test_validate_coverage_build_success(self):
        """Test successful coverage build validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            
            # Create CMakeCache.txt with coverage enabled
            cmake_cache = build_dir / 'CMakeCache.txt'
            cmake_cache.write_text('ENABLE_COVERAGE:BOOL=ON\nOTHER_VAR:STRING=value\n')
            
            manager = PathManager(build_root=build_dir)
            
            assert manager.validate_coverage_build() is True
    
    def test_validate_coverage_build_disabled(self):
        """Test coverage build validation when coverage is disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            
            # Create CMakeCache.txt without coverage enabled
            cmake_cache = build_dir / 'CMakeCache.txt'
            cmake_cache.write_text('ENABLE_COVERAGE:BOOL=OFF\nOTHER_VAR:STRING=value\n')
            
            manager = PathManager(build_root=build_dir)
            
            assert manager.validate_coverage_build() is False


class TestPathManagerUtilities:
    """Test PathManager utility methods."""
    
    def test_relative_to_build(self):
        """Test relative path calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = PathManager(build_root=build_dir)

            test_file = build_dir.resolve() / 'subdir' / 'test.txt'
            relative_path = manager.relative_to_build(test_file)

            assert relative_path == 'subdir/test.txt'
    
    def test_relative_to_build_outside_build(self):
        """Test relative path calculation for files outside build directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = PathManager(build_root=build_dir)
            
            outside_file = Path(temp_dir) / 'outside.txt'
            relative_path = manager.relative_to_build(outside_file)
            
            # Should return absolute path when file is outside build directory
            assert relative_path == str(outside_file)


class TestPathManagerCleanup:
    """Test PathManager cleanup operations."""
    
    def test_clean_coverage_data_all(self):
        """Test cleaning all coverage data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = PathManager(build_root=build_dir)
            
            # Create some coverage data
            coverage_dir = manager.ensure_coverage_dir()
            (coverage_dir / 'test.profraw').touch()
            incremental_dir = manager.ensure_incremental_dir()
            (incremental_dir / 'test.gcda').touch()
            
            manager.clean_coverage_data(incremental_only=False)
            
            assert not coverage_dir.exists()
    
    def test_clean_coverage_data_incremental_only(self):
        """Test cleaning only incremental coverage data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = PathManager(build_root=build_dir)
            
            # Create some coverage data
            coverage_dir = manager.ensure_coverage_dir()
            (coverage_dir / 'test.profraw').touch()
            incremental_dir = manager.ensure_incremental_dir()
            (incremental_dir / 'test.gcda').touch()
            
            manager.clean_coverage_data(incremental_only=True)
            
            assert coverage_dir.exists()
            assert not incremental_dir.exists()
            assert (coverage_dir / 'test.profraw').exists()


class TestPathManagerBackwardCompatibility:
    """Test backward compatibility features."""

    def test_build_dir_alias(self):
        """Test that build_dir is an alias for build_root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = PathManager(build_root=build_dir)

            assert manager.build_dir == manager.build_root
            assert manager.build_dir is manager.build_root


class TestPathManagerIntegration:
    """Test PathManager integration with other components."""

    def test_integration_with_incremental_coverage_manager(self):
        """Test PathManager works with IncrementalCoverageManager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').write_text('ENABLE_COVERAGE:BOOL=ON\n')

            from pydcov.core.incremental_coverage import IncrementalCoverageManager

            # Test API
            manager = IncrementalCoverageManager(build_root=build_dir)
            assert manager.path_manager.build_root == build_dir.resolve()

    def test_different_build_configurations(self):
        """Test PathManager with different CMake build configurations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            # Test different build directory structures
            build_configs = [
                'build',
                'cmake-build-debug',
                'cmake-build-release',
                'out/build',
                'build/Debug',
                'build/Release'
            ]

            for config in build_configs:
                build_dir = project_dir / config
                build_dir.mkdir(parents=True, exist_ok=True)
                (build_dir / 'CMakeCache.txt').touch()

                manager = PathManager(build_root=build_dir)

                assert manager.build_root == build_dir.resolve()
                assert manager.validate_build_dir() is True
                assert manager.coverage_dir == build_dir.resolve() / 'coverage'


if __name__ == '__main__':
    pytest.main([__file__])
