# ==============================================================================
# Coverage Configuration Module for CMake
# ==============================================================================
# This module provides comprehensive code coverage support for C/C++ projects
# using both GCC/gcov and Clang/llvm-cov toolchains.
#
# Features:
# - Cross-platform support (Linux, macOS)
# - Automatic compiler detection and tool configuration
# - Custom targets for coverage data management and report generation
# - Support for both HTML and LCOV format reports
#
# Usage:
#   include(cmake/coverage.cmake)
#   # Then use: cmake .. -DENABLE_COVERAGE=ON
# ==============================================================================

# Coverage option - can be overridden from command line
option(ENABLE_COVERAGE "Enable code coverage" OFF)

# Only proceed if coverage is enabled
if(NOT ENABLE_COVERAGE)
    return()
endif()

message(STATUS "Coverage enabled - configuring coverage tools...")

# ==============================================================================
# Compiler Detection and Flag Configuration
# ==============================================================================

if(CMAKE_C_COMPILER_ID MATCHES "GNU")
    set(COVERAGE_FLAGS "--coverage -fprofile-arcs -ftest-coverage")
    set(COVERAGE_LIBS "gcov")
    message(STATUS "Using GCC coverage with gcov")
elseif(CMAKE_C_COMPILER_ID MATCHES "Clang")
    set(COVERAGE_FLAGS "-fprofile-instr-generate -fcoverage-mapping")
    set(COVERAGE_LIBS "")
    message(STATUS "Using Clang coverage with llvm-cov")
else()
    message(WARNING "Coverage requested but compiler ${CMAKE_C_COMPILER_ID} is not supported")
    message(WARNING "Supported compilers: GCC, Clang")
    return()
endif()

# Apply coverage flags to compiler and linker
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${COVERAGE_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${COVERAGE_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${COVERAGE_FLAGS}")

# ==============================================================================
# Coverage Library Linking Function
# ==============================================================================

function(target_link_coverage_libraries target_name)
    if(COVERAGE_LIBS)
        target_link_libraries(${target_name} ${COVERAGE_LIBS})
        message(STATUS "Linked coverage libraries to ${target_name}: ${COVERAGE_LIBS}")
    endif()
endfunction()

# ==============================================================================
# Coverage Directory Setup
# ==============================================================================

# Create coverage output directory
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/coverage)

# ==============================================================================
# GCC/gcov Coverage Targets
# ==============================================================================

if(CMAKE_C_COMPILER_ID MATCHES "GNU")
    # Clean coverage data
    add_custom_target(coverage-clean
        COMMAND find ${CMAKE_BINARY_DIR} -name "*.gcda" -delete
        COMMAND find ${CMAKE_BINARY_DIR} -name "*.gcno" -delete
        COMMENT "Cleaning GCC coverage data"
    )
    
    # Generate coverage report
    add_custom_target(coverage-report
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/coverage
        COMMAND ${CMAKE_COMMAND} -E echo "Checking for coverage files..."
        COMMAND find ${CMAKE_BINARY_DIR} -name "*.gcda" -o -name "*.gcno" | head -10
        COMMAND ${CMAKE_COMMAND} -E echo "Capturing coverage data..."
        COMMAND lcov --capture --directory ${CMAKE_BINARY_DIR} --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info --rc branch_coverage=1 --ignore-errors gcov,source,unused
        COMMAND ${CMAKE_COMMAND} -E echo "Removing system files from coverage..."
        COMMAND lcov --remove ${CMAKE_BINARY_DIR}/coverage/coverage.info '/usr/*' '*/usr/*' --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info --rc branch_coverage=1 --ignore-errors unused,source
        COMMAND lcov --remove ${CMAKE_BINARY_DIR}/coverage/coverage.info '*/test/*' '*/tests/*' --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info --rc branch_coverage=1 --ignore-errors unused,source
        COMMAND ${CMAKE_COMMAND} -E echo "Generating HTML report..."
        COMMAND genhtml ${CMAKE_BINARY_DIR}/coverage/coverage.info --output-directory ${CMAKE_BINARY_DIR}/coverage/html --rc branch_coverage=1 --ignore-errors source,unused
        COMMAND ${CMAKE_COMMAND} -E echo "Coverage report generated successfully!"
        COMMENT "Generating coverage report with GCC/gcov"
        DEPENDS pydcov
    )

# ==============================================================================
# Clang/llvm-cov Coverage Targets
# ==============================================================================

elseif(CMAKE_C_COMPILER_ID MATCHES "Clang")
    # Find LLVM tools (they might be versioned on Ubuntu)
    find_program(LLVM_PROFDATA_EXECUTABLE NAMES llvm-profdata llvm-profdata-18 llvm-profdata-17 llvm-profdata-16 llvm-profdata-15 llvm-profdata-14)
    find_program(LLVM_COV_EXECUTABLE NAMES llvm-cov llvm-cov-18 llvm-cov-17 llvm-cov-16 llvm-cov-15 llvm-cov-14)

    if(NOT LLVM_PROFDATA_EXECUTABLE)
        message(FATAL_ERROR "llvm-profdata not found. Please install LLVM tools.")
    endif()

    if(NOT LLVM_COV_EXECUTABLE)
        message(FATAL_ERROR "llvm-cov not found. Please install LLVM tools.")
    endif()

    message(STATUS "Found llvm-profdata: ${LLVM_PROFDATA_EXECUTABLE}")
    message(STATUS "Found llvm-cov: ${LLVM_COV_EXECUTABLE}")

    # Clean coverage data
    add_custom_target(coverage-clean
        COMMAND find ${CMAKE_BINARY_DIR} -name "*.profraw" -delete
        COMMAND find ${CMAKE_BINARY_DIR} -name "*.profdata" -delete
        COMMENT "Cleaning Clang coverage data"
    )

    # Merge coverage data
    add_custom_target(coverage-merge
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/coverage
        COMMAND ${LLVM_PROFDATA_EXECUTABLE} merge -sparse ${CMAKE_BINARY_DIR}/*.profraw -o ${CMAKE_BINARY_DIR}/coverage/coverage.profdata
        COMMENT "Merging coverage data with ${LLVM_PROFDATA_EXECUTABLE}"
    )

    # Generate coverage report
    add_custom_target(coverage-report
        COMMAND ${LLVM_COV_EXECUTABLE} show ${CMAKE_BINARY_DIR}/pydcov -instr-profile=${CMAKE_BINARY_DIR}/coverage/coverage.profdata -format=html -output-dir=${CMAKE_BINARY_DIR}/coverage/html
        COMMAND ${LLVM_COV_EXECUTABLE} export ${CMAKE_BINARY_DIR}/pydcov -instr-profile=${CMAKE_BINARY_DIR}/coverage/coverage.profdata -format=lcov > ${CMAKE_BINARY_DIR}/coverage/coverage.info
        COMMENT "Generating coverage report with ${LLVM_COV_EXECUTABLE}"
        DEPENDS coverage-merge pydcov
    )
endif()

# ==============================================================================
# Coverage Status Summary
# ==============================================================================

message(STATUS "Coverage configuration complete:")
message(STATUS "  Coverage Flags: ${COVERAGE_FLAGS}")
if(COVERAGE_LIBS)
    message(STATUS "  Coverage Libraries: ${COVERAGE_LIBS}")
endif()
message(STATUS "  Coverage Output: ${CMAKE_BINARY_DIR}/coverage/")
message(STATUS "  Available targets: coverage-clean, coverage-report")
if(CMAKE_C_COMPILER_ID MATCHES "Clang")
    message(STATUS "  Additional target: coverage-merge")
endif()
