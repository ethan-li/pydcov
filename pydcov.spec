# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for pydcov

This spec file creates a standalone executable for pydcov that includes:
- All Python modules and dependencies
- CMake integration files (coverage.cmake, COVERAGE_USAGE.md)
- Cross-platform compatibility for Linux and macOS

Usage:
    pyinstaller pydcov.spec
"""

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path.cwd()
pydcov_package = project_root / "pydcov"

# Define data files to include
datas = []

# Include CMake integration files
cmake_dir = pydcov_package / "cmake"
if cmake_dir.exists():
    for file_path in cmake_dir.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("__pycache__"):
            # Calculate relative path from pydcov package
            rel_path = file_path.relative_to(pydcov_package)
            datas.append((str(file_path), str(Path("pydcov") / rel_path.parent)))

# Analysis configuration
a = Analysis(
    ['pydcov/cli.py'],  # Main entry point
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Ensure all pydcov modules are included
        'pydcov',
        'pydcov.cli',
        'pydcov.core',
        'pydcov.core.incremental_coverage',
        'pydcov.utils',
        'pydcov.utils.cmake_integration',
        'pydcov.utils.compiler_detection',
        'pydcov.utils.coverage_file_manager',
        'pydcov.utils.coverage_tools',
        'pydcov.utils.logging_config',
        'pydcov.utils.path_utils',
        'pydcov.utils.test_executor',
        'pydcov.cmake',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ (Python ZIP archive)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pydcov',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Optional: Create a COLLECT for directory distribution (one-folder mode)
# Uncomment the following lines if you prefer one-folder distribution
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='pydcov'
# )
