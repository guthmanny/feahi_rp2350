/**
 * @file pad_matrix.h
 * @brief 5×6 Choc matrix on RP2350 GPIO (SP-1 scheme A).
 */
#ifndef FEAHI_PAD_MATRIX_H
#define FEAHI_PAD_MATRIX_H

#include <stdint.h>
#include <stdbool.h>

#define PAD_MATRIX_ROWS 5
#define PAD_MATRIX_COLS 6
#define PAD_MATRIX_KEYS 26

/** Logical pad index 0..25 = row-major (row*6+col), empty cells skipped in map. */
typedef void (*pad_matrix_event_fn)(uint8_t pad_index, bool pressed);

/**
 * Initialize GPIO and start scanner on core 1 (when PICO_SDK is linked).
 * Without SDK, registers a no-op stub for host builds.
 */
void pad_matrix_init(pad_matrix_event_fn on_event);

/** Call periodically from main if not using second core (bare-metal fallback). */
void pad_matrix_poll(void);

/** Map (row,col) to pad_index, or -1 if no key in cell. */
int pad_matrix_cell_to_index(uint8_t row, uint8_t col);

#endif
