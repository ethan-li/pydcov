#!/usr/bin/env python3
"""
Module Coverage Workflow Script for pydcov project.

Python-based module coverage workflow script for pydcov project.
Provides a complete workflow for generating module-specific coverage reports
without modifying the CMake build system.

Usage:
    python coverage_modules.py [command] [module]

Commands:
    full [module]     - Run complete workflow: build, test, generate module reports
    build             - Build project with coverage instrumentation
    test [module]     - Run tests with coverage data collection
    generate [module] - Generate module-specific coverage reports
    clean             - Clean module coverage data
    status [module]   - Show module coverage status
    help              - Show this help message

Modules:
    algorithm         - Dynamic array library module
    statistics        - Statistical analysis library module
    (omit module to process all modules)

Examples:
    # Module-specific workflows (uses default pytest)
    python coverage_modules.py full algorithm # Complete workflow for algorithm module only
    python coverage_modules.py test statistics # Test statistics module only
    python coverage_modules.py generate       # Generate reports for all modules
    python coverage_modules.py status         # Show status for all modules

    # Custom test commands
    python coverage_modules.py test algorithm --test-command "python -m unittest discover algorithm/tests/"
    python coverage_modules.py full statistics --test-command "./test_statistics.sh"
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add the coverage_tools package to the path
coverage_tools_dir = Path(__file__).parent.parent
sys.path.insert(0, str(coverage_tools_dir.parent))

from coverage_tools.core.module_coverage import ModuleCoverageManager
from coverage_tools.utils.logging_config import setup_logging


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Module coverage workflow for pydcov project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'command',
        choices=['full', 'build', 'test', 'generate', 'clean', 'status', 'help'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'module',
        nargs='?',
        choices=['algorithm', 'statistics'],
        help='Module to process (algorithm or statistics). If omitted, processes all modules.'
    )

    parser.add_argument(
        '--test-command',
        nargs='*',
        help='Custom test command for test operations. Required when no module is specified. When module is specified, defaults to pytest with module-specific paths.'
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


def print_status(status: dict, module: Optional[str] = None):
    """Print module coverage status information."""
    print("\n" + "="*60)
    if module:
        print(f"Module Coverage Status - {module.title()}")
    else:
        print("Module Coverage Status - All Modules")
    print("="*60)
    
    print(f"Compiler: {status['compiler']}")
    print()
    
    for mod_name, mod_status in status['modules'].items():
        print(f"{mod_name.title()} Module:")
        print(f"  Source files: {mod_status['source_files']}")
        print(f"  Executable: {'✓' if mod_status['executable_exists'] else '✗'}")
        print(f"  Coverage data: {'✓' if mod_status['coverage_data_exists'] else '✗'}")
        print(f"  Report: {'✓' if mod_status['report_exists'] else '✗'}")
        
        if mod_status['report_exists']:
            print(f"    Path: {mod_status['report_path']}")
        print()
    
    print("="*60)


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
        # Initialize module coverage manager
        module_manager = ModuleCoverageManager(args.project_root)
        
        # Execute command
        if args.command == 'build':
            success = module_manager.build()
            
        elif args.command == 'test':
            if not args.module and not args.test_command:
                logger.error("Either a module must be specified or a test command must be provided.")
                logger.info("Examples: 'python coverage_modules.py test algorithm' or 'python coverage_modules.py test --test-command \"python -m pytest tests/\"'")
                return 1
            success = module_manager.test(args.module, args.test_command)

        elif args.command == 'generate':
            success = module_manager.generate_module_reports(args.module)

        elif args.command == 'clean':
            success = module_manager.clean()

        elif args.command == 'full':
            if not args.module and not args.test_command:
                logger.error("Either a module must be specified or a test command must be provided.")
                logger.info("Examples: 'python coverage_modules.py full algorithm' or 'python coverage_modules.py full --test-command \"python -m pytest tests/\"'")
                return 1
            success = module_manager.full_workflow(args.module, args.test_command)
            
        elif args.command == 'status':
            status = module_manager.status(args.module)
            print_status(status, args.module)
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
