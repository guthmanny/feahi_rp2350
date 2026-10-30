#include "sp1_panel.h"

#include <string.h>

/* (row,col) → pad_index; -1 empty. (4,2)=ENC_SW. Same as pad_matrix.c */
static const int8_t k_cell[SP1_PANEL_ROWS][SP1_PANEL_COLS] = {
    {0, 1, 2, 3, 4, 5},
    {6, 7, 8, 9, 10, 11},
    {12, 13, 14, 15, 16, 17},
    {18, 19, 20, 21, 22, 23},
    {24, 25, SP1_PANEL_ENC_SW, -1, -1, -1},
};

/* Keycap labels from hardware/schematic/sp1_key_matrix.csv */
static const char* const k_label[SP1_PANEL_KEYS] = {
    "1",       "2",      "3",     "4",   "5",      "6",
    "7",       "8",      "9",     "10",  "11",     "12",
    "A",       "B",      "C",     "D",   "REC",    "PLAY",
    "PATTERN", "SAMPLE", "SAMPLES", "FX", "SEQ", "LIBRARY",
    "SYSTEM",  "SHIFT",  "ENC",
};

static const char* const k_sw[SP1_PANEL_KEYS] = {
    "SW1",  "SW2",  "SW3",  "SW4",  "SW5",  "SW6",
    "SW7",  "SW8",  "SW9",  "SW10", "SW11", "SW12",
    "SW13", "SW14", "SW15", "SW16", "SW17", "SW18",
    "SW19", "SW20", "SW21", "SW22", "SW23", "SW24",
    "SW25", "SW26", "ENC_SW",
};

/* SW1–20 key LEDs + SW26 SHIFT (D30). ENC_SW / SW21–25 have none. */
static const uint8_t k_has_led[SP1_PANEL_KEYS] = {
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0,
};

static Sp1PanelCallbacks s_cb;
static uint8_t s_down[SP1_PANEL_KEYS];
static uint8_t s_led_g[SP1_PANEL_KEYS];
static uint8_t s_led_r[SP1_PANEL_KEYS];
static int s_enc_pos;
static float s_pot[SP1_PANEL_POT_COUNT] = {0.5f, 0.5f};

void sp1_panel_init(const Sp1PanelCallbacks* callbacks)
{
  if (callbacks != NULL) {
    s_cb = *callbacks;
  } else {
    memset(&s_cb, 0, sizeof s_cb);
  }
  memset(s_down, 0, sizeof s_down);
  memset(s_led_g, 0, sizeof s_led_g);
  memset(s_led_r, 0, sizeof s_led_r);
  s_enc_pos = 0;
  s_pot[0] = 0.5f;
  s_pot[1] = 0.5f;
}

int sp1_panel_cell_to_index(uint8_t row, uint8_t col)
{
  if (row >= SP1_PANEL_ROWS || col >= SP1_PANEL_COLS) {
    return -1;
  }
  return k_cell[row][col];
}

const char* sp1_panel_label(uint8_t index)
{
  if (index >= SP1_PANEL_KEYS) {
    return "?";
  }
  return k_label[index];
}

const char* sp1_panel_sw_name(uint8_t index)
{
  if (index >= SP1_PANEL_KEYS) {
    return "?";
  }
  return k_sw[index];
}

bool sp1_panel_has_led(uint8_t index)
{
  if (index >= SP1_PANEL_KEYS) {
    return false;
  }
  return k_has_led[index] != 0;
}

void sp1_panel_set_pad(uint8_t index, bool pressed)
{
  if (index >= SP1_PANEL_KEYS) {
    return;
  }
  uint8_t down = pressed ? 1u : 0u;
  if (s_down[index] == down) {
    return;
  }
  s_down[index] = down;
  if (s_cb.on_pad != NULL) {
    s_cb.on_pad(index, pressed, s_cb.user);
  }
}

bool sp1_panel_pad_down(uint8_t index)
{
  if (index >= SP1_PANEL_KEYS) {
    return false;
  }
  return s_down[index] != 0;
}

void sp1_panel_add_enc(int8_t delta)
{
  if (delta == 0) {
    return;
  }
  s_enc_pos += delta;
  if (s_cb.on_enc != NULL) {
    s_cb.on_enc(delta, s_cb.user);
  }
}

int sp1_panel_enc_pos(void)
{
  return s_enc_pos;
}

void sp1_panel_set_pot(uint8_t index, float value)
{
  if (index >= SP1_PANEL_POT_COUNT) {
    return;
  }
  if (value < 0.f) {
    value = 0.f;
  }
  if (value > 1.f) {
    value = 1.f;
  }
  if (s_pot[index] == value) {
    return;
  }
  s_pot[index] = value;
  if (s_cb.on_pot != NULL) {
    s_cb.on_pot(index, value, s_cb.user);
  }
}

float sp1_panel_pot(uint8_t index)
{
  if (index >= SP1_PANEL_POT_COUNT) {
    return 0.f;
  }
  return s_pot[index];
}

void sp1_panel_set_led(uint8_t index, uint8_t green, uint8_t red)
{
  if (index >= SP1_PANEL_KEYS || !sp1_panel_has_led(index)) {
    return;
  }
  s_led_g[index] = green;
  s_led_r[index] = red;
}

uint8_t sp1_panel_led_green(uint8_t index)
{
  if (index >= SP1_PANEL_KEYS) {
    return 0;
  }
  return s_led_g[index];
}

uint8_t sp1_panel_led_red(uint8_t index)
{
  if (index >= SP1_PANEL_KEYS) {
    return 0;
  }
  return s_led_r[index];
}
