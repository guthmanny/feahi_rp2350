#include "sp1_ui.h"

#include <cstdio>
#include <memory>
#include <string>

#include "core/PadCellState.h"
#include "core/StyleData.h"
#include "core/ThemeColors.h"
#include "lvgl/widgets/LvglPadGrid.h"

namespace {

constexpr int kGap = 6;
constexpr int kCell = 40;
constexpr int kGridPx = kCell * 4 + kGap * 3;

constexpr const char* kMidiName[SP1_UI_PAD_COUNT] = {
    "C1", "C#1", "D1",  "D#1", "E1", "F1", "F#1", "G1",
    "G#1", "A1", "A#1", "B1",  "C2", "C#2", "D2", "D#2",
};

struct Home {
  std::unique_ptr<atom::lvgl_widgets::PadGrid> grid;
  lv_obj_t* ble = nullptr;
  lv_obj_t* wifi = nullptr;
  lv_obj_t* hit = nullptr;
};

Home g_home;

lv_obj_t* make_label(lv_obj_t* parent, const char* text, uint32_t colour, int x, int y)
{
  lv_obj_t* label = lv_label_create(parent);
  lv_label_set_text(label, text);
  lv_obj_set_style_text_color(label, lv_color_hex(colour), 0);
  lv_obj_set_pos(label, x, y);
  return label;
}

void fill_cells(atom::lvgl_widgets::PadGrid& grid)
{
  for (int i = 0; i < SP1_UI_PAD_COUNT; ++i) {
    atom::core::PadCellState cell;
    cell.hasSample = true;
    cell.label = std::to_string(i + 1);
    cell.subtitle = kMidiName[i];
    cell.customColour = atom::core::defaultPadColour(i);
    cell.selected = (i == 0);
    grid.setCellState(i, cell);
  }
}

}  // namespace

void sp1_ui_create(lv_obj_t* parent)
{
  lv_obj_set_style_bg_color(parent, lv_color_hex(0x102038), 0);
  lv_obj_set_style_bg_opa(parent, LV_OPA_COVER, 0);
  lv_obj_set_style_pad_all(parent, 0, 0);
  lv_obj_set_style_border_width(parent, 0, 0);
  lv_obj_set_scrollbar_mode(parent, LV_SCROLLBAR_MODE_OFF);

  lv_obj_t* bar = lv_obj_create(parent);
  lv_obj_set_size(bar, SP1_UI_HOR_RES, 26);
  lv_obj_set_pos(bar, 0, 0);
  lv_obj_set_style_bg_color(bar, lv_color_hex(0x182848), 0);
  lv_obj_set_style_bg_opa(bar, LV_OPA_COVER, 0);
  lv_obj_set_style_radius(bar, 0, 0);
  lv_obj_set_style_border_width(bar, 0, 0);
  lv_obj_set_style_pad_all(bar, 0, 0);
  lv_obj_set_scrollbar_mode(bar, LV_SCROLLBAR_MODE_OFF);
  make_label(bar, "SP-1", 0x00DDFF, 8, 4);
  make_label(bar, "SAMPLER", 0x8899AA, 80, 6);
  make_label(bar, "PADS 36-51", 0x8899AA, 176, 6);

  g_home.ble = make_label(parent, "BLE  --", 0xFFFFFF, 12, 30);
  g_home.wifi = make_label(parent, "WIFI --", 0xFFFFFF, 12, 46);
  g_home.hit = make_label(parent, "PAD  --", 0x00DDFF, 176, 30);

  auto theme = atom::core::makeDarkTheme();
  auto style = atom::core::PadGridStyle::fromTheme(theme);
  style.typography.titleSizePx = 14.0f;
  style.typography.subtitleSizePx = 12.0f;
  style.metrics.cornerRadius = 4.0f;
  style.metrics.labelPadding = 2.0f;

  g_home.grid = std::make_unique<atom::lvgl_widgets::PadGrid>(parent);
  g_home.grid->setAtomStyle(style);
  g_home.grid->setGridLayout({4, 4, kGap});
  g_home.grid->setPadCount(SP1_UI_PAD_COUNT);
  fill_cells(*g_home.grid);

  lv_obj_t* grid_obj = g_home.grid->getLvglObject();
  lv_obj_set_size(grid_obj, kGridPx, kGridPx);
  lv_obj_set_pos(grid_obj, (SP1_UI_HOR_RES - kGridPx) / 2, 62);

  g_home.grid->setOnPadTriggered([](int index, float) { sp1_ui_set_pad(index, true); });
  g_home.grid->setOnPadSelected([](int index) { sp1_ui_set_selected(index); });
}

void sp1_ui_set_selected(int index)
{
  if (g_home.grid == nullptr) {
    return;
  }
  g_home.grid->setSelectedIndex(index);
}

void sp1_ui_set_pad(int index, bool pressed)
{
  if (g_home.grid == nullptr || index < 0 || index >= SP1_UI_PAD_COUNT) {
    return;
  }

  if (g_home.hit != nullptr) {
    char hit[48];
    std::snprintf(hit, sizeof hit, "Pad %d  ·  %s %d", index + 1, kMidiName[index],
                  SP1_UI_PAD_MIDI0 + index);
    lv_label_set_text(g_home.hit, hit);
  }

  if (pressed) {
    g_home.grid->setSelectedIndex(index);
    g_home.grid->setTriggerLevel(index, 1.f);
  } else {
    g_home.grid->setTriggerLevel(index, 0.f);
  }
}

void sp1_ui_set_radio(const char* ble, const char* wifi)
{
  if (g_home.ble != nullptr && ble != nullptr) {
    lv_label_set_text(g_home.ble, ble);
  }
  if (g_home.wifi != nullptr && wifi != nullptr) {
    lv_label_set_text(g_home.wifi, wifi);
  }
}

void sp1_ui_set_hit(const char* text)
{
  if (g_home.hit != nullptr && text != nullptr) {
    lv_label_set_text(g_home.hit, text);
  }
}
