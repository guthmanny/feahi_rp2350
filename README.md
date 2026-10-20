# SP-1

Soran **SP-1** 采样器与音序器：**产品语义（平台无关）** + **硬件 profile** + **参考 target**。

| 芯片（参考单板） | 职责 |
|------------------|------|
| **RP2350** + PSRAM | 音频引擎、存储、Pad/Seq/FX、USB Audio、MIDI |
| **ESP32-C6** | 8080 UI、键/灯、BLE/WiFi、IPC（可选拆分） |

## 规范 vs 实现

| 层级 | 位置 | 移植时要什么 |
|------|------|----------------|
| **SP-1 操作语义** | **[spec/](spec/)** | Intent/State、样本 ref、FX 目录、IPC  envelope |
| **App / 框架** | 同级 `../feahi/` | FEAHI Port + Pad/Seq 实现契约 |
| **本板接线** | [hardware/profiles/](hardware/) | binding（Pad/LED/GPIO） |
| **参考固件** | [targets/rp2350-c6/](targets/rp2350-c6/) | Pico SDK + ESP-IDF 示例 |

**SP-1 的行为**（按下 Pad 触发什么、灯怎么表示状态、工程/样本如何引用）由 **spec** 定义；**NAND 还是 NOR、3729 还是 PWM** 由你的 target 决定。

> 规范版本：`spec/` **0.1.0-draft**。参考硬件/固件不代表规范的一部分。

嵌入式框架：[FEAHI](../feahi/) · 音频迁移参考：[feahi_pico](../feahi_pico)

## 仓库布局

```
├── spec/                 # ★ 产品契约（平台无关）
├── docs/                 # 架构说明（含参考实现分工）
├── hardware/profiles/    # sp-1 单板 · b-c6 模板
└── targets/rp2350-c6/    # 参考 target
```

## 设计约束（参考单板 SP-1）

1. Engine 握样本存储；UI 不直接擦写 Flash（见 [spec/voice-and-sample.md](spec/voice-and-sample.md)）  
2. USB Audio 在 Engine 侧（当前 profile）  
3. IPC 仅传 Intent/State（见 [spec/ipc.md](spec/ipc.md)）  
4. 键/灯语义见 [spec/intents.md](spec/intents.md)  

细节与 GPIO 草案：[docs/hardware.md](docs/hardware.md)

## 依赖（参考 target）

- Pico SDK ≥ 2.2.0 · ESP-IDF ≥ 5.2  
- `../feahi/`、`../qdsp/`

## 构建

```powershell
cd targets/rp2350-c6/rp2350_sound
# cmake / build.ps1

cd ..\c6_host
# idf.py build
```

## KiCad

| Profile | 工程 |
|---------|------|
| 单板 | [hardware/profiles/sp-1/kicad/sp-1.kicad_pro](hardware/profiles/sp-1/kicad/sp-1.kicad_pro) |
| CBI-40 模板 | [sp1_cbi40_periph](hardware/profiles/b-c6/kicad/sp1_cbi40_periph/sp1_cbi40_periph.kicad_pro) |

## 文档

- [spec 索引](spec/README.md) · [架构](docs/architecture.md) · [硬件](docs/hardware.md)  
- [Pad/Seq（FEAHI）](../feahi/docs/)
