# ==============================================================================
# Algorithm App - Dynamic Array CLI Interface
# ==============================================================================
# This module provides a command-line interface for the dynamic array library.
# It demonstrates how to use the algorithm library and provides a CLI tool
# for testing and interaction.
#
# The module creates:
# - algorithm_cli: Executable target that links against the algorithm library
# - Proper dependency management
# - C++11 standard compliance for the CLI wrapper
# ==============================================================================

cmake_minimum_required(VERSION 3.15)

# ==============================================================================
# Executable Target Configuration
# ==============================================================================

# Create the CLI executable
add_executable(algorithm_cli
    main.cpp
)

# Set C++ standard for this target
set_property(TARGET algorithm_cli PROPERTY CXX_STANDARD 11)
set_property(TARGET algorithm_cli PROPERTY CXX_STANDARD_REQUIRED ON)

# Link against the algorithm library
target_link_libraries(algorithm_cli 
    PRIVATE 
        pydcov::algorithm
)

# Apply compiler flags if they exist
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(algorithm_cli PRIVATE -Wall -Wextra -pedantic)
endif()

# ==============================================================================
# Coverage Support
# ==============================================================================

# Link coverage libraries if coverage is enabled
# This function is defined in the root cmake/coverage.cmake
if(COMMAND target_link_coverage_libraries)
    target_link_coverage_libraries(algorithm_cli)
endif()

# ==============================================================================
# Installation Configuration
# ==============================================================================

# Install the executable
install(TARGETS algorithm_cli
    RUNTIME DESTINATION bin
)

# ==============================================================================
# Module Summary
# ==============================================================================

message(STATUS "Algorithm CLI configured:")
message(STATUS "  Executable: algorithm_cli (C++11)")
message(STATUS "  Source: ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp")
message(STATUS "  Dependencies: pydcov::algorithm")
