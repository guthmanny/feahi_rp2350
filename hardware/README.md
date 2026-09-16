# SP-1 硬件资料

本目录存放 Soran SP-1 / FEAHI-CBI-40 相关的硬件参考与 PCB 模板。

## 目录

| 路径 | 内容 |
|------|------|
| [datasheets/](datasheets/) | 器件与模组规格书（PDF） |
| [BOM_IC.csv](BOM_IC.csv) | **IC 清单（待复核）** |
| [schematic/](schematic/) | **原理图框架**：网表 CSV、C6 GPIO |
| [kicad/](kicad/) | FEAHI-CBI-40 KiCad 10 PCB + 分层原理图 |
| [../docs/hardware.md](../docs/hardware.md) | 模块化架构与 CBI-40 引脚定义 |

## 选型器件（当前）

| 功能 | 型号 | 规格书 |
|------|------|--------|
| 2" TFT 彩屏 | JME-01 **TFT020B107-C0**（ST7789P3，**8080 并口**） | [datasheets/JME-01_TFT020B107-C0_LCD.pdf](datasheets/JME-01_TFT020B107-C0_LCD.pdf) |
| UI MCU | **ESP32-C6-MINI**（PERIPH-1，驱动 8080 屏） | — |
| ADC（采样输入） | **MS1808**（24-bit ΔΣ，8–96 kHz） | [datasheets/MS1808_ADC.pdf](datasheets/MS1808_ADC.pdf) |
| DAC（播放输出） | **MS4344**（24-bit，至 192 kHz） | [datasheets/MS4344_DAC.pdf](datasheets/MS4344_DAC.pdf) |

> **方案 C：** C6 + 8080 屏 + MS1808/MS4344 均在 PERIPH-1；CBI v0.3 仅 I2S + IPC UART + MIDI。8080 接线见 [datasheets/TFT020B107-C0_C6_GPIO.md](datasheets/TFT020B107-C0_C6_GPIO.md)。
