# SP-1 KiCad 工程

KiCad **10.x** 硬件源文件。

## 主工程（量产）

| 目录 | 说明 |
|------|------|
| **[sp-1/](sp-1/)** | **SP-1 单板** — `sp-1.kicad_pro`（原理图 + PCB） |

根页子图：`MIDI` · `core` · **`C6`**（`c6.kicad_sch`）· **`audio`**（`audio.kicad_sch`，MS1808/MS4344/功放）

硬件说明：[docs/hardware.md](../../docs/hardware.md) · 网表：[../schematic/sp1_nets.csv](../schematic/sp1_nets.csv)

## 项目符号库

| 路径 | 说明 |
|------|------|
| [libs/symbols/feahi.kicad_sym](libs/symbols/feahi.kicad_sym) | **PCM1808** / **MS1808**（TSSOP-14 ADC）、**OR-M611**（SO-5 MIDI 光耦） |
| [libs/symbols/integrated_circuits.kicad_sym](libs/symbols/integrated_circuits.kicad_sym) | **SGM8276/8278**、**W25Q32JVSSIQ** 等（git 跟踪） |
| `sp-1/sym-lib-table` | **双库 IC**：见下表 |

### 符号库双库（`sp-1/sym-lib-table`）

| 库名 | 路径 | 用途 |
|------|------|------|
| **`Integrated_circuits_feahi`** | `${KIPRJMOD}/../libs/symbols/integrated_circuits.kicad_sym` | 工程已用、蔚科库缺失或需版本固定的 IC（**SGM8276/8278** 等） |
| **`Integrated_circuits`** | 本机蔚科 `Integrated_circuits.kicad_sym`（默认 `~/kicad/library/…`） | 全库选元件；`MP2637`、`MS1808` 等仍用 `Integrated_circuits:…` |
| **`feahi`** | `libs/symbols/feahi.kicad_sym` | 项目专用符号 |
| **`MCU_RaspberryPi`** | `sp-1/mcu_raspberrypi.kicad_sym` | RP2350 |

新同事：克隆仓库即可解析 **feahi** 库；蔚科全库路径在 `sym-lib-table` 第二行按本机修改。缺符号时优先 **import 进 `integrated_circuits.kicad_sym`** 并改 `lib_id` 为 `Integrated_circuits_feahi:…`。

## 已废弃（模块化 CBI-40，仅归档）

| 目录 | 说明 |
|------|------|
| [feahi_cbi40_core/](feahi_cbi40_core/) | 原 CORE-B 模板 + CBI 邮票孔 |
| [feahi_cbi40_periph/](feahi_cbi40_periph/) | 原 PERIPH-1 模板 |
| [cbi40_pinout.csv](cbi40_pinout.csv) | 历史引脚表，**新设计勿引用** |

打开归档工程：**File → Open Project** → 对应 `.kicad_pro`。

重新生成 CBI 模板（一般不需要）：

```powershell
py -3 hardware\kicad\tools\generate_cbi40_templates.py
py -3 hardware\kicad\tools\generate_schematic_framework.py
```

## SP-1 单板布局要点

1. **Board Setup**：推荐 **4 层**，1.6 mm  
2. **USB-C J1** → ESD → RP2350；VBUS → PMIC；与 C6 天线区隔离  
3. **C6 + TFT FPC** 相邻，8080 走线短  
4. **RP2350 ↔ Codec** I2S 等长包地；模拟区靠板边  
5. DRC → Gerber
