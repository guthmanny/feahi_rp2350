# LED_SMD.3dshapes credits

| File | Source | Notes |
|------|--------|--------|
| `LED_LiteOn_LTST-C235KGKRKT.step` | Samacsys backup (`LED_LiteOn_LTST-C235KGKRKT.samacsys.step`) | Colored vendor geometry; PCB **`(rotate (xyz -90 0 90))`** (flat + align footprint). |
| `LED_LiteOn_LTST-C235KGKRKT_LTO.step` | [wubneh/MCTR260-pico-firmware](https://github.com/wubneh/MCTR260-pico-firmware) | LTO export; orientation OK in KiCad but body renders **dark/black** — not used as default. |
| `LED_LiteOn_LTST-C235KGKRKT.samacsys.step` | [nrwiersma/aura-mon](https://github.com/nrwiersma/aura-mon) | Samacsys STEP (**56544**); in KiCad 3D often appears **vertical** without extra rotation — kept as backup only. |
| `LED_LiteOn_LTST-C235KGKRKT.wrl` | SP-1 placeholder (removed from PCB once STEP is used) | Box model from footprint F.Fab; superseded by STEP above. |

Alternative community STEP (similar geometry): [Kev1n8088/KicadLibraries](https://github.com/Kev1n8088/KicadLibraries) `3dmodels/LTST-C235KGKRKT.STEP`.

Lite-On / LCSC may provide newer **LTO** exports (e.g. `LTST-C235KGKRKT_LTO.step` on GitHub); re-vendor if you need manufacturer-rev-controlled CAD.
