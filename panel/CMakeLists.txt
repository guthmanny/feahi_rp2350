cmake_minimum_required(VERSION 3.20)

add_library(sp1_panel STATIC
    src/sp1_panel.c
)

target_include_directories(sp1_panel PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(sp1_panel PUBLIC c_std_11)
