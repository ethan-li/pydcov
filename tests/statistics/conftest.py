#!/usr/bin/env python3
"""
Pytest configuration and fixtures for the statistics module test suite.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.statistics.statistics_test_utils import (
    StatisticsCoverageContext,
    cleanup_coverage_files,
    get_statistics_executable_path,
    generate_test_datasets,
    calculate_expected_statistics
)


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


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark tests with "comprehensive" or "large" in name as slow
        if "comprehensive" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark statistical calculation tests
        if "statistics" in item.name or "calculation" in item.name:
            item.add_marker(pytest.mark.statistical)
        
        # Mark all tests as integration tests since they test the CLI
        item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session", autouse=True)
def check_statistics_executable():
    """Ensure the statistics executable exists before running any tests."""
    try:
        executable_path = get_statistics_executable_path()
        print(f"\nUsing statistics executable: {executable_path}")
    except FileNotFoundError as e:
        pytest.exit(f"Statistics executable not found: {e}")


@pytest.fixture(scope="session")
def statistics_coverage_session():
    """Session-wide coverage context for statistics tests."""
    with StatisticsCoverageContext() as ctx:
        yield ctx


@pytest.fixture(scope="function")
def clean_statistics_coverage():
    """Clean coverage data before each test function."""
    cleanup_coverage_files()
    yield
    # Coverage files are left for collection


@pytest.fixture(scope="class")
def statistics_coverage_class():
    """Class-wide coverage context for test classes."""
    with StatisticsCoverageContext() as ctx:
        yield ctx


# Pytest command line options are defined in the root conftest.py


@pytest.fixture(scope="session")
def coverage_build(request):
    """Check if tests are running with coverage build."""
    return request.config.getoption("--coverage-build")


@pytest.fixture(scope="session")
def statistics_executable_path(request):
    """Get the statistics executable path from command line or auto-detect."""
    path = request.config.getoption("--statistics-executable-path")
    if path:
        return path
    return get_statistics_executable_path()


# Test data fixtures
@pytest.fixture(scope="session")
def test_datasets():
    """Provide various test datasets for statistics testing."""
    return generate_test_datasets()


@pytest.fixture(scope="session")
def expected_statistics():
    """Provide expected statistics for test datasets."""
    datasets = generate_test_datasets()
    return {name: calculate_expected_statistics(data) for name, data in datasets.items()}


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_global_state():
    """Ensure global state is cleaned up between tests."""
    # The statistics CLI uses file-based storage, so we need to ensure
    # it's cleaned up between tests. Since the program exits after each
    # command, this is automatically handled, but we include this fixture
    # for completeness and future extensibility.
    yield
    # No cleanup needed as each command runs in a separate process


# Performance testing fixtures
@pytest.fixture
def large_dataset():
    """Provide a large dataset for performance testing."""
    return list(range(1, 1001))  # 1000 elements


@pytest.fixture
def very_large_dataset():
    """Provide a very large dataset for stress testing."""
    return list(range(1, 10001))  # 10000 elements


@pytest.fixture
def precision_dataset():
    """Provide a dataset for testing floating-point precision."""
    return [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


# Parameterized test data
@pytest.fixture(params=[
    [1, 2, 3, 4, 5],
    [10, 20, 30],
    [-5, 0, 5],
    [1.5, 2.5, 3.5],
    [42]
])
def sample_dataset(request):
    """Parameterized fixture for different sample datasets."""
    return request.param


@pytest.fixture(params=[1, 5, 10, 100, 1000])
def dataset_size(request):
    """Parameterized fixture for different dataset sizes."""
    return request.param


# Error testing fixtures
@pytest.fixture
def invalid_inputs():
    """Provide various invalid inputs for error testing."""
    return {
        'empty_args': [],
        'invalid_command': ['invalid_command'],
        'missing_args': ['create'],
        'too_many_args': ['create'] + ['1'] * 1000,
        'non_numeric': ['create', 'abc', 'def'],
        'mixed_valid_invalid': ['create', '1', 'abc', '3'],
    }


# Inter-module testing fixtures
@pytest.fixture
def algorithm_cli_path():
    """Get the algorithm CLI path for inter-module testing."""
    project_root = Path(__file__).parent.parent.parent
    possible_paths = [
        project_root / "build" / "algorithm" / "app" / "algorithm_cli",
        project_root / "algorithm" / "app" / "algorithm_cli",
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_file():
            return str(path)
    
    return None


@pytest.fixture
def temp_array_file():
    """Provide path to temporary array file for inter-module testing."""
    return "/tmp/pydcov_array.dat"
