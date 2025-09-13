# ==============================================================================
# Generic Coverage Configuration Module for CMake
# ==============================================================================
# This module provides comprehensive code coverage support for C/C++ projects
# using both GCC/gcov and Clang/llvm-cov toolchains.
#
# Features:
# - Cross-platform support (Linux, macOS)
# - Automatic compiler detection and tool configuration
# - Custom targets for coverage data management and report generation
# - Support for both HTML and LCOV format reports
# - Automatic detection of executable targets for coverage
# - Generic and reusable across different project structures
#
# Usage:
#   include(cmake/coverage.cmake)
#   # Register executables for coverage (optional - auto-detection available):
#   coverage_add_executable(my_executable)
#   # Then use: cmake .. -DENABLE_COVERAGE=ON
# ==============================================================================

# Coverage option - can be overridden from command line
option(ENABLE_COVERAGE "Enable code coverage" OFF)

# Python tools are the only supported coverage solution
set(USE_PYTHON_COVERAGE_TOOLS ON)

# Global list to store coverage executables
set_property(GLOBAL PROPERTY COVERAGE_EXECUTABLES "")

# Global list to store coverage executable paths
set_property(GLOBAL PROPERTY COVERAGE_EXECUTABLE_PATHS "")

# ==============================================================================
# Coverage Executable Registration Functions
# ==============================================================================

# Function to register an executable for coverage analysis
function(coverage_add_executable target_name)
    if(NOT TARGET ${target_name})
        message(WARNING "coverage_add_executable: Target '${target_name}' does not exist")
        return()
    endif()

    get_target_property(target_type ${target_name} TYPE)
    if(NOT target_type STREQUAL "EXECUTABLE")
        message(WARNING "coverage_add_executable: Target '${target_name}' is not an executable")
        return()
    endif()

    # Add to global list
    get_property(current_executables GLOBAL PROPERTY COVERAGE_EXECUTABLES)
    list(APPEND current_executables ${target_name})
    set_property(GLOBAL PROPERTY COVERAGE_EXECUTABLES "${current_executables}")

    message(STATUS "Registered executable for coverage: ${target_name}")
endfunction()

# Function to auto-detect executable targets
function(coverage_auto_detect_executables)
    # Get all targets in the current directory and subdirectories
    get_property(all_targets DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY BUILDSYSTEM_TARGETS)

    foreach(target ${all_targets})
        if(TARGET ${target})
            get_target_property(target_type ${target} TYPE)
            if(target_type STREQUAL "EXECUTABLE")
                # Skip test executables (common naming patterns)
                string(TOLOWER ${target} target_lower)
                if(NOT target_lower MATCHES "(test|tests|testing|gtest|catch|benchmark)")
                    coverage_add_executable(${target})
                endif()
            endif()
        endif()
    endforeach()
endfunction()

# Function to get all registered executables and their paths
function(coverage_get_executables out_targets out_paths)
    get_property(executables GLOBAL PROPERTY COVERAGE_EXECUTABLES)

    set(target_list "")
    set(path_list "")

    foreach(target ${executables})
        if(TARGET ${target})
            list(APPEND target_list ${target})
            list(APPEND path_list "$<TARGET_FILE:${target}>")
        endif()
    endforeach()

    set(${out_targets} "${target_list}" PARENT_SCOPE)
    set(${out_paths} "${path_list}" PARENT_SCOPE)
endfunction()

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
        target_link_libraries(${target_name} PRIVATE ${COVERAGE_LIBS})
        message(STATUS "Linked coverage libraries to ${target_name}: ${COVERAGE_LIBS}")
    endif()

    # Auto-register executable for coverage if it's an executable
    if(TARGET ${target_name})
        get_target_property(target_type ${target_name} TYPE)
        if(target_type STREQUAL "EXECUTABLE")
            coverage_add_executable(${target_name})
        endif()
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



    # Auto-detect executables if none registered
    add_custom_target(coverage-detect-executables
        COMMAND ${CMAKE_COMMAND} -E echo "Auto-detecting executables for coverage..."
        COMMENT "Detecting coverage executables"
    )

    # Generate coverage report with dynamic executable detection
    add_custom_target(coverage-report
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/coverage
        COMMAND ${CMAKE_COMMAND} -E echo "Checking for coverage files..."
        COMMAND find ${CMAKE_BINARY_DIR} -name "*.gcda" -o -name "*.gcno" | head -10
        COMMAND ${CMAKE_COMMAND} -E echo "Capturing coverage data..."
        COMMAND lcov --capture --directory ${CMAKE_BINARY_DIR} --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info --rc branch_coverage=1 --ignore-errors gcov,source,unused
        COMMAND ${CMAKE_COMMAND} -E echo "Removing system files from coverage..."
        COMMAND lcov --remove ${CMAKE_BINARY_DIR}/coverage/coverage.info '/usr/*' '*/usr/*' --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info --rc branch_coverage=1 --ignore-errors unused,source
        COMMAND lcov --remove ${CMAKE_BINARY_DIR}/coverage/coverage.info '*/test/*' '*/tests/*' '*/testing/*' '*/gtest/*' '*/catch/*' '*/benchmark/*' --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info --rc branch_coverage=1 --ignore-errors unused,source
        COMMAND ${CMAKE_COMMAND} -E echo "Generating HTML report..."
        COMMAND genhtml ${CMAKE_BINARY_DIR}/coverage/coverage.info --output-directory ${CMAKE_BINARY_DIR}/coverage/html --rc branch_coverage=1 --ignore-errors source,unused
        COMMAND ${CMAKE_COMMAND} -E echo "Coverage report generated successfully!"
        COMMENT "Generating coverage report with GCC/gcov"
    )

    # Function to add dependencies for GCC coverage
    function(coverage_finalize_gcc_targets)
        coverage_get_executables(exec_targets exec_paths)

        if(NOT exec_targets)
            message(WARNING "No executables registered for coverage. Use coverage_add_executable() or enable auto-detection.")
            return()
        endif()

        # Add dependencies on the executables
        foreach(target ${exec_targets})
            if(TARGET ${target})
                add_dependencies(coverage-report ${target})
            endif()
        endforeach()

        message(STATUS "Coverage configured for executables: ${exec_targets}")
    endfunction()

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

    # Generate coverage report with dynamic executable detection
    add_custom_target(coverage-report
        COMMENT "Generating coverage report with ${LLVM_COV_EXECUTABLE}"
        DEPENDS coverage-merge
    )



    # Function to add coverage commands for registered executables
    function(coverage_finalize_clang_targets)
        coverage_get_executables(exec_targets exec_paths)

        if(NOT exec_targets)
            message(WARNING "No executables registered for coverage. Use coverage_add_executable() or enable auto-detection.")
            return()
        endif()

        # Build executable list with generator expressions
        set(exec_list "")
        foreach(target ${exec_targets})
            if(TARGET ${target})
                set(exec_list "${exec_list} $<TARGET_FILE:${target}>")
            endif()
        endforeach()

        # Generate a script with proper generator expression handling
        set(coverage_script_template "${CMAKE_BINARY_DIR}/run_coverage_template.sh")
        file(WRITE ${coverage_script_template} "#!/bin/bash\n")
        file(APPEND ${coverage_script_template} "set -e\n")
        file(APPEND ${coverage_script_template} "echo \"Running coverage for executables: ${exec_targets}\"\n")
        file(APPEND ${coverage_script_template} "echo \"Generating HTML coverage report...\"\n")
        file(APPEND ${coverage_script_template} "${LLVM_COV_EXECUTABLE} show${exec_list} -instr-profile=${CMAKE_BINARY_DIR}/coverage/coverage.profdata -format=html -output-dir=${CMAKE_BINARY_DIR}/coverage/html\n")
        file(APPEND ${coverage_script_template} "echo \"Generating LCOV coverage report...\"\n")
        file(APPEND ${coverage_script_template} "${LLVM_COV_EXECUTABLE} export${exec_list} -instr-profile=${CMAKE_BINARY_DIR}/coverage/coverage.profdata -format=lcov > ${CMAKE_BINARY_DIR}/coverage/coverage.info\n")
        file(APPEND ${coverage_script_template} "echo \"Coverage reports generated successfully!\"\n")

        # Use file(GENERATE) to properly expand generator expressions
        file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/run_coverage.sh"
             INPUT "${coverage_script_template}"
             FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE)

        # Add the coverage command that runs the generated script
        add_custom_command(TARGET coverage-report POST_BUILD
            COMMAND bash "${CMAKE_BINARY_DIR}/run_coverage.sh"
            COMMENT "Generating coverage reports for: ${exec_targets}"
            VERBATIM
        )

        # Add dependencies on the executables
        foreach(target ${exec_targets})
            if(TARGET ${target})
                add_dependencies(coverage-report ${target})
            endif()
        endforeach()

        message(STATUS "Coverage configured for executables: ${exec_targets}")
    endfunction()



endif()

# ==============================================================================
# Coverage Finalization and Auto-Detection
# ==============================================================================

# Function to finalize coverage configuration
function(coverage_finalize)
    # Auto-detect executables if none were manually registered
    get_property(current_executables GLOBAL PROPERTY COVERAGE_EXECUTABLES)
    if(NOT current_executables)
        message(STATUS "No executables manually registered, attempting auto-detection...")
        coverage_auto_detect_executables()
    endif()

    # Finalize targets based on compiler
    if(CMAKE_C_COMPILER_ID MATCHES "GNU")
        coverage_finalize_gcc_targets()
    elseif(CMAKE_C_COMPILER_ID MATCHES "Clang")
        coverage_finalize_clang_targets()
    endif()
endfunction()

# Auto-finalize at the end of configuration (can be overridden)
cmake_language(DEFER CALL coverage_finalize)

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

message(STATUS "  Use coverage_add_executable(target) to register specific executables")
message(STATUS "  Or rely on auto-detection of non-test executables")

# Python tools information
find_program(PYTHON3_EXECUTABLE python3)
if(PYTHON3_EXECUTABLE)
    message(STATUS "  Python coverage tools: ENABLED")
    message(STATUS "    Python executable: ${PYTHON3_EXECUTABLE}")
    message(STATUS "    Python tools directory: ${CMAKE_SOURCE_DIR}/coverage_tools/")
    message(STATUS "    Use: python3 coverage_tools/scripts/coverage.py [command]")

    message(STATUS "    Use: python3 coverage_tools/scripts/coverage_modules.py [command]")
else()
    message(WARNING "  Python coverage tools: python3 not found")
    message(WARNING "    Install Python 3 to use the coverage tools")
endif()
