"""
Module-specific coverage manager for generating targeted coverage reports.

This module provides module-specific coverage functionality equivalent to the
module-specific coverage workflow, allowing coverage reports to be
generated for individual modules (algorithm, statistics).
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Set, Union

from ..utils.compiler_detection import CompilerDetector
from ..utils.logging_config import get_logger
from ..utils.path_utils import PathManager
from ..utils.cmake_integration import CMakeHelper
from ..utils.test_executor import TestExecutor


class ModuleCoverageManager:
    """Manages module-specific coverage collection and reporting workflows."""
    
    SUPPORTED_MODULES = {'algorithm', 'statistics'}
    
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
    
    def build(self) -> bool:
        """
        Build project with coverage instrumentation.
        
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
    
    def test(self, module: Optional[str] = None, test_command: Optional[Union[str, List[str]]] = None) -> bool:
        """
        Run tests with coverage data collection.

        Args:
            module: Specific module to test ('algorithm' or 'statistics').
                   If None, runs all tests (requires test_command).
            test_command: Test command to execute. Required when module is None.
                         When module is specified, defaults to pytest with module path.
                         Examples:
                         - "python -m pytest tests/"
                         - ["python", "-m", "unittest", "discover"]
                         - "./run_tests.sh"

        Returns:
            True if successful, False otherwise
        """
        if module and module not in self.SUPPORTED_MODULES:
            self.logger.error(f"Unsupported module: {module}. Supported: {', '.join(self.SUPPORTED_MODULES)}")
            return False
        
        # Determine test command
        if test_command is None:
            if module:
                # Use default pytest command with module-specific path
                self.logger.step(f"Running {module} module tests with coverage data collection...")
                parsed_command = ["python3", "-m", "pytest", f"{module}/tests/", "-v"]
            else:
                # Require explicit test command when no module specified
                self.logger.error("Test command is required when no specific module is specified. "
                                "Please provide a test command or specify a module.")
                return False
        else:
            # Use custom test command
            if module:
                self.logger.step(f"Running {module} module tests with custom command...")
            else:
                self.logger.step("Running tests with custom command...")

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
    
    def generate_module_reports(self, module: Optional[str] = None) -> bool:
        """
        Generate module-specific coverage reports.
        
        Args:
            module: Specific module ('algorithm' or 'statistics').
                   If None, generates reports for all modules.
        
        Returns:
            True if successful, False otherwise
        """
        if module and module not in self.SUPPORTED_MODULES:
            self.logger.error(f"Unsupported module: {module}. Supported: {', '.join(self.SUPPORTED_MODULES)}")
            return False
        
        modules_to_process = [module] if module else list(self.SUPPORTED_MODULES)
        
        self.logger.step(f"Generating coverage reports for: {', '.join(modules_to_process)}")
        
        success = True
        for mod in modules_to_process:
            if not self._generate_single_module_report(mod):
                success = False
        
        if success:
            self.logger.success("Module coverage reports generated successfully")
        else:
            self.logger.error("Some module coverage reports failed")
        
        return success
    
    def _generate_single_module_report(self, module: str) -> bool:
        """Generate coverage report for a single module."""
        self.logger.info(f"Generating coverage report for {module} module...")
        
        compiler = self.compiler_detector.detect_compiler()
        coverage_dir = self.path_manager.coverage_dir
        module_dir = self.path_manager.get_module_coverage_dir(module)
        
        # Get source files for the module
        source_files = self.path_manager.get_source_files(module)
        if not source_files:
            self.logger.warning(f"No source files found for {module} module")
            return False
        
        if compiler == 'clang':
            return self._generate_clang_module_report(module, source_files, module_dir)
        else:
            return self._generate_gcc_module_report(module, source_files, module_dir)
    
    def _generate_clang_module_report(self, module: str, source_files: List[str], output_dir: Path) -> bool:
        """Generate Clang coverage report for a module."""
        coverage_dir = self.path_manager.coverage_dir
        
        # Find coverage data files
        profraw_files = list(coverage_dir.glob('*.profraw'))
        if not profraw_files:
            self.logger.error(f"No .profraw files found for {module} module")
            return False
        
        # Get tools
        tools = self.compiler_detector.find_coverage_tools('clang')
        llvm_profdata = tools.get('llvm_profdata')
        llvm_cov = tools.get('llvm_cov')
        
        if not llvm_profdata or not llvm_cov:
            self.logger.error("Required LLVM tools not found")
            return False
        
        # Merge profraw files
        profdata_file = coverage_dir / f'{module}.profdata'
        merge_cmd = [llvm_profdata, 'merge', '-sparse'] + [str(f) for f in profraw_files] + ['-o', str(profdata_file)]
        
        try:
            result = subprocess.run(merge_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.logger.error(f"Failed to merge profraw files: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to merge profraw files: {e}")
            return False
        
        # Get executable for the module
        executable = self.path_manager.get_executable_path(module)
        if not executable:
            self.logger.error(f"Executable not found for {module} module")
            return False
        
        # Generate HTML report
        html_dir = output_dir / 'html'
        html_dir.mkdir(parents=True, exist_ok=True)
        
        html_cmd = [
            llvm_cov, 'show',
            str(executable),
            f'-instr-profile={profdata_file}',
            '-format=html',
            f'-output-dir={html_dir}',
            '-show-line-counts-or-regions',
            '-show-instantiations=false'
        ]
        
        # Add source file filters
        for source_file in source_files:
            html_cmd.append(source_file)
        
        try:
            result = subprocess.run(html_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.logger.error(f"Failed to generate HTML report: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")
            return False
        
        # Generate LCOV report
        lcov_file = output_dir / f'{module}.info'
        lcov_cmd = [
            llvm_cov, 'export',
            str(executable),
            f'-instr-profile={profdata_file}',
            '-format=lcov'
        ]
        
        # Add source file filters
        for source_file in source_files:
            lcov_cmd.append(source_file)
        
        try:
            with open(lcov_file, 'w') as f:
                result = subprocess.run(lcov_cmd, stdout=f, stderr=subprocess.PIPE, text=True, timeout=120)
                if result.returncode != 0:
                    self.logger.error(f"Failed to generate LCOV report: {result.stderr}")
                    return False
        except Exception as e:
            self.logger.error(f"Failed to generate LCOV report: {e}")
            return False
        
        self.logger.success(f"Generated {module} module coverage report: {html_dir / 'index.html'}")
        return True
    
    def _generate_gcc_module_report(self, module: str, source_files: List[str], output_dir: Path) -> bool:
        """Generate GCC coverage report for a module."""
        # Find .gcda files
        gcda_files = list(self.path_manager.build_dir.rglob('*.gcda'))
        if not gcda_files:
            self.logger.error(f"No .gcda files found for {module} module")
            return False
        
        # Get tools
        tools = self.compiler_detector.find_coverage_tools('gcc')
        lcov = tools.get('lcov')
        genhtml = tools.get('genhtml')
        
        if not lcov or not genhtml:
            self.logger.error("Required GCC tools not found")
            return False
        
        # Generate LCOV info file
        info_file = output_dir / f'{module}.info'
        
        # Create include patterns for module source files
        include_patterns = []
        for source_file in source_files:
            include_patterns.extend(['--include', source_file])
        
        lcov_cmd = [
            lcov,
            '--capture',
            '--directory', str(self.path_manager.build_dir),
            '--output-file', str(info_file),
            '--rc', 'branch_coverage=1',
            '--ignore-errors', 'unused,source'
        ] + include_patterns
        
        try:
            result = subprocess.run(lcov_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.logger.error(f"Failed to generate LCOV info: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to generate LCOV info: {e}")
            return False
        
        # Generate HTML report
        html_dir = output_dir / 'html'
        html_dir.mkdir(parents=True, exist_ok=True)
        
        genhtml_cmd = [
            genhtml,
            str(info_file),
            '--output-directory', str(html_dir),
            '--title', f'{module.title()} Module Coverage',
            '--show-details',
            '--legend',
            '--rc', 'branch_coverage=1'
        ]
        
        try:
            result = subprocess.run(genhtml_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.logger.error(f"Failed to generate HTML report: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")
            return False
        
        self.logger.success(f"Generated {module} module coverage report: {html_dir / 'index.html'}")
        return True

    def clean(self) -> bool:
        """
        Clean module coverage data.

        Returns:
            True if successful, False otherwise
        """
        self.logger.step("Cleaning module coverage data...")

        coverage_dir = self.path_manager.coverage_dir

        # Clean module directories
        for module in self.SUPPORTED_MODULES:
            module_dir = coverage_dir / module
            if module_dir.exists():
                import shutil
                shutil.rmtree(module_dir)
                self.logger.info(f"Cleaned {module} module coverage data")

        self.logger.success("Module coverage data cleaned")
        return True

    def full_workflow(self, module: Optional[str] = None, test_command: Optional[Union[str, List[str]]] = None) -> bool:
        """
        Run complete module coverage workflow: build, test, generate reports.

        Args:
            module: Specific module to process. If None, processes all modules
                   (requires test_command).
            test_command: Test command to execute. Required when module is None.
                         When module is specified, defaults to pytest with module path.
                         Examples:
                         - "python -m pytest tests/"
                         - ["python", "-m", "unittest", "discover"]
                         - "./run_tests.sh"

        Returns:
            True if successful, False otherwise
        """
        if module:
            self.logger.step(f"Starting module coverage workflow for {module}...")
        else:
            self.logger.step("Starting module coverage workflow for all modules...")

        # Build with coverage
        if not self.build():
            return False

        # Run tests
        if not self.test(module, test_command):
            return False

        # Generate reports
        if not self.generate_module_reports(module):
            return False

        self.logger.success("Module coverage workflow completed successfully")
        return True

    def status(self, module: Optional[str] = None) -> dict:
        """
        Get module coverage status information.

        Args:
            module: Specific module to check. If None, checks all modules.

        Returns:
            Dictionary with status information
        """
        status = {
            'compiler': self.compiler_detector.detect_compiler(),
            'modules': {}
        }

        modules_to_check = [module] if module else list(self.SUPPORTED_MODULES)

        for mod in modules_to_check:
            module_status = {
                'source_files': len(self.path_manager.get_source_files(mod)),
                'executable_exists': self.path_manager.get_executable_path(mod) is not None,
                'coverage_data_exists': False,
                'report_exists': False
            }

            # Check for coverage data
            coverage_dir = self.path_manager.coverage_dir
            module_dir = coverage_dir / mod

            if module_dir.exists():
                html_dir = module_dir / 'html'
                if html_dir.exists() and (html_dir / 'index.html').exists():
                    module_status['report_exists'] = True
                    module_status['report_path'] = str(html_dir / 'index.html')

            # Check for general coverage data
            compiler = status['compiler']
            if compiler == 'clang':
                profraw_files = list(coverage_dir.glob('*.profraw'))
                module_status['coverage_data_exists'] = len(profraw_files) > 0
            else:
                gcda_files = list(self.path_manager.build_dir.rglob('*.gcda'))
                module_status['coverage_data_exists'] = len(gcda_files) > 0

            status['modules'][mod] = module_status

        return status
