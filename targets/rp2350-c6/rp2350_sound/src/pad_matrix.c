/**
 * @file pad_matrix.c
 * @brief Column-strobe matrix scan for MAT_C* / MAT_R* nets (see sp1_rp2350_pad_matrix.md).
 */
#include "pad_matrix.h"

#include <string.h>

#ifdef PICO_SDK_VERSION_MAJOR
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "pico/multicore.h"
#endif

/* GPIO pin numbers — must match hardware/schematic/sp1_rp2350_pad_matrix.md */
static const uint8_t col_gpio[PAD_MATRIX_COLS] = {6, 7, 19, 21, 23, 24};
static const uint8_t row_gpio[PAD_MATRIX_ROWS] = {10, 11, 12, 13, 14};

/** pad_index for each (row,col); -1 = empty (row4 col2..5). */
static const int8_t cell_to_pad[PAD_MATRIX_ROWS][PAD_MATRIX_COLS] = {
    {0, 1, 2, 3, 4, 5},
    {6, 7, 8, 9, 10, 11},
    {12, 13, 14, 15, 16, 17},
    {18, 19, 20, 21, 22, 23},
    {24, 25, -1, -1, -1, -1},
};

#define SCAN_HZ 5000u
#define DEBOUNCE_SCANS 3u

static pad_matrix_event_fn s_on_event;
static uint8_t s_stable[PAD_MATRIX_KEYS];
static uint8_t s_debounce[PAD_MATRIX_KEYS];

int pad_matrix_cell_to_index(uint8_t row, uint8_t col)
{
    if (row >= PAD_MATRIX_ROWS || col >= PAD_MATRIX_COLS) {
        return -1;
    }
    return cell_to_pad[row][col];
}

#ifdef PICO_SDK_VERSION_MAJOR

static void matrix_gpio_init(void)
{
    for (unsigned c = 0; c < PAD_MATRIX_COLS; c++) {
        gpio_init(col_gpio[c]);
        gpio_set_dir(col_gpio[c], GPIO_OUT);
        gpio_put(col_gpio[c], 1);
    }
    for (unsigned r = 0; r < PAD_MATRIX_ROWS; r++) {
        gpio_init(row_gpio[r]);
        gpio_set_dir(row_gpio[r], GPIO_IN);
        gpio_pull_up(row_gpio[r]);
    }
}

static bool read_key_raw(uint8_t row, uint8_t col)
{
    for (unsigned c = 0; c < PAD_MATRIX_COLS; c++) {
        gpio_put(col_gpio[c], c == col ? 0 : 1);
    }
    /* settle — ~few µs; tight loop for determinism */
    volatile uint32_t n = 32;
    while (n--) {
        tight_loop_contents();
    }
    return !gpio_get(row_gpio[row]);
}

static void process_scan(void)
{
    for (uint8_t row = 0; row < PAD_MATRIX_ROWS; row++) {
        for (uint8_t col = 0; col < PAD_MATRIX_COLS; col++) {
            int pad = pad_matrix_cell_to_index(row, col);
            if (pad < 0) {
                continue;
            }
            bool down = read_key_raw(row, col);
            uint8_t u = (uint8_t)pad;
            if (down) {
                if (s_debounce[u] < 255) {
                    s_debounce[u]++;
                }
            } else if (s_debounce[u] > 0) {
                s_debounce[u]--;
            }
            bool stable_down = s_debounce[u] >= DEBOUNCE_SCANS;
            if (stable_down != s_stable[u]) {
                s_stable[u] = stable_down;
                if (s_on_event) {
                    s_on_event(u, stable_down);
                }
            }
        }
    }
    for (unsigned c = 0; c < PAD_MATRIX_COLS; c++) {
        gpio_put(col_gpio[c], 1);
    }
}

static void scan_core1(void)
{
    matrix_gpio_init();
    absolute_time_t next = get_absolute_time();
    const uint64_t period_us = 1000000u / SCAN_HZ;
    for (;;) {
        process_scan();
        next = delayed_by_us(next, period_us);
        sleep_until(next);
    }
}

void pad_matrix_init(pad_matrix_event_fn on_event)
{
    s_on_event = on_event;
    memset(s_stable, 0, sizeof s_stable);
    memset(s_debounce, 0, sizeof s_debounce);
    multicore_launch_core1(scan_core1);
}

void pad_matrix_poll(void)
{
    /* scanning runs on core1 */
}

#else /* !PICO_SDK */

void pad_matrix_init(pad_matrix_event_fn on_event)
{
    s_on_event = on_event;
}

void pad_matrix_poll(void)
{
}

#endif
