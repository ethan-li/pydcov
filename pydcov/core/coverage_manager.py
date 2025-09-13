"""
Main coverage manager for standard coverage workflows.

This module provides the core coverage functionality equivalent to the
comprehensive coverage workflow including build, test, and report generation.
"""

import os
import subprocess
from pathlib import Path
from typing import List

from pydcov.utils.compiler_detection import CompilerDetector
from pydcov.utils.logging_config import get_logger
from pydcov.utils.path_utils import PathManager
from pydcov.utils.cmake_integration import CMakeHelper
from pydcov.utils.test_executor import TestExecutor
from pydcov.utils.coverage_file_manager import CoverageFileManager


class CoverageManager:
    """Manages standard coverage collection and reporting workflows."""
    
    def __init__(self, project_root: Path | None = None):
        self.logger = get_logger()
        self.path_manager = PathManager(project_root)
        self.cmake_helper = CMakeHelper(self.path_manager)
        self.test_executor = TestExecutor(self.path_manager.project_root, self.logger)
        self.compiler_detector = CompilerDetector()

        # Initialize file manager for pure Python coverage operations
        self.file_manager = CoverageFileManager(
            self.path_manager.build_dir,
            self.path_manager.coverage_dir
        )

        # Validate tools on initialization
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate that required tools are available."""
        compiler = self.compiler_detector.detect_compiler()
        is_valid, missing = self.compiler_detector.validate_tools(compiler)
        
        if not is_valid:
            self.logger.error(f"Missing required coverage tools: {', '.join(missing)}")
            self.logger.error("Please install the required tools before proceeding")
            raise RuntimeError(f"Missing coverage tools: {missing}")
    
    def clean(self) -> bool:
        """
        Clean all coverage data and build artifacts.

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Cleaning coverage data...")

        # Clean coverage data using pure Python
        self.path_manager.clean_coverage_data()

        # Clean build artifacts with coverage data
        build_dir = self.path_manager.build_dir
        if build_dir.exists():
            # Remove .gcda files (GCC coverage data)
            gcda_files = list(build_dir.rglob('*.gcda'))
            for gcda_file in gcda_files:
                try:
                    gcda_file.unlink()
                    self.logger.debug(f"Removed {gcda_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove {gcda_file}: {e}")

            # Remove .profraw files (Clang coverage data)
            profraw_files = list(build_dir.rglob('*.profraw'))
            for profraw_file in profraw_files:
                try:
                    profraw_file.unlink()
                    self.logger.debug(f"Removed {profraw_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove {profraw_file}: {e}")

            # Remove .profdata files (Clang merged data)
            profdata_files = list(build_dir.rglob('*.profdata'))
            for profdata_file in profdata_files:
                try:
                    profdata_file.unlink()
                    self.logger.debug(f"Removed {profdata_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove {profdata_file}: {e}")

            if gcda_files or profraw_files or profdata_files:
                self.logger.info(f"Cleaned {len(gcda_files)} .gcda, {len(profraw_files)} .profraw, and {len(profdata_files)} .profdata files")

        self.logger.success("Coverage data cleaned")
        return True
    
    def build(self) -> bool:
        """
        Build the project with coverage instrumentation.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Building project with coverage instrumentation...")
        
        # Ensure proper CMake configuration
        if not self.cmake_helper.ensure_build_configured():
            return False
        
        # Build the project
        if not self.cmake_helper.build_project():
            self.logger.error("Project build failed")
            return False
        
        self.logger.success("Project built successfully with coverage instrumentation")
        return True
    
    def test(self, test_command: str | List[str]) -> bool:
        """
        Run tests with coverage data collection.

        Args:
            test_command: Test command to execute. Must be specified explicitly.
                         Examples:
                         - "python -m pytest tests/"
                         - ["python", "-m", "unittest", "discover"]
                         - "./run_tests.sh"

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Running tests with coverage data collection...")

        # Parse and prepare test command
        if isinstance(test_command, list):
            parsed_command = TestExecutor.parse_test_command(test_command)
        else:
            parsed_command = test_command

        # Set up environment for coverage
        env = os.environ.copy()
        compiler = self.compiler_detector.detect_compiler()

        if compiler == 'clang':
            # Set LLVM_PROFILE_FILE for Clang coverage
            coverage_dir = self.path_manager.ensure_coverage_dir()
            env['LLVM_PROFILE_FILE'] = str(coverage_dir / 'coverage-%p.profraw')
            self.logger.info(f"Using Clang coverage with LLVM_PROFILE_FILE={env['LLVM_PROFILE_FILE']}")

        # Execute test command using TestExecutor
        return self.test_executor.execute_test_command(
            parsed_command,
            env=env,
            timeout=600
        )
    
    def report(self) -> bool:
        """
        Generate coverage reports.

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Generating coverage reports...")

        # Generate standard coverage report using pure Python
        compiler = self.compiler_detector.detect_compiler()
        executables = self._find_executables()

        # First collect coverage files from build directory
        profraw_count, gcda_count = self.file_manager.collect_coverage_files()

        if profraw_count == 0 and gcda_count == 0:
            self.logger.warning("No coverage files found to generate report")
            return False

        # Merge coverage data (standard mode, not incremental)
        if not self.file_manager.merge_coverage_data(compiler, incremental=False):
            self.logger.error("Failed to merge coverage data")
            return False

        # Generate report
        if not self.file_manager.generate_standard_report(compiler, executables):
            self.logger.error("Coverage report generation failed")
            return False

        # Check if reports were generated
        coverage_dir = self.path_manager.coverage_dir
        html_dir = coverage_dir / 'html'

        if html_dir.exists() and (html_dir / 'index.html').exists():
            self.logger.success(f"Coverage report generated: {html_dir / 'index.html'}")
        else:
            self.logger.warning("HTML report not found, but report generation completed")

        return True

    def _find_executables(self) -> List[Path]:
        """
        Find executable files for coverage reporting.

        Returns:
            List of executable paths
        """
        executables = []
        build_dir = self.path_manager.build_dir

        if not build_dir.exists():
            return executables

        # First check specific known locations
        known_executables = [
            self.path_manager.algorithm_cli,
            self.path_manager.statistics_cli
        ]

        for exe_path in known_executables:
            if exe_path.exists():
                executables.append(exe_path)

        # If no known executables found, look for common patterns
        if not executables:
            for pattern in ['*_cli', '*_app', '*_test']:
                for exe_file in build_dir.rglob(pattern):
                    # Skip CMake temporary files
                    if 'CMakeFiles' in str(exe_file):
                        continue
                    if exe_file.is_file() and os.access(exe_file, os.X_OK):
                        executables.append(exe_file)

        return executables

    def full_workflow(self, test_command: str | List[str]) -> bool:
        """
        Run the complete coverage workflow: clean, build, test, report.

        Args:
            test_command: Test command to execute. Must be specified explicitly.
                         Examples:
                         - "python -m pytest tests/"
                         - ["python", "-m", "unittest", "discover"]
                         - "./run_tests.sh"

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Starting full coverage workflow...")

        # Clean previous data
        if not self.clean():
            return False

        # Build with coverage
        if not self.build():
            return False

        # Run tests
        if not self.test(test_command):
            return False
        
        # Generate reports
        if not self.report():
            return False
        
        self.logger.success("Full coverage workflow completed successfully")
        return True
    
    def status(self) -> dict:
        """
        Get current coverage status information.
        
        Returns:
            Dictionary with status information
        """
        status = {
            'project_root': str(self.path_manager.project_root),
            'build_configured': self.path_manager.validate_build_dir(),
            'coverage_enabled': self.path_manager.validate_coverage_build(),
            'compiler': self.compiler_detector.detect_compiler(),
            'coverage_tools': self.compiler_detector.find_coverage_tools(),
            'coverage_data_exists': False,
            'reports_exist': False
        }
        
        # Check for coverage data
        coverage_dir = self.path_manager.coverage_dir
        if coverage_dir.exists():
            # Check for .profraw files (Clang)
            profraw_files = list(coverage_dir.rglob('*.profraw'))
            # Check for .gcda files (GCC)
            gcda_files = list(self.path_manager.build_dir.rglob('*.gcda'))
            
            status['coverage_data_exists'] = len(profraw_files) > 0 or len(gcda_files) > 0
            status['profraw_count'] = len(profraw_files)
            status['gcda_count'] = len(gcda_files)
        
        # Check for reports
        html_dir = coverage_dir / 'html'
        if html_dir.exists() and (html_dir / 'index.html').exists():
            status['reports_exist'] = True
            status['html_report'] = str(html_dir / 'index.html')
        
        return status
