#!/usr/bin/env python3
"""Generate FEAHI-CBI-40 KiCad 10 template projects (Core + Periph)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# KiCad 10 file format versions (see KiCad 10.0 generated_pcb example)
KICAD_PCB_VERSION = 20260206
KICAD_SCH_VERSION = 20260306
KICAD_PRO_META_VERSION = 3

BOARD_W = 50.0
BOARD_H = 36.0
PITCH = 2.54
EDGE_MARGIN = 0.87
PAD_DRILL = 0.80
PAD_SIZE = 1.50
MOUNT_DRILL = 2.0
CHAMFER = 1.5

# FEAHI-CBI-40 v0.3 — 方案 C：LCD/C6/I2C/编码器不跨板
PIN_NAMES = [
    "VBAT", "VBAT", "+5V", "+3V3",
    "GND", "GND", "GND", "GND",
    "I2S_MCLK", "I2S_BCLK", "I2S_LRCLK", "I2S_DOUT", "I2S_DIN",
    "HP_DETECT",
    "SPK_MUTE", "NC", "NC",
    "IPC_TX", "IPC_RX", "C6_BOOT",
    "MIDI_TX", "MIDI_RX",
    "DEBUG_TX", "DEBUG_RX",
    "AUD_BOOT", "NC", "NC", "NC", "NC", "NC",
    "NC", "NC", "NC", "NC", "NC",
    "SHIELD",
]

MOUNT_HOLES = [(3.0, 3.0), (47.0, 3.0), (3.0, 33.0), (47.0, 33.0)]


def uid() -> str:
    return str(uuid.uuid4())


def pin_xy(index: int) -> tuple[float, float]:
    row = 0 if index < 20 else 1
    col = index if index < 20 else index - 20
    x = EDGE_MARGIN + col * PITCH
    y = row * PITCH
    return x, y


def net_for_signal(name: str) -> str:
    if name == "GND":
        return '\n\t\t\t(net "GND")'
    if name == "VBAT":
        return '\n\t\t\t(net "VBAT")'
    if name == "+3V3":
        return '\n\t\t\t(net "+3V3")'
    if name == "+5V":
        return '\n\t\t\t(net "+5V")'
    return ""


def board_outline_gr_lines() -> str:
    w, h, r = BOARD_W, BOARD_H, 1.0
    pts = [
        (r, 0.0),
        (w - r, 0.0),
        (w, r),
        (w, h - r),
        (w - r, h),
        (CHAMFER, h),
        (0.0, h - CHAMFER),
        (0.0, r),
        (r, 0.0),
    ]
    lines = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        lines.append(
            f'\t(gr_line\n'
            f'\t\t(start {x1:.4f} {y1:.4f})\n'
            f'\t\t(end {x2:.4f} {y2:.4f})\n'
            f'\t\t(stroke\n'
            f'\t\t\t(width 0.15)\n'
            f'\t\t\t(type solid)\n'
            f'\t\t)\n'
            f'\t\t(layer "Edge.Cuts")\n'
            f'\t\t(uuid "{uid()}")\n'
            f'\t)'
        )
    return "\n".join(lines)


def layers_block(*, four_layer: bool) -> str:
    inner = ""
    if four_layer:
        inner = '\t\t(4 "In1.Cu" signal)\n\t\t(6 "In2.Cu" signal)\n'
    return f"""\t(layers
\t\t(0 "F.Cu" signal)
{inner}\t\t(2 "B.Cu" signal)
\t\t(9 "F.Adhes" user "F.Adhesive")
\t\t(11 "B.Adhes" user "B.Adhesive")
\t\t(13 "F.Paste" user)
\t\t(15 "B.Paste" user)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(17 "Dwgs.User" user "User.Drawings")
\t\t(19 "Cmts.User" user "User.Comments")
\t\t(21 "Eco1.User" user "User.Eco1")
\t\t(23 "Eco2.User" user "User.Eco2")
\t\t(25 "Edge.Cuts" user)
\t\t(27 "Margin" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t\t(35 "F.Fab" user)
\t\t(33 "B.Fab" user)
\t)"""


def setup_block(*, castellated: bool) -> str:
    cast_flag = "\n\t\t\t(castellated_pads yes)" if castellated else ""
    return f"""\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(aux_axis_origin 0 0)
\t\t(grid_origin 0 0)
\t\t(tenting
\t\t\t(front yes)
\t\t\t(back yes)
\t\t)
\t\t(covering
\t\t\t(front no)
\t\t\t(back no)
\t\t)
\t\t(plugging
\t\t\t(front no)
\t\t\t(back no)
\t\t)
\t\t(capping no)
\t\t(filling no)
\t\t(pcbplotparams
\t\t\t(layerselection 0x00000000_00000000_00000000_00000000)
\t\t\t(plot_on_all_layers_selection 0x00000000_00000000_00000000_00000000)
\t\t\t(disableapertmacros no)
\t\t\t(usegerberextensions no)
\t\t\t(usegerberattributes yes)
\t\t\t(usegerberadvancedattributes yes)
\t\t\t(creategerberjobfile yes)
\t\t\t(dashed_line_dash_ratio 12)
\t\t\t(dashed_line_gap_ratio 3)
\t\t\t(svgprecision 4)
\t\t\t(plotframeref no)
\t\t\t(mode 1)
\t\t\t(useauxorigin no)
\t\t\t(outputformat 1)
\t\t\t(mirror no)
\t\t\t(drillshape 1)
\t\t\t(scaleselection 1)
\t\t\t(outputdirectory "")
\t\t)
\t\t(stackup
\t\t\t(layer "F.SilkS" type "Top Silk Screen")
\t\t\t(layer "F.Paste" type "Top Solder Paste")
\t\t\t(layer "F.Mask" type "Top Solder Mask")
\t\t\t(layer "F.Cu" type "copper" thickness 0.035)
\t\t\t(layer "dielectric 1" type "core" thickness 1.51 material "FR4" epsilon_r 4.5 loss_tangent 0.02)
\t\t\t(layer "B.Cu" type "copper" thickness 0.035)
\t\t\t(layer "B.Mask" type "Bottom Solder Mask")
\t\t\t(layer "B.Paste" type "Bottom Solder Paste")
\t\t\t(layer "B.SilkS" type "Bottom Silk Screen")
\t\t\t(copper_finish "ENIG"){cast_flag}
\t\t)
\t)"""


def pcb_header(title: str, *, four_layer: bool, castellated: bool) -> str:
    return f"""(kicad_pcb
\t(version {KICAD_PCB_VERSION})
\t(generator "pcbnew")
\t(generator_version "10.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(title_block
\t\t(title "{title}")
\t\t(date "2026-09-14")
\t\t(rev "v1.0")
\t\t(company "FEAHI / Soran SP-1")
\t\t(comment 1 "FEAHI-CBI-40 mechanical template")
\t\t(comment 2 "KiCad 10 — see docs/hardware.md")
\t)
{layers_block(four_layer=four_layer)}
{setup_block(castellated=castellated)}
"""


def castellation_footprint(is_core: bool) -> str:
    pads = []
    for i, name in enumerate(PIN_NAMES):
        x, y = pin_xy(i)
        pad_num = str(i + 1)
        net = net_for_signal(name)
        pad_shape = "rect" if i == 0 else "circle"

        if is_core:
            prop = ' (property pad_prop_castellated)' if y == 0 else ""
            pads.append(
                f'\t\t(pad "{pad_num}" thru_hole {pad_shape}\n'
                f'\t\t\t(at {x:.4f} {y:.4f})\n'
                f'\t\t\t(size {PAD_SIZE:.2f} {PAD_SIZE:.2f})\n'
                f'\t\t\t(drill {PAD_DRILL:.2f}){prop}{net}\n'
                f'\t\t\t(layers "*.Cu" "*.Mask")\n'
                f'\t\t\t(uuid "{uid()}")\n'
                f'\t\t)'
            )
        else:
            pads.append(
                f'\t\t(pad "{pad_num}" smd roundrect\n'
                f'\t\t\t(at {x:.4f} {y:.4f})\n'
                f'\t\t\t(size {PAD_SIZE:.2f} {PAD_SIZE:.2f})\n'
                f'\t\t\t(layers "F.Cu" "F.Mask"){net}\n'
                f'\t\t\t(roundrect_rratio 0.25)\n'
                f'\t\t\t(uuid "{uid()}")\n'
                f'\t\t)'
            )

    silk_layer = "B.SilkS" if is_core else "F.SilkS"
    fab_layer = "B.Fab" if is_core else "F.Fab"
    at_y = -3.0 if is_core else BOARD_H + 3.0
    fp_name = f"CBI40_{'CORE' if is_core else 'PERIPH'}"
    pin1_y = pin_xy(0)[1] - 2.0

    return f"""\t(footprint "FEAHI:{fp_name}"
\t\t(layer "{fab_layer}")
\t\t(uuid "{uid()}")
\t\t(at 0 0)
\t\t(descr "FEAHI-CBI-40 2x20")
\t\t(tags "FEAHI CBI40")
\t\t(property "Reference" "J1"
\t\t\t(at {BOARD_W / 2:.2f} {at_y:.2f} 0)
\t\t\t(unlocked yes)
\t\t\t(layer "{silk_layer}")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(property "Value" "CBI40"
\t\t\t(at {BOARD_W / 2:.2f} {at_y - 1.5:.2f} 0)
\t\t\t(unlocked yes)
\t\t\t(layer "{silk_layer}")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 0.8 0.8) (thickness 0.12)))
\t\t)
\t\t(property "Footprint" "FEAHI:{fp_name}"
\t\t\t(at 0 0 0)
\t\t\t(unlocked yes)
\t\t\t(layer "{fab_layer}")
\t\t\t(hide yes)
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(duplicate_pad_numbers_are_jumpers no)
{chr(10).join(pads)}
\t\t(fp_text user "Pin1"
\t\t\t(at {pin_xy(0)[0]:.2f} {pin1_y:.2f} 0)
\t\t\t(layer "{silk_layer}")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 0.8 0.8) (thickness 0.12)) (justify left bottom))
\t\t)
\t\t(embedded_fonts no)
\t)"""


def mount_holes_fp() -> str:
    pads = []
    for idx, (x, y) in enumerate(MOUNT_HOLES, start=1):
        pads.append(
            f'\t\t(pad "{idx}" np_thru_hole circle\n'
            f'\t\t\t(at {x:.4f} {y:.4f})\n'
            f'\t\t\t(size {MOUNT_DRILL:.2f} {MOUNT_DRILL:.2f})\n'
            f'\t\t\t(drill {MOUNT_DRILL:.2f})\n'
            f'\t\t\t(layers "*.Cu")\n'
            f'\t\t\t(uuid "{uid()}")\n'
            f'\t\t)'
        )
    return f"""\t(footprint "FEAHI:MOUNT_M2"
\t\t(layer "F.Fab")
\t\t(uuid "{uid()}")
\t\t(at 0 0)
\t\t(descr "M2 NPTH")
\t\t(property "Reference" "MH"
\t\t\t(at {BOARD_W / 2:.2f} {BOARD_H / 2:.2f} 0)
\t\t\t(unlocked yes)
\t\t\t(layer "F.SilkS")
\t\t\t(hide yes)
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(duplicate_pad_numbers_are_jumpers no)
{chr(10).join(pads)}
\t\t(embedded_fonts no)
\t)"""


def core_bay_drawing() -> str:
    return f"""\t(gr_rect
\t\t(start 0 0)
\t\t(end {BOARD_W:.4f} {BOARD_H:.4f})
\t\t(stroke
\t\t\t(width 0.12)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "Dwgs.User")
\t\t(uuid "{uid()}")
\t)
\t(gr_text "CORE_BAY 50x36"
\t\t(at {BOARD_W / 2:.2f} {BOARD_H + 2:.2f} 0)
\t\t(layer "Dwgs.User")
\t\t(uuid "{uid()}")
\t\t(effects (font (size 1 1) (thickness 0.12)) (justify bottom left))
\t)"""


def build_pcb(name: str, is_core: bool) -> str:
    title = f"FEAHI-CBI-40 {'Core' if is_core else 'Periph'} Template"
    parts = [
        pcb_header(title, four_layer=is_core, castellated=is_core),
        board_outline_gr_lines(),
        mount_holes_fp(),
        castellation_footprint(is_core),
    ]
    if not is_core:
        parts.append(core_bay_drawing())
    parts.append("\t(embedded_fonts no)\n)\n")
    return "\n".join(parts)


def kicad_pro(name: str, sch_uuid: str) -> dict:
    return {
        "board": {
            "design_settings": {
                "defaults": {
                    "board_outline_line_width": 0.15,
                    "copper_line_width": 0.2,
                    "copper_text_size_h": 1.5,
                    "copper_text_size_v": 1.5,
                    "copper_text_thickness": 0.3,
                    "other_line_width": 0.15,
                    "silk_line_width": 0.15,
                    "silk_text_size_h": 1.0,
                    "silk_text_size_v": 1.0,
                    "silk_text_thickness": 0.15,
                },
                "diff_pair_dimensions": [],
                "drc_exclusions": [],
                "meta": {"version": 2},
                "rule_severities": {},
                "rules": {},
                "track_widths": [0.15, 0.2, 0.25, 0.5],
                "via_dimensions": [{"diameter": 0.8, "drill": 0.4}],
            },
            "layer_presets": [],
            "viewports": [],
        },
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "libraries": {
            "pinned_footprint_libs": [],
            "pinned_symbol_libs": [],
        },
        "meta": {"filename": f"{name}.kicad_pro", "version": KICAD_PRO_META_VERSION},
        "net_settings": {
            "classes": [
                {
                    "clearance": 0.2,
                    "name": "Default",
                    "track_width": 0.25,
                    "via_diameter": 0.8,
                    "via_drill": 0.4,
                }
            ],
            "meta": {"version": 5},
            "netclass_assignments": None,
        },
        "pcbnew": {
            "last_paths": {
                "gencad": "",
                "idf": "",
                "netlist": "",
                "plot": "",
                "step": "",
                "vrml": "",
            },
            "page_layout_descr_file": "",
        },
        "schematic": {
            "legacy_lib_dir": "",
            "legacy_lib_list": [],
            "meta": {"version": 1},
            "top_level_sheets": [
                {
                    "filename": f"{name}.kicad_sch",
                    "name": name,
                    "uuid": sch_uuid,
                }
            ],
        },
        "sheets": [[sch_uuid, "Root"]],
        "text_variables": {},
    }


def kicad_sch(title: str, sch_uuid: str) -> str:
    return f"""(kicad_sch
\t(version {KICAD_SCH_VERSION})
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{sch_uuid}")
\t(paper "A4")
\t(title_block
\t\t(title "{title}")
\t\t(date "2026-09-14")
\t\t(rev "v1.0")
\t\t(company "FEAHI")
\t)
\t(lib_symbols)
\t(embedded_fonts no)
)
"""


def write_project(dir_path: Path, slug: str, is_core: bool) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)
    title = "Core" if is_core else "Periph"
    sch_uuid = uid()
    (dir_path / f"{slug}.kicad_pcb").write_text(build_pcb(slug, is_core), encoding="utf-8")
    (dir_path / f"{slug}.kicad_sch").write_text(
        kicad_sch(f"FEAHI-CBI-40 {title}", sch_uuid), encoding="utf-8"
    )
    pro = kicad_pro(slug, sch_uuid)
    (dir_path / f"{slug}.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_project(ROOT / "feahi_cbi40_core", "feahi_cbi40_core", is_core=True)
    write_project(ROOT / "feahi_cbi40_periph", "feahi_cbi40_periph", is_core=False)
    print(f"KiCad 10 templates generated under {ROOT}")


if __name__ == "__main__":
    main()
