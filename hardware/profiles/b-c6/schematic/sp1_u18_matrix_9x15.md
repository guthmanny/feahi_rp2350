# U18 IS31FL3729 — 9×15 Pad 灯矩阵分配（40 点）

> **状态：** 与 **`c6.kicad_sch` 网表一致**（2026-09-22 核对）  
> **模式：** Configuration **A0h `SWS = 0000`** → **SW1–9 × CS1–15**（9×15）；本板 **SW1–6、CS1–8**  
> **符号：** **CAx = 手册 SWx**，**CBx = 手册 CSx**

## 接法（LTST-C235 ↔ U18，以当前原理图为准）

| LTST 脚 | 3729 | U18 符号 | 分配规则 |
|---------|------|----------|----------|
| **A1、A2** | **SW** | **CAx** | **x = col + 1**（与同键 Choc 列对齐） |
| **K1**（R 阴） | **CS** | **CBx** | **x = row × 2 + 2**（偶数 CS 轨） |
| **K2**（G 阴） | **CS** | **CBx** | **x = row × 2 + 1**（奇数 CS 轨） |

同一键 **R/G 共 SW、不同 CS** → 2 个 PWM 点。  
**A1/A2 可共网**（同 SW 母线）；**K1/K2 必须分属不同 CS 母线**。

### 原理图母线（`c6.kicad_sch` 实际网名）

KiCad 未用 `U18_SWn` 全局名，而是 **按 SW/CS 汇流**：

| 母线 | 连接的 D_PAD（A1/A2） | U18 |
|------|------------------------|-----|
| 同 **SW1** | 01, 07, 13, 19 | CA1 |
| 同 **SW2** | 02, 08, 14, 20 | CA2 |
| … | col+1 | CA3…CA6 |
| **CS 偶数轨**（K1 / R） | row0: 01–06；row1: 07–12；… | CB2, CB4, CB6, CB8 |
| **CS 奇数轨**（K2 / G） | 同上 | CB1, CB3, CB5, CB7 |

固件 **只认下表 PWM**；`PADxx_R/G` 为 LED 侧网络别名，与 **K1/K2** 对应。

## 分配公式

键位 **(row, col)**（0-based，`sp1_pad_led_map.csv`）：

- **SW** = col + 1  
- **R（K1）→ CS** = row × 2 + 2  
- **G（K2）→ CS** = row × 2 + 1  

## PWM 寄存器（15×9，Fig.9）

`scan_index(SW)`：1→0, 2→1, 4→2, 3→3, 5→4, 6→5, 8→6, 7→7, 9→8  

**`pwm_reg = CS + scan_index(SW) × 16`** → 写入 **01h–8Fh**。

## 按键汇总（固件查表）

| 键 | D_PAD | R K1→SW–CS (CA–CB) | PWM R | G K2→SW–CS | PWM G |
|----|-------|---------------------|-------|------------|-------|
| 1 | D_PAD01 | SW1–CS2 (CA1–CB2) | 0x02 | SW1–CS1 | 0x01 |
| 2 | D_PAD02 | SW2–CS2 (CA2–CB2) | 0x12 | SW2–CS1 | 0x11 |
| 3 | D_PAD03 | SW3–CS2 (CA3–CB2) | 0x32 | SW3–CS1 | 0x31 |
| 4 | D_PAD04 | SW4–CS2 (CA4–CB2) | 0x22 | SW4–CS1 | 0x21 |
| 5 | D_PAD05 | SW5–CS2 (CA5–CB2) | 0x42 | SW5–CS1 | 0x41 |
| 6 | D_PAD06 | SW6–CS2 (CA6–CB2) | 0x52 | SW6–CS1 | 0x51 |
| 7 | D_PAD07 | SW1–CS4 (CA1–CB4) | 0x04 | SW1–CS3 | 0x03 |
| 8 | D_PAD08 | SW2–CS4 (CA2–CB4) | 0x14 | SW2–CS3 | 0x13 |
| 9 | D_PAD09 | SW3–CS4 (CA3–CB4) | 0x34 | SW3–CS3 | 0x33 |
| 10 | D_PAD10 | SW4–CS4 (CA4–CB4) | 0x24 | SW4–CS3 | 0x23 |
| 11 | D_PAD11 | SW5–CS4 (CA5–CB4) | 0x44 | SW5–CS3 | 0x43 |
| 12 | D_PAD12 | SW6–CS4 (CA6–CB4) | 0x54 | SW6–CS3 | 0x53 |
| A | D_PAD13 | SW1–CS6 (CA1–CB6) | 0x06 | SW1–CS5 | 0x05 |
| B | D_PAD14 | SW2–CS6 (CA2–CB6) | 0x16 | SW2–CS5 | 0x15 |
| C | D_PAD15 | SW3–CS6 (CA3–CB6) | 0x36 | SW3–CS5 | 0x35 |
| D | D_PAD16 | SW4–CS6 (CA4–CB6) | 0x26 | SW4–CS5 | 0x25 |
| REC | D_PAD17 | SW5–CS6 (CA5–CB6) | 0x46 | SW5–CS5 | 0x45 |
| PLAY | D_PAD18 | SW6–CS6 (CA6–CB6) | 0x56 | SW6–CS5 | 0x55 |
| PATTERN | D_PAD19 | SW1–CS8 (CA1–CB8) | 0x08 | SW1–CS7 | 0x07 |
| SAMPLE | D_PAD20 | SW2–CS8 (CA2–CB8) | 0x18 | SW2–CS7 | 0x17 |
| **SHIFT** | **D30** | **SW7–CS9 (CA7–CB9)** | **0x79** | — | — | 层指示；**0402 单色** A→CA7 K→CB9 |

40 行明细 + Shift：**[sp1_u18_matrix_9x15.csv](sp1_u18_matrix_9x15.csv)**  
按键一行摘要：**[sp1_pad_led_map.csv](sp1_pad_led_map.csv)**

## U18 配置

1. **A0h `SWS=0000`**（9×15）  
2. **AD → VCC**，I²C **0x37**  
3. **~{SDB}** 高；**R_EXT/ISET** ≈ **10k**；**VCC** 去耦  
4. **CA7/CB9** 已用于 **D30 Shift**；**CA8–9、CB10–15** 仍 NC  

## 修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-09-22 | 初版 9×15 分配 |
| v1.1 | 2026-09-22 | **与 c6 网表对齐**：K1(R)→偶数 CS，K2(G)→奇数 CS；更新 PWM |
