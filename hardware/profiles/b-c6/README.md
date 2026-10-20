# B-C6 硬件 Profile

Soran **SP-1** 量产参考：**CORE-B**（RP2350）+ **PERIPH-1**（ESP32-C6 + 8080 屏），**FEAHI-CBI-40 v0.3** 邮票孔互联。

## 目录

| 路径 | 内容 |
|------|------|
| [datasheets/](datasheets/) | 器件与模组规格书（PDF） |
| [BOM_IC.csv](BOM_IC.csv) | IC 清单（蔚科编码） |
| [schematic/](schematic/) | 网表 CSV、C6 GPIO |
| [kicad/](kicad/) | KiCad 10：`sp1_cbi40_core` / `sp1_cbi40_periph` |

产品级硬件说明：[docs/hardware.md](../../../docs/hardware.md)。

## 打开 KiCad

**File → Open Project** →  
`hardware/profiles/b-c6/kicad/sp1_cbi40_periph/sp1_cbi40_periph.kicad_pro`  
（或 `sp1_cbi40_core`）

符号库：`kicad/libs/symbols/sp1.kicad_sym`（原理图搜索 `sp1:OR-M611` 等）。

## 选型器件（当前）

| 功能 | 型号 |
|------|------|
| 2" TFT | JME-01 **TFT020B107-C0**（8080） |
| UI MCU | **ESP32-C6-MINI** |
| ADC / DAC | **MS1808** / **MS4344** |
| MIDI IN 光耦 | **OR-M611** |

8080 接线：[datasheets/TFT020B107-C0_C6_GPIO.md](datasheets/TFT020B107-C0_C6_GPIO.md)
