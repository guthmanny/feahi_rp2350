# SP-1 效果目录（FX Catalog）

定义 **有哪些效果、参数范围、插入点**；**不** 规定 qdsp、biquad 实现或 CPU 占用。

## 1. 插入点（Bus）

| `bus_id` | 说明 |
|----------|------|
| `pad` | 单 Pad 链（每 Pad 可配置 chain_id） |
| `group` | Pad 组总线 |
| `master` | 主输出前 |
| `cue` | 监听/耳机（若产品支持） |

Engine 将 `TriggerVoice.fx_chain_id` 路由到对应 bus。

## 2. 效果类型（v0.1）

| `fx_type_id` | 名称 | 典型用途 |
|--------------|------|----------|
| `gain` | Gain | 电平 |
| `filter_lp_hp` | Filter | 低/高通、共振 |
| `eq_3band` | 3-Band EQ | 音色 |
| `compressor` | Compressor | 动态 |
| `delay` | Delay | 延迟 |
| `reverb` | Reverb | 空间 |
| `bitcrush` | Bitcrush |  lo-fi |
| `bypass` | Bypass | 占位/直通 |

Target 通过 **capability** 声明支持哪些 `fx_type_id`；不支持时 `PARAM_CHANGE` 返回 `Error{FX_NOT_SUPPORTED}`。

## 3. 参数 schema

每个 `fx_type_id` 有固定 **参数槽**（逻辑名 → 归一化或物理单位）。

### 示例：`filter_lp_hp`

| param_id | 范围 | 默认 | UI 显示 |
|----------|------|------|---------|
| `cutoff_hz` | 20…20000 | 1000 | Hz（UI 可 log 映射） |
| `resonance` | 0.0…1.0 | 0.1 | Q |
| `mode` | 0=LP, 1=HP | 0 | 枚举 |

### 示例：`delay`

| param_id | 范围 | 默认 |
|----------|------|------|
| `time_ms` | 1…2000 | 250 |
| `feedback` | 0.0…1.0 | 0.3 |
| `mix` | 0.0…1.0 | 0.25 |

**规范要求：** 序列化工程时按 `param_id` + 类型存储；**不要求** 不同 target 参数内部表示一致。

## 4. 参数变更意图

与 [intents.md](intents.md) 对齐：

| 意图 | 字段 |
|------|------|
| `ParamChange` | `target`: `pad` \| `fx_slot` \| `master` |
| | `pad_id` 或 `fx_slot_id` |
| | `param_id`, `value` |

UI 旋钮 → `ControlSet` → 映射为 `ParamChange`。

## 5. 效果链配置

| 概念 | 说明 |
|------|------|
| `fx_chain_id` | 0…255，Pad 或工程预设引用 |
| `chain` | 有序 `fx_slot[]`，每 slot：`fx_type_id` + 参数快照 |

链深度上限由 target **capability** 报告（如 `max_fx_slots_per_chain=4`）。

## 6. 实现绑定

| 实现 | 归属 |
|------|------|
| qdsp / 自建 DSP | `targets/*` 或用户工程 |
| 无 FX | `bypass` 或空 chain |
| 桌面插件 | 非 SP-1 v0.1 范围，可扩展 `fx_type_id` 命名空间 |

## 7. 版本

| spec | 变更 |
|------|------|
| 0.1.0-draft | 初版类型表与 schema 约定 |
