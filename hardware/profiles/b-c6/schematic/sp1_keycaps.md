# SP-1 Pad 键帽（Choc V2）

> **轴体定案：** **Kailh Choc V2（PG1353）** — 轴心为 **矮轴 Cherry MX「十字」**，**不是** Choc V1 的「猪鼻子 / MBK」两柱脚。

## 能不能用「十字帽」？

**可以**，但要满足：

| 要求 | 说明 |
|------|------|
| 接口 | **MX 十字（+）**，与 **Cherry MX Low Profile** 同系矮轴键帽 |
| 高度 | 必须 **矮轴 / low-profile** 键帽（短裙边）；普通 MX 高键帽会顶到轴壳、行程不对 |
| **不要** | **MBK / MCC / CFX** 等 **Choc V1 专用**「猪鼻子」键帽 — **装不上 V2** |

## 和「猪鼻子帽」的区别

| | Choc V1（PG1350） | **SP-1 Choc V2（PG1353）** |
|--|-------------------|----------------------------|
| 键帽接口 | 两小柱（MBK 等） | **MX 矮轴十字 +** |
| 常见叫法 | 猪鼻子、MBK | 十字矮轴帽、MX LP 帽 |
| 1u 尺寸参考 | 17.5×16.5 mm | 同网格 **17.5×18.0 mm** 布局；键帽物理约 **18×18 mm 1u** 常见 |

## 采购方向（示例，非 BOM 冻结）

- **Cherry MX Low Profile** 配套键帽（原厂矮轴套）
- 商家 **LPF / THT** 等标注 **Choc V2 / KS-33 / MX low-profile** 的套装（ortho 多 1u 的选 **ergo/ortho**  kitting）
- **DSA** 等矮轮廓 + **确认矮轴兼容** 的 MX 十字帽（部分 DSA 为全高 MX，需看裙高）
- 键帽内部加强筋过高的型号可能 **套不进 V2** — 到手先在单颗轴上试装

## 2U /  stabilizer

SP-1 Pad 以 **1u** 为主；若将来做 **2u**，Choc V2 的 **卫星轴** 与 MX 常规 stab **不通用**，需单独方案（多数客制 Choc V2 ortho 避免 2u）。

## KiCad 3D 说明

Switch 3D 为 **koktoh Choc V2（PG1353）** 键体；**键帽 3D 未包含**。实机键帽仍为 **MX 矮轴十字** 采购件。

## 参考

- [Deskthority: Kailh PG1353 (Choc V2)](https://deskthority.net/wiki/Kailh_PG1353_series) — MX mount, short skirt  
- [Keebio: Low-profile keycap options](https://blog.keeb.io/low-profile-keycap-options-what-works-with-what/) — MBK=V1 only；LPF/THT=V2  
