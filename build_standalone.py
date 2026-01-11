#!/usr/bin/env python3
"""
Build script for creating standalone PyDCov executables using PyInstaller.

This script automates the process of building standalone executables for PyDCov
that can run on systems without Python installed.

Usage:
    python build_standalone.py [--clean] [--test]

Options:
    --clean    Clean build directories before building
    --test     Test the built executable after building
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, check=True, capture_output=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    try:
        if capture_output:
            result = subprocess.run(
                cmd, cwd=cwd, check=check, capture_output=True, text=True
            )
            if result.stdout:
                print(result.stdout)
        else:
            result = subprocess.run(cmd, cwd=cwd, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if hasattr(e, "stderr") and e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def clean_build_dirs():
    """Clean build and dist directories."""
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            print(f"Cleaning {dir_name}/")
            shutil.rmtree(dir_name)


def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller

        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("Building standalone executable...")
    run_command(["pyinstaller", "pydcov.spec"], capture_output=False)


def test_executable():
    """Test the built executable."""
    executable_path = Path("dist/pydcov").absolute()
    if not executable_path.exists():
        print(f"Error: Executable not found at {executable_path}")
        return False

    print("Testing standalone executable...")

    # Test version
    result = run_command([str(executable_path), "--version"], check=False)
    if result.returncode != 0:
        print("Error: Version test failed")
        return False

    # Test help
    result = run_command([str(executable_path), "--help"], check=False)
    if result.returncode != 0:
        print("Error: Help test failed")
        return False

    # Test CMake integration
    test_dir = Path("/tmp/test_pydcov_build")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)

    try:
        result = run_command(
            [str(executable_path), "init-cmake"], cwd=test_dir, check=False
        )
        if result.returncode != 0:
            print("Error: CMake integration test failed")
            return False

        # Check if files were created
        cmake_dir = test_dir / "cmake"
        if not cmake_dir.exists() or not (cmake_dir / "coverage.cmake").exists():
            print("Error: CMake files not created")
            return False

        print("All tests passed!")
        return True
    finally:
        if test_dir.exists():
            shutil.rmtree(test_dir)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clean", action="store_true", help="Clean build directories before building"
    )
    parser.add_argument(
        "--test", action="store_true", help="Test the built executable after building"
    )

    args = parser.parse_args()

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    if args.clean:
        clean_build_dirs()

    install_pyinstaller()
    build_executable()

    if args.test:
        if not test_executable():
            sys.exit(1)

    executable_path = Path("dist/pydcov")
    if executable_path.exists():
        size_mb = executable_path.stat().st_size / (1024 * 1024)
        print(f"\nBuild completed successfully!")
        print(f"Executable: {executable_path}")
        print(f"Size: {size_mb:.1f} MB")
        print(f"\nYou can now distribute the standalone executable:")
        print(f"  {executable_path}")
    else:
        print("Error: Build failed - executable not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
