# ==============================================================================
# Algorithm Module - Dynamic Array Library
# ==============================================================================
# This module provides a C90-compliant dynamic array implementation that can
# be used by other modules in the project.
#
# The module exports:
# - algorithm: Static library target containing the dynamic array implementation
# - Proper include directories for consumers
# - C90 standard compliance
# ==============================================================================

cmake_minimum_required(VERSION 3.9.6)

# Include PyDCov coverage support
include(cmake/coverage.cmake)

# ==============================================================================
# Library Target Configuration
# ==============================================================================

# Create the algorithm library
add_library(algorithm STATIC
    src/algorithm.c
    src/algorithm.h
)

# Set C standard for this target
set_property(TARGET algorithm PROPERTY C_STANDARD 90)
set_property(TARGET algorithm PROPERTY C_STANDARD_REQUIRED ON)

# Configure include directories
target_include_directories(algorithm 
    PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        $<INSTALL_INTERFACE:include>
)

# Apply compiler flags if they exist
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(algorithm PRIVATE -Wall -Wextra -pedantic)
endif()

# ==============================================================================
# Library Export Configuration
# ==============================================================================

# Create an alias for consistent naming
add_library(pydcov::algorithm ALIAS algorithm)

# Export the target for use by other modules
set_target_properties(algorithm PROPERTIES
    EXPORT_NAME algorithm
    OUTPUT_NAME algorithm
)

# ==============================================================================
# Installation Configuration (Optional)
# ==============================================================================

# Install the library
install(TARGETS algorithm
    EXPORT algorithmTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

# Install headers
install(FILES src/algorithm.h
    DESTINATION include
)

# Export targets for find_package support
install(EXPORT algorithmTargets
    FILE algorithmTargets.cmake
    NAMESPACE pydcov::
    DESTINATION lib/cmake/algorithm
)

# ==============================================================================
# Module Summary
# ==============================================================================

message(STATUS "Algorithm module configured:")
message(STATUS "  Library: algorithm (C90 static library)")
message(STATUS "  Headers: ${CMAKE_CURRENT_SOURCE_DIR}/src/algorithm.h")
message(STATUS "  Source: ${CMAKE_CURRENT_SOURCE_DIR}/src/algorithm.c")
