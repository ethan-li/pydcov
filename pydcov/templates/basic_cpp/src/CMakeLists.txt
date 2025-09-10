# Library source files
add_library({{PROJECT_NAME}}_lib
    calculator.cpp
)

target_include_directories({{PROJECT_NAME}}_lib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
