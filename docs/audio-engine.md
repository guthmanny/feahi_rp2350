# SP-1 音频引擎（软件分层）

PC 端所有面向最终用户的 app（bleach 及后续）以 **kbuss** 为音频引擎。  
硬件端产品（SP-1 及后续板）共用 **同一套 kbuss 宿主**，不要再造平行引擎。

## 分层

```
PC app（bleach / …）
  → kbuss（track 串接、混音、参数、MIDI、对 NuDSP 的 C++ 封装）
    → NuDSP（f32 算法单元）

SP-1 / 踏板 / 后续硬件
  → feahi（I2S、UAC、GPIO、存储、IPC）
    → kbuss AudioEngine + StaticPluginFormat（图在 init 里搭死）
      → PadSampler / FX / 合成器 Processor
        → NuDSP
```

| 层 | 仓库 | 职责 |
|---|---|---|
| 算法 | NuDSP | EG、sample player、voice、滤波等 `nx_*_f32`。MCU 与 PC 同一份 C 单元。 |
| 宿主 | kbuss | track / insert 链、通道混合、MIDI 分发、参数表、合成器与 pad 引擎（`PadSampler`）。板上用 `EmbeddedFrontend` + `embedded_host`。 |
| HAL / 板级 | feahi + SP-1 固件 | codec、USB、按键、NAND、屏、BLE。不实现混音或 DSP。 |

## 板上约束

- 只用 **StaticPluginFormat**，不上 `.kbplug`、不上 plugin scanner。
- 图在 `kbuss_host_init` 时建好，**实时线程不改拓扑**。
- I2S / UAC 边缘保持整数（Q31/S32）；内部 float32。
- 缺算法就改 NuDSP，用 CMake 裁模块（`NUDSP_EMBEDDED` / 只编 SSMEL 子集），不要 `extensions/nudsp_embedded`。
- RP2350 扛不住完整 `AudioEngine` 时，在 **kbuss 里瘦宿主**（固定 track 数、无 scanner），不要另起 `ebuss`。

## 现状与目标

`rp2350_sound/src/feahi_pad.c` 是整数 bring-up，**不是**产品音频引擎。浮点路径应对齐 bleach：kbuss 嵌入式宿主 + 静态 `PadSampler` + NuDSP。

## 不要做

- 在 NuDSP 里做混音、track、合成器产品架构
- 在 feahi 里再写一套宿主
- 新建与 kbuss 平行的嵌入式引擎去「对应」PC
- 把 `sample_player` / EG 再抄一份给 MCU
- 把 kbuss 动态插件图搬上 MCU
