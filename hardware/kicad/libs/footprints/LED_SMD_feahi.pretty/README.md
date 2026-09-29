# LED_SMD_feahi

Project footprint overrides for LEDs whose official KiCad `LED_SMD` entry references a 3D model that is **not** shipped under `${KICAD9_3DMODEL_DIR}`.

| Footprint | 3D model |
|-----------|----------|
| `LED_LiteOn_LTST-C235KGKRKT` | Absolute path to `3D/LED_LiteOn_LTST-C235KGKRKT.step` (rotate `-90 0 90`); `3D/*.step` symlink → `libs/3dmodels/...` |

Use **`LED_SMD_feahi:LED_LiteOn_LTST-C235KGKRKT`** in schematic/PCB.

Footprint 3D uses a **host absolute path** so the footprint editor works without custom env vars. Optional: *Preferences → Configure Paths* → **`FEAHI_KICAD_LIBS`** = `<repo>/hardware/kicad/libs` if you re-link models with `${FEAHI_KICAD_LIBS}/...`.

Do **not** use `../../3dmodels/...` — KiCad resolves `../` from the **project** folder, not the `.pretty` library.

**Alt+3 全屏 3D：** KiCad 已知问题，相对/`../` 路径在全屏 3D 可能不显示；请用 **封装属性 → 3D 模型** 页里的预览，或 PCB 的 3D 视图。

Opening the global **`LED_SMD:`** copy still has no STEP under `${KICAD*_3DMODEL_DIR}`.
