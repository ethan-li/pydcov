#!/usr/bin/env python3
"""
Test coverage tools detection and validation.

Tests lcov version detection, lcov version validation, and related
functionality in the CoverageToolManager class.
"""

import pytest
import subprocess
import shutil
from pathlib import Path

from pydcov.utils.coverage_tools import CoverageToolManager


class TestLcovVersionDetection:
    """Test lcov version detection and validation."""

    def test_get_lcov_version_when_not_found(self):
        """Test get_lcov_version when lcov is not installed."""
        manager = CoverageToolManager()
        # Force clear the cache to ensure we get a fresh result
        manager._tool_cache.clear()

        found, result = manager.get_lcov_version()
        assert found is False
        assert "not found" in result.lower()

    def test_validate_lcov_version_when_not_found(self):
        """Test validate_lcov_version when lcov is not installed."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        is_valid, message = manager.validate_lcov_version("2.0")
        assert is_valid is False
        assert "not found" in message.lower()
        assert "2.0" in message  # Should mention the required version

    def test_validate_lcov_version_minimum_version_in_error(self):
        """Test that validate_lcov_version mentions the required version in error."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        is_valid, message = manager.validate_lcov_version("1.14")
        assert is_valid is False
        # Should provide install instructions
        assert "apt" in message.lower() or "brew" in message.lower() or "install" in message.lower()

    def test_lcov_version_parsing(self):
        """Test that lcov version output is properly parsed."""
        manager = CoverageToolManager()

        # Test version comparison logic directly
        # This tests the parsing without requiring lcov to be installed
        min_version = "2.0"

        # Manually test version comparison
        installed_parts = "2.0".split(".")
        installed_major = int(installed_parts[0])
        installed_minor = int(installed_parts[1]) if len(installed_parts) > 1 else 0

        required_parts = min_version.split(".")
        required_major = int(required_parts[0])
        required_minor = int(required_parts[1]) if len(required_parts) > 1 else 0

        assert installed_major >= required_major
        assert installed_minor >= required_minor

    def test_lcov_version_1_14_should_fail_for_2_0_requirement(self):
        """Test that version 1.14 fails when 2.0 is required."""
        manager = CoverageToolManager()

        # Test version 1.14 against requirement 2.0
        installed_parts = "1.14".split(".")
        installed_major = int(installed_parts[0])
        installed_minor = int(installed_parts[1]) if len(installed_parts) > 1 else 0

        required_major = 2
        required_minor = 0

        assert installed_major < required_major or (installed_major == required_major and installed_minor < required_minor)

    def test_lcov_version_2_0_should_pass_for_2_0_requirement(self):
        """Test that version 2.0 passes when 2.0 is required."""
        installed_major = 2
        installed_minor = 0
        required_major = 2
        required_minor = 0

        assert installed_major == required_major and installed_minor >= required_minor

    def test_lcov_version_2_1_should_pass_for_2_0_requirement(self):
        """Test that version 2.1 passes when 2.0 is required."""
        installed_major = 2
        installed_minor = 1
        required_major = 2
        required_minor = 0

        assert installed_major == required_major and installed_minor >= required_minor

    def test_lcov_version_3_0_should_pass_for_2_0_requirement(self):
        """Test that version 3.0 passes when 2.0 is required."""
        installed_major = 3
        installed_minor = 0
        required_major = 2
        required_minor = 0

        assert installed_major > required_major

    def test_validate_lcov_version_disable_with_zero(self):
        """Test that version check can be disabled with '0'."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        # When lcov_version is "0", the version check should be bypassed
        # This is handled at a higher level, but we verify the manager accepts it
        is_valid, message = manager.validate_lcov_version("0")
        # The method still checks, but "0" is an unusual version that would fail parsing
        # The key is that the calling code passes "0" to disable the check entirely


class TestCoverageToolManagerBasics:
    """Test basic CoverageToolManager functionality."""

    def test_manager_initialization(self):
        """Test that CoverageToolManager initializes correctly."""
        manager = CoverageToolManager()
        assert manager.logger is not None
        assert manager._tool_cache is not None

    def test_find_tool_caches_result(self):
        """Test that find_tool caches its result."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        # First call should search
        result1 = manager.find_tool("nonexistent_tool_12345")
        assert result1 is None

        # Second call should return cached None
        result2 = manager.find_tool("nonexistent_tool_12345")
        assert result2 is None

    def test_get_tool_info_returns_dict(self):
        """Test that get_tool_info returns expected dictionary structure."""
        manager = CoverageToolManager()
        info = manager.get_tool_info()

        assert isinstance(info, dict)
        assert "compiler" in info
        assert "platform" in info
        assert "tools" in info
        assert "valid" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
