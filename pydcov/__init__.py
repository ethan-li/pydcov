"""
PyDCov - Python-based C/C++ Code Coverage Tools

A comprehensive coverage management system for CMake-based C/C++ projects.
Provides coverage collection, incremental coverage tracking, and reporting
capabilities with support for both GCC/gcov and Clang/llvm-cov toolchains.

This package provides modern Python implementations for comprehensive
coverage analysis and reporting that integrate seamlessly with CMake
build systems.

Example usage:
    from pydcov import CoverageManager
    
    manager = CoverageManager()
    manager.full_workflow(["python", "-m", "pytest", "tests/"])

Command-line usage:
    pydcov coverage full "python -m pytest tests/"
    pydcov incremental init
    pydcov incremental add "python -m pytest tests/"
    pydcov incremental report
"""

__version__ = "1.0.0"
__author__ = "PyDCov Project"

# Import main classes for easy access
from .core.coverage_manager import CoverageManager
from .core.incremental_coverage import IncrementalCoverageManager
from .utils.compiler_detection import CompilerDetector
from .utils.logging_config import setup_logging

__all__ = [
    "CoverageManager",
    "IncrementalCoverageManager", 
    "CompilerDetector",
    "setup_logging"
]
