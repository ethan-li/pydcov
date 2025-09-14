# PyDCov Standalone Executables

PyDCov provides standalone executables that can run on systems without Python installed. These executables are built using PyInstaller and include all necessary dependencies.

## Available Platforms

- **Linux (x64)**: `pydcov-linux-x64`
- **macOS (ARM64)**: `pydcov-macos-arm64`

## Download

### From GitHub Releases

1. Go to the [GitHub Releases](https://github.com/ethan-li/pydcov/releases) page
2. Download the appropriate executable for your platform
3. Make the file executable: `chmod +x pydcov-linux-x64`
4. Run: `./pydcov-linux-x64 --version`

### From CI Artifacts

Standalone executables are built automatically by GitHub Actions CI for every commit. You can download them from:

1. Go to the [GitHub Actions](https://github.com/ethan-li/pydcov/actions) page
2. Click on a recent CI run
3. Download the artifacts:
   - `pydcov-linux-x64`
   - `pydcov-macos-arm64`

## Usage

The standalone executables work exactly like the Python package:

```bash
# Check version
./pydcov-linux-x64 --version

# Initialize CMake integration
./pydcov-linux-x64 init-cmake

# Initialize incremental coverage
./pydcov-linux-x64 init

# Add coverage data
./pydcov-linux-x64 add python -m pytest tests/

# Generate report
./pydcov-linux-x64 report
```

## Building Your Own

You can build standalone executables yourself using the included build script:

### Prerequisites

- Python 3.11 or later
- PyInstaller (installed automatically by the build script)

### Build Process

```bash
# Clone the repository
git clone https://github.com/ethan-li/pydcov.git
cd pydcov

# Install development dependencies (optional)
pip install -e ".[dev]"

# Build standalone executable
python build_standalone.py --clean --test
```

The build script will:
1. Install PyInstaller if not already installed
2. Build the standalone executable using the PyInstaller spec file
3. Test the executable to ensure it works correctly
4. Report the final executable size and location

### Build Script Options

```bash
python build_standalone.py --help
```

- `--clean`: Clean build directories before building
- `--test`: Test the built executable after building

### Cross-Platform Building

To build for different platforms, you need to run the build on the target platform:

- **Linux**: Run on a Linux system or use Docker
- **macOS**: Run on a macOS system
- **Windows**: Run on a Windows system (not currently supported in CI)

## Technical Details

### PyInstaller Configuration

The standalone executables are built using a custom PyInstaller spec file (`pydcov.spec`) that:

- Includes all PyDCov Python modules
- Bundles CMake integration files (coverage.cmake, COVERAGE_USAGE.md)
- Excludes unnecessary modules to reduce size
- Creates a single-file executable

### File Size

Typical executable sizes:
- Linux (x64): ~10-12 MB
- macOS (ARM64): ~10-12 MB

### Dependencies

The standalone executables include:
- Python runtime
- All PyDCov modules and dependencies
- CMake integration files
- Standard library modules

### Limitations

- Executables are platform-specific (cannot run Linux executable on macOS)
- Larger file size compared to Python package
- Startup time may be slightly slower than Python package

## Troubleshooting

### Permission Denied

```bash
chmod +x pydcov-linux-x64
```

### Command Not Found

Make sure you're using the correct path:
```bash
./pydcov-linux-x64 --version  # Current directory
/path/to/pydcov-linux-x64 --version  # Full path
```

### macOS Security Warning

On macOS, you may need to allow the executable in System Preferences > Security & Privacy if you get a security warning.

### Testing the Executable

```bash
# Test basic functionality
./pydcov-linux-x64 --version
./pydcov-linux-x64 --help

# Test CMake integration
mkdir test_dir && cd test_dir
../pydcov-linux-x64 init-cmake
ls cmake/  # Should show coverage.cmake and COVERAGE_USAGE.md
```

## CI Integration

The standalone executables are automatically built and tested in GitHub Actions CI:

1. **Build Job**: Creates executables for Linux and macOS
2. **Test Job**: Tests basic functionality and CMake integration
3. **Artifact Upload**: Uploads executables as CI artifacts
4. **Release**: Includes executables in GitHub releases

See `.github/workflows/ci.yml` for the complete CI configuration.
