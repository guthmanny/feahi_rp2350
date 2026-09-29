# SP-1 硬件资料

本目录存放 Soran **SP-1 单板** 的硬件参考与 KiCad 工程。

## 目录

| 路径 | 内容 |
|------|------|
| [datasheets/](datasheets/) | 器件与模组规格书（PDF） |
| [BOM_IC.csv](BOM_IC.csv) | **IC 清单（`board=SP-1`）** |
| [schematic/](schematic/) | 网表 CSV、GPIO 表、RP2350 接口说明 |
| [kicad/sp-1/](kicad/sp-1/) | **主 KiCad 10 工程**（原理图 + PCB） |
| [kicad/feahi_cbi40_*](kicad/) | **已废弃** 模块化 CBI-40 模板（仅归档） |
| [../docs/hardware.md](../docs/hardware.md) | SP-1 单板架构与布局要点 |

## 选型器件（当前）

| 功能 | 型号 | 规格书 |
|------|------|--------|
| 2" TFT 彩屏 | **TFT020B107-C0**（华佳，ST7789P3，8080，**FPC 22P/0.5 mm**） | [JME-01 规格书 PDF](datasheets/JME-01_TFT020B107-C0_LCD.pdf)、[sp1_lcd.md](schematic/sp1_lcd.md) |
| LCD FPC 座 J-LCD | **FPC CONNECTOR_26_0.5mm** / **26PIN_FPCZ**，蔚科 **04900-04000-12030** | [sp1_lcd.md](schematic/sp1_lcd.md) |
| UI MCU | **ESP32-C6-MINI**（8080 屏 + I²C 键灯） | — |
| 键矩阵 | **RP2350 GPIO**（5×6 Choc，方案 A） | [schematic/sp1_rp2350_pad_matrix.md](schematic/sp1_rp2350_pad_matrix.md) |
| 编码器 | **EC11 → RP2350** GP2/3/22 | [schematic/sp1_encoder.md](schematic/sp1_encoder.md) |
| Pad 灯 | **IS31FL3729**（蔚科库） | 同上 |
| ADC（采样输入） | **MS1808**（24-bit ΔΣ，8–96 kHz） | [datasheets/MS1808_ADC.pdf](datasheets/MS1808_ADC.pdf) |
| DAC（播放输出） | **MS4344**（24-bit，至 192 kHz） | [datasheets/MS4344_DAC.pdf](datasheets/MS4344_DAC.pdf) |

8080 接线见 [datasheets/TFT020B107-C0_C6_GPIO.md](datasheets/TFT020B107-C0_C6_GPIO.md)。  
板内互连见 [schematic/sp1_nets.csv](schematic/sp1_nets.csv)。
