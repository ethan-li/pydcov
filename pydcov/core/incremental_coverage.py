"""
Incremental coverage manager for accumulating coverage across multiple test runs.

This module provides incremental coverage functionality equivalent to the
incremental coverage collection workflow, allowing coverage data to be
accumulated across multiple pytest executions.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List

from pydcov.utils.compiler_detection import CompilerDetector
from pydcov.utils.logging_config import get_logger
from pydcov.utils.path_utils import PathManager
from pydcov.utils.cmake_integration import CMakeHelper
from pydcov.utils.test_executor import TestExecutor
from pydcov.utils.coverage_file_manager import CoverageFileManager


class IncrementalCoverageManager:
    """Manages incremental coverage collection and reporting workflows."""
    
    def __init__(self, project_root: Path | None = None):
        self.logger = get_logger()
        self.path_manager = PathManager(project_root)
        self.cmake_helper = CMakeHelper(self.path_manager)
        self.compiler_detector = CompilerDetector()
        self.test_executor = TestExecutor(self.path_manager.project_root, self.logger)

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
    
    def init(self) -> bool:
        """
        Initialize incremental coverage collection.

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Initializing incremental coverage collection...")

        # Ensure proper CMake configuration
        if not self.cmake_helper.ensure_build_configured():
            return False

        # Initialize incremental coverage using pure Python
        if not self.file_manager.init_incremental():
            self.logger.error("Incremental coverage initialization failed")
            return False

        self.logger.success("Incremental coverage initialized")
        return True
    
    def add(self, test_command: str | List[str]) -> bool:
        """
        Run tests and add coverage data to incremental collection.

        Args:
            test_command: Test command to execute. Must be specified explicitly.
                         Examples:
                         - "python -m pytest tests/"
                         - ["python", "-m", "unittest", "discover"]
                         - "./run_tests.sh"

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Running tests and collecting coverage data...")

        # Parse and prepare test command
        if isinstance(test_command, list):
            parsed_command = TestExecutor.parse_test_command(test_command)
        else:
            parsed_command = test_command

        # Ensure build is ready
        if not self.path_manager.validate_coverage_build():
            self.logger.error("Coverage build not configured")
            return False

        # Set up environment for coverage
        env = os.environ.copy()
        compiler = self.compiler_detector.detect_compiler()

        if compiler == 'clang':
            # Set LLVM_PROFILE_FILE for Clang coverage
            coverage_dir = self.path_manager.ensure_coverage_dir()
            env['LLVM_PROFILE_FILE'] = str(coverage_dir / 'coverage-%p-%m.profraw')
            self.logger.info(f"Using Clang coverage with LLVM_PROFILE_FILE={env['LLVM_PROFILE_FILE']}")

        # Execute test command using TestExecutor
        if not self.test_executor.execute_test_command(
            parsed_command,
            env=env,
            timeout=600
        ):
            return False

        # Collect all coverage files generated during testing using pure Python
        profraw_count, gcda_count = self.file_manager.collect_coverage_files()

        if profraw_count == 0 and gcda_count == 0:
            self.logger.warning("No coverage files were collected")
            return False

        # Show collection results
        self._show_collection_status()
        return True

    def _show_collection_status(self) -> None:
        """Show status of collected coverage files."""
        status = self.file_manager.get_status()

        if status['profraw_count'] > 0:
            self.logger.info(f"Collected {status['profraw_count']} Clang coverage files")
        if status['gcda_count'] > 0:
            self.logger.info(f"Collected {status['gcda_count']} GCC coverage files")

        if status['profraw_count'] == 0 and status['gcda_count'] == 0:
            self.logger.warning("No coverage files were collected")


    def merge(self) -> bool:
        """
        Merge all accumulated coverage data.

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Merging all incremental coverage data...")

        # Merge coverage data using pure Python
        compiler = self.compiler_detector.detect_compiler()
        if not self.file_manager.merge_coverage_data(compiler):
            self.logger.error("Coverage data merge failed")
            return False

        self.logger.success("Coverage data merged successfully")
        return True
    

    def report(self) -> bool:
        """
        Generate final comprehensive coverage report.

        Automatically merges coverage data if needed before generating the report.

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Generating final comprehensive coverage report...")

        # Check if merged data exists, if not, merge automatically
        compiler = self.compiler_detector.detect_compiler()
        coverage_dir = self.path_manager.coverage_dir

        if compiler == 'clang':
            merged_file = coverage_dir / 'incremental_merged.profdata'
        else:  # gcc
            merged_file = coverage_dir / 'incremental_merged.info'

        if not merged_file.exists():
            self.logger.info("Merged coverage data not found, merging automatically...")
            if not self.merge():
                self.logger.error("Automatic merge failed")
                return False

        # Generate report using pure Python
        executables = self._find_executables()

        if not self.file_manager.generate_report(compiler, executables):
            self.logger.error("Incremental coverage report generation failed")
            return False

        # Check if reports were generated
        coverage_dir = self.path_manager.coverage_dir
        report_dir = coverage_dir / 'incremental_report'

        if report_dir.exists() and (report_dir / 'index.html').exists():
            self.logger.success(f"Final coverage report generated")
            self.logger.success(f"Report available at: {report_dir / 'index.html'}")
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

    def clean(self) -> bool:
        """
        Clean all incremental coverage data.

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Cleaning incremental coverage data...")

        coverage_dir = self.path_manager.coverage_dir

        # Remove incremental directory
        incremental_dir = coverage_dir / 'incremental'
        if incremental_dir.exists():
            shutil.rmtree(incremental_dir)
            self.logger.info("Removed incremental coverage directory")

        # Remove merged files
        merged_files = [
            coverage_dir / 'incremental_merged.profdata',
            coverage_dir / 'incremental_merged.info'
        ]

        for merged_file in merged_files:
            if merged_file.exists():
                merged_file.unlink()
                self.logger.info(f"Removed {merged_file.name}")

        # Remove incremental report
        report_dir = coverage_dir / 'incremental_report'
        if report_dir.exists():
            shutil.rmtree(report_dir)
            self.logger.info("Removed incremental report directory")

        self.logger.success("Incremental coverage data cleaned")
        return True

    def status(self) -> dict:
        """
        Get current incremental coverage status.

        Returns:
            Dictionary with status information
        """
        # Get status from file manager
        file_status = self.file_manager.get_status()

        # Add additional information
        status = {
            'project_root': str(self.path_manager.project_root),
            'compiler': self.compiler_detector.detect_compiler(),
            'incremental_dir_exists': file_status['incremental_dir_exists'],
            'profraw_count': file_status['profraw_count'],
            'gcda_count': file_status['gcda_count'],
            'accumulated_files': file_status['profraw_count'] + file_status['gcda_count'],
            'merged_data_exists': file_status.get('merged_profdata_exists', False) or file_status.get('merged_info_exists', False),
            'report_exists': file_status['report_exists']
        }

        # Add file paths if they exist
        coverage_dir = self.path_manager.coverage_dir
        compiler = status['compiler']

        if compiler == 'clang':
            merged_file = coverage_dir / 'incremental_merged.profdata'
            if merged_file.exists():
                status['merged_file'] = str(merged_file)
        else:
            merged_file = coverage_dir / 'incremental_merged.info'
            if merged_file.exists():
                status['merged_file'] = str(merged_file)

        # Check for final report
        report_dir = coverage_dir / 'incremental_report'
        if report_dir.exists() and (report_dir / 'index.html').exists():
            status['report_path'] = str(report_dir / 'index.html')

        return status

    def full_workflow(self, test_command: str | List[str]) -> bool:
        """
        Run complete incremental coverage workflow: init, add, merge, report.

        Args:
            test_command: Test command to execute. Must be specified explicitly.
                         Examples:
                         - "python -m pytest tests/"
                         - ["python", "-m", "unittest", "discover"]
                         - "./run_tests.sh"

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Starting incremental coverage full workflow...")

        # Initialize
        if not self.init():
            return False

        # Add coverage data
        if not self.add(test_command):
            return False

        # Merge data
        if not self.merge():
            return False

        # Generate report
        if not self.report():
            return False

        self.logger.success("Incremental coverage workflow completed successfully")
        return True
