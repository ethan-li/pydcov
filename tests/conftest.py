#!/usr/bin/env python3
"""
Pytest configuration for PyDCov package tests.

Provides shared fixtures and configuration for testing the PyDCov package functionality.
"""

import pytest
import tempfile
import shutil
import subprocess
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "statistical: marks tests that verify statistical calculations"
    )
    config.addinivalue_line(
        "markers", "algorithm: marks tests for the algorithm module"
    )
    config.addinivalue_line(
        "markers", "statistics: marks tests for the statistics module"
    )
    config.addinivalue_line(
        "markers", "coverage_tools: marks tests for the coverage tools"
    )
    config.addinivalue_line(
        "markers", "package: marks tests for PyDCov package functionality"
    )
    config.addinivalue_line(
        "markers", "cli: marks tests for CLI interface"
    )
    config.addinivalue_line(
        "markers", "template: marks tests for template system"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names and paths."""
    for item in items:
        # Mark tests with "comprehensive" or "large" in name as slow
        if "comprehensive" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Add module-specific markers based on test path
        test_path = str(item.fspath)
        if "/algorithm/" in test_path:
            item.add_marker(pytest.mark.algorithm)
        elif "/statistics/" in test_path:
            item.add_marker(pytest.mark.statistics)
        elif "/coverage_tools/" in test_path:
            item.add_marker(pytest.mark.coverage_tools)
        elif "test_package_installation" in test_path:
            item.add_marker(pytest.mark.package)
        elif "test_cli_commands" in test_path:
            item.add_marker(pytest.mark.cli)
        elif "test_template_system" in test_path:
            item.add_marker(pytest.mark.template)
        elif "test_integration" in test_path:
            item.add_marker(pytest.mark.integration)
        
        # Mark statistical calculation tests
        if "statistics" in item.name or "calculation" in item.name:
            item.add_marker(pytest.mark.statistical)
        
        # Mark template and integration tests as slow by default
        if "template" in test_path or "integration" in test_path:
            item.add_marker(pytest.mark.slow)


# Pytest command line options
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--coverage-build",
        action="store_true",
        default=False,
        help="Run tests assuming coverage build was used"
    )
    parser.addoption(
        "--executable-path",
        action="store",
        default=None,
        help="Path to the algorithm executable"
    )
    parser.addoption(
        "--statistics-executable-path",
        action="store",
        default=None,
        help="Path to the statistics executable"
    )
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )
    parser.addoption(
        "--skip-integration",
        action="store_true",
        default=False,
        help="Skip integration tests"
    )


@pytest.fixture(scope="session")
def coverage_build(request):
    """Check if tests are running with coverage build."""
    return request.config.getoption("--coverage-build")


@pytest.fixture(scope="session")
def project_root_path():
    """Get the project root path."""
    return project_root


@pytest.fixture(scope="function")
def temp_directory():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def pydcov_installed():
    """Check if PyDCov is installed and available."""
    try:
        result = subprocess.run(['pydcov', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


@pytest.fixture(scope="session")
def cmake_available():
    """Check if CMake is available."""
    try:
        result = subprocess.run(['cmake', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


@pytest.fixture(scope="session")
def make_available():
    """Check if make is available."""
    try:
        result = subprocess.run(['make', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


@pytest.fixture(scope="session")
def build_tools_available(cmake_available, make_available):
    """Check if build tools (CMake and make) are available."""
    return cmake_available and make_available


@pytest.fixture(scope="session")
def algorithm_executable_path(request):
    """Get the algorithm executable path."""
    path = request.config.getoption("--executable-path")
    if path:
        return Path(path)

    # Default path
    return Path(__file__).parent.parent / "examples" / "algorithm" / "build" / "algorithm"


@pytest.fixture(scope="session")
def statistics_executable_path(request):
    """Get the statistics executable path."""
    path = request.config.getoption("--statistics-executable-path")
    if path:
        return Path(path)

    # Default path
    return Path(__file__).parent.parent / "examples" / "statistics" / "build" / "statistics"


def skip_if_no_pydcov():
    """Skip test if PyDCov is not installed."""
    try:
        subprocess.run(['pydcov', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("PyDCov not installed or not working")


def skip_if_no_build_tools():
    """Skip test if build tools are not available."""
    try:
        subprocess.run(['cmake', '--version'], capture_output=True, check=True)
        subprocess.run(['make', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("Build tools (CMake/make) not available")


def pytest_runtest_setup(item):
    """Setup for individual test runs."""
    # Skip slow tests unless explicitly requested
    if "slow" in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("Slow test skipped (use --run-slow to run)")

    # Skip integration tests if requested
    if "integration" in item.keywords and item.config.getoption("--skip-integration"):
        pytest.skip("Integration test skipped")


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_global_state():
    """Ensure global state is cleaned up between tests."""
    # Since each command runs in a separate process, this is automatically
    # handled, but we include this fixture for completeness and future extensibility.
    yield
    # No cleanup needed as each command runs in a separate process
