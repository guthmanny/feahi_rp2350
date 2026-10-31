# LED_SMD_feahi

Project footprint overrides for LEDs whose official KiCad `LED_SMD` entry references a 3D model that is **not** shipped under `${KICAD9_3DMODEL_DIR}`.

| Footprint | 3D model |
|-----------|----------|
| `LED_LiteOn_LTST-C235KGKRKT` | `${KIPRJMOD}/../libs/3dmodels/LED_SMD.3dshapes/LED_LiteOn_LTST-C235KGKRKT.step`; see **3D transform** below. `3D/*.step` symlink → `libs/3dmodels/...` |

Use **`LED_SMD_feahi:LED_LiteOn_LTST-C235KGKRKT`** in schematic/PCB.

### 3D transform (verified SP-1, top-mount on `F.Cu`)

Samacsys STEP is drawn for reverse / down-facing assembly. For **top-mount** (no NPTH, lens up), use:

| Property | Value |
|----------|--------|
| Path | `${KIPRJMOD}/../libs/3dmodels/LED_SMD.3dshapes/LED_LiteOn_LTST-C235KGKRKT.step` |
| Offset | `(xyz 0 0 0)` |
| Scale | `(xyz 1 1 1)` |
| Rotate | **`(xyz -90 0 90)`** |

Confirmed in KiCad 3D: body flat on pads, lens toward **+Z**, XY aligned with footprint (2026-09-30).

Do **not** use `(xyz 90 0 90)` or `(xyz 90 0 -90)` for top-mount — both lay the body flat but keep the **lens pointing into the board** (only a spin in the plane; Z rotation does not flip the dome).

If you change STEP vendor file, re-check in **Footprint Editor → 3D model** preview before syncing PCB embedded models.

Footprint 3D uses a **host absolute path** so the footprint editor works without custom env vars. Optional: *Preferences → Configure Paths* → **`FEAHI_KICAD_LIBS`** = `<repo>/hardware/kicad/libs` if you re-link models with `${FEAHI_KICAD_LIBS}/...`.

Do **not** use `../../3dmodels/...` — KiCad resolves `../` from the **project** folder, not the `.pretty` library.

**Alt+3 全屏 3D：** KiCad 已知问题，相对/`../` 路径在全屏 3D 可能不显示；请用 **封装属性 → 3D 模型** 页里的预览，或 PCB 的 3D 视图。

Opening the global **`LED_SMD:`** copy still has no STEP under `${KICAD*_3DMODEL_DIR}`.
