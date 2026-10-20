# SP-1 IPC（RP2350 ↔ C6）

UART 经 **CBI-40**（Pin 18–19），**921600 baud**。大文件（Library 导入）由 RP2350 写 NAND，C6 只传元数据。

## C6 → RP2350

| 消息 | 说明 |
|------|------|
| `PAD_TRIGGER` | pad_index, group, velocity |
| `SEQ_TRANSPORT` | start / stop / continue |
| `PARAM_CHANGE` | pad/FX 参数 |
| `LOAD_PROJECT` | project_id |
| `SAVE_PROJECT` | project_id |

## RP2350 → C6

| 消息 | 说明 |
|------|------|
| `METER_PEAK` | 电平表 |
| `PLAYHEAD_POS` | 步进 / 小节位置 |
| `SAMPLE_DONE` | 采样完成 |
| `ERROR` | 错误码 |

详细架构见 [docs/architecture.md](../docs/architecture.md)。
