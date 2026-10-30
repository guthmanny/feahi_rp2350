# SP-1 前面板（按键 / 旋钮 / 灯）

机械键和旋钮 **不是屏幕的一部分**。板上：RP2350 GPIO 扫描 5×6 矩阵 + EC11，C6 只画 320×240 和键下灯。  
PC 仿真必须保持这条边界：不要把实体键画进 `ui/` 的 LVGL 帧缓冲。

## 分层

```
panel/                 前面板模型（无 GUI）：pad 0–25、ENC_SW=26、encoder Δ/click、LED
  ├── 硬件：rp2350_sound pad_matrix.c / encoder.c
  └── PC：同一套事件，由 sim 机壳或键盘注入

ui/                    仅 TFT 画面（C6 与 ui_sim 共用）
ui_sim/shell           仅 PC：SDL 机壳（键帽、旋钮、LED），中间嵌 320×240 LCD
```

事件走向与硬件相同：

```
键 / 旋钮 → panel 事件 → 音频引擎（kbuss）
                      → IPC 语义 → ui（亮格、选中）
                      → LED 状态 → 机壳灯（PC）或 IS31FL3729（板）
```

屏上 `PadGrid` 是 **显示**，不是 5×6 机械矩阵。点屏格子只适合调 UI；仿真真实操控应走 panel 事件（机壳点击或键盘映射）。

## 仓库位置

| 内容 | 放哪 | 不放哪 |
|---|---|---|
| pad/encoder/LED 状态与事件 | `panel/`（语义对齐 `pad_matrix.h`） | AtomTheme、`ui/`、bleach |
| 机壳可视化 + 鼠标/键盘 | `ui_sim/shell/`（只链进 `sp1_ui_sim`） | `ui/`、C6 固件 |
| TFT 画面 | `ui/` | 机壳 |

可执行文件仍是一个：`ui_sim` 做成「机壳窗口 + 内嵌 LCD」，不要为旋钮再开第二个工程。

机壳按 PCB 分组（非电气 5×6 外观）：4×4 Choc（SW1–16 = 1–12/A–D）、右侧 REC/PLAY/PATTERN/SAMPLE、上方 SAMPLES…SHIFT、EN1 TEMPO、RV1/RV2。LED 为 SW1–20 双色 + SHIFT D30。

## 不要做

- 在 320×240 LVGL 里加仿真专用的大旋钮/额外按键（板上没有这些像素）
- 把 GPIO 扫描抄进 AtomTheme
- 让 `ui/` 直接读 SDL 键盘；屏幕只收 panel/IPC 已经规范过的事件
