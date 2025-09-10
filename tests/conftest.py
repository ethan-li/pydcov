#!/usr/bin/env python3
"""
Root-level pytest configuration for the pydcov test suite.

This configuration file provides shared settings and fixtures for all test modules
in the unified tests/ directory structure.
"""

import pytest
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
        
        # Mark statistical calculation tests
        if "statistics" in item.name or "calculation" in item.name:
            item.add_marker(pytest.mark.statistical)
        
        # Mark all tests as integration tests since they test CLI interfaces
        item.add_marker(pytest.mark.integration)


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


@pytest.fixture(scope="session")
def coverage_build(request):
    """Check if tests are running with coverage build."""
    return request.config.getoption("--coverage-build")


@pytest.fixture(scope="session")
def project_root_path():
    """Get the project root path."""
    return project_root


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_global_state():
    """Ensure global state is cleaned up between tests."""
    # Since each command runs in a separate process, this is automatically
    # handled, but we include this fixture for completeness and future extensibility.
    yield
    # No cleanup needed as each command runs in a separate process
