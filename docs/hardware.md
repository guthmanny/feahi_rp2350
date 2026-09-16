# SP-1 模块化硬件方案

## 设计目标

| 目标 | 做法 |
|------|------|
| 核心板纯音频数字、可互换 | 4 层 **核心板** 放 RP2350/S3 + NAND + USB |
| UI + 模拟靠近接口 | 2 层 **外围板** 放 **C6 + 8080 屏** + MS1808/MS4344 + 功放 |
| 可对比 A/B 主控方案 | 核心板可互换，**PERIPH-1 固定（含 C6 + 屏）** |
| 开发阶段灵活 | 邮票孔（Castellation）叠焊 |

```
                    ┌─────────────────────┐
                    │   CORE-B 或 CORE-A  │  4-layer，纯音频数字
                    │  RP2350/S3+NAND+USB │
                    └──────────┬──────────┘
                               │ 邮票孔 CBI-40 v0.3
                               │  I2S + IPC UART + MIDI …
                    ┌──────────┴──────────┐
                    │     PERIPH-1        │  2-layer
                    │ C6 + 8080 LCD       │  ← 屏与 UI 不跨板
                    │ MS1808/4344 + 键/功放│
                    └─────────────────────┘
```

---

## 板级定义

| 板名 | 层数 | 职责 | SKU |
|------|------|------|-----|
| **CORE-B** | 4L | RP2350 + APS6404L + NAND + USB | 量产首选 |
| **CORE-A** | 4L | ESP32-S3 N16R8 + NAND + USB | A 方案对照 |
| **PERIPH-1** | 2L | **C6 + TFT020B107 8080 屏** + MS1808/MS4344 + 键/功放/电池 | 固定，含 UI |

> 核心板外形、邮票孔位置、定位孔 **完全一致**，仅板内器件不同。  
> **Codec 固定在外围板**，A/B 对照时模拟前端完全一致。

---

## 核心板 vs 外围板分工

### 核心板（4 层）—「纯音频数字」（方案 C）

| 器件 | 说明 |
|------|------|
| **音频 MCU** | CORE-B：**RP2350** + APS6404L；CORE-A：**ESP32-S3** N16R8 |
| **NAND** | W25N01GV（1Gb SPI NAND），SPI/QSPI 接音频 MCU |
| **USB-C** | USB 2.0 OTG（UAC / 烧录） |
| **24.576 MHz 晶振** | I2S MCLK → CBI |
| **LDO** | 3.3 V → CBI +3V3 供外围逻辑 |

**核心板不再放置：** ESP32-C6、LCD、MS1808/MS4344、按键、功放。

### 外围板（2 层）—「UI + 模拟 + 接口」（方案 C）

| 器件 | 说明 |
|------|------|
| **ESP32-C6-MINI** | LVGL、8080 屏、I2C 键灯、BLE/WiFi、IPC 从机 |
| **2" TFT** | **TFT020B107-C0**，ST7789P3，**8080 8-bit 并口**，仅接 C6 |
| **MS1808** | ADC，Mic/Line → I2S_DIN → CBI |
| **MS4344** | DAC，CBI I2S_DOUT → 模拟 → Volume → 功放/TRS |
| **5 W 功放** | Class-D |
| **按键 + LED** | TCA8418 + IS31FL3733 → **C6 I2C（板内）** |
| **编码器 / 电源键** | 接 **C6 GPIO（板内）** |
| **TRS / MIDI 插座** | 模拟/串口在板内；MIDI UART **经 CBI** 接 Core |
| **电池 + 充电 USB-C** | PMIC，VBAT 上送 Core |

8080 屏连接草案：[hardware/datasheets/TFT020B107-C0_C6_GPIO.md](../hardware/datasheets/TFT020B107-C0_C6_GPIO.md)

**方案 C 理由（量产屏 TFT020B107 为 8080，不可换）：**

1. **8080 屏 13+ GPIO 不跨 CBI**，C6 与 FPC 同板最短  
2. DAC/ADC 模拟链与功放同板  
3. 换 CORE-A/B 时 **Periph（含 C6+屏）不变**，A/B 对照公平  
4. Core 仅 RP2350/S3 + NAND，面积更小  

---

## 板间连接：CBI-40 v0.3（方案 C）

### 跨板 vs 板内

| 信号 | 跨 CBI | 说明 |
|------|--------|------|
| I2S ×5 | ✅ | RP2350/S3 ↔ MS1808/MS4344 |
| IPC UART ×2 | ✅ | RP2350/S3 ↔ **C6** |
| MIDI UART ×2 | ✅ | Core ↔ MIDI 插座 |
| DEBUG UART | ✅ | 可选 |
| 电源 | ✅ | VBAT, +3V3, +5V, GND |
| HP_DETECT / SPK_MUTE | ✅ | |
| **8080 LCD** | ❌ | C6 ↔ FPC，**板内** |
| **I2C 键/灯** | ❌ | C6 ↔ TCA8418/IS31，**板内** |
| **编码器 / 电源键** | ❌ | C6 **板内** |

### 规格摘要

| 参数 | 值 |
|------|-----|
| 名称 | **FEAHI-CBI-40**（项目内标准） |
| 形式 | 2×20 邮票孔，2.54 mm |
| Core 外形 | **50.0 × 36.0 mm**，1.6 mm 厚 |
| 定位 | 4× M2（Ø2.0 mm）+ 左上角缺角防呆 |
| 机械详情 | 见下节 **[FEAHI-CBI-40 机械规格](#feahi-cbi-40-机械规格v10-草案)** |

---

## CBI-40 引脚定义（v0.3 — 方案 C）

| Pin | 信号 | 方向 (Core→Periph) | 说明 |
|-----|------|-------------------|------|
| 1 | VBAT | IN | 电池 3.0–4.2 V |
| 2 | VBAT | IN | 并联 |
| 3 | +5V | IN | Periph 升压 |
| 4 | +3V3 | OUT | Core → C6 / MS1808 / MS4344 数字 |
| 5–8 | GND | — | I2S 回流 |
| 9 | I2S_MCLK | OUT | 24.576 MHz |
| 10 | I2S_BCLK | OUT | |
| 11 | I2S_LRCLK | OUT | |
| 12 | I2S_DOUT | OUT | → MS4344 |
| 13 | I2S_DIN | IN | ← MS1808 |
| 14 | HP_DETECT | IN | TRS 插入 |
| 15 | SPK_MUTE | OUT | 静音喇叭 |
| 16–17 | NC | — | 预留 |
| 18 | IPC_TX | OUT | **RP2350/S3 → C6 RX** |
| 19 | IPC_RX | IN | **C6 TX → RP2350/S3** |
| 20 | C6_BOOT | IO | C6 下载 / strap |
| 21 | MIDI_TX | OUT | |
| 22 | MIDI_RX | IN | |
| 23 | DEBUG_TX | OUT | RP2350/S3 调试 |
| 24 | DEBUG_RX | IN | |
| 25 | AUD_BOOT | IO | RP2350 BOOTSEL（CORE-A NC） |
| 26–39 | NC | — | 预留 |
| 40 | SHIELD | — | |

> v0.2 的 LCD_* / I2C / ENC / PWR_BTN 已移出 CBI，改在 PERIPH 板内接 C6。

---

## FEAHI-CBI-40 机械规格（v1.0 草案）

> **文档编号：** FEAHI-CBI-40-MECH v1.0  
> **适用范围：** CORE-A、CORE-B、PERIPH-1 及后续同接口扩展板  
> **状态：** 草案 — 首版 PCB 打样前需与结构件核对

### 1. 标准层级说明

| 层级 | 内容 | 性质 |
|------|------|------|
| L0 | 2.54 mm 间距、1.6 mm 板厚、邮票孔工艺 | 行业惯例 |
| L1 | **FEAHI-CBI-40** 引脚定义（见上表 v0.3） | 项目协议 |
| L2 | **本文档** 外形、坐标、公差、禁布 | 项目机械标准 |

### 2. 坐标系与视图

```
坐标原点 (0, 0)：Core 板左下角（Bottom View，即邮票孔面）
+X：向右
+Y：向上（远离邮票孔边缘，进入板内）

堆叠方向（默认）：
  Core 元件面朝上 → Core 邮票孔面朝下 → 焊接到 Periph 顶面焊盘
  Periph 元件面朝上（屏、C6、键、MS1808/MS4344 等）
```

| 视图 | 用途 |
|------|------|
| Core **Bottom View** | 邮票孔、Pin 1 标记、定位孔 |
| Periph **Top View** | 对应焊盘、Core 禁布区、定位孔 |

### 3. Core 板外形（CORE-A / CORE-B 共用）

| 参数 | 数值 | 公差 |
|------|------|------|
| 板长（X） | **50.0 mm** | ±0.15 mm |
| 板宽（Y） | **36.0 mm** | ±0.15 mm |
| 板厚 | **1.6 mm** | ±0.12 mm |
| 板形 | 矩形，四角 **R1.0 mm** 圆角 | |
| 邮票孔边 | **底边**（Y = 0 边，Bottom View） | |
| 顶层丝印 | 型号、`FEAHI-CBI-40`、`Pin1 ◄` | |

```
Core Bottom View（50 × 36 mm）
                    +Y
                     ↑
         ┌───────────────────────┐ 36 mm
         │  ○ M2              ○  │
         │                       │
         │    [MCU / NAND 区]    │
         │                       │
         │  ○ M2              ○  │
         ├──●═══…═══…═══…═══●──┤ ← 邮票孔 2×20（Y=0 底边）
         └───────────────────────┘
         0                      50 mm → +X
              Pin1 ●          Pin20 ●
                   Pin21 ● … Pin40 ●（内排 Y=2.54 mm）
```

### 4. 邮票孔（Castellation）几何

| 参数 | 数值 |
|------|------|
| 排数 × 每排 pin 数 | **2 × 20 = 40** |
| Pin 间距（同排） | **2.54 mm** |
| 排间距（外排 → 内排） | **2.54 mm** |
| 有效跨距（Pin1–Pin20 中心） | **48.26 mm**（19 × 2.54） |
| 底边留白（Pin1 中心距左缘） | **0.87 mm** |
| 底边留白（Pin20 中心距右缘） | **0.87 mm** |
| 钻孔（castellation 半孔） | **Ø0.80 mm** |
| 焊盘宽度（板边） | **1.50 mm**（推荐） |
| 电镀 | 化学镍金（ENIG）或 HASL（打样可用 HASL） |

**排与逻辑 Pin 对应：**

| 物理排 | 逻辑 Pin | 位置（Bottom View） |
|--------|----------|---------------------|
| **外排**（靠板边） | 1 – 20 | Y = 0（板边半孔中心） |
| **内排** | 21 – 40 | Y = 2.54 mm |

**Pin N（N = 1…20）中心坐标：**

```
X(N) = 0.87 + (N − 1) × 2.54   [mm]
Y = 0                           外排 Pin 1–20

X(N) = 0.87 + (N − 21) × 2.54  [mm]  （N = 21…40 时改用 N-20）
Y = 2.54                        内排 Pin 21–40
```

简化：Pin **k**（k = 1…40）的 X 坐标：

```
X(k) = 0.87 + ((k − 1) mod 20) × 2.54
Y(k) = 0        若 k ≤ 20
Y(k) = 2.54     若 k > 20
```

### 5. 定位孔（4× M2）

| 孔 | 用途 | 中心坐标 (X, Y) mm | 钻孔 | 备注 |
|----|------|-------------------|------|------|
| **H1** | 定位 | **(3.0, 3.0)** | **Ø2.0 NPTH** | 左下，**Pin1 侧** |
| **H2** | 定位 | **(47.0, 3.0)** | **Ø2.0 NPTH** | 右下 |
| **H3** | 定位 | **(3.0, 33.0)** | **Ø2.0 NPTH** | 左上 |
| **H4** | 定位 | **(47.0, 33.0)** | **Ø2.0 NPTH** | 右上 |

| 参数 | 数值 |
|------|------|
| 螺丝 | M2 × 4 mm 尼龙柱或金属柱（开发架） |
| 公差 | 孔位 ±0.05 mm |
| **防呆** | Core 左上角（H3 附近）切 **1.5 × 1.5 mm 缺角**；Periph 同位置不开孔或填实 |

> 量产贴片：可仅用 4 孔 + 邮票孔焊接，不强制螺丝；开发期建议 **2 柱 + 焊接** 减变形。

### 6. Periph 对接区（Landing Zone）

Periph 顶面须预留与 Core **同坐标系对齐** 的 **Core Bay**：

| 参数 | 数值 |
|------|------|
| Core Bay 外形 | **50.0 × 36.0 mm**（与 Core 一致） |
| 焊盘 | 40 个，与 Core 邮票孔 **1:1 镜像**（Top View 看 X 同向） |
| 焊盘类型 | **SMD 圆 pad 或 oval**，Ø1.5 mm |
| 禁布高度 | Bay 内 Periph **Top 面** 元器件 **≤ 0.5 mm**（仅允许 0 Ω、DNP 测试点） |
| 禁布区扩展 | Bay 外扩 **1.0 mm** 环带建议不走高速线 |

**Periph 上 Core Bay 推荐位置（Top View，整机坐标待结构定）：**

| 参数 | 建议值 |
|------|--------|
| Bay 位置 | 板体 **后部中央**（远离 Speaker / Amp 热区） |
| 与 I2S Codec 距离 | Codec 放置在 Bay **前方 ≤ 15 mm**，I2S 直线连接 |
| 与 Class-D 距离 | Bay 至 Amp SW 节点 **≥ 8 mm** |

```
Periph Top View（示意，外轮廓 TBD）
┌────────────────────────────────────────┐
│  [2" TFT]          [Keys]              │
│                                        │
│  ┌── Core Bay 50×36 ──┐  [Codec+Amp]  │
│  │ ○    [焊盘×40]    ○ │  ← 模拟区    │
│  │   (Core 叠放区)     │              │
│  └─────────────────────┘              │
│  [TRS]  [MIDI]  [Battery]             │
└────────────────────────────────────────┘
```

### 7. 堆叠与高度

| 项目 | 高度 |
|------|------|
| Core PCB | 1.6 mm |
| Core 顶面最高元件（模组） | ≤ **4.0 mm**（目标） |
| 邮票孔焊锡填充 | ~0.1 – 0.3 mm |
| Periph PCB | 1.6 mm |
| Periph Core Bay 焊盘区 | 0 mm（无件） |
| **Core+Periph 叠板厚度** | **~3.3 – 3.5 mm**（不含 Core 顶面模组） |
| Core 顶面至 Periph 底面（若 Periph 在下） | 整机结构另计 |

### 8. 电气与 PCB 工艺要求

| 项 | Core（4L） | Periph（2L） |
|----|------------|--------------|
| 层叠 | L1–L4 见本文「4 层核心板」章节 | 1.6 mm 双面板 |
| I2S 线宽 | 0.15 mm（至邮票孔） | 0.15 mm（自 Bay 至 Codec） |
| I2S 阻抗 | 非差分，但 **等长 ±3 mm** | 同左 |
| GND | Pin 5–8 对应 Periph **独立地过孔 ×4** | Bay 下方铺地 |
| USB（Core 板边） | 90 Ω 差分，不经过 CBI | — |
| 邮票孔 | Fab 能力：**Plated half-hole / castellation** 必须支持 | 对应 oval pad |

**Gerber 备注（给 PCB 厂）：**

```
1. Bottom edge row 1-20: castellated holes, plated half-hole required.
2. Row 2 (Y=2.54 mm from edge): castellated or through-hole to edge per fab capability.
3. Pin 1: square pad on Core bottom silkscreen.
4. Board thickness 1.6 mm ±0.12 mm.
5. Do not rotate or mirror CBI pad array on Periph.
```

### 9. Pin 1 与防错

| 措施 | Core | Periph |
|------|------|--------|
| 丝印 | 底面 Pin1 处 **◄ Pin1** + 方焊盘 | Top Bay Pin1 处 **◄ Pin1** + 方焊盘 |
| 缺角防呆 | 左上角 **1.5 mm 切角** | 同位置机械限位或缺角 |
| 颜色（可选） | Core-B / Core-A 不同贴纸 | — |

### 10. 逻辑 Pin ↔ 物理坐标速查（外排 Pin 1–10）

| Pin | 信号 | X (mm) | Y (mm) |
|-----|------|--------|--------|
| 1 | VBAT | 0.87 | 0 |
| 2 | VBAT | 3.41 | 0 |
| 3 | +5V | 5.95 | 0 |
| 4 | +3V3 | 8.49 | 0 |
| 5 | GND | 11.03 | 0 |
| 6 | GND | 13.57 | 0 |
| 7 | GND | 16.11 | 0 |
| 8 | GND | 18.65 | 0 |
| 9 | I2S_MCLK | 21.19 | 0 |
| 10 | I2S_BCLK | 23.73 | 0 |

内排 Pin 21–30 与外排 Pin 1–10 **X 坐标相同**，Y = **2.54 mm**（信号见引脚表 Pin 21 = LCD_DC …）。

### 11. 版本与变更

| 版本 | 日期 | 变更 |
|------|------|------|
| **v1.0** | 2026-09-14 | 初版：50×36 Core、2×20 邮票孔、Codec 在下板、I2S 跨板 |
| v1.1 | TBD | 首版打样反馈：间距 / 缺角 / Periph Bay 整机坐标 |

> 任何变更须 **同时更新** CORE-A、CORE-B、PERIPH-1 的 Gerber，并 bump 版本号。

### 12. 打样检查清单

- [ ] Core / Periph Pin1 丝印对齐，万用表测 Pin1=VBAT
- [ ] 40 焊盘连通性（无开路 / 短接）
- [ ] I2S 自环：Core 输出 → Periph Codec → I2S_DIN 回 Core
- [ ] 定位孔与缺角：Core 仅一种方向可装入 Periph 限位
- [ ] 堆叠后 Core 顶模组不干涉 Periph 结构件
- [ ] CORE-A 与 CORE-B 可互换，PERIPH-1 无需改板

---

## 音频数据流（Codec 在下板）

```
                    CORE                          PERIPH-1
              ┌─────────────┐                ┌─────────────────────────┐
              │ RP2350 / S3 │                │                         │
              │             │  I2S_DOUT ────►│ Codec DAC → VOL → Amp  │──► Speaker
              │             │◄──── I2S_DIN   │         ↘              │──► TRS OUT
              │             │                │ Mic / Line IN → ADC    │
              │             │  I2C ─────────►│ Codec reg (0x18)       │
              └─────────────┘                └─────────────────────────┘
```

| 路径 | 说明 |
|------|------|
| 播放 | Core I2S_DOUT → Codec → 模拟 OUT → Volume → Amp / TRS |
| 采样 | Mic/Line → Codec ADC → I2S_DIN → Core → NAND |
| 配置 | Core I2C 写 Codec 寄存器（PGA、路由、HPF） |
| Volume | **推荐 Periph 纯模拟**（电位器）；可选 I2C 数字增益 |

---

## I2S 跨板设计要点

| 项 | 要求 |
|----|------|
| 线数 | 5（MCLK + BCLK + LRCLK + DOUT + DIN） |
| 等长 | BCLK / LRCLK / DOUT / DIN 组内 ±3 mm |
| MCLK | 可略长，但远离功放 SW 节点 |
| 端接 | 一般不需要；邮票孔距离 < 30 mm 时保持默认 CMOS |
| 地 | Pin 5–8 地针紧邻 I2S 针；Periph 侧 I2S 下方铺地 |
| 串扰 | I2S 走线远离 Class-D 功放电感 / SW 脚 ≥ 5 mm |
| 时钟源 | **24.576 MHz 晶振在 Core**，RP2350/S3 输出 MCLK |

> feahi_pico 已在 RP2350 + AIC3104 @ 48 kHz 验证；跨板 I2S 需 DVT-0 测 THD+N / 串扰。

### 2 层外围板的布局规则（方案 C：C6 + 8080 屏 + 音频同板）

```
┌─────────────────────────────────────────┐
│  [TFT FPC]──[C6]     [Keys / LED]       │  ← 8080 走线 ≤15 mm
│                                         │
│  ┌─ 模拟区 ─────────────────────────┐  │
│  │ MS1808/4344 ─ VOL ─ Amp ─ Speaker│  │
│  │   ↕ Mic   TRS IN/OUT  (短走线)     │  │
│  └──────────────────────────────────┘  │
│  [I2S 从 CBI 进 → MS1808/4344]           │
│  [IPC UART 从 CBI 进 → C6]              │
│  [CBI 邮票孔 — 与 Core 对接]            │
└─────────────────────────────────────────┘
```

1. **C6 与 TFT FPC 相邻**，8080 数据线等长 ±5 mm  
2. **模拟区** 占 Periph 一角：MS1808/MS4344 + LDO + Mic + TRS + Amp  
3. **I2S 从 CBI 边缘直线到 MS1808/MS4344**，不绕经功放或 LCD  
4. **AGND / DGND** 在 ADC/DAC 下方单点汇合  
5. 功放 SW 节点 **不放在 I2S / 8080 走线正下方**  
6. 若 2 层仍困难，可选 **Periph 局部 4 层** 或 **Audio 子板 4L**

---

## 两种核心板（方案 C：均无 C6 / 屏 / Codec）

### CORE-B

```
┌──────────────────────────────────────────┐
│  RP2350 + PSRAM                          │
│       │ I2S ×5    SPI NAND    USB-C      │
└───────┼──────────────────────────────────┘
        │ CBI-40 v0.3（I2S + IPC UART + MIDI）
        ▼
   PERIPH-1 (C6 + 8080 TFT + MS1808/4344 + UI)
        ▲
   IPC UART 在 Periph 上接 C6 ↔ RP2350
```

### CORE-A

```
┌──────────────────────────────────────────┐
│  ESP32-S3  I2S + NAND + USB              │
│  IPC UART 经 CBI 接 Periph 上 C6         │
└───────┼──────────────────────────────────┘
        │ CBI-40（相同 I2S + IPC 引脚）
        ▼
   PERIPH-1（同一块，C6 仍驱动 8080 屏）
```

---

## 4 层核心板层叠（无 Codec 版）

| 层 | 内容 |
|----|------|
| L1 | MCU 模组、PSRAM、去耦 |
| L2 | 完整地 |
| L3 | 3V3、USB 差分、**I2S 至邮票孔** |
| L4 | NAND、USB-C、24.576 MHz 晶振、邮票孔 |

---

## 电源

| 轨 | 位置 | 负载 |
|----|------|------|
| VBAT | Periph 电池 → CBI → Core | Core DCDC |
| 3.3 V | Core LDO → CBI | C6、MS1808/MS4344 数字 |
| AVDD / MICBIAS | **Periph LDO** | MS1808 模拟（靠近芯片） |
| 5 V | **Periph Boost** | 功放、LCD 背光（LEDA） |

---

## 方案对比：C6+屏 在 Core vs 在 Periph（方案 C）

| 维度 | C6+SPI 屏在 Core（旧） | **C6+8080 屏在 Periph（现方案）** |
|------|------------------------|-----------------------------------|
| LCD 接口 | SPI 6 线可跨 CBI | **8080 13+ 线，必须板内** |
| IPC | Core 内 C6↔RP2350 | **UART 跨 CBI（2 线）** |
| 模拟走线 | 跨板或 Core 带 Codec | **Periph 板内短走线** |
| A/B 对照 | UI 随 Core 变 | **Periph 固定，更公平** |
| Core 面积 | 较大（双 MCU） | **更小（单音频 MCU）** |
| Periph 复杂度 | 低 | **高（C6+屏+音频+键）** |

---

## 开发验证顺序

| 阶段 | 内容 |
|------|------|
| **DVT-0** | Core 飞线 I2S 至 Periph Codec 裸板；48 kHz loopback + THD 摸底 |
| **DVT-1** | CBI-40 邮票孔 I2S 连通 + USB Audio |
| **DVT-2** | 全 Periph（Mic 采样、Line IN、Amp、TRS） |
| **DVT-A** | 换 CORE-A，PERIPH-1 不变，对比 CPU 占用与 glitch |

---

## 待决事项

| # | 问题 | 倾向 |
|---|------|------|
| 1 | Volume：模拟电位器 vs I2C 数字增益 | **Periph 模拟**，简单可靠 |
| 2 | Periph 2 层是否够用 | 先 2L + 规则；不过关则 **Audio 区改 4L** |
| 3 | ADC/DAC | **MS1808 + MS4344**（已定） |
| 4 | C6 8080 GPIO | **v0.1 已冻结**，见 [c6_gpio.csv](../hardware/schematic/c6_gpio.csv) |
| 5 | IPC 物理层 | **UART 921600**（CBI Pin 18–19） |

---

## 器件规格书

归档于 [hardware/datasheets/](../hardware/datasheets/)：

| 器件 | 文件 | 说明 |
|------|------|------|
| TFT020B107-C0 | [JME-01_TFT020B107-C0_LCD.pdf](../hardware/datasheets/JME-01_TFT020B107-C0_LCD.pdf) | 2" 240×320，ST7789，**8080 并口** |
| MS1808 | [MS1808_ADC.pdf](../hardware/datasheets/MS1808_ADC.pdf) | 24-bit ADC，8–96 kHz |
| MS4344 | [MS4344_DAC.pdf](../hardware/datasheets/MS4344_DAC.pdf) | 24-bit DAC，至 192 kHz |

> **方案 C 已定：** 量产屏 TFT020B107-C0 为 **8080 并口**，C6 与屏同在 PERIPH-1；CBI v0.3 不再预留 LCD 引脚。

## 原理图框架

块级 KiCad 10 分层原理图 + CSV 网表（占位符号，待换库元件）：

- [hardware/schematic/README.md](../hardware/schematic/README.md)
- [c6_gpio.csv](../hardware/schematic/c6_gpio.csv) — C6 引脚分配 v0.1
- [coreb_nets.csv](../hardware/schematic/coreb_nets.csv) / [periph1_nets.csv](../hardware/schematic/periph1_nets.csv)

| 子页 (CORE-B) | 子页 (PERIPH-1) |
|---------------|-----------------|
| MCU / NAND / USB / Power / CBI40 | C6 / LCD / Audio / UI / Power / Conn / CBI40 |

重新生成：

```powershell
py -3 hardware/kicad/tools/generate_schematic_framework.py
py -3 hardware/kicad/tools/generate_cbi40_templates.py
```

## KiCad PCB 模板

- [hardware/kicad/README.md](../hardware/kicad/README.md)
- [feahi_cbi40_core/](../hardware/kicad/feahi_cbi40_core/) · [feahi_cbi40_periph/](../hardware/kicad/feahi_cbi40_periph/)
- [cbi40_pinout.csv](../hardware/kicad/cbi40_pinout.csv)

## 相关文档

- [architecture.md](./architecture.md)
- [feahi_pico 播放路径](../../feahi_pico/docs/play-path.md)
