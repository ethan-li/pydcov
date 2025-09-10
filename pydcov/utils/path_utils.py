"""
Path management utilities for coverage tools.

Provides centralized path management and validation for the coverage system.
"""

import os
from pathlib import Path
# No typing imports needed for Python 3.11+ union syntax

from .logging_config import get_logger


class PathManager:
    """Manages paths and directories for the coverage system."""
    
    def __init__(self, project_root: Path | None = None):
        self.logger = get_logger()
        
        if project_root is None:
            # Auto-detect project root by looking for CMakeLists.txt
            current = Path.cwd()
            while current != current.parent:
                if (current / 'CMakeLists.txt').exists():
                    project_root = current
                    break
                current = current.parent
            
            if project_root is None:
                # Fallback to current directory
                project_root = Path.cwd()
        
        self.project_root = Path(project_root).resolve()
        self.build_dir = self.project_root / 'build'
        self.coverage_dir = self.build_dir / 'coverage'
        self.scripts_dir = self.project_root / 'scripts'
        self.coverage_tools_dir = self.project_root / 'coverage_tools'
        
        # Module directories
        self.algorithm_src_dir = self.project_root / 'algorithm' / 'src'
        self.statistics_src_dir = self.project_root / 'statistics' / 'src'
        
        # Executable paths
        self.algorithm_cli = self.build_dir / 'algorithm' / 'app' / 'algorithm_cli'
        self.statistics_cli = self.build_dir / 'statistics' / 'app' / 'statistics_cli'
        
        self.logger.debug(f"Project root: {self.project_root}")
        self.logger.debug(f"Build directory: {self.build_dir}")
    
    def ensure_coverage_dir(self) -> Path:
        """Ensure coverage directory exists and return its path."""
        self.coverage_dir.mkdir(parents=True, exist_ok=True)
        return self.coverage_dir
    
    def ensure_incremental_dir(self) -> Path:
        """Ensure incremental coverage directory exists and return its path."""
        incremental_dir = self.coverage_dir / 'incremental'
        incremental_dir.mkdir(parents=True, exist_ok=True)
        return incremental_dir
    
    def get_module_coverage_dir(self, module: str) -> Path:
        """Get coverage directory for a specific module."""
        module_dir = self.coverage_dir / module
        module_dir.mkdir(parents=True, exist_ok=True)
        return module_dir
    
    def validate_build_dir(self) -> bool:
        """Check if build directory exists and contains CMake files."""
        if not self.build_dir.exists():
            self.logger.error(f"Build directory not found: {self.build_dir}")
            return False
        
        cmake_cache = self.build_dir / 'CMakeCache.txt'
        if not cmake_cache.exists():
            self.logger.error(f"CMakeCache.txt not found in {self.build_dir}")
            self.logger.error("Please run CMake configuration first")
            return False
        
        return True
    
    def validate_coverage_build(self) -> bool:
        """Check if build was configured with coverage enabled."""
        if not self.validate_build_dir():
            return False
        
        cmake_cache = self.build_dir / 'CMakeCache.txt'
        try:
            with open(cmake_cache, 'r') as f:
                content = f.read()
                if 'ENABLE_COVERAGE:BOOL=ON' in content:
                    return True
                else:
                    self.logger.error("Coverage not enabled in CMake configuration")
                    self.logger.error("Please reconfigure with: cmake -DENABLE_COVERAGE=ON")
                    return False
        except Exception as e:
            self.logger.error(f"Failed to read CMakeCache.txt: {e}")
            return False
    
    def get_source_files(self, module: str | None = None) -> list:
        """
        Get list of source files for coverage analysis.
        
        Args:
            module: Specific module ('algorithm' or 'statistics'). 
                   If None, returns all source files.
        
        Returns:
            List of source file paths
        """
        source_files = []
        
        if module is None or module == 'algorithm':
            if self.algorithm_src_dir.exists():
                source_files.extend(self.algorithm_src_dir.glob('*.c'))
        
        if module is None or module == 'statistics':
            if self.statistics_src_dir.exists():
                source_files.extend(self.statistics_src_dir.glob('*.c'))
        
        return [str(f) for f in source_files]
    
    def get_executable_path(self, module: str) -> Path | None:
        """
        Get path to module executable.
        
        Args:
            module: Module name ('algorithm' or 'statistics')
            
        Returns:
            Path to executable or None if not found
        """
        if module == 'algorithm':
            exe_path = self.algorithm_cli
        elif module == 'statistics':
            exe_path = self.statistics_cli
        else:
            self.logger.error(f"Unknown module: {module}")
            return None
        
        if exe_path.exists():
            return exe_path
        else:
            self.logger.warning(f"Executable not found: {exe_path}")
            return None
    
    def clean_coverage_data(self, incremental_only: bool = False):
        """
        Clean coverage data files.
        
        Args:
            incremental_only: If True, only clean incremental data
        """
        if incremental_only:
            # Clean only incremental data
            incremental_dir = self.coverage_dir / 'incremental'
            if incremental_dir.exists():
                import shutil
                shutil.rmtree(incremental_dir)
                self.logger.info("Cleaned incremental coverage data")
        else:
            # Clean all coverage data
            if self.coverage_dir.exists():
                import shutil
                shutil.rmtree(self.coverage_dir)
                self.logger.info("Cleaned all coverage data")
    
    def relative_to_project(self, path: Path) -> str:
        """Get path relative to project root."""
        try:
            return str(path.relative_to(self.project_root))
        except ValueError:
            return str(path)
