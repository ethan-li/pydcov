cmake_minimum_required(VERSION 3.15)
project(pydcov VERSION 1.0.0 LANGUAGES C CXX)

# Set C and C++ standards
set(CMAKE_C_STANDARD 90)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options for coverage
option(ENABLE_COVERAGE "Enable code coverage" OFF)

# Compiler-specific settings
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -pedantic")
endif()

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic")
endif()

# Coverage flags
if(ENABLE_COVERAGE)
    if(CMAKE_C_COMPILER_ID MATCHES "GNU")
        set(COVERAGE_FLAGS "--coverage -fprofile-arcs -ftest-coverage")
        set(COVERAGE_LIBS "gcov")
        message(STATUS "Using GCC coverage with gcov")
    elseif(CMAKE_C_COMPILER_ID MATCHES "Clang")
        set(COVERAGE_FLAGS "-fprofile-instr-generate -fcoverage-mapping")
        set(COVERAGE_LIBS "")
        message(STATUS "Using Clang coverage with llvm-cov")
    endif()

    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${COVERAGE_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${COVERAGE_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${COVERAGE_FLAGS}")
endif()

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

if(ENABLE_COVERAGE AND COVERAGE_LIBS)
    target_link_libraries(pydcov ${COVERAGE_LIBS})
endif()

# Install targets
install(TARGETS pydcov DESTINATION bin)

# Testing support
enable_testing()

# Custom targets for coverage
if(ENABLE_COVERAGE)
    # Create coverage directory
    file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/coverage)
    
    if(CMAKE_C_COMPILER_ID MATCHES "GNU")
        # GCC/gcov coverage
        add_custom_target(coverage-clean
            COMMAND find ${CMAKE_BINARY_DIR} -name "*.gcda" -delete
            COMMAND find ${CMAKE_BINARY_DIR} -name "*.gcno" -delete
            COMMENT "Cleaning coverage data"
        )
        
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

        # Clang/llvm-cov coverage
        add_custom_target(coverage-clean
            COMMAND find ${CMAKE_BINARY_DIR} -name "*.profraw" -delete
            COMMAND find ${CMAKE_BINARY_DIR} -name "*.profdata" -delete
            COMMENT "Cleaning coverage data"
        )

        add_custom_target(coverage-merge
            COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_BINARY_DIR}/coverage
            COMMAND ${LLVM_PROFDATA_EXECUTABLE} merge -sparse ${CMAKE_BINARY_DIR}/*.profraw -o ${CMAKE_BINARY_DIR}/coverage/coverage.profdata
            COMMENT "Merging coverage data with ${LLVM_PROFDATA_EXECUTABLE}"
        )

        add_custom_target(coverage-report
            COMMAND ${LLVM_COV_EXECUTABLE} show ${CMAKE_BINARY_DIR}/pydcov -instr-profile=${CMAKE_BINARY_DIR}/coverage/coverage.profdata -format=html -output-dir=${CMAKE_BINARY_DIR}/coverage/html
            COMMAND ${LLVM_COV_EXECUTABLE} export ${CMAKE_BINARY_DIR}/pydcov -instr-profile=${CMAKE_BINARY_DIR}/coverage/coverage.profdata -format=lcov > ${CMAKE_BINARY_DIR}/coverage/coverage.info
            COMMENT "Generating coverage report with ${LLVM_COV_EXECUTABLE}"
            DEPENDS coverage-merge pydcov
        )
    endif()
endif()

# Print configuration summary
message(STATUS "Build configuration:")
message(STATUS "  C Compiler: ${CMAKE_C_COMPILER_ID} ${CMAKE_C_COMPILER_VERSION}")
message(STATUS "  CXX Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Coverage Enabled: ${ENABLE_COVERAGE}")
if(ENABLE_COVERAGE)
    message(STATUS "  Coverage Flags: ${COVERAGE_FLAGS}")
endif()
