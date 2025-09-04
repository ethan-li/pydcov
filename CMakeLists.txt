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
    elseif(CMAKE_C_COMPILER_ID MATCHES "Clang")
        set(COVERAGE_FLAGS "-fprofile-instr-generate -fcoverage-mapping")
        set(COVERAGE_LIBS "")
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
            COMMAND gcov -r ${CMAKE_SOURCE_DIR}/src/*.c
            COMMAND lcov --capture --directory ${CMAKE_BINARY_DIR} --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info
            COMMAND lcov --remove ${CMAKE_BINARY_DIR}/coverage/coverage.info '/usr/*' --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info
            COMMAND lcov --remove ${CMAKE_BINARY_DIR}/coverage/coverage.info '*/test/*' --output-file ${CMAKE_BINARY_DIR}/coverage/coverage.info
            COMMAND genhtml ${CMAKE_BINARY_DIR}/coverage/coverage.info --output-directory ${CMAKE_BINARY_DIR}/coverage/html
            COMMENT "Generating coverage report"
            DEPENDS pydcov
        )
    elseif(CMAKE_C_COMPILER_ID MATCHES "Clang")
        # Clang/llvm-cov coverage
        add_custom_target(coverage-clean
            COMMAND find ${CMAKE_BINARY_DIR} -name "*.profraw" -delete
            COMMAND find ${CMAKE_BINARY_DIR} -name "*.profdata" -delete
            COMMENT "Cleaning coverage data"
        )
        
        add_custom_target(coverage-merge
            COMMAND llvm-profdata merge -sparse ${CMAKE_BINARY_DIR}/*.profraw -o ${CMAKE_BINARY_DIR}/coverage/coverage.profdata
            COMMENT "Merging coverage data"
        )
        
        add_custom_target(coverage-report
            COMMAND llvm-cov show ${CMAKE_BINARY_DIR}/pydcov -instr-profile=${CMAKE_BINARY_DIR}/coverage/coverage.profdata -format=html -output-dir=${CMAKE_BINARY_DIR}/coverage/html
            COMMAND llvm-cov export ${CMAKE_BINARY_DIR}/pydcov -instr-profile=${CMAKE_BINARY_DIR}/coverage/coverage.profdata -format=lcov > ${CMAKE_BINARY_DIR}/coverage/coverage.info
            COMMENT "Generating coverage report"
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
