#ifndef LV_CONF_H
#define LV_CONF_H

/* PC simulator: same panel size as SP-1, RGB565 like the ST7789. */
#define LV_COLOR_DEPTH 16
#define LV_USE_OS LV_OS_NONE
#define LV_USE_SDL 0
#define LV_USE_WINDOWS 0
#define LV_MEM_SIZE (2U * 1024U * 1024U)
#define LV_DEF_REFR_PERIOD 16
#define LV_DPI_DEF 130
#define LV_USE_FLOAT 1

#define LV_FONT_MONTSERRAT_10 1
#define LV_FONT_MONTSERRAT_12 1
#define LV_FONT_MONTSERRAT_14 1
#define LV_FONT_DEFAULT &lv_font_montserrat_14

#define LV_USE_LABEL 1
#define LV_USE_BUTTON 1
#define LV_USE_FLEX 1
#define LV_USE_GRID 1
#define LV_USE_THEME_DEFAULT 1
#define LV_THEME_DEFAULT_DARK 1

#define LV_USE_LOG 1
#define LV_LOG_LEVEL LV_LOG_LEVEL_WARN

#endif /* LV_CONF_H */
