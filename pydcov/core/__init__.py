"""
Core coverage management modules.

This package contains the main coverage management classes:
- CoverageManager: Standard coverage workflows
- IncrementalCoverageManager: Incremental coverage tracking
"""

from .coverage_manager import CoverageManager
from .incremental_coverage import IncrementalCoverageManager

__all__ = [
    "CoverageManager",
    "IncrementalCoverageManager"
]
