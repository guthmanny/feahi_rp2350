# SP-1 原理图框架（单板）

块级原理图 + 网表 CSV，供 KiCad 10 工程 `hardware/kicad/sp-1/` 引用。符号占位，需替换为正式库元件。

## 文件

| 文件 | 说明 |
|------|------|
| [sp1_nets.csv](sp1_nets.csv) | **SP-1 板内网络（主网表）** |
| [c6.kicad_sch](../kicad/sp-1/c6.kicad_sch) | KiCad 子页 **C6**（page 4） |
| [audio.kicad_sch](../kicad/sp-1/audio.kicad_sch) | KiCad 子页 **audio**（page 5） |
| [c6_gpio.csv](c6_gpio.csv) | **ESP32-C6 GPIO 分配（v0.1 冻结）** |
| [sp1_c6_ui.md](sp1_c6_ui.md) | **C6 UI：3729 键灯 + RP2350 GPIO 矩阵（方案 A）** |
| [sp1_rp2350_pad_matrix.md](sp1_rp2350_pad_matrix.md) | **Pad 矩阵 ↔ U7 GPIO / MAT_* 网名** |
| [sp1_encoder.md](sp1_encoder.md) | **EC11 → RP2350 GPIO2/3/22** |
| [sp1_pad_led_map.csv](sp1_pad_led_map.csv) | **20× LTST-C235 键下灯 ↔ 矩阵坐标** |
| [sp1_u18_matrix_9x15.md](sp1_u18_matrix_9x15.md) | **U18 9×15：40 点 SW/CS 与 PWM 分配（连线用）** |
| [sp1_u18_matrix_9x15.csv](sp1_u18_matrix_9x15.csv) | 同上（CSV） |
| [sp1_u16_key_matrix.md](sp1_u16_key_matrix.md) | **已废弃** → 见 [sp1_rp2350_pad_matrix.md](sp1_rp2350_pad_matrix.md) |
| [sp1_key_matrix.csv](sp1_key_matrix.csv) | 5×6 键位 ↔ P00–P05 / P10–P14 |
| [sp1_choc_footprint.md](sp1_choc_footprint.md) | **Choc V2 KiCad 封装（KiSwitch PCM）** |
| [sp1_keycaps.md](sp1_keycaps.md) | **V2 用 MX 矮轴十字键帽（非 MBK 猪鼻子）** |
| [sp1_lcd.md](sp1_lcd.md) | **TFT020B107-C0 + J-LCD FPC 插座（蔚科库）** |
| [rp2350a_gpio.csv](rp2350a_gpio.csv) | **RP2350A GPIO 分配（v2 草案）** |
| [rp2350a_gpio_plan.md](rp2350a_gpio_plan.md) | **U7 外设统一规划 + EXP_ADC** |
| [rp2350a_interfaces.md](rp2350a_interfaces.md) | RP2350A 接口说明（存储 / 串口 / I2S / USB） |
| [coreb_nets.csv](coreb_nets.csv) | **已废弃**（模块化 CORE-B ↔ CBI） |
| [periph1_nets.csv](periph1_nets.csv) | **已废弃**（模块化 PERIPH-1 + CBI） |

## KiCad 工程

| 工程 | 说明 |
|------|------|
| [sp-1](../kicad/sp-1/) | **主工程** `sp-1.kicad_pro` |
| [feahi_cbi40_core](../kicad/feahi_cbi40_core/) | 归档：模块化 Core 模板 |
| [feahi_cbi40_periph](../kicad/feahi_cbi40_periph/) | 归档：模块化 Periph 模板 |

重新生成（仅 CBI 归档模板）：

```powershell
py -3 hardware\kicad\tools\generate_schematic_framework.py
```

## 在 KiCad 中继续

1. 打开 `hardware/kicad/sp-1/sp-1.kicad_pro`
2. 将占位替换为库符号（RP2350、C6-MINI、MS1808、MS4344、FPC…）
3. **Annotate → ERC → 导出网表**，与 `sp1_nets.csv` 核对

## 数据流（核对用）

```
SP-1 单板
RP2350 ──I2S──► MS1808 / MS4344 ──► Mic / TRS / Amp
RP2350 ◄─IPC UART─► C6 ──8080──► TFT020B107
RP2350 ◄─USB-C──► UAC / UF2 / CDC
C6 ──I2C──► IS31FL3729（键灯）
RP2350 ──MAT_*──► 5×6 Choc 矩阵（Pad 触发）
```

## 8080 屏 ↔ C6

详见 [../datasheets/TFT020B107-C0_C6_GPIO.md](../datasheets/TFT020B107-C0_C6_GPIO.md)（GPIO 与 `c6_gpio.csv` 同步）。

## RP2350A 接口

详见 [rp2350a_interfaces.md](rp2350a_interfaces.md)（与 `rp2350a_gpio.csv`、`sp1_nets.csv` 同步）。

## 待原理图阶段确认

| # | 项 | 状态 |
|---|-----|------|
| 1 | C6 GPIO 表 | v0.1 已冻结，打样前复核 strapping |
| 1b | RP2350A GPIO 表 | v0.1 草案，打样前冻结 MCLK/OTP |
| 2 | MS1808 模拟前端（Mic/Line） | 占位，需算阻容 |
| 3 | FPC 连接器 J-LCD | **已定**：`FPC CONNECTOR_26_0.5mm` / `04900-04000-12030`，见 [sp1_lcd.md](sp1_lcd.md) |
| 4 | MIDI 光耦 / TRS 切换 | 占位 |
| 5 | 电池 / 充电 IC | 占位 |
