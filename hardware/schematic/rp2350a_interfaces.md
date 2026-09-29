# SP-1：RP2350A 接口方案

| 项 | 值 |
|----|-----|
| 状态 | **v0.3 草案**（GPIO v2 见 [rp2350a_gpio_plan.md](rp2350a_gpio_plan.md)） |
| MCU | **RP2350A**，QFN-60（7×7 mm），30× Bank0 GPIO |
| 配套表 | [rp2350a_gpio.csv](rp2350a_gpio.csv) |
| 板内网表 | [sp1_nets.csv](sp1_nets.csv) |
| KiCad | [hardware/kicad/sp-1/](../kicad/sp-1/) |

---

## 1. 设计目标

- 音频实时路径（I2S、Pad/Seq、USB Audio、DIN MIDI）集中在 **RP2350A**。
- **ESP32-C6** 同板，经 **IPC UART** 与 RP2350 通信；DIN MIDI **不**接 C6。
- 在 **RP2350A 30 GPIO** 内完成：XIP Flash、Quad PSRAM、SPI NAND、2 路 HW UART（DEBUG 用 USB-CDC）、I2S×5、少量 GPIO（HP/Mute）。

---

## 2. 板内器件与总线

```
                    ┌──────────────── RP2350A ────────────────┐
  Y1 12.288MHz ────►│ XIN/XOUT                                 │
                    │                                          │
  U4 W25Q32JVSSIQ ►│ QSPI (CS0) ── XIP 固件                   │
  U2 APS6404L ─────►│ QSPI (CS1@GP8) ── 8MB PSRAM              │
  U3 W25N01GV ─────►│ SPI1 @ GP2,3,15,25 ── 样本 NAND         │
  J1 USB-C ────────►│ USB_DP/DM ── UAC / UF2 / CDC             │
                    │ GP0–1  UART0 ── MIDI IN/OUT（板内）      │
                    │ GP4–5  UART1 ── C6 IPC（板内交叉）       │
                    │ GP9,16–18,20 ── I2S → MS1808/MS4344      │
                    │ GP14–15 ── HP_DETECT / SPK_MUTE          │
                    └──────────────────────────────────────────┘
```

| Ref | 器件 | 接口 | 说明 |
|-----|------|------|------|
| U1 | **RP2350A** | — | QFN-60 |
| U4 | **W25Q32JVSSIQ**（蔚科 `03000-08000-50520`） | QMI CS0 | **XIP 启动** |
| U2 | APS6404L-3SQR-SN | QMI CS1 + 共线 DQ | USON-8 **Quad** |
| U3 | **W25N01GVZEIG** | SPI1 | 样本/工程；**不作启动** |
| Y1 | 12.288 MHz | XIN/XOUT | 48 kHz × **256 fs**（MCLK = 晶振） |
| J1 | USB-C 16P | USB | 量产 **唯一** 用户 USB；CC 5.1 kΩ；ESD |

---

## 3. 专用焊盘（非 GPIO0–29）

| 焊盘 | 连接 | 备注 |
|------|------|------|
| QSPI_CSn | W25Q32 CS + BOOT 键 | 低电平进 BOOTSEL |
| QSPI_SCK, SD0–SD3 | Flash + PSRAM 共线 | PSRAM **CE# → GP8** |
| USB_DP / USB_DM | J1 USB-C | 差分 90 Ω，短 |
| XIN / XOUT | Y1 + 负载电容 | 见 §6 |
| SWCLK / SWDIO | 调试座 | Tag-Connect 推荐 |
| RUN | 复位 | RC + 按钮可选 |

---

## 4. Bank0 GPIO 分配摘要

完整一行一项见 **rp2350a_gpio.csv**。

| 功能 | GPIO | 连接 |
|------|------|------|
| MIDI | 0, 1 | UART0 → 光耦 / 驱动 |
| NAND SPI | 2, 3, 15, **25** | SPI1 → W25N；**CS=GP25**（**v2**） |
| IPC | 4, 5 | UART1 ↔ C6 UART0 |
| Pad 矩阵列 | 6, 7, 19, 21, 23, 24 | `MAT_C0…5` |
| PSRAM CE | 8 | APS6404L CS1 |
| I2S DIN | 9 | MS1808 DOUT |
| Pad 矩阵行 | **10–14** | `MAT_R0…4`（**不占 GP25**） |
| I2S BCLK/LRCLK/DOUT | 16–18 | MS1808 + MS4344 |
| I2S MCLK | 20 | CLK_GPOUT0 |
| ENC A | 22 | EC11 |
| **EXP_ADC / ENC B** | 26–29 | **AIN0–3**；默认 **27=ENC_B**，**26/28/29=模拟扩展 DNP** |
| HP / Mute / LED | — | **v2 默认不占 U7**（见 gpio_plan §6） |

**RP2350A 约束：** I2S 走 **PIO**，引脚 **0–31**。

---

## 5. 板内信号映射（替代原 CBI-40）

| 网络 | RP2350A | 对端（SP-1 同板） |
|------|---------|-------------------|
| I2S_MCLK | GP20 | MS1808 + MS4344 MCLK |
| I2S_BCLK | GP16 | 两 Codec BCLK |
| I2S_LRCLK | GP17 | 两 Codec LRCLK |
| I2S_DOUT | GP18 | MS4344 SDIN |
| I2S_DIN | GP9 | MS1808 DOUT |
| BATT_DET | GP26 / ADC0 | 电池分压，Vadc = Vbat × 470/1220 |
| EXP_ADC2 | GP28 | （空闲 AIN2；电源键已迁 C6 IO12） |
| EXP_ADC3 | GP29 | （空闲 AIN3；POW_CTL 已迁 C6 IO13） |
| ENC_A / ENC_B | GP22 / GP27 | EC11（SW→矩阵） |
| IPC_TX | GP4 | C6 UART RX |
| IPC_RX | GP5 | C6 UART TX |
| MIDI_TX | GP0 | MIDI OUT |
| MIDI_RX | GP1 | MIDI IN（光耦后） |
| USB_DP/DM | USB 焊盘 | J1（经 ESD） |

电源 **VBAT / +3V3 / +5V / GND** 见 [sp1_nets.csv](sp1_nets.csv) 与 PMIC 原理图页。

---

## 6. 时钟与 MCLK（已定：方案 A）

- Y1 **12.288 MHz** → `XIN`/`XOUT`（`XOSC_CTRL` 使用 **1–15 MHz** 档，与 Pico 默认 12 MHz 同类）
- **I2S_MCLK**：**GP20（CLK_GPOUT0）** → **12.288 MHz**（48 kHz × 256fs）→ MS1808 / MS4344
- **固件**：`PICO_XOSC_FREQ_HZ=12288000`（或 `board.h` 等价项）；USB 48 MHz 需按 12.288 重算 PLL（`vcocalc.py --input 12.288 48`，常用 **REFDIV=2** 可得精确 48 MHz）

---

## 7. 串口策略

| 链路 | 硬件 UART | 波特率 | 说明 |
|------|-----------|--------|------|
| IPC | UART1 @ GP4/5 | 921600 | 与 [c6_gpio.csv](c6_gpio.csv) UART0 **交叉** |
| DIN MIDI | UART0 @ GP0/1 | 31250 | 板内至 MIDI 座 |
| 调试 | **USB-CDC**（主） | — | J1 → RP2350 |

---

## 8. 固件配置草案（`board.h`）

```c
#define PICO_RP2350A 1

#define FEAHI_UART_IPC     uart1
#define FEAHI_PIN_IPC_TX   4
#define FEAHI_PIN_IPC_RX   5

#define FEAHI_UART_MIDI    uart0
#define FEAHI_PIN_MIDI_TX  0
#define FEAHI_PIN_MIDI_RX  1

#define FEAHI_I2S_PIN_MCLK  20
#define FEAHI_I2S_PIN_BCLK  16
#define FEAHI_I2S_PIN_DOUT  18
#define FEAHI_I2S_PIN_DIN   9

#define FEAHI_PSRAM_CS_GPIO 8

#define FEAHI_NAND_SPI      spi1
#define FEAHI_NAND_PIN_SCK  2
#define FEAHI_NAND_PIN_MOSI 3
#define FEAHI_NAND_PIN_MISO 15
#define FEAHI_NAND_PIN_CS   25
```

---

## 9. 原理图 / ERC 检查清单

- [ ] U1 封装 **QFN-60 RP2350A**
- [ ] U4 W25Q32 QMI CS0；U2 PSRAM CS1@GP8
- [ ] BOOT 键与 QSPI_CSn 同一网络
- [ ] Y1 = 12.288 MHz；SDK/OTP 时钟树（非默认 12 MHz）
- [ ] I2S 至 Codec **等长包地**（同板通常 ≤30 mm 量级）
- [ ] IPC：**RP2350 TX → C6 RX**，交叉
- [ ] USB：**仅 J1 → RP2350**，不经 C6
- [ ] GP26–29 未滥用

---

## 10. 未决项（v0.2 → 冻结）

| # | 项 | 状态 |
|---|-----|------|
| 1 | MCLK | **已定 GP20** |
| 2 | XIP Flash | **已定 W25Q32JVSSIQ** |
| 3 | NAND MPN | **W25N01GVZEIG** |
| 4 | GP23–25 strap | 对照 RP2350 Minimal Viable Board |

---

## 11. 变更记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-09-18 | CORE-B + CBI-40 映射 |
| **v0.2** | **2026-09-19** | **SP-1 单板；§5 改为板内直连** |
