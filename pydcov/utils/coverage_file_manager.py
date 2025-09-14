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
    
    def merge_coverage_data(self, compiler: str = None) -> bool:
        """
        Merge collected coverage data.

        Args:
            compiler: Compiler type ('clang' or 'gcc')

        Returns:
            True if successful, False otherwise
        """
        if compiler is None:
            compiler = self.tool_manager.detect_compiler()

        self.coverage_dir.mkdir(parents=True, exist_ok=True)

        if compiler == 'clang':
            return self._merge_clang_data()
        elif compiler == 'gcc':
            return self._merge_gcc_data()
        else:
            self.logger.error(f"Unsupported compiler: {compiler}")
            return False
    
    def _merge_clang_data(self) -> bool:
        """Merge Clang coverage data using llvm-profdata."""
        tools = self.tool_manager.get_coverage_tools('clang')
        llvm_profdata = tools.get('llvm_profdata')

        if not llvm_profdata:
            self.logger.error("llvm-profdata not found")
            return False

        # Find .profraw files in incremental directory
        profraw_files = list(self.incremental_dir.glob('*.profraw'))
        output_file = self.coverage_dir / 'incremental_merged.profdata'
        source_desc = "incremental directory"

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
    
    def _merge_gcc_data(self) -> bool:
        """Merge GCC coverage data using lcov."""
        tools = self.tool_manager.get_coverage_tools('gcc')
        lcov = tools.get('lcov')

        if not lcov:
            self.logger.error("lcov not found")
            return False

        # Check for .gcda files in incremental directory
        gcda_files = list(self.incremental_dir.glob('*.gcda'))
        output_file = self.coverage_dir / 'incremental_merged.info'
        source_dir = self.incremental_dir
        source_desc = "incremental directory"

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

        # For Clang coverage, find object files and filter those with coverage data
        object_files = []
        for obj_file in self.build_dir.rglob('*.o'):
            # Skip CMake compiler ID files
            if 'CMakeFiles' in str(obj_file) and ('CompilerIdC' in str(obj_file) or 'CompilerIdCXX' in str(obj_file)):
                continue
            object_files.append(obj_file)

        if not object_files:
            self.logger.error("No object files found for coverage report")
            return False

        # Filter object files that actually have coverage data
        valid_object_files = []
        for obj_file in object_files:
            try:
                # Test if this object file has coverage data
                test_cmd = [llvm_cov, 'report', f'-instr-profile={profdata_file}', str(obj_file)]
                result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and 'TOTAL' in result.stdout:
                    valid_object_files.append(obj_file)
                    self.logger.debug(f"Object file {obj_file.name} has coverage data")
            except Exception as e:
                self.logger.debug(f"Skipping {obj_file.name}: {e}")

        if not valid_object_files:
            self.logger.error("No object files with coverage data found")
            return False

        self.logger.info(f"Found {len(valid_object_files)} object files with coverage data")

        # Try to generate combined report first
        try:
            cmd = [llvm_cov, 'show'] + [str(obj) for obj in valid_object_files] + [
                f'-instr-profile={profdata_file}',
                '-format=html',
                f'-output-dir={report_dir}'
            ]

            self.logger.info(f"Generating combined HTML coverage report...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                # Check if the report actually contains coverage data
                index_file = report_dir / 'index.html'
                if index_file.exists():
                    with open(index_file, 'r') as f:
                        content = f.read()
                    # Check if the report contains actual coverage data (not just empty totals)
                    if '- (0/0)' not in content or 'coverage/' in content:
                        self.logger.success(f"HTML report generated at {report_dir / 'index.html'}")
                        return True
                    else:
                        self.logger.warning("Combined report generated but contains no coverage data")
                        # Remove only the empty index.html and fall back to individual reports
                        index_file = report_dir / 'index.html'
                        if index_file.exists():
                            index_file.unlink()
                        # Fall back to individual reports
                        return self._generate_individual_clang_reports(report_dir, profdata_file, valid_object_files)
                else:
                    self.logger.warning("Combined report command succeeded but no index.html was created")
                    # Fall back to individual reports
                    return self._generate_individual_clang_reports(report_dir, profdata_file, valid_object_files)
            else:
                self.logger.warning(f"Combined report failed: {result.stderr}")
                # Fall back to individual reports
                return self._generate_individual_clang_reports(report_dir, profdata_file, valid_object_files)

        except Exception as e:
            self.logger.warning(f"Combined report failed: {e}")
            # Fall back to individual reports
            return self._generate_individual_clang_reports(report_dir, profdata_file, valid_object_files)
    
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





    def _generate_individual_clang_reports(self, report_dir: Path, profdata_file: Path, object_files: List[Path]) -> bool:
        """Generate individual Clang coverage reports for each object file and create a combined index."""
        llvm_cov = self.tool_manager.find_tool('llvm-cov')
        if not llvm_cov:
            self.logger.error("llvm-cov not found")
            return False

        self.logger.info(f"Generating individual coverage reports for {len(object_files)} object files...")

        # Create subdirectories for individual reports
        individual_reports_dir = report_dir / 'individual'
        individual_reports_dir.mkdir(parents=True, exist_ok=True)

        successful_reports = []
        total_coverage_data = []

        for i, obj_file in enumerate(object_files):
            obj_name = obj_file.stem
            obj_report_dir = individual_reports_dir / obj_name
            obj_report_dir.mkdir(parents=True, exist_ok=True)

            try:
                # Generate individual HTML report
                cmd = [llvm_cov, 'show', str(obj_file),
                       f'-instr-profile={profdata_file}',
                       '-format=html',
                       f'-output-dir={obj_report_dir}']

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    successful_reports.append((obj_name, obj_report_dir))
                    self.logger.debug(f"Generated report for {obj_name}")

                    # Also get text summary for combined report
                    summary_cmd = [llvm_cov, 'report', str(obj_file), f'-instr-profile={profdata_file}']
                    summary_result = subprocess.run(summary_cmd, capture_output=True, text=True, timeout=30)
                    if summary_result.returncode == 0:
                        total_coverage_data.append(summary_result.stdout)
                else:
                    self.logger.warning(f"Failed to generate report for {obj_name}: {result.stderr}")

            except Exception as e:
                self.logger.warning(f"Failed to generate report for {obj_name}: {e}")

        if not successful_reports:
            self.logger.error("No individual reports were generated successfully")
            return False

        # Create a combined index.html
        self._create_combined_index(report_dir, successful_reports, total_coverage_data)

        self.logger.success(f"Generated {len(successful_reports)} individual coverage reports")
        self.logger.success(f"Combined report available at {report_dir / 'index.html'}")
        return True

    def _generate_clang_executable_report(self, report_dir: Path, profdata_file: Path, executables: List[Path]) -> bool:
        """Generate Clang coverage report using executables (fallback method)."""
        llvm_cov = self.tool_manager.find_tool('llvm-cov')
        if not llvm_cov:
            self.logger.error("llvm-cov not found")
            return False

        try:
            # Generate HTML report using executables
            cmd = [llvm_cov, 'show'] + [str(e) for e in executables] + [
                f'-instr-profile={profdata_file}',
                '-format=html',
                f'-output-dir={report_dir}'
            ]

            self.logger.info(f"Generating HTML coverage report using {len(executables)} executables...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                self.logger.success(f"HTML report generated at {report_dir / 'index.html'}")
                return True
            else:
                self.logger.error(f"llvm-cov show failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to generate executable-based Clang report: {e}")
            return False

    def _create_combined_index(self, report_dir: Path, successful_reports: List[tuple], coverage_data: List[str]) -> None:
        """Create a combined index.html that links to individual reports."""
        index_file = report_dir / 'index.html'

        # Parse coverage data to get summary statistics
        total_functions = 0
        total_lines = 0
        covered_functions = 0
        covered_lines = 0

        for data in coverage_data:
            lines = data.strip().split('\n')
            for line in lines:
                if line.startswith('TOTAL'):
                    parts = line.split()
                    if len(parts) >= 10:
                        try:
                            # Parse function coverage (e.g., "100.00% (5/5)")
                            func_part = parts[5]
                            if '(' in func_part and ')' in func_part:
                                func_nums = func_part.split('(')[1].split(')')[0].split('/')
                                covered_functions += int(func_nums[0])
                                total_functions += int(func_nums[1])

                            # Parse line coverage
                            line_part = parts[8]
                            if '(' in line_part and ')' in line_part:
                                line_nums = line_part.split('(')[1].split(')')[0].split('/')
                                covered_lines += int(line_nums[0])
                                total_lines += int(line_nums[1])
                        except (ValueError, IndexError):
                            continue

        # Calculate percentages
        func_percent = (covered_functions / total_functions * 100) if total_functions > 0 else 0
        line_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0

        # Create HTML content
        html_content = f"""<!doctype html>
<html>
<head>
    <meta name='viewport' content='width=device-width,initial-scale=1'>
    <meta charset='UTF-8'>
    <title>PyDCov Coverage Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #fff; }}
        .header {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .summary {{ margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
        .module-list {{ margin: 20px 0; }}
        .module-item {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 3px; background-color: #fff; }}
        .module-item:hover {{ background-color: #f8f9fa; }}
        .module-item a {{ text-decoration: none; color: #007bff; font-weight: bold; }}
        .module-item a:hover {{ text-decoration: underline; }}
        .coverage-good {{ color: #28a745; font-weight: bold; }}
        .coverage-medium {{ color: #ffc107; font-weight: bold; }}
        .coverage-poor {{ color: #dc3545; font-weight: bold; }}
        h1, h2, h3 {{ color: #333; }}
        .stats {{ display: inline-block; margin-right: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PyDCov Coverage Report</h1>
        <p>Generated on {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>Overall Coverage Summary</h2>
        <div class="stats">
            <strong>Function Coverage:</strong>
            <span class="{'coverage-good' if func_percent >= 80 else 'coverage-medium' if func_percent >= 60 else 'coverage-poor'}">{func_percent:.1f}% ({covered_functions}/{total_functions})</span>
        </div>
        <div class="stats">
            <strong>Line Coverage:</strong>
            <span class="{'coverage-good' if line_percent >= 80 else 'coverage-medium' if line_percent >= 60 else 'coverage-poor'}">{line_percent:.1f}% ({covered_lines}/{total_lines})</span>
        </div>
    </div>

    <div class="module-list">
        <h2>Module Reports</h2>
"""

        for module_name, module_dir in successful_reports:
            html_content += f"""        <div class="module-item">
            <h3><a href="individual/{module_name}/index.html">{module_name}</a></h3>
            <p>Click to view detailed coverage report for this module.</p>
        </div>
"""

        html_content += """    </div>
</body>
</html>"""

        with open(index_file, 'w') as f:
            f.write(html_content)

        self.logger.debug(f"Created combined index at {index_file}")

    def export_coverage_data(self, format_type: str = 'lcov', output_file: Path = None) -> bool:
        """
        Export coverage data to standard formats for external tools.

        Args:
            format_type: Export format ('lcov', 'json', 'cobertura')
            output_file: Output file path (optional, will use default if not provided)

        Returns:
            True if successful, False otherwise
        """
        compiler = self.tool_manager.detect_compiler()

        if compiler == 'clang':
            return self._export_clang_coverage(format_type, output_file)
        elif compiler == 'gcc':
            return self._export_gcc_coverage(format_type, output_file)
        else:
            self.logger.error(f"Unsupported compiler for export: {compiler}")
            return False

    def _export_clang_coverage(self, format_type: str, output_file: Path = None) -> bool:
        """Export Clang coverage data to specified format."""
        llvm_cov = self.tool_manager.find_tool('llvm-cov')
        if not llvm_cov:
            self.logger.error("llvm-cov not found")
            return False

        profdata_file = self.coverage_dir / 'incremental_merged.profdata'
        if not profdata_file.exists():
            self.logger.error(f"Merged profdata file not found: {profdata_file}")
            return False

        # Find object files with coverage data
        object_files = []
        for obj_file in self.build_dir.rglob('*.o'):
            if 'CMakeFiles' in str(obj_file) and ('CompilerIdC' in str(obj_file) or 'CompilerIdCXX' in str(obj_file)):
                continue
            try:
                test_cmd = [llvm_cov, 'report', f'-instr-profile={profdata_file}', str(obj_file)]
                result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and 'TOTAL' in result.stdout:
                    object_files.append(obj_file)
            except Exception:
                continue

        if not object_files:
            self.logger.error("No object files with coverage data found for export")
            return False

        # Set default output file if not provided
        if output_file is None:
            if format_type == 'lcov':
                output_file = self.coverage_dir / 'incremental_merged.info'
            elif format_type == 'json':
                output_file = self.coverage_dir / 'incremental_merged.json'
            elif format_type == 'cobertura':
                output_file = self.coverage_dir / 'incremental_merged.xml'
            else:
                self.logger.error(f"Unsupported export format: {format_type}")
                return False

        try:
            if format_type == 'lcov':
                # Export to lcov format
                cmd = [llvm_cov, 'export'] + [str(obj) for obj in object_files] + [
                    f'-instr-profile={profdata_file}',
                    '-format=lcov'
                ]
            elif format_type == 'json':
                # Export to JSON format
                cmd = [llvm_cov, 'export'] + [str(obj) for obj in object_files] + [
                    f'-instr-profile={profdata_file}',
                    '-format=text'
                ]
            else:
                self.logger.error(f"Export format {format_type} not yet implemented for Clang")
                return False

            self.logger.info(f"Exporting coverage data to {format_type} format...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.returncode == 0:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
                self.logger.success(f"Coverage data exported to {output_file}")
                return True
            else:
                self.logger.error(f"llvm-cov export failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to export Clang coverage data: {e}")
            return False

    def _export_gcc_coverage(self, format_type: str, output_file: Path = None) -> bool:
        """Export GCC coverage data to specified format."""
        # For GCC, the .info file is already in lcov format
        info_file = self.coverage_dir / 'incremental_merged.info'

        if not info_file.exists():
            self.logger.error(f"GCC coverage info file not found: {info_file}")
            return False

        if format_type == 'lcov':
            if output_file is None:
                output_file = info_file
            elif output_file != info_file:
                # Copy the file to the requested location
                import shutil
                shutil.copy2(info_file, output_file)
            self.logger.success(f"GCC coverage data available in lcov format at {output_file}")
            return True
        else:
            self.logger.error(f"Export format {format_type} not yet implemented for GCC")
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


