# B-C6 架构说明（方案 C）

## 总览

**方案 C：** 量产屏 **TFT020B107-C0** 为 **8080 8-bit 并口**，ESP32-C6 与 LCD 同在 **PERIPH-1**；RP2350 在 **CORE-B**，经 **CBI-40 v0.3** 传 I2S 与 IPC UART。

```
┌─────────────────────────────┐         ┌─────────────────────────────┐
│         CORE-B                │  CBI    │         PERIPH-1            │
│  RP2350 + APS6404L PSRAM     │◄───────►│  ESP32-C6                   │
│  W25N01GV SPI NAND          │ I2S×5   │  TFT020B107 8080 + LVGL     │
│  USB-C (UAC2 / 烧录)          │ IPC UART│  MS1808 / MS4344            │
├─────────────────────────────┤         ├─────────────────────────────┤
│ Core0: I2S ISR + 混音       │         │ 按键 / LED (I2C, 板内)      │
│ Core1: Pad 预取 / FX        │         │ 编码器 / 电源键 (GPIO)      │
│ 音序器 advance              │         │ BLE MIDI / WiFi OTA         │
│ NAND 读写                   │         │ 上位机 Library 元数据       │
│ USB Audio                   │         │                             │
│ MIDI IN/OUT (经 CBI)        │         │                             │
└─────────────────────────────┘         └─────────────────────────────┘
         │                                           │
    I2S → MS1808/4344                          WiFi / BLE
    SPI NAND                                   C6 USB (可选)
    USB OTG
```

## 芯片分工

| 子系统 | 归属 | 说明 |
|--------|------|------|
| I2S（至 MS1808/MS4344） | RP2350（Core） | 48 kHz；模拟链在 PERIPH-1 |
| 1 Gb NAND Flash | RP2350 | 样本 / Project / Pattern |
| USB Audio | RP2350 | 低延迟，复用 feahi_pico 路径 |
| Pad / Seq / FX DSP | RP2350 | 实时，不进 ISR 读 Flash |
| 2" TFT (TFT020B107 8080) | C6（Periph） | ST7789P3，PARLIO + LVGL |
| 机械键 + LED | C6 | TCA8418 / IS31FL3733，**板内 I2C** |
| 编码器 / 电源键 | C6 | **板内 GPIO** |
| BLE MIDI | C6 | BLE 5 only |
| WiFi OTA | C6 | WiFi 6 (2.4 GHz) |
| 上位机 Library 管理 | C6 | USB 或 WiFi |
| IPC | RP2350 ↔ C6 | **UART 经 CBI**（Pin 18–19），921600 baud |

## IPC 消息（草案）

### C6 → RP2350

| 消息 | 说明 |
|------|------|
| `PAD_TRIGGER` | pad_index, group, velocity |
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

大文件（Library 导入）由 RP2350 代理写 NAND，C6 只传元数据。

## feahi 迁移

| 模块 | 来源 | 复用度 |
|------|------|--------|
| Pad 引擎 / Port | feahi_pico | ~85% |
| 音序器契约 | feahi | ~70%（需扩展 Group / Timing） |
| USB Audio 桥 | feahi_pico | ~70% |
| NAND 驱动 | feahi_pico W25N | ~85%（BOM 已定 W25N01GV） |
| C6 UI / IPC / 8080 驱动 | 新建 | 0% |

## 明确不做

- Bluetooth Classic / A2DP（C6 不支持）
- C6 侧音频 DSP / I2S 主控
- 双主控同时访问 NAND SPI
- SPI 替代 8080 屏（量产模组固定为并口）

## 硬件

软件架构对应 **CORE-B** + **PERIPH-1（方案 C）**；可替换 **CORE-A**（ESP32-S3）做对照，**Periph 不变**（C6 仍负责 UI）。

- 8080 接线草案：[hardware/datasheets/TFT020B107-C0_C6_GPIO.md](../hardware/datasheets/TFT020B107-C0_C6_GPIO.md)
- 完整硬件说明：[hardware.md](./hardware.md)
