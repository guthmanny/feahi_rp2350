# SP-1 IPC（多处理器传输）

**规范版本：** `0.1.0-draft`

当 UI 与 Audio Engine 分布在不同 MCU 时，链路上只传 **[intents.md](intents.md) 意图** 与 **[intents.md#2-反馈状态engine--ui--呈现) 状态]**（及 [voice-and-sample.md](voice-and-sample.md) 中的 **Project/Library 元数据**）。  
**不得** 传输 Flash 命令、DMA 配置、原始 PCM bulk（除非单独的 **Bulk Channel** 且与实时 Intent 分离）。

物理层（UART/USB/BT）与波特率属于 **profile/target**，不在此固定。

## 1. 消息 envelope（逻辑）

| 字段 | 说明 |
|------|------|
| `ver` | spec 版本，当前 `1` |
| `type` | 消息类型名 |
| `seq` | 可选，去重/ACK |
| `payload` | JSON/CBOR/紧凑二进制（实现自选，需版本协商） |

## 2. UI / Host → Engine

| type | payload 要点 | 对应 Intent |
|------|----------------|-------------|
| `PadPress` | `pad_id`, `velocity` | §1.1 |
| `PadRelease` | `pad_id` | §1.1 |
| `PadChoke` | `pad_id` \| `group_id` | §1.1 |
| `ModeSelect` | `mode` | §1.2 |
| `EncoderTurn` | `encoder_id`, `delta` | §1.3 |
| `ControlSet` | `control_id`, `value_norm` | §1.3 |
| `Transport` | `cmd` | §1.4 |
| `ProjectOpen` | `project_ref` | §1.4 |
| `ProjectSave` | `project_ref` | §1.4 |
| `ParamChange` | 见 [fx-catalog.md](fx-catalog.md) | §4 |
| `LibraryImport` | `manifest_ref` only | §1.4 |

## 3. Engine → UI / Host

| type | payload 要点 | 对应 State |
|------|----------------|------------|
| `PadLed` | `pad_id`, `pattern`, `color_index?` | §2.1 |
| `StepLed` | `step_index`, `pattern` | §2.1 |
| `ModeIndicator` | `mode` | §2.2 |
| `TransportState` | `state` | §2.2 |
| `MeterPeak` | `bus_id`, `peak_norm` | §2.2 |
| `Playhead` | `bar`, `step`, `tick` | §2.2 |
| `SampleDone` | `sample_ref`, `pad_id?` | [voice-and-sample.md](voice-and-sample.md) §5 |
| `Error` | `code`, `message?` | §2.3 |

## 4. Bulk / Storage Job（非实时）

大文件（Library 包、固件 OTA 包）**不得** 挤占 Intent 通道。

| type | 方向 | 说明 |
|------|------|------|
| `StorageJobBegin` | UI→Engine | `job_id`, `manifest_ref` |
| `StorageJobProgress` | Engine→UI | `job_id`, `percent` |
| `StorageJobEnd` | Engine→UI | `job_id`, `ok`, `Error?` |

Engine 通过 **Storage Adapter** 写介质；UI 仅见 job 进度。

## 5. 参考实现（非规范）

| Profile | 物理 | 备注 |
|---------|------|------|
| b-c6 模块化 | UART @ CBI-40, 921600 | 历史草案 |
| sp-1 单板 | 板内 UART RP2350↔C6 | 见 [hardware/profiles/sp-1](../hardware/profiles/sp-1/) |

芯片分工（谁跑 Engine、谁跑 UI）见 [docs/architecture.md](../docs/architecture.md) —— **参考架构**，单芯片产品可在同一 MCU 内用队列代替 IPC。

## 6. 版本

| spec | 变更 |
|------|------|
| 0.1.0-draft | Intent/State 命名与 Bulk 分离 |
