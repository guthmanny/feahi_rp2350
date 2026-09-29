# SP-1 单板硬件方案

> **状态：** v0.4（2026-09-23）  
> **变更：** Pad 矩阵 **方案 A** — **RP2350 GPIO** 直扫 `MAT_*`；C6 I²C 仅 **IS31FL3729**（见 [sp1_rp2350_pad_matrix.md](../hardware/schematic/sp1_rp2350_pad_matrix.md)、[sp1_c6_ui.md](../hardware/schematic/sp1_c6_ui.md)）。  
> v0.2：放弃 **CORE + PERIPH 叠板 / CBI-40**，改为 **单板 SP-1**。

## 设计目标

| 目标 | 做法 |
|------|------|
| 结构简单、量产一致 | **一块 PCB** 集成 RP2350、C6、Codec、屏、接口与电源 |
| 音频实时路径 | RP2350：I2S、NAND、Pad/Seq、**USB Audio**、DIN MIDI |
| UI 与连接 | ESP32-C6：8080 屏、I2C 键灯、BLE/WiFi、IPC 从机 |
| 用户接口 | **单一 USB-C**（供电 + USB 2.0 至 RP2350：UF2 / CDC / UAC） |
| 便携 | 锂电池 + 充电 PMIC；VBAT 经升压供功放 / 背光 |

```
┌──────────────────────────── SP-1 单板 ────────────────────────────┐
│  J1 USB-C ──► VBUS→PMIC │ D+/D−→ESD→RP2350 (UAC/UF2/CDC)        │
│  U1 RP2350A + U2 PSRAM + U4 Flash + U3 NAND                       │
│       │ I2S ─────────────► MS1808 / MS4344 ──► 模拟 / 功放 / TRS  │
│       │ UART1 ───────────► ESP32-C6-MINI ──► TFT020B107 8080       │
│       │ UART0 ───────────► MIDI IN/OUT                             │
│  C6 ──I2C──► IS31FL3729 │ RP2350 ──MAT_* + EC11 编码器 ──► IPC → C6  │
│  BAT + 充电 PMIC + 3.3 V / 5 V 电源树                              │
└───────────────────────────────────────────────────────────────────┘
```

---

## 板级定义

| 项 | 值 |
|----|-----|
| **产品 PCB** | **SP-1**（与 KiCad 工程 `hardware/kicad/sp-1/` 对应） |
| **推荐层数** | **4 层**（USB / RP2350 / C6 8080 走线 + 完整地 + 模拟分区） |
| **主控（音频）** | **RP2350A** QFN-60 |
| **主控（UI）** | **ESP32-C6-MINI-1** |
| **已取消** | CORE-A / CORE-B / PERIPH-1 分板、**FEAHI-CBI-40** 邮票孔、ESP32-S3 A 方案对照板 |

---

## 功能分区（同板布局建议）

| 区域 | 主要器件 | 说明 |
|------|----------|------|
| **数字核心** | RP2350、W25Q32、APS6404L、W25N01GV、**12.288 MHz** 晶振 | Flash/PSRAM/NAND 走线短；48k×256fs MCLK；时钟见 `rp2350a_interfaces.md` |
| **USB** | Type-C 16P、USBLC6-2 类 ESD | **唯一用户 USB 口**；CC1/CC2 各 5.1 kΩ→GND（Device）；D+/D−→RP2350 |
| **UI** | C6、TFT020B107 FPC、**IS31FL3729** Pad 灯；**RP2350** 扫 **5×6 Choc** | 8080 **仅 C6**；Pad 热路径在 RP2350；见 [sp1_c6_ui.md](../hardware/schematic/sp1_c6_ui.md) |
| **音频模拟** | MS1808、MS4344、NE5532/SGM5532、电位器、Class-D | I2S 数字线来自 RP2350；模拟地与数字地单点/分区 |
| **接口** | MIDI DIN、TRS、Mic、喇叭 pad | MIDI UART 接 RP2350；模拟链在 Codec 周边 |
| **电源** | 锂电、充电 PMIC、3.3 V LDO、5 V 升压 | 插 USB 时 PMIC **power path** 供 SYS；电池与 USB OR |

---

## 关键互连（无 CBI，板内直连）

| 信号 | 从 | 到 | 说明 |
|------|-----|-----|------|
| I2S ×5 | RP2350 GP20/16/17/18/9 | MS1808 + MS4344 | MCLK/BCLK/LRCLK 两 Codec 共线 |
| IPC UART | RP2350 GP4/5 | C6 UART0（交叉 TX/RX） | 921600 baud |
| MIDI UART | RP2350 GP0/1 | MIDI 光耦 / 驱动 | 31250 baud |
| USB D+/D− | J1 | ESD → RP2350 USB 焊盘 | 90 Ω 差分，短、少过孔 |
| +3V3 | PMIC/LDO 树 | RP2350、C6、Codec 数字、I2C 外设 | 按电流分区去耦 |
| VBAT / +5V | 电池 / PMIC / 升压 | 功放、背光、PMIC 输入 | 见电源原理图 |

完整网表见 [hardware/schematic/sp1_nets.csv](../hardware/schematic/sp1_nets.csv)。  
GPIO 表：[rp2350a_gpio.csv](../hardware/schematic/rp2350a_gpio.csv)、[c6_gpio.csv](../hardware/schematic/c6_gpio.csv)。

---

## USB（量产单口）

| 项 | 说明 |
|----|------|
| **物理** | 板边 **一个** Type-C 母座（BOM：`05000-02000-00100` 一类 16P 沉板，或结构确认后的等价件） |
| **数据** | **RP2350** 实现 UAC2、UF2、USB-CDC；**C6 不使用 USB 设备功能**（量产） |
| **供电** | VBUS → 充电/电源 PMIC → 系统 3.3 V / 电池 / 5 V 升压；插线可工作 + 可充电 |
| **CC** | 各 **5.1 kΩ 到 GND**（USB 2.0 Device） |

---

## 8080 屏

- 模组：**TFT020B107-C0**（江西华佳 / JME-01 规格书，ST7789P3，8080 8-bit）  
- **FPC：22 pin、0.5 mm 间距**；板端插座 **J-LCD**：蔚科 **04900-04000-12030**（`FPC CONNECTOR_26_0.5mm`，footprint `26PIN_FPCZ`，仅用 pin 1～22）  
- 接线：**仅 C6** — [TFT020B107-C0_C6_GPIO.md](../hardware/datasheets/TFT020B107-C0_C6_GPIO.md)、[sp1_lcd.md](../hardware/schematic/sp1_lcd.md)  
- 单板优势：FPC 与 C6 同板，无跨板 8080 走线约束  

---

## C6 UI 与 Pad 矩阵（方案 A，v1.3）

| 器件 | 职责 |
|------|------|
| **RP2350A（U7）** | **5×6 Choc** 矩阵 GPIO 扫描、Pad 引擎 / I2S 低延迟触发 |
| **ESP32-C6-MINI-1** | 8080 + LVGL、I²C 主站（3729）、IPC（UI，非 Pad 热路径） |
| **IS31FL3729（U18）** | **20** 路键下 LED，8 bit PWM；蔚科库有符号/料 |

- I²C：**U18 = 0x37**（AD=VCC）；**无 TCA9555**。  
- 矩阵网 **`MAT_C0…5` / `MAT_R0…4`** 自 c6 子页经板内走线接 U7；拓扑 **Choc + 二极管** 不变。  
- 接线与 GPIO 表：[sp1_rp2350_pad_matrix.md](../hardware/schematic/sp1_rp2350_pad_matrix.md)、[sp1_c6_ui.md](../hardware/schematic/sp1_c6_ui.md)。

---

## 原理图 / PCB 工程

| 路径 | 说明 |
|------|------|
| [hardware/kicad/sp-1/](../hardware/kicad/sp-1/) | **主工程** `sp-1.kicad_pro`（原理图 + PCB） |
| [hardware/schematic/rp2350a_interfaces.md](../hardware/schematic/rp2350a_interfaces.md) | RP2350 存储、I2S、串口、USB |
| [hardware/BOM_IC.csv](../hardware/BOM_IC.csv) | IC 与连接器清单（`board=SP-1`） |

---

## 布局要点

1. **RP2350 ↔ Codec**：I2S 等长包地，优先 ≤30 mm 量级（同板通常足够）。  
2. **C6 ↔ FPC**：8080 数据/控制线短；背光电源从 5 V 树单独滤波。  
3. **USB**：J1 → ESD → RP2350，**不要**经 C6；与晶振/时钟远离。  
4. **模拟**：MS1808/MS4344/功放/TRS 靠板边；数字开关远离 Mic/Line 输入。  
5. **天线**：C6 模组远离 USB 差分与 D 类功放开关节点。

---

## 已废弃文档（仅供考古）

以下内容为 **模块化方案 C** 遗留，**勿再用于新设计**：

- FEAHI-CBI-40 引脚与机械（原 `hardware/kicad/cbi40_pinout.csv`、`feahi_cbi40_*` 工程）  
- `coreb_nets.csv` / `periph1_nets.csv` 中的 **CBI Pin** 列（已由 `sp1_nets.csv` 替代）  
- CORE-A（ESP32-S3 可互换核心板）对照实验  

Git 历史中可查阅完整 CBI 机械规格。

---

## 修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-09-18 | 模块化 CORE-B + PERIPH-1 + CBI-40 |
| **v0.2** | **2026-09-19** | **改为 SP-1 单板；取消核心板/叠焊** |
| **v0.3** | **2026-09-22** | **C6 UI：TCA9555 + IS31FL3729；TFT020B107 + 蔚科 26P FPC 座** |
| **v0.4** | **2026-09-23** | **方案 A：Pad 矩阵迁 RP2350 GPIO；移除 TCA9555** |
