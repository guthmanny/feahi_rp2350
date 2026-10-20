# SP-1

Soran **SP-1** 采样器与音序器：**产品定义 + 硬件 profile + 平台实现** 同仓管理。

| 芯片 | 职责 |
|------|------|
| **RP2350** + 8 MB PSRAM | I2S、NAND、Pad/Seq/FX、USB Audio、MIDI |
| **ESP32-C6** | 8080 TFT、键/灯、BLE MIDI、WiFi OTA、IPC |

嵌入式 **FEAHI** 框架与 App 契约在同级目录 `../feahi/`；音频路径从 [feahi_pico](../feahi_pico) 迁移。

## 仓库布局

```
sp-1/                              # GitHub 仓库名仍为 feahi_rp2350，可改名
├── docs/                          # 架构与硬件说明
├── spec/                          # IPC 等产品契约
├── hardware/
│   ├── README.md
│   └── profiles/
│       ├── sp-1/                  # ★ 量产单板 KiCad（主工程）
│       └── b-c6/                  # 模块化 CBI-40 参考（Core + Periph 模板）
└── targets/
    └── rp2350-c6/                 # Pico SDK + ESP-IDF
        ├── rp2350_sound/         # 含 Pad 矩阵脚手架（scheme A）
        ├── c6_host/
        └── feahi_port/
```

## 设计约束（B-C6 · 单板 SP-1）

1. **NAND 只接 RP2350** — C6 经 IPC 请求读写  
2. **USB Audio 在 RP2350** — 板边 **USB-C**  
3. **I2S / Codec 只接 RP2350** — C6 不走音频数据  
4. **C6**：BLE MIDI + WiFi OTA（无 Classic / A2DP）  
5. **IPC**：板内 UART，921600 baud — [spec/ipc.md](spec/ipc.md)  
6. **8080 屏**仅接 C6  
7. **C6 UI I²C** — TCA9555（Choc 矩阵）+ IS31FL3729（Pad 灯）；见 [hardware/profiles/b-c6/schematic/sp1_c6_ui.md](hardware/profiles/b-c6/schematic/sp1_c6_ui.md)

## 依赖

- [Pico SDK](https://github.com/raspberrypi/pico-sdk) ≥ 2.2.0  
- [ESP-IDF](https://docs.espressif.com/projects/esp-idf/) ≥ 5.2  
- 同级 `../feahi/`、`../qdsp/`

## 构建

```powershell
cd targets/rp2350-c6/rp2350_sound
# cmake / build.ps1（见 CMakeLists.txt）

cd ..\c6_host
# idf.py build
```

## KiCad

| Profile | 工程 |
|---------|------|
| **单板（主）** | [hardware/profiles/sp-1/kicad/sp-1.kicad_pro](hardware/profiles/sp-1/kicad/sp-1.kicad_pro) |
| **CBI-40 模板** | [sp1_cbi40_periph](hardware/profiles/b-c6/kicad/sp1_cbi40_periph/sp1_cbi40_periph.kicad_pro) |

符号库：`hardware/profiles/b-c6/kicad/libs/symbols/sp1.kicad_sym`、`integrated_circuits.kicad_sym`（搜索 `sp1:OR-M611` 等）。

## 文档

- [架构](docs/architecture.md) · [硬件方案](docs/hardware.md)  
- [单板 profile](hardware/profiles/sp-1/) · [B-C6 模块化 profile](hardware/profiles/b-c6/README.md)  
- [Pad / Seq 契约](../feahi/docs/)
