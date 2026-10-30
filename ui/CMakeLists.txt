# SP-1 product screens. Expects targets: lvgl (or lvgl::lvgl) and atom_theme_lvgl.
cmake_minimum_required(VERSION 3.20)

add_library(sp1_ui STATIC
    src/home_screen.cpp
)

target_include_directories(sp1_ui PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(sp1_ui PUBLIC cxx_std_17)

if(TARGET lvgl::lvgl)
    set(SP1_UI_LVGL lvgl::lvgl)
else()
    set(SP1_UI_LVGL lvgl)
endif()

target_link_libraries(sp1_ui PUBLIC
    atom_theme_lvgl
    ${SP1_UI_LVGL}
)
