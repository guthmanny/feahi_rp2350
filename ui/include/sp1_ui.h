#pragma once

#include <lvgl.h>

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** SP-1 panel geometry (landscape ST7789). Shared by ui_sim and C6. */
#define SP1_UI_HOR_RES 320
#define SP1_UI_VER_RES 240

#define SP1_UI_PAD_COUNT 16
#define SP1_UI_PAD_MIDI0 36

void sp1_ui_create(lv_obj_t* parent);
void sp1_ui_set_pad(int index, bool pressed);
void sp1_ui_set_selected(int index);
void sp1_ui_set_radio(const char* ble, const char* wifi);
void sp1_ui_set_hit(const char* text);

#ifdef __cplusplus
}
#endif
