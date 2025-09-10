# ==============================================================================
# PyDCov - C Code Coverage for Python-Driven Tests
# ==============================================================================
# A focused sample project demonstrating how to measure code coverage for C code
# that is executed via command-line interface from Python tests.
#
# This CMakeLists.txt contains the core build configuration. Coverage support
# is provided through a separate module (cmake/coverage.cmake) that can be
# optionally included.
#
# Basic build:    cmake .. -DCMAKE_BUILD_TYPE=Release
# With coverage:  cmake .. -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
# ==============================================================================

cmake_minimum_required(VERSION 3.15)
project(pydcov VERSION 1.0.0 LANGUAGES C CXX)

# ==============================================================================
# Language Standards Configuration
# ==============================================================================

# Set C and C++ standards
set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ==============================================================================
# Compiler Configuration
# ==============================================================================

# Compiler-specific warning flags
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -pedantic")
endif()

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic")
endif()

# ==============================================================================
# Coverage Support (Optional Module)
# ==============================================================================

# Include coverage configuration if requested
# This module handles all coverage-related settings, compiler flags, and targets
include(cmake/coverage.cmake)

# ==============================================================================
# Module Configuration
# ==============================================================================
# This project follows a modular architecture where each module contains:
# - src/: Core library implementation
# - app/: Command-line interface application
# - CMakeLists.txt: Module-specific build configuration
#
# Modules are designed to be:
# - Self-contained with clear interfaces
# - Reusable across different applications
# - Independently testable and maintainable
# - Following consistent naming conventions (pydcov::module_name)
# ==============================================================================

# Add algorithm module (library + app)
add_subdirectory(algorithm)
add_subdirectory(algorithm/app)

# Add statistics module (library + app)
add_subdirectory(statistics)
add_subdirectory(statistics/app)

# Create an alias for the main executable to maintain backward compatibility
add_executable(pydcov ALIAS algorithm_cli)

# ==============================================================================
# Installation Configuration
# ==============================================================================

# Installation is handled by individual modules

# ==============================================================================
# Testing Support
# ==============================================================================

# Enable CTest for testing support
enable_testing()

# ==============================================================================
# Build Configuration Summary
# ==============================================================================

# Print configuration summary
message(STATUS "PyDCov Build Configuration:")
message(STATUS "  Project Version: ${PROJECT_VERSION}")
message(STATUS "  C Compiler: ${CMAKE_C_COMPILER_ID} ${CMAKE_C_COMPILER_VERSION}")
message(STATUS "  CXX Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C Standard: C${CMAKE_C_STANDARD}")
message(STATUS "  CXX Standard: C++${CMAKE_CXX_STANDARD}")

# Module summary
message(STATUS "Configured Modules:")
message(STATUS "  - algorithm: Dynamic array library + CLI")
message(STATUS "  - statistics: Statistical analysis library + CLI")
message(STATUS "Available Executables:")
message(STATUS "  - algorithm_cli: Dynamic array operations")
message(STATUS "  - statistics_cli: Statistical analysis")
message(STATUS "  - pydcov: Alias for algorithm_cli (backward compatibility)")

# Coverage status is reported by the coverage module if enabled
