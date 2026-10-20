# Target: RP2350 + ESP32-C6（B-C6）

本目录为 **SP-1** 在 **方案 C** 硬件上的平台实现（Pico SDK + ESP-IDF）。

| 目录 | 说明 |
|------|------|
| [rp2350_sound/](rp2350_sound/) | CORE-B 音频固件（CMake，待接 Pico SDK） |
| [c6_host/](c6_host/) | PERIPH-1 UI/连接固件（ESP-IDF） |
| [feahi_port/](feahi_port/) | RP2350 **FEAHI Port** 层（HAL、tick、QP 移植） |

## 依赖

- [Pico SDK](https://github.com/raspberrypi/pico-sdk) ≥ 2.2.0
- [ESP-IDF](https://docs.espressif.com/projects/esp-idf/) ≥ 5.2
- 同级仓库：`../feahi/`、`../qdsp/`（框架与 DSP）
- 音频迁移参考：`../feahi_pico/`

## 构建（脚手架）

```powershell
cd rp2350_sound
# .\build.ps1 -Clean

cd ..\c6_host
# idf.py build
```

硬件 profile：[../../hardware/profiles/b-c6/](../../hardware/profiles/b-c6/)
