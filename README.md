# SP-1

Soran **SP-1** 采样器与音序器：**产品定义 + 硬件 profile + 平台实现** 同仓管理。

当前默认实现为 **方案 B-C6**（RP2350 音频 Core + ESP32-C6 UI Periph，CBI-40 互联）。

| 芯片 | 职责 |
|------|------|
| **RP2350** + 8 MB PSRAM | I2S、NAND、Pad/Seq/FX、USB Audio、MIDI |
| **ESP32-C6**（PERIPH-1） | 8080 TFT、键/灯、BLE MIDI、WiFi OTA、IPC |

嵌入式 **FEAHI** 框架与 App 契约在同级目录 `../feahi/`；音频路径从 [feahi_pico](../feahi_pico) 迁移。

## 仓库布局

```
sp-1/                          # 本仓库（GitHub: feahi_rp2350，可改名为 sp-1）
├── docs/                      # 产品架构与硬件说明
├── spec/                      # 与 MCU 无关的契约（IPC 等）
├── hardware/
│   ├── README.md
│   └── profiles/
│       └── b-c6/              # CORE-B + PERIPH-1 参考硬件
│           ├── BOM_IC.csv
│           ├── datasheets/
│           ├── schematic/
│           └── kicad/         # sp1_cbi40_core / sp1_cbi40_periph
└── targets/
    └── rp2350-c6/             # Pico SDK + ESP-IDF 实现
        ├── rp2350_sound/
        ├── c6_host/
        └── feahi_port/        # FEAHI Port（随板变化）
```

## 设计约束（B-C6）

1. **NAND 只接 RP2350** — C6 经 IPC 请求读写  
2. **USB Audio 在 RP2350**  
3. **I2S / Codec 只接 RP2350**  
4. **C6**：BLE MIDI + WiFi OTA（无 Classic / A2DP）  
5. **IPC**：UART @ CBI-40，921600 baud — 见 [spec/ipc.md](spec/ipc.md)  
6. **8080 屏**与 C6 同在 PERIPH-1  

## 依赖

- [Pico SDK](https://github.com/raspberrypi/pico-sdk) ≥ 2.2.0（RP2350）
- [ESP-IDF](https://docs.espressif.com/projects/esp-idf/) ≥ 5.2（ESP32-C6）
- 同级目录 `../feahi/`、`../qdsp/`

## 构建

> 脚手架阶段。详见 [targets/rp2350-c6/README.md](targets/rp2350-c6/README.md)。

```powershell
cd targets/rp2350-c6/rp2350_sound
# .\build.ps1 -Clean

cd ..\c6_host
# idf.py build
```

## KiCad

打开：`hardware/profiles/b-c6/kicad/sp1_cbi40_periph/sp1_cbi40_periph.kicad_pro`  
项目符号库：`sp1.kicad_sym`（搜索 `sp1:OR-M611`）。若升级 KiCad 全局库表，请指向本仓 `hardware/profiles/b-c6/kicad/libs/symbols/sp1.kicad_sym`。

## 文档

- [架构说明](docs/architecture.md)
- [硬件模块化](docs/hardware.md)
- [B-C6 硬件 profile](hardware/profiles/b-c6/README.md)
- [Pad / Seq 契约](../feahi/docs/)（FEAHI 仓库）
