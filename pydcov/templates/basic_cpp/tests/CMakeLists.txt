# Test executable
add_executable(test_{{PROJECT_NAME}}
    test_calculator.cpp
)

target_link_libraries(test_{{PROJECT_NAME}}
    {{PROJECT_NAME}}_lib
)

target_include_directories(test_{{PROJECT_NAME}} PRIVATE
    ${CMAKE_SOURCE_DIR}/src
)

# Add test to CTest
add_test(NAME {{PROJECT_NAME}}_tests COMMAND test_{{PROJECT_NAME}})
