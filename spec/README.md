# SP-1 产品规范

**规范版本：** `0.1.0-draft`（2026-09）

本目录定义 **SP-1 的操作语义与状态模型**，与 MCU、Flash 类型、具体 GPIO/驱动无关。  
硬件如何把物理输入/输出映射到这些语义，见各 [hardware profile](../hardware/README.md) 下的 **binding** 文档。

## 文档索引

| 文档 | 说明 |
|------|------|
| [intents.md](intents.md) | 输入意图、反馈状态、模式与优先级 |
| [voice-and-sample.md](voice-and-sample.md) | 发声请求、样本/工程资源 ID、存储适配边界 |
| [fx-catalog.md](fx-catalog.md) | 效果类型与参数 schema（非 DSP 实现） |
| [ipc.md](ipc.md) | 多处理器时 **Intent / State** 的传输契约 |
| [binding-template.md](binding-template.md) | Profile 如何声明 Pad/LED/键位映射 |

## 与 FEAHI 的关系

| 层 | 负责方 |
|----|--------|
| **SP-1 产品语义** | 本目录 `spec/` |
| **App / 组件 API** | 同级 [FEAHI](../README.md#依赖)（`../feahi/`，Pad/Seq 等实现契约） |
| **平台实现** | 本仓 `targets/*` + 用户自选栈；存储、I2S、矩阵扫描等 **不得** 写入 spec |

移植 SP-1：**实现 spec 中的 Intent/State + FEAHI Port（或等价调度层）+ profile binding** 即可；不必复制 RP2350+C6 原理图。

## 成熟度

| 状态 | 含义 |
|------|------|
| `draft` | 语义已定方向，字段/枚举可能变更 |
| `frozen` | Breaking change 需升 spec 主版本 |

当前全部为 **draft**。参考硬件：[profiles/sp-1](../hardware/profiles/sp-1/) · 参考固件：[targets/rp2350-c6](../targets/rp2350-c6/)。
