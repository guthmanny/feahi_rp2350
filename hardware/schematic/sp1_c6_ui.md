# SP-1 UI：Pad 矩阵 + C6 屏/灯（v1.3）

> **状态：** v1.3（2026-09-23）  
> **Pad 触发：** **RP2350 U7 GPIO** 直扫（方案 A，MPC 级延迟）— 见 **[sp1_rp2350_pad_matrix.md](sp1_rp2350_pad_matrix.md)**  
> **C6：** 8080 + LVGL、**IS31FL3729** 键下灯、I²C、IPC（UI 慢路径）

## 架构

```text
RP2350 U7 ── MAT_C0…5 / MAT_R0…4 ── c6 页：26× Choc + D3…28（全局网名）
         └── Pad 引擎 / I2S（实时触发，不经 UART）

C6 GPIO6/7 (I2C) ── U18 IS31FL3729 ── 20× D_PAD（R+G）
C6：8080、IPC ↔ RP2350（**编码器在 U7**，见 [sp1_encoder.md](sp1_encoder.md)）
```

| 子系统 | 位置 | 固件 |
|--------|------|------|
| **Choc 矩阵** | c6 原理图 + **core U7 GPIO** | **RP2350** `pad_matrix.c` @ 5 kHz |
| **Pad 灯** | c6 **U18** | **C6** 3729 PWM |
| **UI / 连接** | **U9** C6 | LVGL、WiFi/BLE、可选 IPC 状态 |

## I²C（仅 U18，C6 GPIO6/7）

- **400 kHz**；**R72/R73 = 4.7 kΩ** 上拉至 **`3.3VD`**。  
- **IS31FL3729 U18：** **0x37**（AD → VCC）。

## 键矩阵（RP2350）

| 项 | 说明 |
|----|------|
| 拓扑 | **5×6**，26 键；**列─\|>─开关─行**；**MAT_*** 全局网至 U7 |
| GPIO | **MAT_C0…5 → 6,7,19,21,23,24**；**MAT_R0…4 → 10–14**；**GP25=NAND_CS**（v2） |
| 键位 | **[sp1_key_matrix.csv](sp1_key_matrix.csv)** |
| Choc | **Kailh Choc V2**；**sp1_keycaps.md** |

## 电源键（C6 GPIO12/13）

- **POW_DET → IO12**：低有效；**R69** 上拉 **3.3VD**（Q2 与 K1 检测侧隔离）。
- **POW_CTL → IO13**：高有效，经 **R36 → D2 → U15 MODE (19)** 与 **K1** 路径 **OR**；**R35** 对地下拉。
- **硬件按住 K1**：**K1-2 接 VBAT**；按下时 **K1-1 ≈ VBAT → R37 → D2/1 → MODE**（与 **POW_CTL → D2/2** 并联到阴极）；松键后须 **IO13 保持** 或系统掉电。
- **RP2350 GP28/29** 已释放；关机/长按在 **C6**，RP2350 经 **IPC** 配合。
- C6 须 early **`gpio_config` IO12/13**，关 **USB Serial/JTAG**（console 走 UART0/IPC）。

## Pad 灯（U18）

同 v1.2：**20× LTST-C235KGKRKT**；**sp1_pad_led_map.csv**、**sp1_u18_matrix_9x15.md v1.1**。

## Shift 指示灯（D30 → U18）

- **D30**（**0402 单色 LED**，`Discrete parts:LED0402`）接 **U18 CA7（SW7）× CB9（CS9）**；**A→CA7，K→CB9**。
- 固件经 **3729 I²C** 写 PWM **`0x79`**（与键下灯同一驱动）；**IO5/GPIO5 不再使用**。
- 矩阵 **SHIFT** 键仍由 **RP2350** 扫描；此灯为 **C6 侧锁存/层指示**。

## 面板电位器（core 页）

- **VR1 / VR2**（10kΩ）→ **U7 GP28 / GP29（ADC）**；两端 **3.3VD–GNDA**，**C75/C76 100n** 滤波。

## 相关文件

- [sp1_rp2350_pad_matrix.md](sp1_rp2350_pad_matrix.md)  
- [sp1_encoder.md](sp1_encoder.md)  
- [rp2350a_gpio.csv](rp2350a_gpio.csv)  
- [c6_gpio.csv](c6_gpio.csv)  
- [rp2350_sound/src/pad_matrix.c](../../rp2350_sound/src/pad_matrix.c)  

## 修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.8 | 2026-09-24 | **D30 改为 0402 单色 LED**（仍 U18 SW7×CS9） |
| v1.7 | 2026-09-24 | **D30 Shift → U18 SW7×CS9**；**GPIO5 释放** |
| v1.6 | 2026-09-24 | **POW_DET/POW_CTL → C6 IO12/13**；I²C 上拉文档 **3.3VD** |
| v1.5 | 2026-09-24 | I²C 上拉 **R72/R73 → 3.3VD** |
| v1.4 | 2026-09-23 | 编码器迁至 RP2350（[sp1_encoder.md](sp1_encoder.md)） |
| v1.3 | 2026-09-23 | **方案 A：** 移除 TCA9555；矩阵接 RP2350 GPIO |
| v1.2 | 2026-09-22 | 3729 与 c6 网表对齐 |
| v1.0 | 2026-09-22 | 初版 TCA9555 + 3729 |
