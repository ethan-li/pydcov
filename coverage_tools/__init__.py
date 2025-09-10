"""
PyDCov Coverage Tools

Python-based coverage management system for the pydcov project.
Provides comprehensive coverage collection, incremental coverage tracking,
and module-specific reporting capabilities.

This package provides modern Python implementations for comprehensive
coverage analysis and reporting.
"""

__version__ = "1.0.0"
__author__ = "PyDCov Project"

# Import main classes for easy access
from .core.coverage_manager import CoverageManager
from .core.incremental_coverage import IncrementalCoverageManager
from .core.module_coverage import ModuleCoverageManager
from .utils.compiler_detection import CompilerDetector
from .utils.logging_config import setup_logging

__all__ = [
    "CoverageManager",
    "IncrementalCoverageManager", 
    "ModuleCoverageManager",
    "CompilerDetector",
    "setup_logging"
]
