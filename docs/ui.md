# SP-1 UI（AtomTheme × LVGL）

bleach 与 SP-1 **画面不同**，只共享底层音频（kbuss + NuDSP）和 feahi 公共契约。  
两边都用 AtomTheme，但后台不同：bleach 走 **JUCE**，SP-1 走 **LVGL**。

## 分层

```
AtomTheme
  core/                 主题、几何、PadGridBase、Painter（无 GUI 框架）
  modules/juce_…        bleach 等 PC 插件 UI
  backends/lvgl/        SP-1 产品 UI（PC 仿真 + 硬件同一套控件）

SP-1 产品界面（本仓库 ui/，不进 AtomTheme、不进 bleach）
  屏幕 / 导航 / 与 IPC·feahi 的绑定
    ├── ui_sim/：PC 上 LVGL + SDL，分辨率与屏一致
    └── c6_*：同一套屏幕 + 显示/输入适配（PARLIO ST7789、键 IPC）
```

## 仓库位置

仿真不是独立产品，是 **同一份屏幕** 的第二个构建目标。放在 SP-1 仓库里，不要放进 AtomTheme、bleach 或 `rp2350_sound`。

```
feahi_rp2350/
├── ui/            SP-1 屏幕库（AtomTheme LVGL 控件 + 导航 + 契约绑定）
├── ui_sim/        PC 可执行文件：LVGL + SDL、mock IPC、可选接 kbuss
├── c6_led_bringup/  （过渡）硬件 bring-up；产品固件吃 ui/
└── c6_host/       C6 产品固件：只留显示驱动、键灯、无线、IPC
```

- `ui/`：纯屏幕，不链 SDL，不链 PARLIO。桌面 CMake 库；C6 用 IDF 组件包一层同一批源文件。
- `ui_sim/`：桌面 `main`、窗口。实体键/旋钮见 [panel.md](./panel.md)，画在 `ui_sim/shell/`，**不要**画进 `ui/`。
- 硬件固件只换 display/input/tick。

不要：AtomTheme `demos/`（那是控件示例）、bleach 里加 SDL 窗、在 `c6_led_bringup` 里塞桌面 target。

| | bleach | SP-1 |
|---|---|---|
| 产品 UI | JUCE `PluginEditor` + `atom::PadGrid` | LVGL 屏幕 + `atom::lvgl_widgets::PadGrid` |
| AtomTheme | JUCE 后端 | LVGL 后端 |
| 音频 | kbuss → NuDSP | 板上 kbuss → NuDSP（见 [audio-engine.md](./audio-engine.md)） |
| 契约 | feahi pad/seq 等 | 同一套 feahi 契约，**不是**同一套屏幕树 |

## PC 仿真 → 硬件

「无缝移植」指 **同一份 SP-1 屏幕源码** 链两套显示后端，不是在 JUCE 里画完再翻到 LVGL。

- 仿真目标：AtomTheme 已有先例（`AtomLvglScopeDemo` SDL ↔ ESP32 LVGL demo）。
- 仿真窗口 = 硬件屏几何（当前 320×240）和色深（RGB565），LVGL 主版本与 C6 一致。
- 板上只换：显示驱动、输入（触摸/键 IPC）、tick。控件与布局不改。
- 屏幕代码放 SP-1 UI 模块，**不要**写进 AtomTheme core（core 是控件包）。

## 现状与目标

`c6_led_bringup/main/ui.c` 是手写 LVGL 格子（TAL 色板对齐），**不是** AtomTheme `PadGrid`。产品 UI 应换成 `backends/lvgl` 控件；C6 需能编 AtomTheme 的 C++17。

## 不要做

- 把 bleach 的 JUCE 编辑器搬上 SP-1，或把 SP-1 屏幕搬进 bleach
- 用 JUCE 仿真 SP-1 再「移植」到 LVGL（多一层后端，无法无缝）
- 在 C6 再实现一套 PadGrid / 主题，与 AtomTheme `core/` 分叉
- 让 UI 直接依赖 kbuss 图拓扑；UI 只通过 feahi 契约和 IPC 说话
