# FEAHI-CBI-40 KiCad 模板

KiCad **10.x** 机械模板，对应 [docs/hardware.md](../../docs/hardware.md) 中的 **FEAHI-CBI-40-MECH v1.0**。

> PCB 格式：`version 20260206`，KiCad 10 网表为 `(net "name")` 按名引用，无顶层 `(net 0 "")` 列表。

## 工程列表

| 目录 | 说明 | 层数 |
|------|------|------|
| [feahi_cbi40_core/](feahi_cbi40_core/) | CORE-B 原理图框架 + PCB 外形 + CBI 邮票孔 | 4L |
| [feahi_cbi40_periph/](feahi_cbi40_periph/) | PERIPH-1 原理图框架 + PCB + CBI 焊盘 | 2L |

原理图网表与 C6 GPIO：[../schematic/README.md](../schematic/README.md)

## 项目符号库

| 路径 | 说明 |
|------|------|
| [libs/symbols/feahi.kicad_sym](libs/symbols/feahi.kicad_sym) | **PCM1808** / **MS1808**（TSSOP-14 ADC）、**OR-M611**（SO-5 MIDI 光耦） |
| `feahi_cbi40_*/sym-lib-table` | 工程已链接上述库 |

原理图按 **`A`** 搜索 `feahi:OR-M611`、`feahi:MS1808` 或 `feahi:PCM1808`。

从参考 sch 重新提取符号：

```powershell
py -3 hardware\kicad\tools\extract_pcm1808_symbol.py
```

## 打开方式

1. 安装 [KiCad 10](https://www.kicad.org/download/)（或 9.x 可能需升级文件格式）  
2. **File → Open Project** → 选择对应目录下的 `.kicad_pro`  
3. 打开 **PCB Editor** 查看板框与 `J1`（CBI-40）

## 板内对象

| 位号 | 内容 |
|------|------|
| **J1** | CBI-40：Core 为底边邮票孔 + 内排 PTH；Periph 为顶面 SMD 焊盘 |
| **MH** | 4× M2 定位孔 (3,3) (47,3) (3,33) (47,33) mm |
| **Edge.Cuts** | 50×36 mm，左上 1.5 mm 防呆切角 |
| **Dwgs.User** | Periph 上 Core Bay 50×36 禁布参考框 |

## 坐标系

- 原点 **(0,0)**：板 **左下角**（邮票孔底边）
- **Pin 1**：左下外排，丝印 `Pin1 ◄`，焊盘方角（Core pad 1 rect）
- 视图：Core 编辑时建议看 **Bottom** 层（邮票孔面）

## 重新生成

修改引脚表或尺寸后：

```powershell
py -3 hardware\kicad\tools\generate_cbi40_templates.py
py -3 hardware\kicad\tools\generate_schematic_framework.py
```

## 下一步（在模板基础上）

### Core 板

1. **Board Setup → Physical Stackup**：确认 4 层与厚度 1.6 mm  
2. 放置 RP2350 / S3 / NAND / USB-C（**无 C6、无 LCD**）  
3. 自 **J1** 拉线；I2S + IPC UART 等长 ±3 mm  
4. 确认 **Edge.Cuts 底边** 穿过外排邮票孔中心（castellation）  
5. DRC → Gerber；备注 `castellated half-hole on bottom edge`

### Periph 板

1. **J1 焊盘区禁止器件**（高度 ≤ 0.5 mm）  
2. **C6 + TFT FPC** 相邻，8080 走线 ≤15 mm（**不经过 J1**）  
3. MS1808/MS4344 放在 J1 前方 ≤15 mm，I2S 直线连接  
4. 功放远离 I2S / 8080 ≥8 mm  

## 引脚表

见 [cbi40_pinout.csv](cbi40_pinout.csv)。

## 与 PCB 厂沟通

```
Board: FEAHI-CBI-40 Core / Periph
Thickness: 1.6 mm +/- 0.12 mm
Core bottom edge: plated half-holes (castellation), 20 pads, 2.54 mm pitch
Finish: ENIG
```
