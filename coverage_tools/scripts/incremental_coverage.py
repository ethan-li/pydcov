#!/usr/bin/env python3
"""
Incremental Coverage Collection Script for pydcov project.

Python-based incremental coverage collection script for pydcov project.
Provides incremental coverage collection across multiple test executions,
where each test run adds to the cumulative coverage data.

Usage:
    python incremental_coverage.py [command] [options]

Commands:
    init                  - Initialize incremental coverage collection
    add [test_args]       - Run tests and add coverage data to collection
    merge                 - Merge all accumulated coverage data
    report                - Generate final comprehensive coverage report
    full [test_args]      - Complete workflow: init, add, merge, report
    clean                 - Clean all incremental coverage data
    status                - Show current incremental coverage status
    help                  - Show this help message

Examples:
    # Using pytest
    python incremental_coverage.py init
    python incremental_coverage.py add python -m pytest tests/test_basic.py
    python incremental_coverage.py add python -m pytest tests/test_advanced.py -v
    python incremental_coverage.py merge
    python incremental_coverage.py report

    # Using unittest
    python incremental_coverage.py add python -m unittest tests.test_basic

    # Complete workflow
    python incremental_coverage.py full python -m pytest tests/
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Add the coverage_tools package to the path
coverage_tools_dir = Path(__file__).parent.parent
sys.path.insert(0, str(coverage_tools_dir.parent))

from coverage_tools.core.incremental_coverage import IncrementalCoverageManager
from coverage_tools.utils.logging_config import setup_logging


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Incremental coverage collection for pydcov project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'command',
        choices=['init', 'add', 'merge', 'report', 'full', 'clean', 'status', 'help'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'test_args',
        nargs='*',
        help='Test command arguments (required for add and full commands). Examples: "python -m pytest tests/" or "python -m unittest discover"'
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
    """Print incremental coverage status information."""
    print("\n" + "="*50)
    print("Incremental Coverage Status")
    print("="*50)
    
    print(f"Compiler: {status['compiler']}")
    
    if status['compiler'] == 'clang':
        file_type = '.profraw files'
    else:
        file_type = '.info files'
    
    print(f"Accumulated {file_type}: {status['accumulated_files']}")
    
    if status['merged_data_exists']:
        print(f"✓ Merged coverage data available: {Path(status['merged_file']).name}")
    else:
        print("✗ No merged coverage data found")
    
    if status['report_exists']:
        print(f"✓ Final report available: {status['report_path']}")
    else:
        print("✗ No final report generated yet")
    
    print("="*50)


def print_workflow_header():
    """Print workflow header."""
    print("\n" + "="*50)
    print("Incremental Coverage Full Workflow")
    print("="*50)


def print_workflow_footer(report_path: Optional[str] = None):
    """Print workflow completion message."""
    print("\n" + "="*50)
    print("Incremental Coverage Workflow Completed")
    print("="*50)
    
    if report_path:
        print(f"\n✓ Final comprehensive coverage report available at:")
        print(f"✓   {report_path}")


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
        # Initialize incremental coverage manager
        incremental_manager = IncrementalCoverageManager(args.project_root)
        
        # Execute command
        if args.command == 'init':
            success = incremental_manager.init()
            
        elif args.command == 'add':
            if not args.test_args:
                logger.error("Test command is required for 'add' command. Please specify a test command.")
                logger.info("Examples: python -m pytest tests/, python -m unittest discover, ./run_tests.sh")
                return 1
            success = incremental_manager.add(args.test_args)

        elif args.command == 'merge':
            success = incremental_manager.merge()

        elif args.command == 'report':
            success = incremental_manager.report()

        elif args.command == 'clean':
            success = incremental_manager.clean()

        elif args.command == 'status':
            status = incremental_manager.status()
            print_status(status)
            success = True

        elif args.command == 'full':
            if not args.test_args:
                logger.error("Test command is required for 'full' command. Please specify a test command.")
                logger.info("Examples: python -m pytest tests/, python -m unittest discover, ./run_tests.sh")
                return 1

            print_workflow_header()
            logger.info("Running complete incremental coverage workflow")
            logger.info(f"Test arguments: {' '.join(args.test_args)}")

            success = incremental_manager.full_workflow(args.test_args)
            
            if success:
                # Get final status to show report path
                status = incremental_manager.status()
                report_path = status.get('report_path')
                print_workflow_footer(report_path)
            
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
