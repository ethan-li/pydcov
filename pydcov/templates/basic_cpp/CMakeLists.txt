cmake_minimum_required(VERSION 3.10)
project({{PROJECT_NAME}})

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include PyDCov coverage support
include(cmake/coverage.cmake)

# Add source directory
add_subdirectory(src)

# Add executable
add_executable(${PROJECT_NAME} app/main.cpp)
target_link_libraries(${PROJECT_NAME} ${PROJECT_NAME}_lib)

# Enable testing
enable_testing()
add_subdirectory(tests)

# Coverage targets are automatically created by coverage.cmake
# Use: make coverage-clean, make coverage-report
