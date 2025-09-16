#!/usr/bin/env python3
"""
Test PyDCov package installation and basic functionality.

Tests package installation, imports, version reporting, and basic API functionality.
"""

import pytest
import subprocess
import sys
import importlib
import tempfile
import shutil
from pathlib import Path


class TestPackageInstallation:
    """Test PyDCov package installation and basic imports."""
    
    def test_package_imports(self):
        """Test that all main package components can be imported."""
        # Test main package import
        import pydcov
        assert hasattr(pydcov, '__version__')
        assert hasattr(pydcov, 'IncrementalCoverageManager')
        assert hasattr(pydcov, 'CompilerDetector')

        # Test core module imports
        from pydcov.core.incremental_coverage import IncrementalCoverageManager
        
        # Test utility imports
        from pydcov.utils.compiler_detection import CompilerDetector
        from pydcov.utils.logging_config import setup_logging
        
        # Test CLI import
        from pydcov import cli
    
    def test_version_available(self):
        """Test that version information is available."""
        import pydcov
        version = pydcov.__version__
        assert isinstance(version, str)
        assert len(version) > 0
        assert '.' in version  # Should be semantic version
    

    def test_incremental_coverage_manager_instantiation(self):
        """Test that IncrementalCoverageManager can be instantiated."""
        from pydcov import IncrementalCoverageManager
        import tempfile
        from pathlib import Path

        # Create a temporary build directory with CMakeCache.txt
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            build_dir.mkdir()
            (build_dir / 'CMakeCache.txt').touch()

            manager = IncrementalCoverageManager(build_root=build_dir)
            assert manager is not None
        
        # Test that required methods exist
        assert hasattr(manager, 'init')
        assert hasattr(manager, 'add')
        assert hasattr(manager, 'merge')
        assert hasattr(manager, 'report')
        assert hasattr(manager, 'status')
        assert hasattr(manager, 'clean')
    
    def test_compiler_detector_instantiation(self):
        """Test that CompilerDetector can be instantiated."""
        from pydcov.utils.compiler_detection import CompilerDetector
        
        detector = CompilerDetector()
        assert detector is not None
        
        # Test that required methods exist
        assert hasattr(detector, 'detect_compiler')
        assert hasattr(detector, 'validate_tools')


class TestCLIEntryPoint:
    """Test that CLI entry point is properly installed."""
    
    def test_pydcov_command_available(self):
        """Test that pydcov command is available in PATH."""
        result = subprocess.run(['which', 'pydcov'], capture_output=True, text=True)
        assert result.returncode == 0, "pydcov command not found in PATH"
        assert len(result.stdout.strip()) > 0
    
    def test_pydcov_version_command(self):
        """Test pydcov --version command."""
        result = subprocess.run(['pydcov', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, f"pydcov --version failed: {result.stderr}"
        assert 'PyDCov' in result.stdout
        assert len(result.stdout.strip()) > 0
    
    def test_pydcov_help_command(self):
        """Test pydcov --help command."""
        result = subprocess.run(['pydcov', '--help'], capture_output=True, text=True)
        assert result.returncode == 0, f"pydcov --help failed: {result.stderr}"
        assert 'usage:' in result.stdout
        assert 'incremental' in result.stdout
        assert 'init-cmake' in result.stdout


class TestPackageStructure:
    """Test that package structure is correct."""
    
    def test_package_data_files(self):
        """Test that package data files are accessible."""
        import pydcov
        from pathlib import Path
        
        # Get package path
        package_path = Path(pydcov.__file__).parent
        
        # Test CMake files exist
        cmake_dir = package_path / 'cmake'
        assert cmake_dir.exists(), "cmake directory not found in package"
        assert (cmake_dir / 'coverage.cmake').exists(), "coverage.cmake not found"

    
    def test_no_unwanted_files(self):
        """Test that unwanted files are not included in package."""
        import pydcov
        from pathlib import Path

        package_path = Path(pydcov.__file__).parent

        # Check for unwanted files (skip cache files as they're created during import)
        unwanted_patterns = ['.git', 'build', 'dist']

        for pattern in unwanted_patterns:
            unwanted_files = list(package_path.rglob(pattern))
            assert len(unwanted_files) == 0, f"Found unwanted files matching {pattern}: {unwanted_files}"


class TestBasicAPI:
    """Test basic API functionality without requiring external tools."""
    

    def test_incremental_manager_basic_methods(self):
        """Test IncrementalCoverageManager basic method calls."""
        from pydcov import IncrementalCoverageManager
        
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / 'build'
            manager = IncrementalCoverageManager(build_root=build_dir)
            
            # Test status method (should not fail)
            try:
                manager.status()
            except Exception as e:
                # Status might fail due to missing tools, but shouldn't crash
                assert "not found" in str(e).lower() or "missing" in str(e).lower()
    
    def test_compiler_detection(self):
        """Test compiler detection functionality."""
        from pydcov.utils.compiler_detection import CompilerDetector

        detector = CompilerDetector()

        # Test compiler detection (should return a string)
        compiler = detector.detect_compiler()
        assert isinstance(compiler, str)
        assert compiler in ['gcc', 'clang', 'unknown']

        # Test tool validation (returns tuple: (success, missing_tools))
        tools = detector.validate_tools()
        assert isinstance(tools, tuple)
        assert len(tools) == 2
        success, missing_tools = tools
        assert isinstance(success, bool)
        assert isinstance(missing_tools, list)


if __name__ == '__main__':
    pytest.main([__file__])
