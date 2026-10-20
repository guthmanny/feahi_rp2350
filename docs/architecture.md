# B-C6 架构说明（方案 C）

> **规范（平台无关）：** [spec/](../spec/README.md) — Intent、样本 ref、FX 目录、IPC envelope。  
> **本文档：** 参考实现如何把 SP-1 语义映射到 **RP2350 + C6**（及单板 SP-1 profile）。  
> 存储介质、引脚、芯片型号均为 **profile 决策**，不是 SP-1  invariant。

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

## 芯片分工（参考 profile：rp2350-c6 / sp-1 单板）

| 子系统 | 参考归属 | 说明 |
|--------|----------|------|
| 音频 Engine（Pad/Seq/FX/Storage） | RP2350 | 实现 [spec/intents](../spec/intents.md) 与 [voice-and-sample](../spec/voice-and-sample.md) |
| I2S → Codec | RP2350 | 48 kHz；MS1808/MS4344 为 **本 profile** 模拟链 |
| 样本持久化 | RP2350 | 当前常用 SPI NAND；spec 允许任意 Storage Adapter |
| USB Audio | RP2350 | feahi_pico 路径 |
| UI / 键灯 / 屏 | C6 | 产生 Intent、消费 State；见 [binding-template](../spec/binding-template.md) |
| BLE MIDI / WiFi OTA | C6 | 可选 |
| IPC | RP2350 ↔ C6 | 仅 Intent/State + Storage Job；见 [spec/ipc.md](../spec/ipc.md) |

旧消息名 `PAD_TRIGGER` 等已对齐为 spec 中的 `PadPress`、`Transport` 等类型名。

## feahi 迁移

| 模块 | 来源 | 复用度 |
|------|------|--------|
| Pad 引擎 / Port | feahi_pico | ~85% |
| 音序器契约 | feahi | ~70%（需扩展 Group / Timing） |
| USB Audio 桥 | feahi_pico | ~70% |
| Storage Adapter（例：W25N NAND） | feahi_pico | ~85%；介质可换，见 spec |
| C6 UI / IPC / 8080 驱动 | 新建 | 0% |

## 明确不做

- Bluetooth Classic / A2DP（C6 不支持）
- C6 侧音频 DSP / I2S 主控
- 双主控同时访问 NAND SPI
- SPI 替代 8080 屏（量产模组固定为并口）

## 硬件

**量产**为 [单板 SP-1](../hardware/profiles/sp-1/)（RP2350 + C6 同板）；本仓另保留 [b-c6 模块化模板](../hardware/profiles/b-c6/)（CORE-B + PERIPH-1 + CBI-40）作对照与归档。

- 8080 接线草案：[hardware/profiles/b-c6/datasheets/TFT020B107-C0_C6_GPIO.md](../hardware/profiles/b-c6/datasheets/TFT020B107-C0_C6_GPIO.md)
- 完整硬件说明：[hardware.md](./hardware.md)
