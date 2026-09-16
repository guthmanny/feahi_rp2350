# TFT020B107-C0 ↔ ESP32-C6 8080 连接（v0.1 冻结）

模组规格书：[JME-01_TFT020B107-C0_LCD.pdf](JME-01_TFT020B107-C0_LCD.pdf)

**方案 C：** 8080 走线 **仅在 PERIPH-1 板内**，不经过 CBI-40。

完整 C6 分配（含 I2C/IPC/编码器）：[../schematic/c6_gpio.csv](../schematic/c6_gpio.csv)

## 模组 FPC 引脚

| FPC Pin | 符号 | 接 C6 |
|---------|------|--------|
| 1 | LEDA | GPIO4 PWM（经 NPN + 限流） |
| 2 | LEDK | GND |
| 6 | VCC | 2.8/3.3 V（与 IOVCC 同域） |
| 7–14 | DB0–DB7 | GPIO2,3,14,20,21,22,23,19 |
| 15 | RD | 接 **IOVCC**（只写不读） |
| 16 | WR | GPIO18（PARLIO CLK） |
| 17 | RS | GPIO1（DC） |
| 18 | CS | GPIO0 |
| 19 | TE | NC（可选） |
| 20 | RESET | GPIO15（10k 上拉） |
| 21–22 | GND | GND |

## ESP32-C6 GPIO 分配（LCD 部分）

| 功能 | C6 GPIO | 模块 Pin | 备注 |
|------|---------|----------|------|
| DB0 | GPIO2 | IO2 | PARLIO `data_gpio_nums[0]` |
| DB1 | GPIO3 | IO3 | |
| DB2 | GPIO14 | IO14 | |
| DB3 | GPIO20 | IO20 | |
| DB4 | GPIO21 | IO21 | |
| DB5 | GPIO22 | IO22 | |
| DB6 | GPIO23 | IO23 | |
| DB7 | GPIO19 | IO19 | |
| WR | GPIO18 | IO18 | PARLIO `clk_gpio_num` |
| RS | GPIO1 | IO1 | PARLIO `dc_gpio_num` |
| CS | GPIO0 | IO0 | |
| RESET | GPIO15 | IO15 | strapping；10k PU |
| BL | GPIO4 | IO4 | LEDA；strapping；10k PU |
| TE | — | — | 不连接 |

> PARLIO 不要求 GPIO 连续；`data_gpio_nums[]` 顺序对应 LCD DB0–DB7。

## 其他 C6 外设（同板）

| 功能 | GPIO | 说明 |
|------|------|------|
| I2C SDA/SCL | GPIO6 / GPIO7 | TCA8418 + IS31FL3733 |
| I2C INT | GPIO5 | TCA8418 INT# |
| IPC TX/RX | GPIO16 / GPIO17 | UART0 ↔ CBI ↔ RP2350 |
| C6_BOOT | GPIO9 | CBI Pin20 |
| ENC A/B/SW | GPIO12 / GPIO13 / GPIO8 | 与 USB D± 复用；量产可不用 USB |

## ESP-IDF 驱动

- 接口：**Intel 8080 8-bit**（C6 经 PARLIO 模拟 I80）
- 驱动 IC：**ST7789P3** → `esp_lcd_new_panel_st7789()`
- IO 层：`esp_lcd_new_panel_io_parl()`，`data_width = 8`
- UI：**LVGL** on ESP32-C6
- 建议 IDF **≥ 5.5**

## 布局

- FPC 插座靠近 C6 **≤ 15 mm**
- 8080 数据线等长 ±5 mm
- LCD 数字区远离 Class-D 功放 **≥ 10 mm**
