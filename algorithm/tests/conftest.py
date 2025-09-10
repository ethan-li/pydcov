#!/usr/bin/env python3
"""
Pytest configuration and fixtures for the pydcov test suite.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils import CoverageContext, cleanup_coverage_files, get_executable_path


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark tests with "comprehensive" or "large" in name as slow
        if "comprehensive" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark all tests as integration tests since they test the CLI
        item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session", autouse=True)
def check_executable():
    """Ensure the executable exists before running any tests."""
    try:
        executable_path = get_executable_path()
        print(f"\nUsing executable: {executable_path}")
    except FileNotFoundError as e:
        pytest.exit(f"Executable not found: {e}")


@pytest.fixture(scope="session")
def coverage_session():
    """Session-wide coverage context."""
    with CoverageContext() as ctx:
        yield ctx


@pytest.fixture(scope="function")
def clean_coverage():
    """Clean coverage data before each test function."""
    cleanup_coverage_files()
    yield
    # Coverage files are left for collection


@pytest.fixture(scope="class")
def coverage_class():
    """Class-wide coverage context for test classes."""
    with CoverageContext() as ctx:
        yield ctx


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
        help="Path to the pydcov executable"
    )


@pytest.fixture(scope="session")
def coverage_build(request):
    """Check if tests are running with coverage build."""
    return request.config.getoption("--coverage-build")


@pytest.fixture(scope="session")
def executable_path(request):
    """Get the executable path from command line or auto-detect."""
    path = request.config.getoption("--executable-path")
    if path:
        return path
    return get_executable_path()


# Test data fixtures for dynamic arrays


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_global_state():
    """Ensure global state is cleaned up between tests."""
    # The C++ program uses a global dynamic array, so we need to ensure
    # it's cleaned up between tests. Since the program exits after each
    # command, this is automatically handled, but we include this fixture
    # for completeness and future extensibility.
    yield
    # No cleanup needed as each command runs in a separate process


# Performance testing fixtures for dynamic arrays
@pytest.fixture
def large_dataset():
    """Provide a large dataset for performance testing."""
    return list(range(1000, 0, -1))  # 1000 elements in reverse order


@pytest.fixture
def very_large_dataset():
    """Provide a very large dataset for stress testing."""
    return list(range(10000, 0, -1))  # 10000 elements in reverse order


# Parameterized test data
@pytest.fixture(params=[1, 5, 10, 100])
def array_capacity(request):
    """Parameterized fixture for different array capacities."""
    return request.param
