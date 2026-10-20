# Pad 键矩阵 → RP2350 GPIO（方案 A，v1.0）

> **状态：** 2026-09-23 冻结  
> **目标：** MPC 级触发 — Pad 检测与采样引擎同在 **RP2350**，不经 C6 / UART。  
> **Choc + 二极管拓扑不变**；**U16 TCA9555 已自原理图移除**。

## 架构

```text
c6 页：SW1…26 + D3…28 + D_PAD* → U18（仅灯）
         │
         │ 全局网 MAT_C0…5 / MAT_R0…4（板内走线）
         ▼
core 页：U7 RP2350 GPIO 直扫矩阵 → Pad 引擎 / I2S
C6：I²C 仅 U18（3729）；8080 / LVGL / IPC（UI，非 Pad 热路径）
```

## GPIO 分配（U7）

| 矩阵 | 网名 | RP2350 GPIO | QFN 脚号（符号） |
|------|------|-------------|-----------------|
| 列 0 | **MAT_C0** | GPIO6 | 9 |
| 列 1 | **MAT_C1** | GPIO7 | 10 |
| 列 2 | **MAT_C2** | GPIO19 | 31 |
| 列 3 | **MAT_C3** | GPIO21 | 33 |
| 列 4 | **MAT_C4** | GPIO23 | 35 |
| 列 5 | **MAT_C5** | GPIO24 | 36 |
| 行 0 | **MAT_R0** | GPIO10 | 14 |
| 行 1 | **MAT_R1** | GPIO11 | 15 |
| 行 2 | **MAT_R2** | GPIO12 | 16 |
| 行 3 | **MAT_R3** | GPIO13 | 17 |
| 行 4 | **MAT_R4** | GPIO14 | 18 |

> **v2：** 五行 **连续 GP10–14**；**GP25 = NAND_CS**（矩阵不占 25）；**GP26–29 = EXP_ADC**（见 [rp2350a_gpio_plan.md](rp2350a_gpio_plan.md)）。QFN 脚号以符号为准。

键位 ↔ `(row,col)` 仍见 **[sp1_key_matrix.csv](sp1_key_matrix.csv)**。

## 电气（与 ex-U16 方案相同）

- **列 MAT_Cy**：RP2350 **输出**，扫描时逐列 **拉低**（其余列高）。
- **行 MAT_Rx**：RP2350 **输入**，**内部上拉**。
- **二极管：** `MAT_Cy ──|>|── SW ── MAT_Rx`，**阴极靠列**（SOD-323 D3…D28）。

## 固件（RP2350）

- 模块：`rp2350_sound/src/pad_matrix.c`（5 kHz 扫描、短消抖、note on/off 回调）。
- **Core1** 扫描 + **Core0** 音频/Pad 引擎（见 `pad_matrix.h`）。
- **不再**经 IPC 发送 `PAD_TRIGGER` 做实时触发；C6 可选接收 **UI 同步**（慢路径，后续 IPC 扩展）。

## 原理图

- **c6.kicad_sch：** 矩阵 + 全局标号 `MAT_*`；无 U16 / R_I2C_INT / C_U19。
- **core.kicad_sch：** `MAT_*` 接 U7 对应 GPIO。

## 修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.2 | 2026-09-23 | 矩阵行 **仅 GP10–14**；GP25=NAND_CS（曾误写 R0→25） |
| v1.1 | 2026-09-23 | （已作废）矩阵行 GPIO10–13/25 |
| v1.0 | 2026-09-23 | 自 TCA9555+C6 迁移至 RP2350 GPIO |
