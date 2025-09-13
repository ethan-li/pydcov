"""
Pure Python coverage file management.

This module handles coverage file collection, merging, and report generation
without relying on CMake targets or shell scripts.
"""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from pydcov.utils.coverage_tools import CoverageToolManager
from pydcov.utils.logging_config import get_logger


class CoverageFileManager:
    """Manages coverage file operations using pure Python."""
    
    def __init__(self, build_dir: Path, coverage_dir: Path):
        self.build_dir = Path(build_dir)
        self.coverage_dir = Path(coverage_dir)
        self.incremental_dir = self.coverage_dir / 'incremental'
        self.logger = get_logger()
        self.tool_manager = CoverageToolManager()
    
    def init_incremental(self) -> bool:
        """
        Initialize incremental coverage collection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove existing incremental directory
            if self.incremental_dir.exists():
                shutil.rmtree(self.incremental_dir)
            
            # Create fresh incremental directory
            self.incremental_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Incremental coverage initialized at {self.incremental_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize incremental coverage: {e}")
            return False
    
    def collect_coverage_files(self) -> Tuple[int, int]:
        """
        Collect coverage files from build directory to incremental directory.
        
        Returns:
            Tuple of (profraw_count, gcda_count)
        """
        self.incremental_dir.mkdir(parents=True, exist_ok=True)
        
        profraw_count = 0
        gcda_count = 0
        
        try:
            # Collect .profraw files (Clang)
            profraw_files = list(self.build_dir.rglob('*.profraw'))
            # Exclude files already in incremental directory
            profraw_files = [f for f in profraw_files if not str(f).startswith(str(self.incremental_dir))]
            
            for profraw_file in profraw_files:
                try:
                    dest = self.incremental_dir / profraw_file.name
                    shutil.copy2(profraw_file, dest)
                    profraw_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to copy {profraw_file}: {e}")
            
            # Collect .gcda files (GCC)
            gcda_files = list(self.build_dir.rglob('*.gcda'))
            gcda_files = [f for f in gcda_files if not str(f).startswith(str(self.incremental_dir))]
            
            for gcda_file in gcda_files:
                try:
                    dest = self.incremental_dir / gcda_file.name
                    shutil.copy2(gcda_file, dest)
                    gcda_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to copy {gcda_file}: {e}")
            
            # Also collect .gcno files for GCC
            gcno_files = list(self.build_dir.rglob('*.gcno'))
            gcno_files = [f for f in gcno_files if not str(f).startswith(str(self.incremental_dir))]
            
            for gcno_file in gcno_files:
                try:
                    dest = self.incremental_dir / gcno_file.name
                    shutil.copy2(gcno_file, dest)
                except Exception as e:
                    self.logger.warning(f"Failed to copy {gcno_file}: {e}")
            
            self.logger.info(f"Collected {profraw_count} .profraw files and {gcda_count} .gcda files")
            return profraw_count, gcda_count
            
        except Exception as e:
            self.logger.error(f"Failed to collect coverage files: {e}")
            return 0, 0
    
    def merge_coverage_data(self, compiler: str = None, incremental: bool = True) -> bool:
        """
        Merge collected coverage data.

        Args:
            compiler: Compiler type ('clang' or 'gcc')
            incremental: Whether this is for incremental coverage (True) or standard coverage (False)

        Returns:
            True if successful, False otherwise
        """
        if compiler is None:
            compiler = self.tool_manager.detect_compiler()

        self.coverage_dir.mkdir(parents=True, exist_ok=True)

        if compiler == 'clang':
            return self._merge_clang_data(incremental)
        elif compiler == 'gcc':
            return self._merge_gcc_data(incremental)
        else:
            self.logger.error(f"Unsupported compiler: {compiler}")
            return False
    
    def _merge_clang_data(self, incremental: bool = True) -> bool:
        """Merge Clang coverage data using llvm-profdata."""
        tools = self.tool_manager.get_coverage_tools('clang')
        llvm_profdata = tools.get('llvm_profdata')

        if not llvm_profdata:
            self.logger.error("llvm-profdata not found")
            return False

        if incremental:
            # Find .profraw files in incremental directory
            profraw_files = list(self.incremental_dir.glob('*.profraw'))
            output_file = self.coverage_dir / 'incremental_merged.profdata'
            source_desc = "incremental directory"
        else:
            # For standard coverage, look in build directory and coverage directory
            profraw_files = list(self.build_dir.rglob('*.profraw'))
            # Exclude files already in incremental directory
            profraw_files = [f for f in profraw_files if not str(f).startswith(str(self.incremental_dir))]
            output_file = self.coverage_dir / 'merged.profdata'
            source_desc = "build directory"

        if not profraw_files:
            self.logger.warning(f"No .profraw files found in {source_desc}")
            return False

        try:
            cmd = [llvm_profdata, 'merge', '-sparse'] + [str(f) for f in profraw_files] + ['-o', str(output_file)]

            self.logger.info(f"Merging {len(profraw_files)} .profraw files...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                self.logger.success(f"Successfully merged coverage data to {output_file}")
                return True
            else:
                self.logger.error(f"llvm-profdata merge failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("llvm-profdata merge timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to merge Clang coverage data: {e}")
            return False
    
    def _merge_gcc_data(self, incremental: bool = True) -> bool:
        """Merge GCC coverage data using lcov."""
        tools = self.tool_manager.get_coverage_tools('gcc')
        lcov = tools.get('lcov')

        if not lcov:
            self.logger.error("lcov not found")
            return False

        if incremental:
            # Check for .gcda files in incremental directory
            gcda_files = list(self.incremental_dir.glob('*.gcda'))
            output_file = self.coverage_dir / 'incremental_merged.info'
            source_dir = self.incremental_dir
            source_desc = "incremental directory"
        else:
            # For standard coverage, look in build directory
            gcda_files = list(self.build_dir.rglob('*.gcda'))
            # Exclude files already in incremental directory
            gcda_files = [f for f in gcda_files if not str(f).startswith(str(self.incremental_dir))]
            output_file = self.coverage_dir / 'merged.info'
            source_dir = self.build_dir
            source_desc = "build directory"

        if not gcda_files:
            self.logger.warning(f"No .gcda files found in {source_desc}")
            return False

        try:
            cmd = [
                lcov, '--capture',
                '--directory', str(source_dir),
                '--output-file', str(output_file),
                '--rc', 'branch_coverage=1',
                '--ignore-errors', 'gcov,source,unused'
            ]

            self.logger.info(f"Generating coverage info from {len(gcda_files)} .gcda files...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                self.logger.success(f"Successfully generated coverage info at {output_file}")
                return True
            else:
                self.logger.error(f"lcov failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("lcov timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to merge GCC coverage data: {e}")
            return False
    
    def generate_report(self, compiler: str = None, executables: List[Path] = None) -> bool:
        """
        Generate coverage report.
        
        Args:
            compiler: Compiler type
            executables: List of executable paths for Clang coverage
            
        Returns:
            True if successful, False otherwise
        """
        if compiler is None:
            compiler = self.tool_manager.detect_compiler()
        
        report_dir = self.coverage_dir / 'incremental_report'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        if compiler == 'clang':
            return self._generate_clang_report(report_dir, executables)
        elif compiler == 'gcc':
            return self._generate_gcc_report(report_dir)
        else:
            self.logger.error(f"Unsupported compiler: {compiler}")
            return False
    
    def _generate_clang_report(self, report_dir: Path, executables: List[Path] = None) -> bool:
        """Generate Clang coverage report using llvm-cov."""
        tools = self.tool_manager.get_coverage_tools('clang')
        llvm_cov = tools.get('llvm_cov')
        
        if not llvm_cov:
            self.logger.error("llvm-cov not found")
            return False
        
        profdata_file = self.coverage_dir / 'incremental_merged.profdata'
        if not profdata_file.exists():
            self.logger.error(f"Merged profdata file not found: {profdata_file}")
            return False
        
        if not executables:
            # Try to find executables automatically, excluding CMake files
            all_files = list(self.build_dir.rglob('*'))
            executables = []
            for e in all_files:
                if (e.is_file() and
                    e.stat().st_mode & 0o111 and
                    'CMakeFiles' not in str(e) and
                    not str(e).endswith('.bin')):
                    executables.append(e)

        if not executables:
            self.logger.warning("No executables found for coverage report")
            # For library-only projects, try to find object files
            object_files = list(self.build_dir.rglob('*.o'))
            if object_files:
                self.logger.info(f"Found {len(object_files)} object files, attempting coverage report without executables")
                # Use a different approach for library coverage
                return self._generate_clang_library_report(report_dir, profdata_file)
            else:
                self.logger.error("No executables or object files found for coverage report")
                return False
        
        try:
            # Generate HTML report
            cmd = [llvm_cov, 'show'] + [str(e) for e in executables] + [
                f'-instr-profile={profdata_file}',
                '-format=html',
                f'-output-dir={report_dir}'
            ]
            
            self.logger.info("Generating HTML coverage report...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.logger.success(f"HTML report generated at {report_dir / 'index.html'}")
                return True
            else:
                self.logger.error(f"llvm-cov show failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to generate Clang report: {e}")
            return False
    
    def _generate_gcc_report(self, report_dir: Path) -> bool:
        """Generate GCC coverage report using genhtml."""
        tools = self.tool_manager.get_coverage_tools('gcc')
        genhtml = tools.get('genhtml')
        
        if not genhtml:
            self.logger.error("genhtml not found")
            return False
        
        info_file = self.coverage_dir / 'incremental_merged.info'
        if not info_file.exists():
            self.logger.error(f"Merged info file not found: {info_file}")
            return False
        
        try:
            cmd = [
                genhtml, str(info_file),
                '--output-directory', str(report_dir),
                '--rc', 'branch_coverage=1',
                '--ignore-errors', 'source,unused'
            ]
            
            self.logger.info("Generating HTML coverage report...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.logger.success(f"HTML report generated at {report_dir / 'index.html'}")
                return True
            else:
                self.logger.error(f"genhtml failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to generate GCC report: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get current status of incremental coverage."""
        profraw_files = list(self.incremental_dir.glob('*.profraw')) if self.incremental_dir.exists() else []
        gcda_files = list(self.incremental_dir.glob('*.gcda')) if self.incremental_dir.exists() else []
        
        merged_profdata = self.coverage_dir / 'incremental_merged.profdata'
        merged_info = self.coverage_dir / 'incremental_merged.info'
        report_dir = self.coverage_dir / 'incremental_report'
        
        return {
            'incremental_dir_exists': self.incremental_dir.exists(),
            'profraw_count': len(profraw_files),
            'gcda_count': len(gcda_files),
            'merged_profdata_exists': merged_profdata.exists(),
            'merged_info_exists': merged_info.exists(),
            'report_exists': report_dir.exists() and (report_dir / 'index.html').exists(),
            'compiler': self.tool_manager.detect_compiler()
        }

    def generate_standard_report(self, compiler: str = None, executables: List[Path] = None) -> bool:
        """
        Generate standard coverage report (non-incremental).

        Args:
            compiler: Compiler type
            executables: List of executable paths for Clang coverage

        Returns:
            True if successful, False otherwise
        """
        if compiler is None:
            compiler = self.tool_manager.detect_compiler()

        report_dir = self.coverage_dir / 'html'
        report_dir.mkdir(parents=True, exist_ok=True)

        if compiler == 'clang':
            return self._generate_clang_standard_report(report_dir, executables)
        elif compiler == 'gcc':
            return self._generate_gcc_standard_report(report_dir)
        else:
            self.logger.error(f"Unsupported compiler: {compiler}")
            return False

    def _generate_clang_standard_report(self, report_dir: Path, executables: List[Path] = None) -> bool:
        """Generate standard Clang coverage report."""
        llvm_cov = self.tool_manager.find_tool('llvm-cov')
        if not llvm_cov:
            self.logger.error("llvm-cov not found")
            return False

        # Look for merged profdata file
        profdata_file = self.coverage_dir / 'merged.profdata'
        if not profdata_file.exists():
            # Try incremental merged file as fallback
            profdata_file = self.coverage_dir / 'incremental_merged.profdata'
            if not profdata_file.exists():
                self.logger.error("No merged profdata file found")
                return False

        if not executables:
            self.logger.warning("No executables found for coverage report")
            # For library-only projects, try to find object files
            object_files = list(self.build_dir.rglob('*.o'))
            if object_files:
                self.logger.info(f"Found {len(object_files)} object files, attempting coverage report without executables")
                # Use a different approach for library coverage
                return self._generate_clang_library_report(report_dir, profdata_file)
            else:
                self.logger.error("No executables or object files found for coverage report")
                return False

        try:
            # Generate HTML report
            cmd = [llvm_cov, 'show'] + [str(e) for e in executables] + [
                f'-instr-profile={profdata_file}',
                '-format=html',
                f'-output-dir={report_dir}'
            ]

            self.logger.info("Generating HTML coverage report...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                self.logger.success(f"HTML report generated at {report_dir / 'index.html'}")
                return True
            else:
                self.logger.error(f"llvm-cov show failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to generate Clang report: {e}")
            return False

    def _generate_clang_library_report(self, report_dir: Path, profdata_file: Path) -> bool:
        """Generate Clang coverage report for library-only projects."""
        llvm_cov = self.tool_manager.find_tool('llvm-cov')
        if not llvm_cov:
            self.logger.error("llvm-cov not found")
            return False

        try:
            # For library projects, find source files and generate a summary report
            project_root = self.build_dir.parent
            source_files = []

            # Look for source files in common directories
            search_dirs = [
                project_root / 'src',
                project_root / 'algorithm' / 'src',
                project_root / 'statistics' / 'src',
                project_root / 'app'
            ]

            for search_dir in search_dirs:
                if search_dir.exists():
                    for src_ext in ['.c', '.cpp', '.cc', '.cxx']:
                        for src_file in search_dir.glob(f'*{src_ext}'):
                            source_files.append(str(src_file))

            if source_files:
                # For library projects, we need to find the object files that were compiled with coverage
                object_files = []
                for obj_file in self.build_dir.rglob('*.o'):
                    # Skip CMake compiler ID files
                    if 'CMakeFiles' in str(obj_file) and ('CompilerIdC' in str(obj_file) or 'CompilerIdCXX' in str(obj_file)):
                        continue
                    object_files.append(str(obj_file))

                if object_files:
                    # Try to generate a report using object files
                    cmd = [llvm_cov, 'report', f'-instr-profile={profdata_file}'] + object_files

                    self.logger.info(f"Generating coverage summary report for {len(object_files)} object files...")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

                    if result.returncode == 0:
                        # Save the text report
                        report_file = report_dir / 'coverage_report.txt'
                        with open(report_file, 'w') as f:
                            f.write(result.stdout)

                        self.logger.success(f"Coverage summary report generated at {report_file}")
                        return True
                    else:
                        # If object files don't work, try a simple text summary
                        self.logger.warning("Object file approach failed, generating simple summary")
                        summary = f"Coverage Summary\n"
                        summary += f"================\n\n"
                        summary += f"Profdata file: {profdata_file}\n"
                        summary += f"Source files found: {len(source_files)}\n"
                        summary += f"Object files found: {len(object_files)}\n\n"
                        summary += "Source files:\n"
                        for src in source_files:
                            summary += f"  - {src}\n"

                        report_file = report_dir / 'coverage_summary.txt'
                        with open(report_file, 'w') as f:
                            f.write(summary)

                        self.logger.success(f"Basic coverage summary generated at {report_file}")
                        return True
                else:
                    self.logger.error("No valid object files found for coverage report")
                    return False
            else:
                self.logger.error("No source files found for coverage report")
                return False

        except Exception as e:
            self.logger.error(f"Failed to generate library coverage report: {e}")
            return False

    def _generate_gcc_standard_report(self, report_dir: Path) -> bool:
        """Generate standard GCC coverage report."""
        genhtml = self.tool_manager.find_tool('genhtml')
        if not genhtml:
            self.logger.error("genhtml not found")
            return False

        # Look for merged info file
        info_file = self.coverage_dir / 'merged.info'
        if not info_file.exists():
            # Try incremental merged file as fallback
            info_file = self.coverage_dir / 'incremental_merged.info'
            if not info_file.exists():
                self.logger.error("No merged info file found")
                return False

        try:
            cmd = [
                genhtml, str(info_file),
                '--output-directory', str(report_dir),
                '--rc', 'branch_coverage=1',
                '--ignore-errors', 'source,unused'
            ]

            self.logger.info("Generating HTML coverage report...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                self.logger.success(f"HTML report generated at {report_dir / 'index.html'}")
                return True
            else:
                self.logger.error(f"genhtml failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to generate GCC report: {e}")
            return False
