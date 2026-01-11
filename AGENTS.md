# AGENTS.md

This file provides guidelines for agentic coding tools working on the pydcov repository.

## Build, Lint, and Test Commands

```bash
# Run all tests
python -m pytest -v --tb=short

# Run a single test file
python -m pytest tests/test_file.py -v --tb=short

# Run a specific test method
python -m pytest tests/test_file.py::TestClass::test_method -v --tb=short

# Run a specific test class
python -m pytest tests/test_file.py::TestClass -v --tb=short

# Run slow tests (excluded by default)
python -m pytest --run-slow

# Skip integration tests
python -m pytest --skip-integration

# Run tests by marker
python -m pytest -m "not slow"
python -m pytest -m integration
python -m pytest -m "not (integration or slow)"

# Run tests with coverage (optional, requires pytest-cov)
python -m pytest --cov=pydcov --cov-report=term-missing

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Build wheel package
python -m build --wheel

# Build standalone executable
pyinstaller pydcov.spec
```

## Code Style Guidelines

### Python & Types
- Python Version: 3.11+ required
- Type Hints: Required for all functions (mypy disallows untyped defs)
- Union Syntax: Use `str | None` syntax, NOT `Optional[str]`
- Typing Imports: Only import typing for complex types (List, Dict, Tuple)
- Add comment when not needed: `# No typing imports needed for Python 3.11+ union syntax`
- Optional Parameters: Use `param: type | None = None` for optional parameters

### Docstrings
- Format: Google-style with Args/Returns sections
- Module Docstrings: At top of each file describing purpose
- Function Docstrings: Describe purpose, parameters, and return values
- No Doc Comments: Don't use docstring-style comments inside functions

### Import Style
- Order: stdlib → third-party → local (pydcov)
- Separation: Blank line between each group
- No Unused Imports: Keep imports minimal and necessary
- Import Location: Place imports at module top, after docstring

### Naming Conventions
- Classes: PascalCase (e.g., `IncrementalCoverageManager`, `CoverageFileManager`)
- Functions/Variables: snake_case (e.g., `get_build_root`, `collect_coverage_files`)
- Constants: UPPER_SNAKE_CASE (e.g., `CONFIG_FILE_NAME`, `CMAKE_CACHE_FILE`)
- Test Methods: test_* (e.g., `test_function_coverage`, `test_collect_only_mode`)
- Private Methods: _leading_underscore (e.g., `_validate_environment`, `_detect_from_system`)
- Test Classes: Test* (e.g., `TestIncrementalCoverage`, `TestCLIBasicCommands`)

### Error Handling & Logging
- Logger Access: Use `get_logger()` for all logging
- Log Errors: Log errors with `self.logger.error(message)` or `self.logger.warning(message)`
- Exceptions: Raise meaningful exceptions (RuntimeError, ValueError, OSError, FileNotFoundError)
- Return Values: Methods return `False` on failure, `True` on success
- Validation: Validate inputs at method entry points
- Exception Messages: Provide context about what failed and why
- Try-Except: Use specific exceptions where possible, broad `Exception` only for cleanup
- Log Levels: DEBUG (detailed diagnostics), INFO (general info), WARNING (potential issues), ERROR (failures), SUCCESS (successful operations), STEP (major workflow steps)
- Colored Output: Use colored formatter for console output
- No Print: Use logging instead of print statements
- User-Facing Messages: Use SUCCESS and STEP levels for user feedback
- Debug Messages: Use DEBUG level for detailed technical info

### Path Handling
- Type: Always use `pathlib.Path` for file paths
- Normalization: Use `.resolve()` for path normalization
- Centralization: Manage paths via `PathManager` class
- Auto-Detection: Build directory auto-detected via CMakeCache.txt
- Path Operations: Use Path methods instead of os.path for better readability

### CLI Development
- ArgumentParser: Use argparse with clear help messages
- Subcommands: Each command has its own parser
- Required Args: Make required arguments explicit in help
- Optional Args: Use flags for optional parameters (e.g., `--collect-only`)
- Defaults: Provide sensible defaults for optional parameters
- Error Messages: Print user-friendly error messages to stdout
- Exit Codes: Return 0 for success, 1 for errors

### Testing
- Framework: pytest
- Test Files: `test_*.py` in tests/ directory
- Test Organization: Group related tests in test classes
- Fixtures: Use fixtures defined in `conftest.py` for common test setup
- Markers: slow, integration, statistical, algorithm, statistics, coverage_tools, package, cli, template
- Isolation: Use `tempfile.TemporaryDirectory()` for test isolation
- Subprocess: Run CLI commands via `subprocess.run()` in tests
- Skip: Use `pytest.skip()` for conditional test skipping with reason
- Assertions: Use clear assertion messages for debugging
- Collect-Only Tests: Include tests for collect-only mode with timestamp filtering

### Collect-Only Mode Implementation
- Parameter: Add `collect_only: bool = False` to collection methods
- Test Commands: Allow `test_command` to be `None` when `collect_only=True`
- Timestamp Filtering: For Clang, filter files by modification time when `collect_only=True`
- GCC Handling: Always collect all .gcda files (they are cumulative)
- Config Updates: Update `last_collect_time` in config after collect-only operations
- Logging: Log informative messages about timestamp filtering behavior

### Comments
- Minimal: Only comment complex/non-obvious logic
- Purpose: Comments should explain "why", not "what"
- Placement: Inline comments for single lines, block comments for multi-line explanations

### File Structure & Configuration
- pydcov/**: Main package
  - core/**: Core business logic (managers, workflows)
  - utils/**: Helper modules (tools, utilities, logging)
  - cmake/**: CMake integration files (.cmake)
  - cli.py: Command-line interface entry point
  - tests/**: Package tests (unit and integration tests)
  - examples/**: Example C/C++ projects with tests
  - docs/**: Documentation files (.md)
  - pyproject.toml: Package configuration and dependencies
  - pytest.ini: Test configuration
  - .github/workflows/**: CI/CD configuration
- PyDCov Config: Stored in `.pydcov.json` in project root
- Config Settings: build_root, pydcov_dir, last_collect_time
- Config Loading: Use `PyDCovConfig` class for config management
- Config Auto-save: Configuration saved during `init` command
- Code Organization:
  - Single Responsibility: One main class per module with clear purpose
  - Utils: Helper modules in `pydcov/utils/` for specific functionality
  - Core: Main business logic in `pydcov/core/`
  - CLI: Command-line interface in `pydcov/cli.py` (separate from core logic)
  - Dependencies: Minimize circular dependencies between modules

### Performance & Cross-Platform
- Subprocess: Use subprocess timeouts (default 30-120s depending on operation)
- Caching: Cache tool detection results (compiler, coverage tools) in instance variables
- Validation: Validate environment once at initialization
- Lazy Loading: Load resources only when needed
- Efficient File Operations: Use efficient file operations (rglob, copy2)
- Cross-Platform Paths: Use `Path` for cross-platform path handling
- Executable Detection: Use `os.access(path, os.X_OK)` for executable checks
- Shell Commands: Avoid shell-specific commands; prefer subprocess
- Environment Isolation: Use `os.environ.copy()` for environment isolation

### CI/CD Integration & API Design
- CI Test Coverage: Run pytest with appropriate markers in CI
- CI Build Testing: Test package builds in CI workflows
- CI Standalone Testing: Test standalone executable builds separately
- API Return Types: Use `-> bool` for success/failure methods
- API Optional Returns: Use `-> Path | None` for methods that may not find items
- API Tuple Returns: Use `-> Tuple[type1, type2]` for multiple return values
- API Default Args: Provide sensible defaults in method signatures

### Debugging, Testing, & Committing
- Verbose Mode: Use `-v` flag for detailed logging output
- Log Levels: Use DEBUG level for detailed step-by-step execution info
- Error Context: Include full context in error messages (paths, commands, outputs)
- AAA Pattern: Follow Arrange-Act-Assert pattern in test methods
- Descriptive Test Names: Use test method names that describe what is being tested
- Test Data: Use fixtures or helper functions for common test data
- Mocking: Mock external dependencies (subprocess calls, file system) when appropriate
- Clean Up: Ensure tests clean up temporary files and directories
- Pre-commit Checks: Ensure black, flake8, and mypy pass before committing
- Test Locally: Run tests before pushing to avoid CI failures
- Test Examples: Verify examples work after changes to core functionality
- Documentation: Update README and relevant docs when adding new features
