#pragma once

#include <SDL2/SDL.h>

#include <cstdint>

#include "sp1_panel.h"

struct Sp1ShellLayout
{
  int window_w = 0;
  int window_h = 0;
  SDL_Rect lcd{};
  int lcd_zoom = 2;
  SDL_Rect enc{};
  SDL_Rect pot[SP1_PANEL_POT_COUNT]{};
  SDL_Rect key[SP1_PANEL_KEYS]{};
};

void sp1_shell_layout(Sp1ShellLayout* layout);
void sp1_shell_draw(SDL_Renderer* renderer, const Sp1ShellLayout* layout, const char* status);

int sp1_shell_hit_key(const Sp1ShellLayout* layout, int x, int y);
bool sp1_shell_hit_enc(const Sp1ShellLayout* layout, int x, int y);
int sp1_shell_hit_pot(const Sp1ShellLayout* layout, int x, int y);

int sp1_shell_key_for_sdl(SDL_Keycode key);
