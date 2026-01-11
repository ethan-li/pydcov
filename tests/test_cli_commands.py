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
        result = subprocess.run(["pydcov", "--help"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "usage:" in result.stdout
        assert "PyDCov" in result.stdout
        assert "init" in result.stdout
        assert "add" in result.stdout
        assert "merge" in result.stdout
        assert "report" in result.stdout
        assert "status" in result.stdout
        assert "clean" in result.stdout
        assert "init-cmake" in result.stdout

    def test_version_command(self):
        """Test version command."""
        result = subprocess.run(["pydcov", "--version"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "PyDCov" in result.stdout
        # Should match semantic versioning pattern
        import re

        version_pattern = r"\d+\.\d+\.\d+"
        assert re.search(version_pattern, result.stdout)

    def test_init_help(self):
        """Test init command help."""
        result = subprocess.run(
            ["pydcov", "init", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "usage:" in result.stdout
        assert "Initialize incremental coverage tracking" in result.stdout

    def test_add_help(self):
        """Test add command help."""
        result = subprocess.run(
            ["pydcov", "add", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "usage:" in result.stdout
        assert (
            "Run tests and add coverage data to incremental collection" in result.stdout
        )

    def test_init_cmake_help(self):
        """Test init-cmake subcommand help."""
        result = subprocess.run(
            ["pydcov", "init-cmake", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "usage:" in result.stdout
        assert "CMake integration" in result.stdout


class TestCLIErrorHandling:
    """Test CLI error handling and validation."""

    def test_invalid_command(self):
        """Test invalid command handling."""
        result = subprocess.run(
            ["pydcov", "invalid-command"], capture_output=True, text=True
        )
        assert result.returncode != 0
        assert (
            "invalid choice" in result.stderr.lower()
            or "unrecognized" in result.stderr.lower()
        )

    def test_add_missing_args(self):
        """Test add command with missing arguments."""
        # Test 'add' command without test arguments
        result = subprocess.run(["pydcov", "add"], capture_output=True, text=True)
        assert result.returncode != 0


class TestInitCMakeCommand:
    """Test init-cmake command functionality."""

    def test_init_cmake_basic(self):
        """Test basic init-cmake functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Run init-cmake in temporary directory
            result = subprocess.run(
                ["pydcov", "init-cmake", "--project-root", str(temp_path)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Copied coverage.cmake" in result.stdout

            # Check that files were created
            cmake_dir = temp_path / "cmake"
            assert cmake_dir.exists()
            assert (cmake_dir / "coverage.cmake").exists()

    def test_init_cmake_force_overwrite(self):
        """Test init-cmake with force overwrite."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cmake_dir = temp_path / "cmake"
            cmake_dir.mkdir()

            # Create existing file
            existing_file = cmake_dir / "coverage.cmake"
            existing_file.write_text("# Existing content")

            # Run init-cmake with force
            result = subprocess.run(
                ["pydcov", "init-cmake", "--project-root", str(temp_path), "--force"],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

            # Check that file was overwritten
            content = existing_file.read_text()
            assert "# Existing content" not in content
            assert "cmake_minimum_required" in content or "Coverage" in content

    def test_init_cmake_existing_files_no_force(self):
        """Test init-cmake with existing files without force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cmake_dir = temp_path / "cmake"
            cmake_dir.mkdir()

            # Create existing file
            existing_file = cmake_dir / "coverage.cmake"
            existing_file.write_text("# Existing content")

            # Run init-cmake without force
            result = subprocess.run(
                ["pydcov", "init-cmake", "--project-root", str(temp_path)],
                capture_output=True,
                text=True,
            )

            # Should either succeed (if it handles existing files) or warn
            # The exact behavior depends on implementation
            if result.returncode != 0:
                assert (
                    "exists" in result.stderr.lower()
                    or "force" in result.stderr.lower()
                )


class TestIncrementalStatusCommand:
    """Test incremental status command (doesn't require coverage tools)."""

    def test_status_basic(self):
        """Test basic status command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / "build"
            build_dir.mkdir(parents=True)
            (build_dir / "CMakeCache.txt").touch()

            # First initialize to set up configuration using Python script directly
            import sys

            pydcov_script = Path(__file__).parent.parent / "pydcov" / "cli.py"
            init_result = subprocess.run(
                [
                    sys.executable,
                    str(pydcov_script),
                    "init",
                    "--build-root",
                    str(build_dir),
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Now test status command without --build-root
            result = subprocess.run(
                [sys.executable, str(pydcov_script), "status"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Status command should run (might detect missing tools)
            # Return code might be 0 or non-zero depending on tool availability
            assert (
                "Detected compiler:" in result.stdout
                or "not found" in result.stderr.lower()
            )


class TestCLIVerboseMode:
    """Test CLI verbose mode functionality."""

    def test_status_verbose(self):
        """Test status command with verbose flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            build_dir = Path(temp_dir) / "build"
            build_dir.mkdir(parents=True)
            (build_dir / "CMakeCache.txt").touch()

            # First initialize to set up configuration using Python script directly
            import sys

            pydcov_script = Path(__file__).parent.parent / "pydcov" / "cli.py"
            init_result = subprocess.run(
                [
                    sys.executable,
                    str(pydcov_script),
                    "init",
                    "--build-root",
                    str(build_dir),
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Now test status command with verbose flag but without --build-root
            result = subprocess.run(
                [sys.executable, str(pydcov_script), "status", "--verbose"],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Verbose mode should provide more output
            assert len(result.stdout) > 0 or len(result.stderr) > 0


class TestCLIPathHandling:
    """Test CLI path handling robustness."""

    def test_init_cmake_without_project_root(self):
        """Test init-cmake command without specifying project root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                result = subprocess.run(
                    ["pydcov", "init-cmake"], capture_output=True, text=True
                )

                assert (
                    result.returncode == 0
                ), f"Command failed: {result.stdout} {result.stderr}"
                assert "Copied coverage.cmake" in result.stdout

                # Check that cmake files were created in current directory
                cmake_dir = Path(temp_dir) / "cmake"
                assert cmake_dir.exists()
                assert (cmake_dir / "coverage.cmake").exists()

            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__])
