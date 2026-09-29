# RP2350A GPIO 统一规划（v2.0 草案）

> **状态：** 2026-09-23 草案（待你确认后冻结原理图/PCB）  
> **替代：** [rp2350a_gpio.csv](rp2350a_gpio.csv) 中 **v1**（矩阵行占 GPIO26–29）  
> **目标：** 同一表里收齐 **所有 U7 外设**，并 **尽量留出模拟/数字扩展**。

---

## 1. 硬约束（不可挪）

| 资源 | GPIO / 焊盘 | 说明 |
|------|-------------|------|
| XIP Flash | QSPI 专用焊盘 | W25Q32；**BOOTSEL** 与 `QSPI_CSn` 同网 |
| PSRAM CE | **GPIO8** | APS6404L **CS1**（QMI XIP CS1n） |
| USB | USB_DP / USB_DM | J1 |
| SWD | SWCLK / SWDIO | 调试 |
| MIDI | **0, 1** | **UART0** @ 31250（建议保留 HW UART） |
| IPC | **4, 5** | **UART1** @ 921600 ↔ C6（交叉） |
| I2S | **9, 16, 17, 18, 20** | MCLK/BCLK/LRCLK/DOUT/DIN；布局已定则不宜动 |
| Pad 矩阵 | **11 脚** | 6 列输出 + 5 行输入（`MAT_C*` / `MAT_R*`） |
| SAR ADC | **26–29** | 芯片 **AIN0–AIN3**；宜 **仅** 作模拟扩展，不跑矩阵行 |

**C6-MINI-1** 侧编码器 **不能** 占满 strapping 脚 → **EC11 在 U7**（见 [sp1_encoder.md](sp1_encoder.md)）。

---

## 2. 引脚预算（为什么 v1 会占满 ADC）

| 功能块 | 需要 GPIO 数 |
|--------|----------------|
| MIDI + IPC + I2S + PSRAM CS | 2+2+5+1 = **10** |
| Pad 矩阵 | **11** |
| NAND SPI1 | **4** |
| EC11（A/B/SW） | **3**（或 2+矩阵，见 §5） |
| HP 检测 / 功放 Mute（可选） | **0–2** |
| **合计（全要）** | **28–30** → 与 **30 个 Bank0 GPIO** 几乎贴满 |

v1 把 **MAT_R1–R4** 放在 **26–29**，等于把 **4 路 ADC 当普通行线用**，以后 **本机电位器/模拟扩展** 会很难做——你的判断正确。

---

## 3. v2 核心策略

> **勘误（逻辑）：** 初稿写「行迁到 **10–13 + GP25(R0)**」——**GP25 并未腾出**，却又把 **从 26–29 迁出的行** 接到 **25**，与「释放 ADC 脚」并列时容易读成矛盾。**现行定案如下，矩阵行与 GP25 完全脱钩。**

1. **矩阵行** 仅在 **GPIO10–14**（`MAT_R0…R4` 一一对应 **10…14**）。**没有任何 `MAT_R*` 接 GP25。**  
2. **从 26–29 迁出的是 R1–R4（v1）** → v2 落在 **11–14**；**R0（v1 在 GP25）** → v2 落在 **GP10**（不是 GP25）。  
3. **GP25** 专用于 **NAND `#CS`**（与 **2 / 3 / 15** 组成 SPI1），**不是**扩展空闲脚，也**不是**矩阵行。  
4. **腾出给模拟的是 GP26–29（AIN0–3）**，与 GP25 无关。**BATT_DET=26** 仍在 U7；**POW_DET/POW_CTL 已迁 C6 IO12/13**（2026-09-24），**GP28/29** 可作 **EXP_ADC2/3** 或 NC。  
5. **EC11**：占 **2 路 GPIO（A/B）**；**SW** 优先 **并入矩阵空位**（见 §5），少占 1 脚。  
6. **HP_DETECT / SPK_MUTE**：v2 **默认不占 U7 GPIO**（常开 Mute / 检测改 C6 或模拟默认）；若量产必须要，用 **§6 牺牲项** 换回来。

---

## 4. v2 GPIO 总表（推荐冻结）

| GPIO | 网名 / 功能 | 方向 | 连接 | 固件 / 备注 |
|------|-------------|------|------|-------------|
| 0 | MIDI_TX | out | MIDI OUT | UART0 |
| 1 | MIDI_RX | in | MIDI IN | UART0 |
| 2 | NAND_SCLK | out | W25N CLK | SPI1 |
| 3 | NAND_MOSI | out | W25N DI | SPI1 |
| 4 | IPC_TX | out | C6 IPC_RX | UART1 |
| 5 | IPC_RX | in | C6 IPC_TX | UART1 |
| 6 | MAT_C0 | out | 矩阵列 0 | Pad scan |
| 7 | MAT_C1 | out | 矩阵列 1 | |
| 8 | PSRAM_CS | out | APS6404L CE | QMI CS1 |
| 9 | I2S_DIN | in | MS1808 DOUT | PIO I2S |
| 10 | MAT_R0 | in | 矩阵行 0 | 内部上拉 |
| 11 | MAT_R1 | in | 矩阵行 1 | |
| 12 | MAT_R2 | in | 矩阵行 2 | |
| 13 | MAT_R3 | in | 矩阵行 3 | |
| 14 | MAT_R4 | in | 矩阵行 4 | |
| 15 | NAND_MISO | in | W25N DO | SPI1 |
| 16 | I2S_BCLK | out | Codecs BCLK | |
| 17 | I2S_LRCLK | out | Codecs LRCLK | |
| 18 | I2S_DOUT | out | MS4344 SDIN | |
| 19 | MAT_C2 | out | 矩阵列 2 | |
| 20 | I2S_MCLK | out | Codecs MCLK | CLK_GPOUT0 |
| 21 | MAT_C3 | out | 矩阵列 3 | |
| 22 | ENC_A | in | EC11 A | 正交解码 |
| 23 | MAT_C4 | out | 矩阵列 4 | |
| 24 | MAT_C5 | out | 矩阵列 5 | |
| 25 | NAND_CS | out | W25N #CS | SPI1 |
| 26 | **BATT_DET** | in | 电池分压 | **AIN0**；Vadc = Vbat × 470/1220 |
| 27 | **EXP_ADC1** | in | EC11 B 或 DNP | **AIN1**；方案 5a 优先 ENC_B |
| 28 | **EXP_ADC2** | in | （空闲） | AIN2；原 POW_DET→**C6 GPIO12** |
| 29 | **EXP_ADC3** | in | （空闲） | AIN3；原 POW_CTL→**C6 GPIO13** |
| — | ENC_B | in | EC11 B | 见 §5（与 ADC 数量二选一） |
| — | ENC_SW | in | EC11 SW | 见 §5 |

**专用焊盘（非上表 0–29）：** QSPI、USB、XOSC、SWD、RUN。

---

## 5. 编码器 vs 4 路 ADC（必须二选一或折中）

迁出行线后，**真正「空闲」且适合做 enc/ADC 的只有 {22, 26, 27, 28, 29} 共 5 个脚**。电源三线已占用 **26 / 28 / 29**，下表里这三脚的 EXP_ADC 不再可用；编码器仍按 **5a**（A=22，B=27）。

| 方案 | EC11 | EXP_ADC | 说明 |
|------|------|---------|------|
| **5a（推荐量产）** | A=**22**，B=**27**；SW→**矩阵 (row4,col2)** | **26, 28, 29**（**3 路**） | **4 路 ADC 与双通道正交 + 独立 SW 不能同时占满** |
| **5b（偏模拟扩展）** | A=**22**，B=**26**；SW→矩阵 | **28, 29**（**2 路**） | 再让 1 路 ADC |
| **5c（4×ADC 优先）** | **不装 EC11** 或 **仅 C6/UI**（IPC 虚拟旋钮） | **26–29 全开** | 旋钮改屏 + 编码器 DNP |
| **5d（加芯片）** | 外置 I²C/SPI ADC / 多路复用 | 26–29 或 1×ADC+MUX | BOM 成本 ↑，GPIO 压力 ↓ |

**矩阵接 SW（方案 5a/5b）：** 利用 [sp1_key_matrix.csv](sp1_key_matrix.csv) **row4 col2** 空位，EC11 按键 **经二极管按矩阵规则** 接入 `MAT_C2`/`MAT_R4`（与 Choc 相同拓扑），固件把该 cell 映射为 **ENC_SW**，不占额外 GPIO。

---

## 6. 若必须保留 HP / Mute 的牺牲顺序

1. 放弃 **1 路 EXP_ADC**（仍保留 3 路）。  
2. **ENC_SW** 仅用矩阵、不占用 GPIO3。  
3. **Mute** 改 **硬件默认非静音** + 软件增益；**HP** 改 C6 GPIO 或固定插入检测电路到 **C6**。  
4. 最后才考虑 **动 I2S / IPC / MIDI**（不推荐）。

---

## 7. 数字扩展（不占 ADC）

| 接口 | 建议 |
|------|------|
| 更多按键/LED | **C6 I²C**（U18 已有；可加 **0x20–0x27** 类 GPIO 扩展 **DNP**） |
| 更多模拟 | **U7 EXP_ADC*** 或 C6 外接 ADC |
| 第二 SPI / I²C | RP2350 **PIO** 位带；或 C6 第二 I²C（需规划 GPIO） |

---

## 8. v1 → v2 迁移（改板时）

| 项目 | v1 | v2 |
|------|----|----|
| MAT_R0–R4 | 25, **26–29** | **10, 11, 12, 13, 14** |
| NAND SPI | **10–13** | **2, 3, 15, 25**（CS=25） |
| EXP_ADC | （无） | **26–29** |
| ENC | 22, 3, 26（旧表混乱） | **22 + 27**（B）+ 矩阵 SW（见 §5） |
| HP / Mute | 14, 15 | **默认移除**（§6） |

需同步：`core.kicad_sch` / `c6.kicad_sch` 全局标号、`pad_matrix.c`、`sp1_key_matrix.csv` 行 GPIO 列、[rp2350a_interfaces.md](rp2350a_interfaces.md) §8 `board.h` 片段。

---

## 9. 修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v2.0 | 2026-09-23 | 统一外设；矩阵行迁出 ADC；EXP_ADC0–3 |
| v2.1 | 2026-09-23 | GP26/28/29 改为 BATT_DET、POW_DET、POW_CTL |
