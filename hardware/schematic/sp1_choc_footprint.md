# KiCad：Kailh Choc V2 封装

> **结论：** KiCad **自带** `Button_Switch_Keyboard` 里 **只有 Cherry MX / Matias**，**没有** Kailh Choc。  
> **Choc V2（PG1353）** 需装 **第三方 footprint 库**。

## 推荐库

### 1. Keyswitch KiCad Library（KiSwitch，首选）

- **安装：** KiCad **PCM**（插件与内容管理器）→ **Libraries** → **「Keyswitch Kicad Library」**（或 *kiswitch/keyswitch-kicad-library*）→ 安装 **≥ v2.1.2**（旧版 Choc V1 尺寸有误，见 [issue #26](https://github.com/kiswitch/keyswitch-kicad-library/issues/26)）。
- **库名：** `Switch_Keyboard_Kailh`
- **常用 footprint（1u Pad）：**
  - **`Switch_Keyboard_Kailh:SW_Kailh_Choc_V2`** — V2 PCB 安装
  - **`Switch_Keyboard_Kailh:SW_Kailh_Choc_V2_1.00u`** — 带 1u 定位/间距参考
  - 另有 `SW_Kailh_Choc_V1`、V1/V2 兼容旧款 **CPG1350**
- **3D：** 库内 **`SW_Kailh_Choc_V1`** 等模型可借用于预览（V2 以 PCM 更新为准）。
- 链接：[github.com/kiswitch/kiswitch](https://github.com/kiswitch/kiswitch)

### 2. siderakb/key-switches.pretty（备选）

- GitHub：**[siderakb/key-switches.pretty](https://github.com/siderakb/key-switches.pretty)**
- **V2 THT：** `SW_Kailh_Choc_V2_THT`（板载直插脚位 + 中心定位柱）
- **V1/V2 兼容：** `SW_Kailh_Choc_V1V2_THT_Hybrid`（打样不确定 V1/V2 时可考虑）
- 需手动把 `.pretty` 目录加入 **FP 库表**（`fp-lib-table`）。

## SP-1 建议

| 项 | 建议 |
|----|------|
| 轴体 | **Kailh Choc V2**（如 Choc Red PG1353），与 **SW_Kailh_Choc_V2** 配套 |
| 安装 | **PCB mount** 为主；若用 **热插拔** 用 KiSwitch 的 **Choc hotswap** 系列（另选 footprint） |
| 符号 | KiCad 无专用 Choc **符号** 时，可用 **Switch:SW_Push** 或 **Device:SW_SPST** + Footprint 指向 Choc |
| 电气 | 两焊盘 → **MAT_Rx / MAT_Cy** + 串 **二极管**（见 [sp1_u16_key_matrix.md](sp1_u16_key_matrix.md)） |
| 间距 | 键帽网格 **17.5 mm × 18.0 mm**（与 [sp1_c6_ui.md](sp1_c6_ui.md) 一致）；1u  footprint 轴心对齐 |
| 键下灯 | Choc **0°**；**LTST-C235** **Δ(0, −5.013) mm** + **封装 180°**（灯在轴心下侧空槽，与实装轴体朝向一致）；矩阵二极管 **Δ(+6, −5) mm** |

## 本仓库（已 vendoring）

- 路径：**`hardware/kicad/libs/footprints/Switch_Keyboard_Kailh.pretty/`**
- **`sp-1/fp-lib-table`** 已注册库名 **`Switch_Keyboard_Kailh`**
- 默认 Footprint：**`Switch_Keyboard_Kailh:SW_Kailh_Choc_V2`**（源：[kiswitch/kiswitch](https://github.com/kiswitch/kiswitch) main）
- 可选：**`SW_Kailh_Choc_V2_1.00u`**（带 1u 参考外形）
- 文件为 KiSwitch **legacy `(module …)` 语法**；KiCad 8/9 打开时若提示迁移，按向导升级即可。
- **3D 模型（已 vendoring）：** `hardware/kicad/libs/3dmodels/Switch_Keyboard_Kailh.3dshapes/`  
  - **`SW_Kailh_Choc_V2.wrl`** — 已写入 footprint 的 `(model …)`  
  - 模型为 **koktoh Choc V2**（PG1353 / MX 矮轴十字外观），**非** V1 猪鼻子占位  
- 在 **3D 视图** 刷新即可；不显示时在封装属性改绑 `.step` 或检查 `${KIPRJMOD}` 路径。
- **LTST-C235 键下灯 3D：** KiCad 官方 **无** packages3d；工程 vendoring **`LED_LiteOn_LTST-C235KGKRKT.step`**（来源见 `libs/3dmodels/LED_SMD.3dshapes/CREDITS.md`）。封装用 **`LED_SMD_feahi:LED_LiteOn_LTST-C235KGKRKT`**（相对路径 3D + `rotate -90 0 90`），封装编辑器与 PCB 一致；勿再编辑全局 **`LED_SMD:`** 同名封装（系统路径下无 STEP）。

## 修订

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-09-22 | 初版：PCM KiSwitch + siderakb 备选 |
| v1.1 | 2026-09-22 | 工程内 vendoring + fp-lib-table |
