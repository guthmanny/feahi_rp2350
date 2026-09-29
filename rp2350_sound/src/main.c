/**
 * @file main.c
 * @brief feahi_rp2350 — RP2350 audio + Pad matrix (scheme A).
 */
#include "pad_matrix.h"

#include <stdio.h>

#ifdef PICO_SDK_VERSION_MAJOR
#include "pico/stdlib.h"
#endif

static void on_pad_event(uint8_t pad_index, bool pressed)
{
    (void)pad_index;
    (void)pressed;
    /* TODO: voice_trigger(pad_index, velocity); optional IPC UI notify (non-realtime) */
}

int main(void)
{
#ifdef PICO_SDK_VERSION_MAJOR
    stdio_init_all();
#endif
    pad_matrix_init(on_pad_event);

    for (;;) {
        pad_matrix_poll();
#ifdef PICO_SDK_VERSION_MAJOR
        tight_loop_contents();
#endif
    }
    return 0;
}
