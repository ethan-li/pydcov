# ==============================================================================
# Statistics Module - Statistical Analysis Library
# ==============================================================================
# This module provides statistical analysis functionality for dynamic arrays.
# It demonstrates inter-module dependencies by using the algorithm module.
#
# The module exports:
# - statistics: Static library target containing statistical analysis functions
# - Proper include directories for consumers
# - C90 standard compliance
# - Dependencies on the algorithm module
# ==============================================================================

cmake_minimum_required(VERSION 3.15)

# ==============================================================================
# Library Target Configuration
# ==============================================================================

# Create the statistics library
add_library(statistics STATIC
    src/statistics.c
    src/statistics.h
)

# Set C standard for this target
set_property(TARGET statistics PROPERTY C_STANDARD 90)
set_property(TARGET statistics PROPERTY C_STANDARD_REQUIRED ON)

# Configure include directories
target_include_directories(statistics 
    PUBLIC 
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        $<INSTALL_INTERFACE:include>
)

# Link against the algorithm library (inter-module dependency)
target_link_libraries(statistics 
    PUBLIC 
        pydcov::algorithm
)

# Apply compiler flags if they exist
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(statistics PRIVATE -Wall -Wextra -pedantic)
endif()

# Link math library on Unix systems
if(UNIX)
    target_link_libraries(statistics PRIVATE m)
endif()

# ==============================================================================
# Library Export Configuration
# ==============================================================================

# Create an alias for consistent naming
add_library(pydcov::statistics ALIAS statistics)

# Export the target for use by other modules
set_target_properties(statistics PROPERTIES
    EXPORT_NAME statistics
    OUTPUT_NAME statistics
)

# ==============================================================================
# Installation Configuration (Optional)
# ==============================================================================

# Install the library
install(TARGETS statistics
    EXPORT statisticsTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

# Install headers
install(FILES src/statistics.h
    DESTINATION include
)

# Export targets for find_package support
install(EXPORT statisticsTargets
    FILE statisticsTargets.cmake
    NAMESPACE pydcov::
    DESTINATION lib/cmake/statistics
)

# ==============================================================================
# Module Summary
# ==============================================================================

message(STATUS "Statistics module configured:")
message(STATUS "  Library: statistics (C90 static library)")
message(STATUS "  Headers: ${CMAKE_CURRENT_SOURCE_DIR}/src/statistics.h")
message(STATUS "  Source: ${CMAKE_CURRENT_SOURCE_DIR}/src/statistics.c")
message(STATUS "  Dependencies: pydcov::algorithm")
