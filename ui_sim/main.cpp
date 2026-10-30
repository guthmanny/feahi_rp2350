#include <lvgl.h>

#include <SDL2/SDL.h>

#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "sp1_panel.h"
#include "sp1_shell.h"
#include "sp1_ui.h"

namespace {

Sp1ShellLayout g_layout;
SDL_Window* g_window = nullptr;
SDL_Renderer* g_renderer = nullptr;
SDL_Texture* g_lcd = nullptr;
uint16_t g_fb[SP1_UI_HOR_RES * SP1_UI_VER_RES];
char g_status[96] = "chassis: keys / TEMPO / RV1 RV2";

int g_ptr_x = 0;
int g_ptr_y = 0;
bool g_ptr_down = false;
bool g_ptr_in_lcd = false;

int g_held_key = -1;
int g_drag_pot = -1;
bool g_enc_grab = false;
int g_last_mx = 0;
int g_last_my = 0;

uint32_t tick_cb()
{
  return SDL_GetTicks();
}

void lcd_flush(lv_display_t* display, const lv_area_t* area, uint8_t* px_map)
{
  (void)area;
  (void)px_map;
  if (g_lcd != nullptr) {
    SDL_UpdateTexture(g_lcd, nullptr, g_fb, SP1_UI_HOR_RES * static_cast<int>(sizeof(uint16_t)));
  }
  lv_display_flush_ready(display);
}

void pointer_read(lv_indev_t* indev, lv_indev_data_t* data)
{
  (void)indev;
  data->point.x = static_cast<int32_t>(g_ptr_x);
  data->point.y = static_cast<int32_t>(g_ptr_y);
  data->state = (g_ptr_in_lcd && g_ptr_down) ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

void set_status(const char* text)
{
  std::snprintf(g_status, sizeof g_status, "%s", text);
}

void apply_led(uint8_t index, bool on)
{
  if (!sp1_panel_has_led(index)) {
    return;
  }
  sp1_panel_set_led(index, on ? 0x80u : 0u, 0u);
}

void on_pad(uint8_t index, bool pressed, void* user)
{
  (void)user;
  apply_led(index, pressed);
  if (index < SP1_UI_PAD_COUNT) {
    sp1_ui_set_pad(static_cast<int>(index), pressed);
  }
  char line[80];
  std::snprintf(line, sizeof line, "%s %s %s", sp1_panel_sw_name(index), sp1_panel_label(index),
                pressed ? "down" : "up");
  set_status(line);
  sp1_ui_set_hit(line);
}

void on_enc(int8_t delta, void* user)
{
  (void)user;
  char line[64];
  std::snprintf(line, sizeof line, "ENC %+d  pos=%d", static_cast<int>(delta), sp1_panel_enc_pos());
  set_status(line);
  sp1_ui_set_hit(line);
}

void on_pot(uint8_t index, float value, void* user)
{
  (void)user;
  char line[64];
  std::snprintf(line, sizeof line, "%s %.2f", index == 0 ? "RV1" : "RV2", static_cast<double>(value));
  set_status(line);
}

bool map_to_lcd(int x, int y, int* lx, int* ly)
{
  const SDL_Rect& lcd = g_layout.lcd;
  if (x < lcd.x || y < lcd.y || x >= lcd.x + lcd.w || y >= lcd.y + lcd.h) {
    return false;
  }
  *lx = (x - lcd.x) / g_layout.lcd_zoom;
  *ly = (y - lcd.y) / g_layout.lcd_zoom;
  return true;
}

void release_held_key()
{
  if (g_held_key >= 0) {
    sp1_panel_set_pad(static_cast<uint8_t>(g_held_key), false);
    g_held_key = -1;
  }
}

}  // namespace

int main()
{
  if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) != 0) {
    std::fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
    return EXIT_FAILURE;
  }

  sp1_shell_layout(&g_layout);

  g_window = SDL_CreateWindow("SP-1", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, g_layout.window_w,
                              g_layout.window_h, SDL_WINDOW_SHOWN);
  if (g_window == nullptr) {
    std::fprintf(stderr, "SDL_CreateWindow: %s\n", SDL_GetError());
    return EXIT_FAILURE;
  }
  g_renderer = SDL_CreateRenderer(g_window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
  if (g_renderer == nullptr) {
    g_renderer = SDL_CreateRenderer(g_window, -1, 0);
  }
  g_lcd = SDL_CreateTexture(g_renderer, SDL_PIXELFORMAT_RGB565, SDL_TEXTUREACCESS_STREAMING, SP1_UI_HOR_RES,
                            SP1_UI_VER_RES);
  if (g_renderer == nullptr || g_lcd == nullptr) {
    std::fprintf(stderr, "SDL renderer/texture failed\n");
    return EXIT_FAILURE;
  }

  lv_init();
  lv_tick_set_cb(tick_cb);

  lv_display_t* display = lv_display_create(SP1_UI_HOR_RES, SP1_UI_VER_RES);
  lv_display_set_flush_cb(display, lcd_flush);
  lv_display_set_buffers(display, g_fb, nullptr, sizeof g_fb, LV_DISPLAY_RENDER_MODE_DIRECT);

  lv_indev_t* indev = lv_indev_create();
  lv_indev_set_type(indev, LV_INDEV_TYPE_POINTER);
  lv_indev_set_read_cb(indev, pointer_read);

  Sp1PanelCallbacks cb{};
  cb.on_pad = on_pad;
  cb.on_enc = on_enc;
  cb.on_pot = on_pot;
  sp1_panel_init(&cb);

  sp1_ui_create(lv_screen_active());
  sp1_ui_set_radio("BLE  sim", "WIFI sim");

  std::fprintf(stderr, "sp1_ui_sim: chassis %dx%d  lcd %dx%d x%d\n", g_layout.window_w, g_layout.window_h,
               SP1_UI_HOR_RES, SP1_UI_VER_RES, g_layout.lcd_zoom);

  bool running = true;
  while (running) {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
      if (event.type == SDL_QUIT) {
        running = false;
      } else if (event.type == SDL_KEYDOWN && event.key.repeat == 0) {
        if (event.key.keysym.sym == SDLK_ESCAPE) {
          running = false;
        } else if (event.key.keysym.sym == SDLK_LEFT || event.key.keysym.sym == SDLK_COMMA) {
          sp1_panel_add_enc(-1);
        } else if (event.key.keysym.sym == SDLK_RIGHT || event.key.keysym.sym == SDLK_PERIOD) {
          sp1_panel_add_enc(1);
        } else {
          const int pad = sp1_shell_key_for_sdl(event.key.keysym.sym);
          if (pad >= 0) {
            sp1_panel_set_pad(static_cast<uint8_t>(pad), true);
          }
        }
      } else if (event.type == SDL_KEYUP) {
        const int pad = sp1_shell_key_for_sdl(event.key.keysym.sym);
        if (pad >= 0) {
          sp1_panel_set_pad(static_cast<uint8_t>(pad), false);
        }
      } else if (event.type == SDL_MOUSEWHEEL) {
        int mx = 0;
        int my = 0;
        SDL_GetMouseState(&mx, &my);
        if (sp1_shell_hit_enc(&g_layout, mx, my) || map_to_lcd(mx, my, &g_ptr_x, &g_ptr_y)) {
          sp1_panel_add_enc(event.wheel.y > 0 ? 1 : -1);
        }
      } else if (event.type == SDL_MOUSEBUTTONDOWN && event.button.button == SDL_BUTTON_LEFT) {
        g_ptr_down = true;
        g_last_mx = event.button.x;
        g_last_my = event.button.y;
        int lx = 0;
        int ly = 0;
        g_ptr_in_lcd = map_to_lcd(event.button.x, event.button.y, &lx, &ly);
        if (g_ptr_in_lcd) {
          g_ptr_x = lx;
          g_ptr_y = ly;
        } else if (sp1_shell_hit_enc(&g_layout, event.button.x, event.button.y)) {
          g_enc_grab = true;
          sp1_panel_set_pad(SP1_PANEL_ENC_SW, true);
        } else {
          const int pot = sp1_shell_hit_pot(&g_layout, event.button.x, event.button.y);
          if (pot >= 0) {
            g_drag_pot = pot;
          } else {
            g_held_key = sp1_shell_hit_key(&g_layout, event.button.x, event.button.y);
            if (g_held_key >= 0) {
              sp1_panel_set_pad(static_cast<uint8_t>(g_held_key), true);
            }
          }
        }
      } else if (event.type == SDL_MOUSEBUTTONUP && event.button.button == SDL_BUTTON_LEFT) {
        g_ptr_down = false;
        g_ptr_in_lcd = false;
        if (g_enc_grab) {
          sp1_panel_set_pad(SP1_PANEL_ENC_SW, false);
          g_enc_grab = false;
        }
        g_drag_pot = -1;
        release_held_key();
      } else if (event.type == SDL_MOUSEMOTION) {
        int lx = 0;
        int ly = 0;
        if (g_ptr_in_lcd && map_to_lcd(event.motion.x, event.motion.y, &lx, &ly)) {
          g_ptr_x = lx;
          g_ptr_y = ly;
        }
        if (g_enc_grab) {
          const int dx = event.motion.x - g_last_mx;
          if (std::abs(dx) >= 8) {
            sp1_panel_add_enc(dx > 0 ? 1 : -1);
            g_last_mx = event.motion.x;
          }
        }
        if (g_drag_pot >= 0) {
          const float dy = static_cast<float>(g_last_my - event.motion.y) / 80.f;
          sp1_panel_set_pot(static_cast<uint8_t>(g_drag_pot), sp1_panel_pot(static_cast<uint8_t>(g_drag_pot)) + dy);
          g_last_my = event.motion.y;
        }
      }
    }

    lv_timer_handler();
    sp1_shell_draw(g_renderer, &g_layout, g_status);
    SDL_RenderCopy(g_renderer, g_lcd, nullptr, &g_layout.lcd);
    SDL_RenderPresent(g_renderer);
  }

  SDL_DestroyTexture(g_lcd);
  SDL_DestroyRenderer(g_renderer);
  SDL_DestroyWindow(g_window);
  SDL_Quit();
  return EXIT_SUCCESS;
}
