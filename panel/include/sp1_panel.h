#pragma once

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Electrical matrix — same as pad_matrix.h. */
#define SP1_PANEL_ROWS 5
#define SP1_PANEL_COLS 6
#define SP1_PANEL_KEYS 27
#define SP1_PANEL_ENC_SW 26
#define SP1_PANEL_PAD_UI 16
#define SP1_PANEL_POT_COUNT 2
#define SP1_PANEL_POT_RV1 0
#define SP1_PANEL_POT_RV2 1

typedef struct Sp1PanelCallbacks
{
  void (*on_pad)(uint8_t index, bool pressed, void* user);
  void (*on_enc)(int8_t delta, void* user);
  void (*on_pot)(uint8_t index, float value, void* user);
  void* user;
} Sp1PanelCallbacks;

void sp1_panel_init(const Sp1PanelCallbacks* callbacks);

int sp1_panel_cell_to_index(uint8_t row, uint8_t col);
const char* sp1_panel_label(uint8_t index);
const char* sp1_panel_sw_name(uint8_t index);
bool sp1_panel_has_led(uint8_t index);

void sp1_panel_set_pad(uint8_t index, bool pressed);
bool sp1_panel_pad_down(uint8_t index);

void sp1_panel_add_enc(int8_t delta);
int sp1_panel_enc_pos(void);

void sp1_panel_set_pot(uint8_t index, float value);
float sp1_panel_pot(uint8_t index);

/** 0–255 PWM, matching C6 IS31 path (G / R). */
void sp1_panel_set_led(uint8_t index, uint8_t green, uint8_t red);
uint8_t sp1_panel_led_green(uint8_t index);
uint8_t sp1_panel_led_red(uint8_t index);

#ifdef __cplusplus
}
#endif
