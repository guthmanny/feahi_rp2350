# SP-1 发声与样本资源

规范 **「播放什么」** 与 **「资源如何引用」**；不规定 NAND/NOR/SD、缓存大小或预读算法。

## 1. 核心请求

| 请求 | 说明 |
|------|------|
| `TriggerVoice` | 一次发声意图，通常由 `PadPress` 或音序器步进产生 |
| `ReleaseVoice` | 对应释放或 choke |
| `PreviewSample` | UI 试听（低优先级，可打断） |

### TriggerVoice 逻辑字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `voice_id` | opaque | Engine 分配，用于 Release/Choke |
| `pad_id` | u8 | 逻辑 Pad |
| `sample_ref` | string | 见 §2 |
| `velocity` | 0…127 | |
| `pitch_semitones` | float 可选 | Pad 微调 |
| `group_id` | u8 可选 | Choke 组 |
| `fx_chain_id` | u8 可选 | 见 [fx-catalog.md](fx-catalog.md) |

Engine **不得** 要求 UI 提供物理扇区、Flash 厂商或 DMA 描述符。

## 2. 资源引用（sample_ref / project_ref）

统一为 **逻辑路径或 UUID**，与存储介质无关。

| 形式 | 示例 | 说明 |
|------|------|------|
| 工程内相对路径 | `pads/03/main.wav` | 工程打包内 |
| 库 ID | `lib:factory:808_kick` | 预置库 |
| UUID | `550e8400-e29b-41d4-a716-446655440000` | 导入后稳定 ID |

**Project** 为命名容器：`project_ref` 例如 `projects/live_set_01` 或 UUID。

持久化格式（文件布局、压缩）由 **Storage Adapter** 定义；SP-1 spec 只要求：

- 给定 `sample_ref`，Adapter 能提供 **只读 byte stream** 或 **已解码 PCM 块句柄**
- 缺失资源时返回 `Error{code=RESOURCE_NOT_FOUND}`

## 3. Storage Adapter（平台实现）

Adapter 在 target 层实现，对上暴露抽象能力：

| 能力 | 说明 |
|------|------|
| `open_read(ref) → stream` | 流式读；可 mmap、可 cache |
| `open_write(ref) → stream` | 采样写入、Library 导入 |
| `enumerate(project_ref) → refs[]` | 工程列表 |
| `sync_job(job_id)` | 大文件导入/备份；**异步** |

**禁止** 在 IPC/UI 协议中传递「擦除块」「SPI 命令」等细节。  
`LibraryImport` 意图只带 `manifest_ref`；bulk 由 `sync_job` 在 Engine 与 Adapter 之间完成。

参考 profile 当前选用 SPI NAND —— 见 [hardware](../hardware/README.md)，**非规范要求**。

## 4. Voice 生命周期（语义）

```
TriggerVoice → Active → (ReleaseVoice | Choke | NaturalEnd) → Idle
```

- **NaturalEnd**：样本播放完毕或 one-shot 结束  
- **Choke**：同 `group_id` 或 `PadChoke` 意图  
- 复音上限、steal 策略：Engine 配置，不在 spec 固定

## 5. 采样（Record）语义

| 阶段 | UI 状态 | Engine 行为 |
|------|---------|-------------|
| Arm | `TransportState=recording` 或 Pad `pulse` | 分配 `record_target_ref` |
| Capture | 输入电平 → `MeterPeak` | 写入 Adapter（格式由 Adapter/工程定义） |
| Done | `SampleDone` 状态 + 新 `sample_ref` | UI 绑定到 Pad |

输入源（Mic/Line/USB）为 **profile/target** 能力声明，不在此枚举硬件。

## 6. 与 FEAHI / feahi_pico

Pad 引擎、voice 池、Flash 预取属于 **FEAHI / 音频 target** 实现。  
本文件约束 **对外语义**；实现迁移时保持 `sample_ref` 与 `TriggerVoice` 字段稳定即可。

## 7. 版本

| spec | 变更 |
|------|------|
| 0.1.0-draft | 初版：ref 模型、Adapter 边界 |
