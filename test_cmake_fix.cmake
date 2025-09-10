# Test script to verify the CMake target_link_libraries fix
# This script demonstrates that the fix resolves the keyword signature inconsistency

cmake_minimum_required(VERSION 3.10)
project(TestCMakeFix)

# Simulate the coverage system setup
set(COVERAGE_LIBS "gcov")

# Define the problematic function (before fix)
function(target_link_coverage_libraries_old target_name)
    if(COVERAGE_LIBS)
        # This would cause the error: plain signature
        target_link_libraries(${target_name} ${COVERAGE_LIBS})
    endif()
endfunction()

# Define the fixed function (after fix)
function(target_link_coverage_libraries_new target_name)
    if(COVERAGE_LIBS)
        # This is the fix: keyword signature
        target_link_libraries(${target_name} PRIVATE ${COVERAGE_LIBS})
    endif()
endfunction()

# Create a test executable
add_executable(test_target test.cpp)

# First, use the modern keyword signature (like our example modules do)
target_link_libraries(test_target PRIVATE some_library)

# Now try the old function - this would fail with:
# "The keyword signature for target_link_libraries has already been used"
# target_link_coverage_libraries_old(test_target)

# But the new function works fine:
target_link_coverage_libraries_new(test_target)

message(STATUS "CMake fix test completed successfully!")
