#!/usr/bin/env python3
"""
PyDCov Command Line Interface

Unified command-line interface for PyDCov coverage tools.
Provides coverage collection, incremental coverage tracking, and reporting
capabilities for CMake-based C/C++ projects.

Usage:
    pydcov coverage [command] [options]
    pydcov incremental [command] [options]
    pydcov --help
    pydcov --version

Commands:
    coverage      - Standard coverage workflows
    incremental   - Incremental coverage tracking
    init-cmake    - Initialize CMake integration
    init-template - Create new project from template
    version       - Show version information
    help          - Show help information

Examples:
    pydcov coverage full "python -m pytest tests/"
    pydcov coverage clean
    pydcov coverage build
    pydcov coverage test "python -m pytest tests/"
    pydcov coverage report

    pydcov incremental init
    pydcov incremental add "python -m pytest tests/"
    pydcov incremental report

    pydcov init-cmake
    pydcov init-template my_project --template basic_cpp
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from pydcov import __version__
from pydcov.core.coverage_manager import CoverageManager
from pydcov.core.incremental_coverage import IncrementalCoverageManager
from pydcov.utils.logging_config import setup_logging


def create_coverage_parser(subparsers):
    """Create coverage command parser."""
    coverage_parser = subparsers.add_parser(
        'coverage',
        help='Standard coverage workflows',
        description='Standard coverage collection and reporting workflows'
    )
    
    coverage_parser.add_argument(
        'command',
        choices=['clean', 'build', 'test', 'report', 'full', 'status'],
        help='Coverage command to execute'
    )
    
    coverage_parser.add_argument(
        'test_args',
        nargs='*',
        help='Test command arguments (required for test and full commands)'
    )
    
    coverage_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    coverage_parser.add_argument(
        '--no-colors',
        action='store_true',
        help='Disable colored output'
    )
    
    coverage_parser.add_argument(
        '--project-root',
        type=Path,
        help='Project root directory (auto-detected if not specified)'
    )
    
    return coverage_parser


def create_incremental_parser(subparsers):
    """Create incremental coverage command parser."""
    incremental_parser = subparsers.add_parser(
        'incremental',
        help='Incremental coverage tracking',
        description='Incremental coverage collection and tracking workflows'
    )
    
    incremental_parser.add_argument(
        'command',
        choices=['init', 'add', 'merge', 'report', 'status', 'clean'],
        help='Incremental coverage command to execute'
    )
    
    incremental_parser.add_argument(
        'test_args',
        nargs='*',
        help='Test command arguments (required for add command)'
    )
    
    incremental_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    incremental_parser.add_argument(
        '--no-colors',
        action='store_true',
        help='Disable colored output'
    )
    
    incremental_parser.add_argument(
        '--project-root',
        type=Path,
        help='Project root directory (auto-detected if not specified)'
    )
    
    return incremental_parser


def create_init_cmake_parser(subparsers):
    """Create init-cmake command parser."""
    init_parser = subparsers.add_parser(
        'init-cmake',
        help='Initialize CMake integration',
        description='Copy CMake integration files to your project'
    )

    init_parser.add_argument(
        '--project-root',
        type=str,
        help='Project root directory (current directory if not specified)'
    )

    init_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing files'
    )

    return init_parser


def create_init_template_parser(subparsers):
    """Create init-template command parser."""
    template_parser = subparsers.add_parser(
        'init-template',
        help='Create new project from template',
        description='Bootstrap a new C/C++ project with PyDCov coverage support'
    )

    template_parser.add_argument(
        'project_name',
        help='Name of the new project'
    )

    template_parser.add_argument(
        '--template',
        default='basic_cpp',
        choices=['basic_cpp'],
        help='Template to use (default: basic_cpp)'
    )

    template_parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (current directory if not specified)'
    )

    template_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing directory'
    )

    return template_parser


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='pydcov',
        description='PyDCov - Python-based C/C++ Code Coverage Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'PyDCov {__version__}'
    )
    
    subparsers = parser.add_subparsers(
        dest='subcommand',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Create subcommand parsers
    create_coverage_parser(subparsers)
    create_incremental_parser(subparsers)
    create_init_cmake_parser(subparsers)
    create_init_template_parser(subparsers)
    
    return parser.parse_args()


def handle_coverage_command(args) -> int:
    """Handle coverage subcommand."""
    try:
        manager = CoverageManager(args.project_root)
        
        if args.command == 'clean':
            success = manager.clean()
        elif args.command == 'build':
            success = manager.build()
        elif args.command == 'test':
            if not args.test_args:
                print("Error: test command requires test arguments")
                return 1
            success = manager.test(args.test_args)
        elif args.command == 'report':
            success = manager.report()
        elif args.command == 'full':
            if not args.test_args:
                print("Error: full command requires test arguments")
                return 1
            success = manager.full_workflow(args.test_args)
        elif args.command == 'status':
            success = manager.status()
        else:
            print(f"Error: Unknown coverage command: {args.command}")
            return 1
            
        return 0 if success else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


def handle_incremental_command(args) -> int:
    """Handle incremental coverage subcommand."""
    try:
        manager = IncrementalCoverageManager(args.project_root)
        
        if args.command == 'init':
            success = manager.init()
        elif args.command == 'add':
            if not args.test_args:
                print("Error: add command requires test arguments")
                return 1
            success = manager.add(args.test_args)
        elif args.command == 'merge':
            success = manager.merge()
        elif args.command == 'report':
            success = manager.report()
        elif args.command == 'status':
            success = manager.status()
        elif args.command == 'clean':
            success = manager.clean()
        else:
            print(f"Error: Unknown incremental command: {args.command}")
            return 1
            
        return 0 if success else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


def handle_init_template_command(args) -> int:
    """Handle init-template command."""
    try:
        import shutil
        import importlib.resources
        import re

        # Handle output directory with robust path resolution
        if args.output_dir is not None:
            output_dir = Path(args.output_dir)
        else:
            try:
                output_dir = Path.cwd()
            except (OSError, RuntimeError) as e:
                print(f"Error: Cannot determine current working directory: {e}")
                return 1

        # Ensure output_dir is a valid Path object
        if not isinstance(output_dir, Path):
            try:
                output_dir = Path(output_dir)
            except (TypeError, ValueError) as e:
                print(f"Error: Invalid output directory: {e}")
                return 1

        project_dir = output_dir / args.project_name

        # Check if project directory already exists
        if project_dir.exists() and not args.force:
            print(f"Error: Directory {project_dir} already exists. Use --force to overwrite.")
            return 1

        # Create project directory
        project_dir.mkdir(parents=True, exist_ok=True)

        # Copy template files
        try:
            # Try new importlib.resources API (Python 3.9+)
            with importlib.resources.as_file(
                importlib.resources.files(f'pydcov.templates.{args.template}')
            ) as template_dir:
                copy_template_files(template_dir, project_dir, args.project_name)

        except (ImportError, AttributeError):
            # Fallback for older Python versions
            import pkg_resources
            template_dir = Path(pkg_resources.resource_filename('pydcov', f'templates/{args.template}'))
            copy_template_files(template_dir, project_dir, args.project_name)

        # Copy CMake integration files
        cmake_dir = project_dir / "cmake"
        cmake_dir.mkdir(exist_ok=True)

        try:
            with importlib.resources.as_file(
                importlib.resources.files('pydcov.cmake')
            ) as package_cmake_dir:
                for cmake_file in package_cmake_dir.glob('*.cmake'):
                    shutil.copy2(cmake_file, cmake_dir / cmake_file.name)
                for doc_file in package_cmake_dir.glob('*.md'):
                    shutil.copy2(doc_file, cmake_dir / doc_file.name)

        except (ImportError, AttributeError):
            import pkg_resources
            package_cmake_dir = Path(pkg_resources.resource_filename('pydcov', 'cmake'))
            for cmake_file in package_cmake_dir.glob('*.cmake'):
                shutil.copy2(cmake_file, cmake_dir / cmake_file.name)
            for doc_file in package_cmake_dir.glob('*.md'):
                shutil.copy2(doc_file, cmake_dir / doc_file.name)

        print(f"✅ Created new project '{args.project_name}' in {project_dir}")
        print(f"📁 Template: {args.template}")
        print(f"\nNext steps:")
        print(f"  cd {args.project_name}")
        print(f"  mkdir build && cd build")
        print(f"  cmake ..")
        print(f"  make")
        print(f"  pydcov coverage full \"make test\"")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def copy_template_files(template_dir: Path, project_dir: Path, project_name: str):
    """Copy template files and substitute placeholders."""
    import shutil

    for item in template_dir.rglob('*'):
        if item.is_file():
            # Calculate relative path
            rel_path = item.relative_to(template_dir)
            dest_path = project_dir / rel_path

            # Create parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Read file content and substitute placeholders
            try:
                content = item.read_text(encoding='utf-8')
                content = content.replace('{{PROJECT_NAME}}', project_name)
                dest_path.write_text(content, encoding='utf-8')
            except UnicodeDecodeError:
                # Binary file, copy as-is
                shutil.copy2(item, dest_path)


def handle_init_cmake_command(args) -> int:
    """Handle init-cmake command."""
    try:
        import shutil
        import importlib.resources

        # Handle project root with robust path resolution
        if args.project_root is not None:
            project_root = Path(args.project_root)
        else:
            try:
                project_root = Path.cwd()
            except (OSError, RuntimeError) as e:
                print(f"Error: Cannot determine current working directory: {e}")
                return 1

        # Ensure project_root is a valid Path object
        if not isinstance(project_root, Path):
            try:
                project_root = Path(project_root)
            except (TypeError, ValueError) as e:
                print(f"Error: Invalid project root: {e}")
                return 1

        cmake_dir = project_root / "cmake"

        # Create cmake directory if it doesn't exist
        cmake_dir.mkdir(exist_ok=True)

        # Copy CMake files from package
        try:
            # Try new importlib.resources API (Python 3.9+)
            with importlib.resources.as_file(
                importlib.resources.files('pydcov.cmake')
            ) as package_cmake_dir:
                for cmake_file in package_cmake_dir.glob('*.cmake'):
                    dest_file = cmake_dir / cmake_file.name

                    if dest_file.exists() and not getattr(args, 'force', False):
                        print(f"File {dest_file} already exists. Use --force to overwrite.")
                        continue

                    shutil.copy2(cmake_file, dest_file)
                    print(f"Copied {cmake_file.name} to {dest_file}")

                # Copy documentation files
                for doc_file in package_cmake_dir.glob('*.md'):
                    dest_file = cmake_dir / doc_file.name

                    if dest_file.exists() and not getattr(args, 'force', False):
                        continue

                    shutil.copy2(doc_file, dest_file)
                    print(f"Copied {doc_file.name} to {dest_file}")

        except (ImportError, AttributeError):
            # Fallback for older Python versions
            import pkg_resources
            package_cmake_dir = Path(pkg_resources.resource_filename('pydcov', 'cmake'))

            for cmake_file in package_cmake_dir.glob('*.cmake'):
                dest_file = cmake_dir / cmake_file.name

                if dest_file.exists() and not getattr(args, 'force', False):
                    print(f"File {dest_file} already exists. Use --force to overwrite.")
                    continue

                shutil.copy2(cmake_file, dest_file)
                print(f"Copied {cmake_file.name} to {dest_file}")

            # Copy documentation files
            for doc_file in package_cmake_dir.glob('*.md'):
                dest_file = cmake_dir / doc_file.name

                if dest_file.exists() and not getattr(args, 'force', False):
                    continue

                shutil.copy2(doc_file, dest_file)
                print(f"Copied {doc_file.name} to {dest_file}")

        print(f"\nCMake integration files copied to {cmake_dir}")
        print("Add the following line to your CMakeLists.txt:")
        print("    include(cmake/coverage.cmake)")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    # Setup logging
    level = "DEBUG" if getattr(args, 'verbose', False) else "INFO"
    setup_logging(
        level=level,
        use_colors=not getattr(args, 'no_colors', False)
    )
    
    if not args.subcommand:
        print("Error: No command specified. Use 'pydcov --help' for usage information.")
        return 1
    
    if args.subcommand == 'coverage':
        return handle_coverage_command(args)
    elif args.subcommand == 'incremental':
        return handle_incremental_command(args)
    elif args.subcommand == 'init-cmake':
        return handle_init_cmake_command(args)
    elif args.subcommand == 'init-template':
        return handle_init_template_command(args)
    else:
        print(f"Error: Unknown command: {args.subcommand}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
