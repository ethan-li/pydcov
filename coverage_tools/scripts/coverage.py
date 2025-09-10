#!/usr/bin/env python3
"""
Coverage collection and reporting script for pydcov project.

Python-based coverage collection and reporting script for pydcov project.
Supports both GCC (gcov) and Clang (llvm-cov) on Linux and macOS.

Usage:
    python coverage.py [command] [options]

Commands:
    clean                 - Clean all coverage data
    build                 - Build project with coverage instrumentation
    test [test_args]      - Run tests with coverage data collection
    report                - Generate coverage reports
    full [test_args]      - Complete workflow: clean, build, test, report
    status                - Show current coverage status
    help                  - Show this help message

Examples:
    # Using pytest
    python coverage.py test python -m pytest tests/
    python coverage.py test python -m pytest tests/test_basic.py -v
    python coverage.py full python -m pytest tests/ --tb=short

    # Using unittest
    python coverage.py test python -m unittest discover
    python coverage.py full python -m unittest tests.test_basic

    # Using custom test commands
    python coverage.py test make test
    python coverage.py test ./run_tests.sh
    python coverage.py full tests/ -v
    python coverage.py status
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Add the coverage_tools package to the path
coverage_tools_dir = Path(__file__).parent.parent
sys.path.insert(0, str(coverage_tools_dir.parent))

from coverage_tools.core.coverage_manager import CoverageManager
from coverage_tools.utils.logging_config import setup_logging


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Coverage collection and reporting for pydcov project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'command',
        choices=['clean', 'build', 'test', 'report', 'full', 'status', 'help'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'test_args',
        nargs='*',
        help='Test command arguments (required for test and full commands). Examples: "python -m pytest tests/" or "python -m unittest discover"'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--no-colors',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--project-root',
        type=Path,
        help='Project root directory (auto-detected if not specified)'
    )
    
    return parser.parse_args()


def print_help():
    """Print detailed help information."""
    print(__doc__)


def print_status(status: dict):
    """Print coverage status information."""
    print("\n" + "="*50)
    print("Coverage Status")
    print("="*50)
    
    print(f"Project Root: {status['project_root']}")
    print(f"Build Configured: {'✓' if status['build_configured'] else '✗'}")
    print(f"Coverage Enabled: {'✓' if status['coverage_enabled'] else '✗'}")
    print(f"Compiler: {status['compiler']}")
    
    print("\nCoverage Tools:")
    tools = status['coverage_tools']
    for tool, path in tools.items():
        status_icon = '✓' if path else '✗'
        print(f"  {tool}: {status_icon} {path or 'Not found'}")
    
    print(f"\nCoverage Data: {'✓' if status['coverage_data_exists'] else '✗'}")
    if status['coverage_data_exists']:
        if 'profraw_count' in status:
            print(f"  .profraw files: {status['profraw_count']}")
        if 'gcda_count' in status:
            print(f"  .gcda files: {status['gcda_count']}")
    
    print(f"Reports Generated: {'✓' if status['reports_exist'] else '✗'}")
    if status['reports_exist']:
        print(f"  HTML Report: {status['html_report']}")
    
    print("="*50)


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Set up logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    use_colors = not args.no_colors
    logger = setup_logging(log_level, use_colors)
    
    # Handle help command
    if args.command == 'help':
        print_help()
        return 0
    
    try:
        # Initialize coverage manager
        coverage_manager = CoverageManager(args.project_root)
        
        # Execute command
        if args.command == 'clean':
            success = coverage_manager.clean()
            
        elif args.command == 'build':
            success = coverage_manager.build()
            
        elif args.command == 'test':
            if not args.test_args:
                logger.error("Test command is required for 'test' command. Please specify a test command.")
                logger.info("Examples: python -m pytest tests/, python -m unittest discover, ./run_tests.sh")
                return 1
            success = coverage_manager.test(args.test_args)

        elif args.command == 'report':
            success = coverage_manager.report()

        elif args.command == 'full':
            if not args.test_args:
                logger.error("Test command is required for 'full' command. Please specify a test command.")
                logger.info("Examples: python -m pytest tests/, python -m unittest discover, ./run_tests.sh")
                return 1
            success = coverage_manager.full_workflow(args.test_args)
            
        elif args.command == 'status':
            status = coverage_manager.status()
            print_status(status)
            success = True
            
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
