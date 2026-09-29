# SP-1 架构说明（单板）

## 总览

**SP-1** 在 **一块 PCB** 上集成 **RP2350A（音频）** 与 **ESP32-C6（UI/连接）**，以及 Codec、8080 屏、接口与电源。  
不再使用 CORE / PERIPH 分板或 CBI-40。

```
┌──────────────────────────────── SP-1 ────────────────────────────────┐
│  RP2350 + APS6404L + W25Q32 + W25N01GV                              │
│       │ USB-C (UAC / UF2 / CDC)                                      │
│       │ I2S ──► MS1808 / MS4344 ──► 模拟 I/O / 功放                  │
│       │ UART1 ◄──► ESP32-C6 ──► TFT020B107 8080 + LVGL               │
│       │ UART0 ──► MIDI                                               │
│  C6: I2C 键下灯 │ BLE/WiFi │ IPC(UI) │ Pad/Enc 在 RP2350 GPIO        │
└──────────────────────────────────────────────────────────────────────┘
```

## 芯片分工

| 子系统 | 归属 | 说明 |
|--------|------|------|
| I2S（MS1808/MS4344） | RP2350 | 48 kHz；**板内直连** |
| 1 Gb NAND | RP2350 | 样本 / Project / Pattern |
| USB Audio / 烧录 / CDC | RP2350 | **唯一 USB-C 数据** 接 RP2350 |
| Pad / Seq / FX DSP | RP2350 | 实时 |
| 2" TFT (8080) | C6 | PARLIO + LVGL |
| 机械键 | **RP2350** | **GPIO 矩阵** 直扫（`MAT_*`），见 [sp1_rp2350_pad_matrix.md](../hardware/schematic/sp1_rp2350_pad_matrix.md) |
| Pad 键下灯 | C6 | **IS31FL3729** + I²C；见 [sp1_c6_ui.md](../hardware/schematic/sp1_c6_ui.md) |
| 编码器 EC11 | RP2350 | GP22/27 + 矩阵 SW；**EXP_ADC** GP26–29；见 `rp2350a_gpio_plan.md` |
| BLE MIDI | C6 | BLE 5 |
| WiFi OTA | C6 | WiFi 6 (2.4 GHz) |
| 上位机 Library 管理 | C6 | WiFi；大文件写 NAND 由 RP2350 代理 |
| IPC | RP2350 ↔ C6 | **UART 板内**，921600 baud |

## IPC 消息（草案）

### C6 → RP2350

| 消息 | 说明 |
|------|------|
| `PAD_TRIGGER` | （可选 UI 同步）pad 状态；**实时触发在 RP2350 本地** |
| `SEQ_TRANSPORT` | start / stop / continue |
| `PARAM_CHANGE` | pad/FX 参数 |
| `LOAD_PROJECT` | project_id |
| `SAVE_PROJECT` | project_id |

### RP2350 → C6

| 消息 | 说明 |
|------|------|
| `METER_PEAK` | 电平表 |
| `PLAYHEAD_POS` | 步进 / 小节位置 |
| `SAMPLE_DONE` | 采样完成 |
| `ERROR` | 错误码 |
| `ENC_DELTA` | 旋钮步进（有符号） |
| `ENC_CLICK` / `ENC_LONG` | 按键短按 / 长按（可选） |

大文件（Library 导入）由 RP2350 代理写 NAND，C6 只传元数据。

## feahi 迁移

| 模块 | 来源 | 复用度 |
|------|------|--------|
| Pad 引擎 / Port | feahi_pico | ~85% |
| 音序器契约 | feahi | ~70% |
| USB Audio 桥 | feahi_pico | ~70% |
| NAND 驱动 | feahi_pico W25N | ~85% |
| C6 UI / IPC / 8080 / 3729 灯驱 | 新建 | 0% |

## 明确不做

- Bluetooth Classic / A2DP（C6 不支持）
- C6 侧音频 DSP / I2S 主控
- 双主控同时访问 NAND SPI
- SPI 替代 8080 屏（量产模组固定并口）
- **模块化核心板 / CBI-40**（已取消）
- **CORE-A ESP32-S3 对照板**（已取消）

## 硬件文档

- 单板方案：[hardware.md](./hardware.md)
- RP2350 接口：[hardware/schematic/rp2350a_interfaces.md](../hardware/schematic/rp2350a_interfaces.md)
- 8080 接线：[hardware/datasheets/TFT020B107-C0_C6_GPIO.md](../hardware/datasheets/TFT020B107-C0_C6_GPIO.md)
- C6 键/灯：[hardware/schematic/sp1_c6_ui.md](../hardware/schematic/sp1_c6_ui.md)
- 液晶 FPC：[hardware/schematic/sp1_lcd.md](../hardware/schematic/sp1_lcd.md)
- KiCad：[hardware/kicad/sp-1/](../hardware/kicad/sp-1/)
