# Example project demonstrating generic coverage system
cmake_minimum_required(VERSION 3.15)
project(ExampleProject VERSION 1.0.0 LANGUAGES C CXX)

# Include the generic coverage system
include(../cmake/coverage.cmake)

# Create some example executables with different naming and structure
add_executable(calculator src/calc.cpp)
add_executable(file_processor tools/processor.cpp)
add_executable(data_analyzer analyzers/main.cpp)

# These would be automatically excluded by the coverage system
add_executable(unit_tests tests/unit_test.cpp)
add_executable(integration_testing tests/integration.cpp)

# Example of manual registration (optional)
# coverage_add_executable(calculator)
# coverage_add_executable(file_processor)

# The coverage system will automatically:
# 1. Detect calculator, file_processor, data_analyzer
# 2. Exclude unit_tests, integration_testing
# 3. Generate coverage reports for the detected executables
