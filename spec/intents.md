# SP-1 意图与反馈（Intents & Feedback）

平台无关：**用户/UI 侧只产生「意图」；引擎侧只发布「状态」**。  
物理键、Pad、编码器、BLE MIDI 等必须先映射为下列类型（见 [binding-template.md](binding-template.md)）。

## 1. 输入意图（UI → Engine）

### 1.1 Pad

| 意图 | 字段 | 说明 |
|------|------|------|
| `PadPress` | `pad_id` 0…N-1, `velocity` 0…127 | 按下；是否复音由 Engine 策略决定 |
| `PadRelease` | `pad_id`, `release_vel` 可选 | 释放；支持 aftertouch 的平台可扩展 |
| `PadChoke` | `pad_id` 或 `group_id` | 同组静音（实现方式不在此规范） |

`pad_id` 为 **逻辑 Pad**，与矩阵坐标、GPIO 无关。

### 1.2 功能键 / 模式键

| 意图 | 字段 | 说明 |
|------|------|------|
| `ModeSelect` | `mode` 见下表 | 切换全局模式 |
| `FnPress` / `FnRelease` | `fn_id` | Shift/Alt 层；与 Pad 组合时由 Engine 解释 |

**`mode` 枚举（v0.1）**

| 值 | 含义 |
|----|------|
| `play` | 演奏 / 触发 Pad |
| `seq` | 音序编辑或步进输入 |
| `sample` | 采样输入武装 |
| `settings` | 系统/工程设置（UI 主导） |

### 1.3 编码器 / 连续控制

| 意图 | 字段 | 说明 |
|------|------|------|
| `EncoderTurn` | `encoder_id`, `delta` | 增量；UI 可加速 |
| `EncoderClick` | `encoder_id` | 按下 |
| `ControlSet` | `control_id`, `value_norm` 0.0…1.0 | 绝对值（Pot、推子） |

`control_id` 绑定到当前焦点（Pad 参数、Master、FX slot），由 UI 状态机维护。

### 1.4 传输 / 工程

| 意图 | 字段 | 说明 |
|------|------|------|
| `Transport` | `cmd`: `start` \| `stop` \| `continue` \| `record_arm` | 音序/采样传输 |
| `ProjectOpen` | `project_ref` | 逻辑工程 ID（见 [voice-and-sample.md](voice-and-sample.md)） |
| `ProjectSave` | `project_ref` | 请求持久化 |
| `LibraryImport` | `manifest_ref` | **仅元数据**； bulk 数据走 Storage Job |

### 1.5 外部 MIDI（可选）

| 意图 | 说明 |
|------|------|
| `MidiNoteOn/Off` | 可映射到 `PadPress/Release` 或专用 voice 路由 |
| `MidiCC` | 映射到 `ControlSet` |

## 2. 反馈状态（Engine / UI → 呈现）

呈现层（LED、屏、RGB）只订阅状态，不假设驱动芯片。

### 2.1 Pad / 步进灯

| 状态 | 字段 | 说明 |
|------|------|------|
| `PadLed` | `pad_id`, `pattern` | 见 **LED pattern** |
| `StepLed` | `step_index`, `pattern` | 音序步进指示 |

**LED pattern（v0.1）**

| pattern | 用户含义 |
|---------|----------|
| `off` | 灭 |
| `dim` | 待命 / 未选中 |
| `on` | 选中 / 正在响 |
| `pulse` | 录音武装、等待输入 |
| `blink_fast` | 错误 / .clip |
| `blink_slow` | 同步/等待 |

颜色：若硬件支持多色，增加 `color_index`（profile 定义 palette）；单色机忽略。

### 2.2 全局 / 模式

| 状态 | 说明 |
|------|------|
| `ModeIndicator` | 当前 `mode` |
| `TransportState` | `stopped` \| `playing` \| `recording` |
| `MeterPeak` | `bus_id`, `peak_norm` 0.0…1.0 |
| `Playhead` | `bar`, `step`, `tick`（UI 用，非音频时钟） |

### 2.3 错误

| 状态 | 字段 |
|------|------|
| `Error` | `code`, `message_optional` |

`code` 为产品级枚举（存储满、资源缺失、FX 不支持等），与 errno/驱动无关。

## 3. 优先级（UI 合并规则）

1. `Error` / `blink_fast` 覆盖 Pad 显示  
2. `TransportState=recording` 时 Pad `pulse` 优先于 `dim`  
3. 同 Pad 同时 `on`（发声）与 `StepLed`：profile 可配置 **发声优先** 或 **步进优先**

## 4. 与 FEAHI 的边界

- FEAHI 侧实现 **任务/事件投递** 与 Pad 引擎 API。  
- 本文件定义 **SP-1 产品可见** 的 intent/state 名称与语义。  
- 映射示例：`PadPress` → FEAHI `pad_trigger`；具体函数名以 `../feahi/docs/pad-contract.md` 为准。

## 5. 版本

| spec | 变更 |
|------|------|
| 0.1.0-draft | 初版：Pad/Mode/Transport/LED pattern |
