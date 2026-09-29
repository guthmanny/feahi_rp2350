# TFT020B107-C0 ↔ ESP32-C6 8080 连接（v0.2 冻结）

模组规格书：[JME-01_TFT020B107-C0_LCD.pdf](JME-01_TFT020B107-C0_LCD.pdf)（与「JME-01 液晶屏 TFT020B107-C0 产品规格书」同版）

**SP-1 单板：** 8080 走线 **C6 ↔ J-LCD ↔ 模组 FPC** 同板。  
**FPC 插座与 22P 定义：** [../schematic/sp1_lcd.md](../schematic/sp1_lcd.md)（蔚科 **04900-04000-12030**，`FPC CONNECTOR_26_0.5mm` / `26PIN_FPCZ`）。

完整 C6 分配（含 I2C/IPC）：[../schematic/c6_gpio.csv](../schematic/c6_gpio.csv)  
编码器 / EXP_ADC → RP2350：[../schematic/sp1_encoder.md](../schematic/sp1_encoder.md)、[../schematic/rp2350a_gpio_plan.md](../schematic/rp2350a_gpio_plan.md)

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
| 19 | TE | **GPIO8**（LCD_TE，帧同步 / 抗撕裂） |
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
| TE | GPIO8 | IO8 | 输入；等 TE 有效沿再刷 GRAM（见下） |

> PARLIO 不要求 GPIO 连续；`data_gpio_nums[]` 顺序对应 LCD DB0–DB7。

## 其他 C6 外设（同板）

| 功能 | GPIO | 说明 |
|------|------|------|
| I2C SDA/SCL | GPIO6 / GPIO7 | IS31FL3729 U18（键下灯） |
| GPIO5 (IO5) | — | 预留（MTDI strapping） |
| POW_DET / POW_CTL | GPIO12 / GPIO13 | 电源键检测 / MP2637 EN 保持（见 power 页） |
| IPC TX/RX | GPIO16 / GPIO17 | UART0 ↔ RP2350 GP4/5（板内） |
| C6_BOOT | GPIO9 | **仅** DNP 下载测试 pad（strapping） |

## ESP-IDF 驱动

- 接口：**Intel 8080 8-bit**（C6 经 PARLIO 模拟 I80）
- 驱动 IC：**ST7789P3** → `esp_lcd_new_panel_st7789()`
- IO 层：`esp_lcd_new_panel_io_parl()`，`data_width = 8`
- UI：**LVGL** on ESP32-C6
- 建议 IDF **≥ 5.5**

### 抗撕裂（TE / GPIO8）

- **硬件：** FPC-19 `TE` → **GPIO8**，模组侧推挽输出；MCU 配置为 **输入、关闭内部上下拉**。
- **思路：** 在 **TE 上升沿（或规格书/示波器确认的有效窗口）** 之后再发起本帧 GRAM 写，避免扫描与写冲突。
- **LVGL：** 使用 **全屏缓冲** 或 `full_refresh` + TE 同步回调；在 `flush_cb` 里 **等待 TE** 再 `esp_lcd_panel_draw_bitmap()`，或在 `on_color_trans_done` 与 TE 组合节流。
- **验证：** 首版用示波器看 TE 周期与 PARLIO 写时序，再定中断沿（上升/下降）与极性。

## 布局

- FPC 插座靠近 C6 **≤ 15 mm**
- 8080 数据线等长 ±5 mm
- LCD 数字区远离 Class-D 功放 **≥ 10 mm**
