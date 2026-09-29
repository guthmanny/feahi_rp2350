# SP-1 液晶：TFT020B107-C0 + FPC 插座（冻结）

> **状态：** v1.0（2026-09-22）  
> **模组规格书：** [JME-01_TFT020B107-C0_LCD.pdf](../datasheets/JME-01_TFT020B107-C0_LCD.pdf)（江西华佳 **TFT020B107-C0**，ST7789P3，8080 8-bit）  
> **C6 接线：** [TFT020B107-C0_C6_GPIO.md](../datasheets/TFT020B107-C0_C6_GPIO.md)

## 模组（MOD1）

| 项 | 值 |
|----|-----|
| 型号 | **TFT020B107-C0** |
| 尺寸 | 2.0″ IPS，240×RGB×320 |
| 接口 | **8080 并口 8-bit**（MCU parallel，非 SPI 量产路径） |
| 驱动 IC | **ST7789P3**（模组内置） |
| 蔚科编码 | **03300-12000-00100**（BOM `MOD1`） |
| 供电 | VCC / IOVCC **2.7～3.3 V**（典型 2.8 V）；背光 **LEDA/LEDK** ~3 V / ~60 mA |

## 模组 FPC（规格书 §2、§5 模组图）

| 项 | 值 |
|----|-----|
| **Pin 数** | **22**（有效信号；Pin 3～5 为 NC） |
| **间距** | **0.5 mm** |
| **触点跨距** | **P0.5×(22−1) = 10.5 mm**（±0.05 mm） |
| **FPC** | 含 PI 补强；弯折区勿高温久焊（见规格书 §8） |

## 板端插座 J-LCD（蔚科库定案）

库内 **无单独「22P 0.5 mm」采购符号**；选用 **26P / 0.5 mm** 卧式翻盖 **下接** 插座，**只用 Pin 1～22**，与模组 10.5 mm 跨距一致（库 footprint 上 Pin1～Pin22 中心距 = 10.5 mm）。

| 项 | 值 |
|----|-----|
| **Ref** | **J-LCD** |
| **KiCad 符号** | `Connectors:FPC CONNECTOR_26_0.5mm` |
| **Footprint** | `Connectors:26PIN_FPCZ` |
| **蔚科编码** | **04900-04000-12030** |
| **规格** | 26PIN，间距 0.5 mm，卧式翻盖下接，中电华威 |
| **Pin 23～26** | **不接线**（NC）；若改 22P 专用料需重新对位 |

> 原 BOM 占位 `04900-12000-10100` 未在 `Connectors.kicad_sym` 中匹配到符号；以 **04900-04000-12030 + 26PIN_FPCZ** 为 SP-1 原理图/PCB 依据。首批发模组后 **用 FPC 试插确认 Pin1 方向与锁扣**。

## FPC Pin → 网络（与 c6_gpio 一致）

| FPC | 符号 | 网络 / 接法 |
|-----|------|-------------|
| 1 | LEDA | 背光 +（C6 GPIO4 PWM，见 GPIO  doc） |
| 2 | LEDK | GND |
| 3～5 | NC | 不连接 |
| 6 | VCC | +2V8 或 +3V3（与 IOVCC 同域） |
| 7～14 | DB0～DB7 | LCD_DB0～7 → C6 |
| 15 | RD | **IOVCC**（只写模式） |
| 16 | WR | LCD_WR |
| 17 | RS | LCD_RS |
| 18 | CS | LCD_CS |
| 19 | TE | **LCD_TE** → C6 **GPIO8**（抗撕裂） |
| 20 | RESET | LCD_RST |
| 21～22 | GND | GND |

## 原理图（`c6.kicad_sch`）

| Ref | 蔚科符号 | 作用 |
|-----|----------|------|
| **J_LCD** | `Connectors:FPC CONNECTOR_26_0.5mm` / **04900-04000-12030** | 接 MOD1 FPC（pin 1～22） |
| **U9** | `RF_Module:ESP32-C6-MINI-1` | 8080 GPIO → FPC |
| **C_LCD1** | `Capacitors:MLCC0402-104K16V` | VCC 去耦 100 nF |
| **R_LCD1** | `Resistors:RC0402F103` | **LCD_RST** 上拉 10 kΩ |
| **R_LCD2** | `Resistors:RC0402F103` | **GPIO4 / LCD_BL** 上拉 10 kΩ（strapping） |
| **R_LCD3** | `Resistors:RC0402F103` | **LCD_BL → NPN 基极** 10 kΩ |
| **R_LCD4** | `Resistors:RC0402F103`（值 **10 Ω** 级，打样前按背光电流改） | **+5V_LCD → LEDA** 限流 |
| **Q_LCD1** | `ciscrete_parts:LMBT3904LT1G` | **LEDK** 低边 PWM（C 接 FPC-2，E→GND，B←R_LCD3） |

- 层次电源：**+3V3**、**GND**、**+5V_LCD**（背光，需在 **power** 页接到 **+5V** 树）。  
- FPC **pin 3～5、23～26**：NC（原理图需补 **no_connect**）。**Pin 19 TE** 接 C6 GPIO8。

## 布局

- **J-LCD** 靠近 **ESP32-C6-MINI-1**，8080 线 **≤ 15 mm** 量级；数据组等长 ±5 mm。  
- 背光 **LEDA** 走线短；电流从 **+5 V 树**经限流/PWM，**LEDK** 回 GND。  
- LCD 数字区远离 Class-D 功放开关节 **≥ 10 mm**。

## 修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-09-22 | 定案 TFT020B107-C0 + 蔚科 26P/0.5 mm FPC 座（用 1～22） |
