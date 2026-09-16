# feahi_rp2350

Soran **SP-1** 采样器与音序器固件工程，采用 **方案 B-C6** 双芯片架构：

| 芯片 | 职责 |
|------|------|
| **RP2350** + 8 MB PSRAM | 音频引擎：I2S、NAND 样本、Pad/Seq/FX、USB Audio、MIDI |
| **ESP32-C6**（PERIPH-1） | UI 与连接：2" **8080** TFT、按键/LED、BLE MIDI、WiFi OTA、上位机 |

本仓库负责 **板级 Port + 双固件构建 + 芯片间 IPC**；框架与 App 契约在同级目录 `../feahi/`。

音频路径从 [feahi_pico](../feahi_pico) 迁移，UI/连接为新建。

## 目录结构

```
feahi_rp2350/
├── README.md
├── docs/
│   └── architecture.md       # B-C6 架构与 IPC 约定
├── feahi_port/               # RP2350 Port 层（HAL、tick、QP 移植）
│   └── pal/
├── rp2350_sound/             # RP2350 音频固件（CMake + main）
│   └── src/
└── c6_host/                  # ESP32-C6 搭档固件（ESP-IDF）
    └── main/
```

## 设计约束（B-C6）

1. **NAND 只接 RP2350** — C6 通过 IPC 请求读写
2. **USB Audio 在 RP2350** — 与 feahi_pico 一致
3. **I2S / Codec 只接 RP2350** — C6 不参与音频数据路径
4. **C6 无线** — BLE MIDI + WiFi OTA（无 Bluetooth Classic / A2DP）
5. **IPC** — UART 经 CBI-40（RP2350 ↔ C6），实时事件延迟 < 1 ms
6. **方案 C** — 量产屏 TFT020B107 为 8080 并口，C6 与屏在 PERIPH-1，不跨板

## 依赖

- [Pico SDK](https://github.com/raspberrypi/pico-sdk) ≥ 2.2.0（RP2350）
- [ESP-IDF](https://docs.espressif.com/projects/esp-idf/) ≥ 5.2（ESP32-C6）
- 同级目录 `../feahi/`、`../qdsp/`

## 构建

> 脚手架阶段，构建脚本待补充。参考 `../feahi_pico/pico_sound/build.ps1`。

```powershell
# RP2350 音频固件
cd rp2350_sound
# .\build.ps1 -Clean

# ESP32-C6 搭档固件
cd ../c6_host
# idf.py build
```

## 硬件

模块化 **核心板（4L）+ 外围板（2L）**，邮票孔 CBI-40 连接：

| 板 | 说明 |
|----|------|
| **CORE-B** | RP2350 + PSRAM + NAND + USB（纯音频数字，量产） |
| **CORE-A** | ESP32-S3 + NAND + USB（A 方案对照） |
| **PERIPH-1** | **C6 + 8080 屏** + MS1808/MS4344 + 键 / 功放 / 电池（固定） |

详见 [docs/hardware.md](docs/hardware.md)。  
硬件目录：[hardware/](hardware/)（[原理图框架](hardware/schematic/) · [规格书 PDF](hardware/datasheets/) · [KiCad](hardware/kicad/)）。

## 相关文档

- SP-1 产品设计任务书 V1.1.0
- [硬件模块化方案](docs/hardware.md)
- [feahi_pico 播放路径](../feahi_pico/docs/play-path.md)
- [Pad 契约](../feahi/docs/pad-contract.md)
- [音序器契约](../feahi/docs/seq-contract.md)
