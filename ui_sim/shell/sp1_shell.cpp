#include "sp1_shell.h"

#include <cmath>
#include <cstring>

namespace {

constexpr int kMargin = 16;
constexpr int kLcdW = 320;
constexpr int kLcdH = 240;
constexpr int kZoom = 2;
constexpr int kPad = 56;
constexpr int kGap = 6;
constexpr int kFuncW = 72;
constexpr int kFuncH = 28;
constexpr int kKnob = 64;

/* 5x7 glyphs for 0-9 A-Z space. Bit0 = leftmost. */
const uint8_t k_font[37][7] = {
    {0, 0, 0, 0, 0, 0, 0},                                          // space
    {0x0e, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0e},                    // 0
    {0x04, 0x0c, 0x04, 0x04, 0x04, 0x04, 0x0e},                    // 1
    {0x0e, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1f},                    // 2
    {0x0e, 0x11, 0x01, 0x06, 0x01, 0x11, 0x0e},                    // 3
    {0x02, 0x06, 0x0a, 0x12, 0x1f, 0x02, 0x02},                    // 4
    {0x1f, 0x10, 0x1e, 0x01, 0x01, 0x11, 0x0e},                    // 5
    {0x06, 0x08, 0x10, 0x1e, 0x11, 0x11, 0x0e},                    // 6
    {0x1f, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08},                    // 7
    {0x0e, 0x11, 0x11, 0x0e, 0x11, 0x11, 0x0e},                    // 8
    {0x0e, 0x11, 0x11, 0x0f, 0x01, 0x02, 0x0c},                    // 9
    {0x0e, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11},                    // A
    {0x1e, 0x11, 0x11, 0x1e, 0x11, 0x11, 0x1e},                    // B
    {0x0e, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0e},                    // C
    {0x1c, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1c},                    // D
    {0x1f, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x1f},                    // E
    {0x1f, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x10},                    // F
    {0x0e, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0f},                    // G
    {0x11, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11},                    // H
    {0x0e, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0e},                    // I
    {0x01, 0x01, 0x01, 0x01, 0x11, 0x11, 0x0e},                    // J
    {0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11},                    // K
    {0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1f},                    // L
    {0x11, 0x1b, 0x15, 0x15, 0x11, 0x11, 0x11},                    // M
    {0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11},                    // N
    {0x0e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e},                    // O
    {0x1e, 0x11, 0x11, 0x1e, 0x10, 0x10, 0x10},                    // P
    {0x0e, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0d},                    // Q
    {0x1e, 0x11, 0x11, 0x1e, 0x14, 0x12, 0x11},                    // R
    {0x0e, 0x11, 0x10, 0x0e, 0x01, 0x11, 0x0e},                    // S
    {0x1f, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04},                    // T
    {0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e},                    // U
    {0x11, 0x11, 0x11, 0x11, 0x11, 0x0a, 0x04},                    // V
    {0x11, 0x11, 0x11, 0x15, 0x15, 0x1b, 0x11},                    // W
    {0x11, 0x11, 0x0a, 0x04, 0x0a, 0x11, 0x11},                    // X
    {0x11, 0x11, 0x0a, 0x04, 0x04, 0x04, 0x04},                    // Y
    {0x1f, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1f},                    // Z
};

int glyph_index(char c)
{
  if (c == ' ') {
    return 0;
  }
  if (c >= '0' && c <= '9') {
    return 1 + (c - '0');
  }
  if (c >= 'a' && c <= 'z') {
    c = static_cast<char>(c - 'a' + 'A');
  }
  if (c >= 'A' && c <= 'Z') {
    return 11 + (c - 'A');
  }
  return 0;
}

void fill_circle(SDL_Renderer* r, int cx, int cy, int rad)
{
  for (int y = -rad; y <= rad; ++y) {
    const int span = static_cast<int>(std::sqrt(static_cast<float>(rad * rad - y * y)));
    SDL_RenderDrawLine(r, cx - span, cy + y, cx + span, cy + y);
  }
}

void draw_text(SDL_Renderer* r, int x, int y, const char* text, int scale)
{
  if (text == nullptr) {
    return;
  }
  int cx = x;
  for (const char* p = text; *p != '\0'; ++p) {
    if (*p == '\n') {
      y += 8 * scale;
      cx = x;
      continue;
    }
    const uint8_t* g = k_font[glyph_index(*p)];
    for (int row = 0; row < 7; ++row) {
      for (int col = 0; col < 5; ++col) {
        if ((g[row] >> (4 - col)) & 1) {
          SDL_Rect px{cx + col * scale, y + row * scale, scale, scale};
          SDL_RenderFillRect(r, &px);
        }
      }
    }
    cx += 6 * scale;
  }
}

int text_width(const char* text, int scale)
{
  return static_cast<int>(std::strlen(text ? text : "")) * 6 * scale;
}

bool contains(const SDL_Rect& r, int x, int y)
{
  return x >= r.x && y >= r.y && x < r.x + r.w && y < r.y + r.h;
}

}  // namespace

void sp1_shell_layout(Sp1ShellLayout* layout)
{
  layout->lcd_zoom = kZoom;
  layout->lcd = {kMargin, kMargin, kLcdW * kZoom, kLcdH * kZoom};

  const int knobs_x = layout->lcd.x + layout->lcd.w + 28;
  layout->enc = {knobs_x, layout->lcd.y + 8, kKnob, kKnob};
  layout->pot[0] = {knobs_x, layout->enc.y + kKnob + 36, kKnob, kKnob};
  layout->pot[1] = {knobs_x + kKnob + 20, layout->pot[0].y, kKnob, kKnob};

  const int func_y = layout->lcd.y + layout->lcd.h + 16;
  for (int i = 0; i < 6; ++i) {
    layout->key[20 + i] = {kMargin + i * (kFuncW + kGap), func_y, kFuncW, kFuncH};
  }

  const int pad_y = func_y + kFuncH + 12;
  for (int i = 0; i < 16; ++i) {
    const int col = i % 4;
    const int row = i / 4;
    layout->key[i] = {kMargin + col * (kPad + kGap), pad_y + row * (kPad + kGap), kPad, kPad};
  }
  for (int i = 0; i < 4; ++i) {
    layout->key[16 + i] = {kMargin + 4 * (kPad + kGap) + 8, pad_y + i * (kPad + kGap), kPad + 8, kPad};
  }

  const int right = knobs_x + kKnob * 2 + 20;
  const int pads_right = layout->key[16].x + layout->key[16].w;
  layout->window_w = (right > pads_right ? right : pads_right) + kMargin;
  layout->window_h = layout->key[12].y + layout->key[12].h + 36;
}

void sp1_shell_draw(SDL_Renderer* renderer, const Sp1ShellLayout* layout, const char* status)
{
  SDL_SetRenderDrawColor(renderer, 18, 22, 30, 255);
  SDL_RenderClear(renderer);

  SDL_SetRenderDrawColor(renderer, 10, 14, 20, 255);
  SDL_Rect bezel = layout->lcd;
  bezel.x -= 4;
  bezel.y -= 4;
  bezel.w += 8;
  bezel.h += 8;
  SDL_RenderFillRect(renderer, &bezel);

  auto draw_knob = [&](const SDL_Rect& box, const char* name, float angle_turns, bool pressed) {
    const int cx = box.x + box.w / 2;
    const int cy = box.y + box.h / 2;
    const int rad = box.w / 2 - 2;
    SDL_SetRenderDrawColor(renderer, pressed ? 70 : 48, pressed ? 74 : 52, pressed ? 86 : 62, 255);
    fill_circle(renderer, cx, cy, rad);
    SDL_SetRenderDrawColor(renderer, 180, 190, 200, 255);
    const float a = (angle_turns - 0.25f) * 6.283185f;
    const int tx = cx + static_cast<int>(std::cos(a) * (rad - 8));
    const int ty = cy + static_cast<int>(std::sin(a) * (rad - 8));
    SDL_RenderDrawLine(renderer, cx, cy, tx, ty);
    SDL_SetRenderDrawColor(renderer, 160, 170, 180, 255);
    draw_text(renderer, box.x + (box.w - text_width(name, 1)) / 2, box.y + box.h + 6, name, 1);
  };

  float enc_turns = std::fmod(static_cast<float>(sp1_panel_enc_pos()), 24.f) / 24.f;
  if (enc_turns < 0.f) {
    enc_turns += 1.f;
  }
  draw_knob(layout->enc, "TEMPO", enc_turns, sp1_panel_pad_down(SP1_PANEL_ENC_SW));
  draw_knob(layout->pot[0], "RV1", sp1_panel_pot(0) * 0.75f - 0.375f, false);
  draw_knob(layout->pot[1], "RV2", sp1_panel_pot(1) * 0.75f - 0.375f, false);

  for (int i = 0; i < SP1_PANEL_KEYS; ++i) {
    if (i == SP1_PANEL_ENC_SW) {
      continue;
    }
    const SDL_Rect& box = layout->key[i];
    const bool down = sp1_panel_pad_down(static_cast<uint8_t>(i));
    SDL_SetRenderDrawColor(renderer, down ? 58 : 36, down ? 64 : 40, down ? 78 : 50, 255);
    SDL_RenderFillRect(renderer, &box);
    SDL_SetRenderDrawColor(renderer, 70, 78, 92, 255);
    SDL_RenderDrawRect(renderer, &box);

    if (sp1_panel_has_led(static_cast<uint8_t>(i))) {
      const uint8_t g = sp1_panel_led_green(static_cast<uint8_t>(i));
      const uint8_t red = sp1_panel_led_red(static_cast<uint8_t>(i));
      SDL_SetRenderDrawColor(renderer, red, g ? g : 18, 18, 255);
      fill_circle(renderer, box.x + 8, box.y + 8, 4);
    }

    const char* label = sp1_panel_label(static_cast<uint8_t>(i));
    const int scale = (i < 16 && std::strlen(label) <= 2) ? 2 : 1;
    const int tw = text_width(label, scale);
    SDL_SetRenderDrawColor(renderer, 230, 234, 240, 255);
    draw_text(renderer, box.x + (box.w - tw) / 2, box.y + (box.h - 7 * scale) / 2, label, scale);
  }

  SDL_SetRenderDrawColor(renderer, 140, 150, 160, 255);
  draw_text(renderer, kMargin, layout->window_h - 18, status ? status : "", 1);
}

int sp1_shell_hit_key(const Sp1ShellLayout* layout, int x, int y)
{
  for (int i = 0; i < SP1_PANEL_KEYS; ++i) {
    if (i == SP1_PANEL_ENC_SW) {
      continue;
    }
    if (contains(layout->key[i], x, y)) {
      return i;
    }
  }
  return -1;
}

bool sp1_shell_hit_enc(const Sp1ShellLayout* layout, int x, int y)
{
  return contains(layout->enc, x, y);
}

int sp1_shell_hit_pot(const Sp1ShellLayout* layout, int x, int y)
{
  for (int i = 0; i < SP1_PANEL_POT_COUNT; ++i) {
    if (contains(layout->pot[i], x, y)) {
      return i;
    }
  }
  return -1;
}

int sp1_shell_key_for_sdl(SDL_Keycode key)
{
  switch (key) {
    case SDLK_1:
      return 0;
    case SDLK_2:
      return 1;
    case SDLK_3:
      return 2;
    case SDLK_4:
      return 3;
    case SDLK_q:
      return 4;
    case SDLK_w:
      return 5;
    case SDLK_e:
      return 6;
    case SDLK_r:
      return 7;
    case SDLK_a:
      return 8;
    case SDLK_s:
      return 9;
    case SDLK_d:
      return 10;
    case SDLK_f:
      return 11;
    case SDLK_z:
      return 12;
    case SDLK_x:
      return 13;
    case SDLK_c:
      return 14;
    case SDLK_v:
      return 15;
    case SDLK_5:
      return 16;
    case SDLK_t:
      return 17;
    case SDLK_g:
      return 18;
    case SDLK_b:
      return 19;
    case SDLK_y:
      return 20;
    case SDLK_u:
      return 21;
    case SDLK_i:
      return 22;
    case SDLK_o:
      return 23;
    case SDLK_p:
      return 24;
    case SDLK_LSHIFT:
    case SDLK_RSHIFT:
      return 25;
    case SDLK_RETURN:
      return SP1_PANEL_ENC_SW;
    default:
      return -1;
  }
}
