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
from typing import List, Optional, Union

from pydcov.utils.compiler_detection import CompilerDetector
from pydcov.utils.logging_config import get_logger
from pydcov.utils.path_utils import PathManager
from pydcov.utils.cmake_integration import CMakeHelper
from pydcov.utils.test_executor import TestExecutor


class IncrementalCoverageManager:
    """Manages incremental coverage collection and reporting workflows."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.logger = get_logger()
        self.path_manager = PathManager(project_root)
        self.cmake_helper = CMakeHelper(self.path_manager)
        self.compiler_detector = CompilerDetector()
        self.test_executor = TestExecutor(self.path_manager.project_root, self.logger)

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
        
        # Run CMake initialization target
        if not self.cmake_helper.run_incremental_init():
            self.logger.error("Incremental coverage initialization failed")
            return False
        
        # Ensure incremental directory exists
        self.path_manager.ensure_incremental_dir()
        
        self.logger.success("Incremental coverage initialized")
        return True
    
    def add(self, test_command: Union[str, List[str]]) -> bool:
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
        self.logger.step("Running tests and adding coverage data...")

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
            env['LLVM_PROFILE_FILE'] = str(coverage_dir / 'coverage-%p.profraw')
            self.logger.info(f"Using Clang coverage with LLVM_PROFILE_FILE={env['LLVM_PROFILE_FILE']}")

        # Execute test command using TestExecutor
        if not self.test_executor.execute_test_command(
            parsed_command,
            env=env,
            timeout=600
        ):
            return False
        
        # Add coverage data to incremental collection
        if not self.cmake_helper.run_incremental_add():
            self.logger.error("Failed to add coverage data to incremental collection")
            return False
        
        # Copy coverage files to incremental directory
        return self._copy_coverage_files()
    
    def _copy_coverage_files(self) -> bool:
        """Copy coverage files to incremental directory."""
        compiler = self.compiler_detector.detect_compiler()
        coverage_dir = self.path_manager.coverage_dir
        incremental_dir = self.path_manager.ensure_incremental_dir()
        
        if compiler == 'clang':
            # Copy .profraw files
            profraw_files = list(coverage_dir.glob('*.profraw'))
            if profraw_files:
                for profraw_file in profraw_files:
                    try:
                        shutil.copy2(profraw_file, incremental_dir)
                    except Exception as e:
                        self.logger.warning(f"Failed to copy {profraw_file}: {e}")
                
                self.logger.info(f"Copied {len(profraw_files)} profraw files to incremental collection")
                self.logger.success("Coverage data added to incremental collection")
                return True
            else:
                self.logger.warning("No profraw files found to copy")
                return False
        else:
            # For GCC, copy .info files if they exist
            info_files = list(coverage_dir.glob('*.info'))
            if info_files:
                for info_file in info_files:
                    try:
                        # Copy with timestamp to avoid overwriting
                        import time
                        timestamp = int(time.time())
                        dest_name = f"{info_file.stem}_{timestamp}.info"
                        shutil.copy2(info_file, incremental_dir / dest_name)
                    except Exception as e:
                        self.logger.warning(f"Failed to copy {info_file}: {e}")
                
                self.logger.info(f"Copied {len(info_files)} info files to incremental collection")
                self.logger.success("Coverage data added to incremental collection")
                return True
            else:
                self.logger.warning("No info files found to copy")
                return False
    
    def merge(self) -> bool:
        """
        Merge all accumulated coverage data.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Merging all incremental coverage data...")
        
        # Run CMake merge target
        if not self.cmake_helper.run_incremental_merge():
            self.logger.error("CMake incremental merge failed")
            return False
        
        # Perform the actual merging
        return self._merge_coverage_files()
    
    def _merge_coverage_files(self) -> bool:
        """Merge coverage files in incremental directory."""
        compiler = self.compiler_detector.detect_compiler()
        incremental_dir = self.path_manager.ensure_incremental_dir()
        coverage_dir = self.path_manager.coverage_dir
        
        if compiler == 'clang':
            # Merge .profraw files
            profraw_files = list(incremental_dir.glob('*.profraw'))
            if not profraw_files:
                self.logger.warning("No profraw files found in incremental directory")
                return False
            
            self.logger.info(f"Merging {len(profraw_files)} profraw files...")
            
            # Find llvm-profdata
            tools = self.compiler_detector.find_coverage_tools(compiler)
            llvm_profdata = tools.get('llvm_profdata')
            
            if not llvm_profdata:
                self.logger.error("llvm-profdata not found")
                return False
            
            # Merge files
            output_file = coverage_dir / 'incremental_merged.profdata'
            cmd = [llvm_profdata, 'merge', '-sparse'] + [str(f) for f in profraw_files] + ['-o', str(output_file)]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    self.logger.success(f"Merged profraw files into {output_file.name}")
                    return True
                else:
                    self.logger.error(f"llvm-profdata merge failed: {result.stderr}")
                    return False
            except Exception as e:
                self.logger.error(f"Failed to merge profraw files: {e}")
                return False
        
        else:
            # Merge .info files for GCC
            info_files = list(incremental_dir.glob('*.info'))
            if not info_files:
                self.logger.warning("No info files found in incremental directory")
                return False
            
            self.logger.info(f"Merging {len(info_files)} info files...")
            
            # Find lcov
            tools = self.compiler_detector.find_coverage_tools(compiler)
            lcov = tools.get('lcov')
            
            if not lcov:
                self.logger.error("lcov not found")
                return False
            
            # Build lcov command
            output_file = coverage_dir / 'incremental_merged.info'
            cmd = [lcov]
            
            for info_file in info_files:
                cmd.extend(['--add-tracefile', str(info_file)])
            
            cmd.extend([
                '--output-file', str(output_file),
                '--rc', 'branch_coverage=1',
                '--ignore-errors', 'unused,source'
            ])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    # Remove system files
                    self._filter_lcov_output(output_file, lcov)
                    self.logger.success(f"Merged info files into {output_file.name}")
                    return True
                else:
                    self.logger.error(f"lcov merge failed: {result.stderr}")
                    return False
            except Exception as e:
                self.logger.error(f"Failed to merge info files: {e}")
                return False
    
    def _filter_lcov_output(self, info_file: Path, lcov: str):
        """Filter system files from lcov output."""
        try:
            # Remove system files
            cmd = [
                lcov, '--remove', str(info_file),
                '/usr/*', '*/usr/*',
                '--output-file', str(info_file),
                '--rc', 'branch_coverage=1',
                '--ignore-errors', 'unused,source'
            ]
            subprocess.run(cmd, capture_output=True, timeout=60)
            
            # Remove test files
            cmd = [
                lcov, '--remove', str(info_file),
                '*/test/*', '*/tests/*', '*/testing/*', '*/gtest/*', '*/catch/*', '*/benchmark/*',
                '--output-file', str(info_file),
                '--rc', 'branch_coverage=1',
                '--ignore-errors', 'unused,source'
            ]
            subprocess.run(cmd, capture_output=True, timeout=60)
            
        except Exception as e:
            self.logger.warning(f"Failed to filter lcov output: {e}")
    
    def report(self) -> bool:
        """
        Generate final comprehensive coverage report.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Generating final comprehensive coverage report...")
        
        # Run CMake report target
        if not self.cmake_helper.run_incremental_report():
            self.logger.error("Incremental coverage report generation failed")
            return False
        
        # Check if reports were generated
        coverage_dir = self.path_manager.coverage_dir
        report_dir = coverage_dir / 'incremental_report'
        
        if report_dir.exists() and (report_dir / 'index.html').exists():
            self.logger.success(f"Final coverage report generated")
            self.logger.success(f"Report available at: {report_dir / 'index.html'}")
        else:
            self.logger.warning("HTML report not found, but CMake target completed")

        return True

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
        status = {
            'compiler': self.compiler_detector.detect_compiler(),
            'incremental_dir_exists': False,
            'accumulated_files': 0,
            'merged_data_exists': False,
            'report_exists': False
        }

        coverage_dir = self.path_manager.coverage_dir
        incremental_dir = coverage_dir / 'incremental'

        # Check incremental directory
        if incremental_dir.exists():
            status['incremental_dir_exists'] = True

            compiler = status['compiler']
            if compiler == 'clang':
                profraw_files = list(incremental_dir.glob('*.profraw'))
                status['accumulated_files'] = len(profraw_files)
            else:
                info_files = list(incremental_dir.glob('*.info'))
                status['accumulated_files'] = len(info_files)

        # Check for merged data
        compiler = status['compiler']
        if compiler == 'clang':
            merged_file = coverage_dir / 'incremental_merged.profdata'
        else:
            merged_file = coverage_dir / 'incremental_merged.info'

        status['merged_data_exists'] = merged_file.exists()
        if status['merged_data_exists']:
            status['merged_file'] = str(merged_file)

        # Check for final report
        report_dir = coverage_dir / 'incremental_report'
        if report_dir.exists() and (report_dir / 'index.html').exists():
            status['report_exists'] = True
            status['report_path'] = str(report_dir / 'index.html')

        return status

    def full_workflow(self, test_command: Union[str, List[str]]) -> bool:
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
