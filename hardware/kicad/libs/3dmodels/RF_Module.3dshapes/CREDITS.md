# RF module 3D models

| File | Source | Notes |
| --- | --- | --- |
| `ESP32-C6-MINI-1.step` | [espressif/kicad-libraries](https://github.com/espressif/kicad-libraries) `3dmodels/espressif.3dshapes/ESP32-C6-MINI-1.STEP` | Espressif footprint offset is (−6.55, −8.3, 0.5) mm. KiCad `RF_Module:ESP32-C6-MINI-1` origin is 2.7 mm lower in Y (pad 1 at (−5.9, −4) vs (−5.9, −1.3)). The 3D view maps model +Y to footprint −Y, so the board uses **offset (−6.55, −5.6, 0.5) mm**. |
| `ESP32-C6-WROOM-1.step` | [espressif/kicad-libraries](https://github.com/espressif/kicad-libraries) `3dmodels/espressif.3dshapes/ESP32-C6-WROOM-1.STEP` | PCB-antenna module. Official footprint `Espressif:ESP32-C6-WROOM-1` uses offset (−9, −9.75, 0) mm, rotate 0. The u.FL variant is `ESP32-C6-WROOM-1U` (not vendored). |
