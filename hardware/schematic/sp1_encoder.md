# EC11 编码器 → RP2350 GPIO（v2.0）

> **状态：** 2026-09-23（随 [rp2350a_gpio_plan.md](rp2350a_gpio_plan.md) v2）  
> **C6** 不接 EC11（strapping / GPIO 已满）。

## 接线（ENC1 → U7）

| EC11 | 网名 | RP2350 | 说明 |
|------|------|--------|------|
| **A** | **ENC_A** | **GPIO22** | 内部上拉；PIO/QEI 或周期采样 |
| **B** | **ENC_B** | **GPIO27** | 与 **EXP_ADC1** 复用脚位 — 见下方 SKU |
| **SW** | （矩阵） | **row4 col2** | 经 **MAT_C2 + MAT_R4** 与 Choc 相同二极管拓扑；固件当 **ENC_SW** |
| **C** | GND | 板地 | 公共端 |

### SKU / 二选一（与 4 路 ADC 的关系）

| 配置 | ENC_B | EXP_ADC |
|------|-------|---------|
| **默认（5a）** | **GPIO27** | **26, 28, 29** 可用（**3 路** ADC） |
| **4×ADC（5c）** | 不贴或改 IPC UI | **26–29 全开** |

主音量仍用模拟 **VR1**（Codec 链），不占用 `EXP_ADC*`。

## 固件

- **RP2350**：解码 A/B；矩阵 cell **(4,2)** 作 SW；经 **IPC** 发 `ENC_DELTA` / `ENC_CLICK`（见 `docs/architecture.md`）。
- **C6**：LVGL 消费 IPC，不读编码器 GPIO。

## 相关

- [rp2350a_gpio.csv](rp2350a_gpio.csv)  
- [sp1_key_matrix.csv](sp1_key_matrix.csv)（row4 col2 = ENC_SW）  
- [sp1_nets.csv](sp1_nets.csv)

## 修订

| 版本 | 说明 |
|------|------|
| v2.0 | B→GP27；SW→矩阵；释放 26–29 作 EXP_ADC |
| v1.0 | A/B/SW 全 GPIO（占 ADC 行） |
