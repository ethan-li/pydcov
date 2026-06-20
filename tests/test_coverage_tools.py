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
from unittest.mock import patch, MagicMock

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

    def test_get_lcov_version_parses_version_correctly(self):
        """Test get_lcov_version correctly parses lcov version output."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        # Mock lcov being found and returning version 2.0
        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="lcov version 2.0",
                    stderr=""
                )
                found, version = manager.get_lcov_version()

                assert found is True
                assert version == "2.0"
                mock_run.assert_called_once_with(
                    ['/usr/bin/lcov', '--version'],
                    capture_output=True, text=True, timeout=10
                )

    def test_get_lcov_version_parses_1_14(self):
        """Test get_lcov_version correctly parses lcov version 1.14."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="LCOV version 1.14",
                    stderr=""
                )
                found, version = manager.get_lcov_version()

                assert found is True
                assert version == "1.14"

    def test_get_lcov_version_handles_lowercase_lcov(self):
        """Test get_lcov_version handles lowercase 'lcov' in output."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="lcov version 1.16",
                    stderr=""
                )
                found, version = manager.get_lcov_version()

                assert found is True
                assert version == "1.16"

    def test_get_lcov_version_returns_raw_on_unparseable_output(self):
        """Test get_lcov_version returns raw output when version pattern not matched."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="some unexpected output",
                    stderr=""
                )
                found, result = manager.get_lcov_version()

                assert found is True
                assert result == "some unexpected output"

    def test_validate_lcov_version_when_not_found(self):
        """Test validate_lcov_version when lcov is not installed."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        is_valid, message = manager.validate_lcov_version("2.0")
        assert is_valid is False
        assert "not found" in message.lower()
        assert "2.0" in message  # Should mention the required version

    def test_validate_lcov_version_passes_for_2_0_with_2_0_required(self):
        """Test validate_lcov_version passes when installed version meets requirement."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="lcov version 2.0",
                    stderr=""
                )
                is_valid, message = manager.validate_lcov_version("2.0")

                assert is_valid is True
                assert "2.0" in message
                assert "meets requirement" in message

    def test_validate_lcov_version_passes_for_newer_version(self):
        """Test validate_lcov_version passes when installed version exceeds requirement."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="lcov version 2.3",
                    stderr=""
                )
                is_valid, message = manager.validate_lcov_version("2.0")

                assert is_valid is True
                assert "2.3" in message

    def test_validate_lcov_version_fails_for_old_version(self):
        """Test validate_lcov_version fails when installed version is too old."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="lcov version 1.14",
                    stderr=""
                )
                is_valid, message = manager.validate_lcov_version("2.0")

                assert is_valid is False
                assert "1.14" in message
                assert "too old" in message.lower()
                assert "2.0" in message
                # Should provide update instructions
                assert "apt" in message.lower() or "brew" in message.lower()

    def test_validate_lcov_version_fails_for_1_16_when_2_0_required(self):
        """Test validate_lcov_version fails for 1.16 when 2.0 is required."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="lcov version 1.16",
                    stderr=""
                )
                is_valid, message = manager.validate_lcov_version("2.0")

                assert is_valid is False
                assert "1.16" in message
                assert "too old" in message.lower()

    def test_validate_lcov_version_error_message_is_human_readable(self):
        """Test that error messages are human-readable and direct."""
        manager = CoverageToolManager()
        manager._tool_cache.clear()

        with patch.object(manager, 'find_tool', return_value='/usr/bin/lcov'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="lcov version 1.14",
                    stderr=""
                )
                is_valid, message = manager.validate_lcov_version("2.0")

                # Message should be a single, coherent sentence
                assert "lcov" in message.lower()
                assert "2.0" in message
                # Should not contain technical jargon or tracebacks
                assert "traceback" not in message.lower()
                assert "exception" not in message.lower()


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
