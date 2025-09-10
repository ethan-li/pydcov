# ==============================================================================
# Statistics App - Statistical Analysis CLI Interface
# ==============================================================================
# This module provides a command-line interface for statistical analysis.
# It demonstrates inter-module dependencies by using both the algorithm and
# statistics libraries.
#
# The module creates:
# - statistics_cli: Executable target that links against both libraries
# - Proper dependency management
# - C++11 standard compliance for the CLI wrapper
# ==============================================================================

cmake_minimum_required(VERSION 3.15)

# ==============================================================================
# Executable Target Configuration
# ==============================================================================

# Create the CLI executable
add_executable(statistics_cli
    main.cpp
)

# Set C++ standard for this target
set_property(TARGET statistics_cli PROPERTY CXX_STANDARD 11)
set_property(TARGET statistics_cli PROPERTY CXX_STANDARD_REQUIRED ON)

# Link against both the algorithm and statistics libraries
target_link_libraries(statistics_cli 
    PRIVATE 
        pydcov::statistics
        pydcov::algorithm
)

# Apply compiler flags if they exist
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(statistics_cli PRIVATE -Wall -Wextra -pedantic)
endif()

# ==============================================================================
# Coverage Support
# ==============================================================================

# Link coverage libraries if coverage is enabled
# This function is defined in the root cmake/coverage.cmake
if(COMMAND target_link_coverage_libraries)
    target_link_coverage_libraries(statistics_cli)
endif()

# ==============================================================================
# Installation Configuration
# ==============================================================================

# Install the executable
install(TARGETS statistics_cli
    RUNTIME DESTINATION bin
)

# ==============================================================================
# Module Summary
# ==============================================================================

message(STATUS "Statistics CLI configured:")
message(STATUS "  Executable: statistics_cli (C++11)")
message(STATUS "  Source: ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp")
message(STATUS "  Dependencies: pydcov::statistics, pydcov::algorithm")
