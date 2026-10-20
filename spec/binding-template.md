# Profile Binding 模板

**Binding** 把物理世界映射到 [intents.md](intents.md) / [intents 反馈](intents.md#2-反馈状态engine--ui--呈现)。  
每个 [hardware profile](../hardware/README.md) 应提供 `binding.md`（或等价 CSV + 说明）。

## 1. 必须声明的内容

| 章节 | 内容 |
|------|------|
| Pad 矩阵 | 物理位置 → `pad_id` |
| 功能键 | 键位 → `fn_id` / `ModeSelect` |
| 编码器 | `encoder_id` → 默认 `control_id` 映射 |
| Pad LED | `pad_id` → 逻辑 `PadLed` 槽（驱动可以是 IS31FL3729、PWM、屏上绘制） |
| 能力缺失 | 若无步进灯，声明 `StepLed` 由 UI 屏代替 |

## 2. 表示例（逻辑）

```yaml
# 片段示例 — 非正式语法，profile 可用 CSV/Markdown 表
pads:
  - pad_id: 0
    label: "A1"
    source: matrix[0,0]   # 或 gpio_bank: U7, pin: 12
    led_slot: pad_led[0]

encoders:
  - encoder_id: 0
    turn: EncoderTurn
    click: EncoderClick
    default_control: master_volume

modes:
  - key: FN+PAD1
    intent: ModeSelect(mode=seq)
```

**禁止** 在 binding 里写 Engine 内部行为（例如「读 NAND 扇区 0x1000」）。

## 3. 参考 binding

| Profile | 文档 |
|---------|------|
| SP-1 单板 | [sp1_pad_led_map.csv](../hardware/profiles/b-c6/schematic/sp1_pad_led_map.csv)、[sp1_rp2350_pad_matrix.md](../hardware/profiles/b-c6/schematic/sp1_rp2350_pad_matrix.md)、[sp1_c6_ui.md](../hardware/profiles/b-c6/schematic/sp1_c6_ui.md) |

上述文件偏 **硬件网名**；后续可收敛为各 profile 根目录下的 `binding.md` 并链接 CSV。

## 4. Target 声明（固件）

`targets/<name>/README.md` 应列出：

- 使用的 profile binding 版本  
- Storage Adapter 后端（例：SPI NAND、仅 SD 仿真）  
- FX capability 列表（见 [fx-catalog.md](fx-catalog.md)）  
- 是否拆分 UI/Engine 进程（若拆分，使用 [ipc.md](ipc.md)）
