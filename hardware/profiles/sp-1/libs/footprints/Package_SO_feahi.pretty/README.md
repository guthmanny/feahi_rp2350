# Package_SO_feahi

Pad-size variants for **0.65 mm pitch** gullwing packages when KiCad IPC defaults fail **0.20 mm** copper clearance.

| Footprint | Pad change | Typical use |
|-----------|------------|-------------|
| `Texas_DGN0008D_VSSOP-8-1EP_3x3mm_P0.65mm_EP2x2.94mm_Pad0.45mm` | **1.45 × 0.45 mm** (was 0.5 mm) | **U24** TPA2005D1 |
| `MSOP-8-1EP_3x3mm_P0.65mm_EP1.68x1.88mm_Pad0.38mm` | **1.45 × 0.38 mm** (was 0.4 mm) | **U18** SGM8278 (extra DRC margin) |

3D models: same `${KICAD9_3DMODEL_DIR}/Package_SO.3dshapes/…` as stock KiCad footprints.
