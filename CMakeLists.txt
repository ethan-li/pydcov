# ==============================================================================
# PyDCov - C Code Coverage for Python-Driven Tests
# ==============================================================================
# This CMakeLists.txt serves dual purposes:
# 1. Demonstrates how to integrate the PyDCov coverage tools into a C/C++ project
# 2. Builds the example modules for testing and demonstration
#
# Users can use this file as a template for integrating coverage tools into
# their own projects. The core coverage functionality is provided through
# cmake/coverage.cmake which can be included in any CMake project.
#
# Basic build:    cmake .. -DCMAKE_BUILD_TYPE=Release
# With coverage:  PYDCOV_ENABLE_COVERAGE=1 cmake .. -DCMAKE_BUILD_TYPE=Debug
# ==============================================================================

cmake_minimum_required(VERSION 3.9.6)
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
# Example Module Configuration
# ==============================================================================
# The examples/ directory contains demonstration modules that show how to use
# the PyDCov coverage tools with real C/C++ projects. Each module follows
# a consistent architecture:
# - src/: Core library implementation
# - app/: Command-line interface application
# - tests/: Module-specific test suite
# - CMakeLists.txt: Module-specific build configuration
#
# These modules serve as both working examples and test subjects for the
# coverage tools, demonstrating best practices for modular C/C++ development.
# ==============================================================================

# Add algorithm module (library + app)
add_subdirectory(examples/algorithm)
add_subdirectory(examples/algorithm/app)

# Add statistics module (library + app)
add_subdirectory(examples/statistics)
add_subdirectory(examples/statistics/app)

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
