# 器件规格书索引

原始 PDF 自 `Downloads` 归档至本目录，文件名采用 ASCII 便于工具链引用。

| 文件 | 原件 | 用途 |
|------|------|------|
| [JME-01_TFT020B107-C0_LCD.pdf](JME-01_TFT020B107-C0_LCD.pdf) | JME-01液晶屏TFT020B107-C0产品规格书.pdf | 2" IPS 液晶模组 |
| [MS1808_ADC.pdf](MS1808_ADC.pdf) | ms1808.pdf | 立体声 ADC |
| [MS4344_DAC.pdf](MS4344_DAC.pdf) | ms4344.pdf | 立体声 DAC |

---

## TFT020B107-C0（JME-01）

| 项 | 规格 |
|----|------|
| 尺寸 | 2.0 inch IPS |
| 分辨率 | **240 × 320**（240×RGB×320） |
| 驱动 IC | **ST7789P3** |
| 模组外形 | 36.05 (H) × 51.8 (V) × 2.25 (D) mm |
| 可视区 | 30.60 × 40.80 mm |
| 接口（规格书） | **8080 并口 8-bit**（DB0–DB7, WR, RD, RS, CS） |
| 背光 | 3× white LED，LEDA/LEDK，Typ. 60 mA @ 3.0 V |
| 逻辑电压 | IOVCC 1.65–3.3 V（Typ. 2.8 V） |
| 工作温度 | -20 ~ +70 ℃ |

**方案 C（已定）：** 量产屏为 **8080 并口，不可更换**。ESP32-C6 与 FPC **同在 PERIPH-1**，8080 走线 **不跨 CBI-40**。CBI v0.3 仅保留 I2S、IPC UART、MIDI 等。

- 接线草案：[TFT020B107-C0_C6_GPIO.md](TFT020B107-C0_C6_GPIO.md)
- 驱动：ESP-IDF PARLIO + `esp_lcd_new_panel_st7789()` + LVGL

---

## MS1808（ADC）

| 项 | 规格 |
|----|------|
| 类型 | 24-bit ΔΣ 立体声 **ADC** |
| 采样率 | 8 kHz – **96 kHz** |
| 接口 | I2S / 左对齐 24-bit |
| 输入 | 单端模拟（Line/Mic 需外部分压与偏置） |
| SNR / DR | 95 dB SNR，95 dB 动态范围 |
| MCLK | 256/384/512/768 × fs |
| 电源 | 模拟 4.5–5.5 V，数字 2.7–5.5 V |
| 封装 | TSSOP14 / QFN16 |

**SP-1 用途：** Mic / Line IN → MS1808 → I2S_DIN → RP2350 录音与采样。

---

## MS4344（DAC）

| 项 | 规格 |
|----|------|
| 类型 | 24-bit ΔΣ 立体声 **DAC** |
| 采样率 | 最高 **192 kHz**（自动检测） |
| 接口 | I2S（SDIN, SCLK, LRCK, MCLK） |
| 输出 | 模拟 OUTL / OUTR（线性滤波） |
| THD | 0.003% |
| 动态范围 | 110 dB |
| 电源 | 3.0–5.5 V（MSOP10） |
| 封装 | MSOP10 |

**SP-1 用途：** RP2350 I2S_DOUT → MS4344 → Volume → 功放 / TRS OUT。

---

## 建议音频链（PERIPH-1）

```
Mic / Line IN ──► MS1808 ── I2S ──► CBI I2S_DIN ──► RP2350
RP2350 ── I2S ──► CBI I2S_DOUT ──► MS4344 ──► VOL ──► Amp / TRS
```

MS1808/MS4344 与 MCLK/BCLK/LRCLK 可共用同一 I2S 总线（注意 MS1808 模拟 5 V 与数字 3.3 V 电平）。

---

## 更新记录

| 日期 | 说明 |
|------|------|
| 2026-09-14 | 从 Downloads 归档三份 PDF |
| 2026-09-14 | 方案 C 定案：8080 屏 + C6 在 PERIPH-1，CBI v0.3 |
