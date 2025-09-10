"""
Core coverage management modules.

This package contains the main coverage management classes:
- CoverageManager: Standard coverage workflow
- IncrementalCoverageManager: Incremental coverage collection
- ModuleCoverageManager: Module-specific coverage reports
"""

from .coverage_manager import CoverageManager
from .incremental_coverage import IncrementalCoverageManager
from .module_coverage import ModuleCoverageManager

__all__ = [
    "CoverageManager",
    "IncrementalCoverageManager",
    "ModuleCoverageManager"
]
