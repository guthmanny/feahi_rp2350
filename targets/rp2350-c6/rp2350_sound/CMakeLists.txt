cmake_minimum_required(VERSION 3.13)

if(NOT PICO_SDK_PATH)
    message(STATUS "PICO_SDK_PATH not set — pad_matrix builds as stub only")
    project(feahi_rp2350_sound_stub C)
    add_executable(feahi_rp2350_sound
        src/main.c
        src/pad_matrix.c
    )
    target_include_directories(feahi_rp2350_sound PRIVATE src)
    return()
endif()

include(pico_sdk_import.cmake)
project(feahi_rp2350_sound C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

add_executable(feahi_rp2350_sound
    src/main.c
    src/pad_matrix.c
)
target_include_directories(feahi_rp2350_sound PRIVATE src)
target_link_libraries(feahi_rp2350_sound pico_stdlib hardware_gpio pico_multicore)
pico_add_extra_outputs(feahi_rp2350_sound)
