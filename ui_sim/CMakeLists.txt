cmake_minimum_required(VERSION 3.20)
project(sp1_ui_sim LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SP1_UI_SIM_ROOT "${CMAKE_CURRENT_SOURCE_DIR}")
set(SP1_REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/..")

set(ATOMTHEME_ROOT "$ENV{HOME}/source/AtomTheme" CACHE PATH "AtomTheme checkout")
if(NOT EXISTS "${ATOMTHEME_ROOT}/CMakeLists.txt")
    set(ATOMTHEME_ROOT "${SP1_REPO_ROOT}/../AtomTheme")
endif()
if(NOT EXISTS "${ATOMTHEME_ROOT}/CMakeLists.txt")
    message(FATAL_ERROR "AtomTheme not found. Set ATOMTHEME_ROOT.")
endif()

set(LVGL_PATH "$ENV{HOME}/source/lvgl" CACHE PATH "LVGL checkout")
if(NOT EXISTS "${LVGL_PATH}/CMakeLists.txt")
    message(FATAL_ERROR "LVGL not found. Set LVGL_PATH.")
endif()

find_package(SDL2 QUIET)
if(NOT SDL2_FOUND)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(SDL2 REQUIRED sdl2)
endif()

if(TARGET SDL2::SDL2)
    set(SP1_SDL2 SDL2::SDL2)
elseif(TARGET SDL2::SDL2-static)
    set(SP1_SDL2 SDL2::SDL2-static)
endif()

set(LV_BUILD_CONF_PATH "${SP1_UI_SIM_ROOT}/lv_conf.h" CACHE FILEPATH "" FORCE)
set(CONFIG_LV_BUILD_DEMOS OFF CACHE BOOL "" FORCE)
set(CONFIG_LV_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(CONFIG_LV_USE_THORVG_INTERNAL OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
add_subdirectory("${LVGL_PATH}" "${CMAKE_BINARY_DIR}/lvgl" EXCLUDE_FROM_ALL)

add_subdirectory("${SP1_REPO_ROOT}/panel" "${CMAKE_BINARY_DIR}/sp1_panel")

add_library(atom_theme_core INTERFACE)
target_include_directories(atom_theme_core INTERFACE "${ATOMTHEME_ROOT}")
target_compile_features(atom_theme_core INTERFACE cxx_std_17)

add_library(atom_theme_core_impl STATIC
    "${ATOMTHEME_ROOT}/core/ThemeColors.cpp"
    "${ATOMTHEME_ROOT}/core/StyleData.cpp"
)
target_link_libraries(atom_theme_core_impl PUBLIC atom_theme_core)
target_compile_features(atom_theme_core_impl PUBLIC cxx_std_17)

# PadGrid only — do not pull JUCE or the rest of AtomTheme CMake.
add_library(atom_theme_lvgl STATIC
    "${ATOMTHEME_ROOT}/backends/lvgl/widgets/LvglPadGrid.cpp"
)
target_link_libraries(atom_theme_lvgl PUBLIC
    atom_theme_core
    atom_theme_core_impl
    lvgl
)
target_compile_features(atom_theme_lvgl PUBLIC cxx_std_17)
target_include_directories(atom_theme_lvgl PUBLIC
    "${ATOMTHEME_ROOT}"
    "${ATOMTHEME_ROOT}/backends"
)

add_subdirectory("${SP1_REPO_ROOT}/ui" "${CMAKE_BINARY_DIR}/sp1_ui")

add_executable(sp1_ui_sim
    main.cpp
    shell/sp1_shell.cpp
)
target_include_directories(sp1_ui_sim PRIVATE
    ${SP1_UI_SIM_ROOT}/shell
)
target_link_libraries(sp1_ui_sim PRIVATE sp1_ui sp1_panel)
target_compile_definitions(sp1_ui_sim PRIVATE SDL_MAIN_HANDLED)

if(SP1_SDL2)
    target_link_libraries(sp1_ui_sim PRIVATE ${SP1_SDL2})
elseif(SDL2_LIBRARIES)
    target_link_libraries(sp1_ui_sim PRIVATE ${SDL2_LIBRARIES})
    target_include_directories(sp1_ui_sim PRIVATE ${SDL2_INCLUDE_DIRS})
endif()

if(NOT MSVC)
    target_compile_options(sp1_ui_sim PRIVATE -Wall -Wextra)
endif()
