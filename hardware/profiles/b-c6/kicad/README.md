# FEAHI-CBI-40 KiCad 模板（b-c6 profile）

KiCad **10.x** 模块化 **Core / Periph** 模板；量产单板请用 [../../sp-1/kicad/sp-1.kicad_pro](../../sp-1/kicad/sp-1.kicad_pro)。

机械规格见 [docs/hardware.md](../../../../docs/hardware.md) 中 **FEAHI-CBI-40-MECH v1.0**。

## 工程列表

| 目录 | 说明 | 层数 |
|------|------|------|
| [sp1_cbi40_core/](sp1_cbi40_core/) | CORE-B 原理图 + PCB + CBI 邮票孔 | 4L |
| [sp1_cbi40_periph/](sp1_cbi40_periph/) | PERIPH-1 原理图 + PCB（含 MIDI IN/OUT） | 2L |

## 项目符号库

| 路径 | 说明 |
|------|------|
| [libs/symbols/sp1.kicad_sym](libs/symbols/sp1.kicad_sym) | PCM1808 / MS1808、OR-M611 等 |
| [libs/symbols/integrated_circuits.kicad_sym](libs/symbols/integrated_circuits.kicad_sym) | 单板工程共用 IC 符号 |

搜索：`sp1:OR-M611`、`sp1:MS1808`。

## 重新生成

```powershell
py -3 hardware\profiles\b-c6\kicad\tools\generate_cbi40_templates.py
py -3 hardware\profiles\b-c6\kicad\tools\generate_schematic_framework.py
py -3 hardware\profiles\b-c6\kicad\tools\rebuild_sp1_symbols.py
```
