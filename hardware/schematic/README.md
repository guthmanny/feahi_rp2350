# SP-1 原理图框架（方案 C）

块级原理图 + 网表 CSV，供 KiCad 10 工程引用。符号占位，需替换为正式库元件。

## 文件

| 文件 | 说明 |
|------|------|
| [c6_gpio.csv](c6_gpio.csv) | **ESP32-C6 GPIO 分配（v0.1 冻结）** |
| [coreb_nets.csv](coreb_nets.csv) | CORE-B ↔ CBI 网络 |
| [periph1_nets.csv](periph1_nets.csv) | PERIPH-1 板内 + CBI 网络 |

## KiCad 工程

| 工程 | 根原理图 | 子页 |
|------|----------|------|
| [feahi_cbi40_core](../kicad/feahi_cbi40_core/) | `feahi_cbi40_core.kicad_sch` | `sheets/core_*.kicad_sch` |
| [feahi_cbi40_periph](../kicad/feahi_cbi40_periph/) | `feahi_cbi40_periph.kicad_sch` | `sheets/periph_*.kicad_sch` |

重新生成：

```powershell
py -3 hardware\kicad\tools\generate_schematic_framework.py
```

## 在 KiCad 中继续

1. 打开对应 `.kicad_pro`
2. 进入各 **子页**，将文字占位替换为库符号（RP2350、C6-MINI、MS1808、MS4344、FPC…）
3. 回到根页，对每个 **Sheet Symbol** 右键 → **Import Sheet Pins**
4. 用导线 / 标签连接各块（同名 hierarchical label 已预置）
5. **Annotate → ERC → 导出网表**

## 数据流（核对用）

```
CORE-B                          PERIPH-1
RP2350 ──I2S──► CBI ──► MS1808/MS4344 ──► Mic/TRS/Amp
RP2350 ◄─IPC UART─► CBI ◄─► C6 ──8080──► TFT020B107
C6 ──I2C──► TCA8418 / IS31FL3733 (板内)
```

## 8080 屏 ↔ C6

详见 [../datasheets/TFT020B107-C0_C6_GPIO.md](../datasheets/TFT020B107-C0_C6_GPIO.md)（GPIO 与 `c6_gpio.csv` 同步）。

## 待原理图阶段确认

| # | 项 | 状态 |
|---|-----|------|
| 1 | C6 GPIO 表 | v0.1 已冻结，打样前复核 strapping |
| 2 | MS1808 模拟前端（Mic/Line） | 占位，需算阻容 |
| 3 | FPC 连接器型号 | 依 TFT 规格书 pitch |
| 4 | MIDI 光耦 / TRS 切换 | 占位 |
| 5 | 电池 / 充电 IC | 占位 |
