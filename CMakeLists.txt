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
# Build Targets
# ==============================================================================

# Create the C library
add_library(algorithm STATIC
    src/algorithm.c
    src/algorithm.h
)

target_include_directories(algorithm PUBLIC src)

# Create the main executable
add_executable(pydcov
    src/main.cpp
)

target_link_libraries(pydcov algorithm)

# Link coverage libraries if coverage is enabled
# This function is defined in cmake/coverage.cmake
if(COMMAND target_link_coverage_libraries)
    target_link_coverage_libraries(pydcov)
endif()

# ==============================================================================
# Installation Configuration
# ==============================================================================

# Install targets
install(TARGETS pydcov DESTINATION bin)

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

# Coverage status is reported by the coverage module if enabled
