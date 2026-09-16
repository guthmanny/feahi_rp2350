#!/usr/bin/env python3
"""Generate FEAHI SP-1 hierarchical schematic framework (KiCad 10).

Block-level sheets with hierarchical labels — not production-ready symbols.
Re-run after editing SHEETS dict or net lists.

Usage:
    py -3 hardware/kicad/tools/generate_schematic_framework.py
"""

from __future__ import annotations

import json
import textwrap
import uuid
from pathlib import Path

KICAD_SCH_VERSION = 20260306
ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC_DIR = ROOT.parent / "schematic"


def uid() -> str:
    return str(uuid.uuid4())


def sch_header(title: str, rev: str = "v0.1-framework") -> str:
    return f"""(kicad_sch
\t(version {KICAD_SCH_VERSION})
\t(generator "feahi_generate_schematic_framework")
\t(generator_version "1.0")
\t(uuid "{uid()}")
\t(paper "A4")
\t(title_block
\t\t(title "{title}")
\t\t(date "2026-09-14")
\t\t(rev "{rev}")
\t\t(company "FEAHI / Soran SP-1")
\t\t(comment 1 "Block diagram — replace placeholders with library symbols")
\t)
"""


def text_block(x: float, y: float, body: str, size: float = 1.5) -> str:
    lines = [ln for ln in body.strip().splitlines() if ln.strip()]
    parts: list[str] = []
    for i, line in enumerate(lines):
        safe = line.replace('"', "'")
        parts.append(
            f'\t(text "{safe}"\n'
            f"\t\t(exclude_from_sim yes)\n"
            f"\t\t(at {x:.2f} {y + i * size * 1.8:.2f} 0)\n"
            f"\t\t(effects (font (size {size} {size})) (justify left bottom))\n"
            f'\t\t(uuid "{uid()}")\n'
            f"\t)"
        )
    return "\n".join(parts)


def hierarchical_label(name: str, x: float, y: float, shape: str, angle: int = 0) -> str:
    return f"""\t(hierarchical_label "{name}"
\t\t(shape {shape})
\t\t(at {x:.2f} {y:.2f} {angle})
\t\t(effects (font (size 1.27 1.27)) (justify left))
\t\t(uuid "{uid()}")
\t)"""


def sheet_symbol(
    x: float,
    y: float,
    w: float,
    h: float,
    sheet_name: str,
    sheet_file: str,
    project: str,
    page: str,
    pins: list[tuple[str, str, float, float, int]],
) -> str:
    pin_lines: list[str] = []
    for pin_name, pin_type, px, py, angle in pins:
        pin_lines.append(
            f'\t\t(pin "{pin_name}" {pin_type}\n'
            f"\t\t\t(at {px:.2f} {py:.2f} {angle})\n"
            f"\t\t\t(effects (font (size 1.27 1.27)) (justify left))\n"
            f'\t\t\t(uuid "{uid()}")\n'
            f"\t\t)"
        )
    pins_txt = "\n".join(pin_lines)
    return f"""\t(sheet
\t\t(at {x:.2f} {y:.2f})
\t\t(size {w:.2f} {h:.2f})
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(stroke (width 0.1524) (type solid))
\t\t(fill (color 0 0 0 0.0000))
\t\t(uuid "{uid()}")
\t\t(property "Sheetname" "{sheet_name}"
\t\t\t(at {x:.2f} {y - 0.5:.2f} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom))
\t\t)
\t\t(property "Sheetfile" "{sheet_file}"
\t\t\t(at {x:.2f} {y + h + 0.5:.2f} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects (font (size 1.27 1.27)) (justify left top))
\t\t)
{pins_txt}
\t\t(instances
\t\t\t(project "{project}"
\t\t\t\t(path "/{uid()}"
\t\t\t\t\t(page "{page}")
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        f'\t(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))\n'
        f'\t\t(stroke (width 0) (type default))\n'
        f'\t\t(uuid "{uid()}")\n'
        f"\t)"
    )


def label(name: str, x: float, y: float, angle: int = 0) -> str:
    return (
        f'\t(label "{name}"\n'
        f"\t\t(at {x:.2f} {y:.2f} {angle})\n"
        f"\t\t(effects (font (size 1.27 1.27)) (justify left))\n"
        f'\t\t(uuid "{uid()}")\n'
        f"\t)"
    )


def build_subsheet(
    title: str,
    description: str,
    out_labels: list[tuple[str, float, float]],
    in_labels: list[tuple[str, float, float]],
    bidir_labels: list[tuple[str, float, float]] | None = None,
) -> str:
    bidir_labels = bidir_labels or []
    parts = [sch_header(title)]
    parts.append(text_block(25, 25, description, size=1.8))
    y = 60.0
    for name, x, ly in out_labels:
        parts.append(hierarchical_label(name, x, ly, "output"))
    for name, x, ly in in_labels:
        parts.append(hierarchical_label(name, x, ly, "input"))
    for name, x, ly in bidir_labels:
        parts.append(hierarchical_label(name, x, ly, "bidirectional"))
    parts.append("\t(lib_symbols)")
    parts.append("\t(embedded_fonts no)")
    parts.append(")\n")
    return "\n".join(parts)


def build_root(title: str, project: str, sheets: list[dict]) -> str:
    parts = [sch_header(title)]
    parts.append(
        text_block(
            20,
            15,
            "SP-1 schematic framework (方案 C)\n"
            "Replace blocks with KiCad library symbols.\n"
            f"Netlists: hardware/schematic/",
            size=1.6,
        )
    )
    page = 2
    for sh in sheets:
        pins = sh.get("pins", [])
        parts.append(
            sheet_symbol(
                sh["x"],
                sh["y"],
                sh["w"],
                sh["h"],
                sh["name"],
                sh["file"],
                project,
                str(page),
                pins,
            )
        )
        page += 1
    parts.append("\t(lib_symbols)")
    parts.append('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)')
    parts.append("\t(embedded_fonts no)")
    parts.append(")\n")
    return "\n".join(parts)


CORE_SHEETS = [
    {
        "name": "MCU",
        "file": "core_mcu.kicad_sch",
        "x": 30,
        "y": 50,
        "w": 40,
        "h": 30,
        "desc": textwrap.dedent(
            """
            U1  RP2350 (QFN-80)
            U2  APS6404L-3SQR-SN 8MB PSRAM (QSPI)
            Y1  24.576 MHz → I2S MCLK

            Placeholders:
            - Decoupling 100nF per power pin
            - QSPI to PSRAM (match feahi_pico)
            - I2S0 → hierarchical to CBI sheet
            - UART → IPC (CBI)
            """
        ),
        "out": [
            ("I2S_MCLK", 180, 70),
            ("I2S_BCLK", 180, 75),
            ("I2S_LRCLK", 180, 80),
            ("I2S_DOUT", 180, 85),
            ("I2S_DIN", 180, 90),
            ("IPC_TX", 180, 95),
            ("IPC_RX", 180, 100),
            ("MIDI_TX", 180, 105),
            ("MIDI_RX", 180, 110),
            ("DEBUG_TX", 180, 115),
            ("DEBUG_RX", 180, 120),
            ("+3V3", 180, 125),
            ("GND", 180, 130),
        ],
        "in": [("VBAT", 30, 70), ("AUD_BOOT", 30, 75)],
    },
    {
        "name": "NAND",
        "file": "core_nand.kicad_sch",
        "x": 85,
        "y": 50,
        "w": 35,
        "h": 25,
        "desc": textwrap.dedent(
            """
            U3  W25N01GV (SPI NAND 1Gb)
            SPI from RP2350 — stays on Core only

            CS / CLK / IO0-3
            Do NOT route to CBI
            """
        ),
        "out": [("+3V3", 180, 70), ("GND", 180, 75)],
        "in": [],
    },
    {
        "name": "USB",
        "file": "core_usb.kicad_sch",
        "x": 30,
        "y": 95,
        "w": 35,
        "h": 25,
        "desc": textwrap.dedent(
            """
            J-USB  USB-C 2.0 (USB device / BOOT)
            RP2350 native USB
            ESD + 5.1k CC (device) or IDF HW design guide
            """
        ),
        "out": [("GND", 180, 70)],
        "in": [("+5V", 30, 70)],
    },
    {
        "name": "Power",
        "file": "core_power.kicad_sch",
        "x": 85,
        "y": 95,
        "w": 35,
        "h": 25,
        "desc": textwrap.dedent(
            """
            VBAT from CBI → DCDC → 3.3V LDO
            Feed CBI Pin4 (+3V3) to Periph
            Bulk 10uF + 100nF at LDO out
            """
        ),
        "out": [("+3V3", 180, 70), ("GND", 180, 75)],
        "in": [("VBAT", 30, 70), ("+5V", 30, 75)],
    },
    {
        "name": "CBI40",
        "file": "core_cbi.kicad_sch",
        "x": 130,
        "y": 50,
        "w": 45,
        "h": 70,
        "desc": textwrap.dedent(
            """
            J1  FEAHI-CBI-40 v0.3 (castellation bottom)
            See hardware/kicad/cbi40_pinout.csv

            Audio + IPC + MIDI cross to PERIPH-1
            NO LCD / NO I2C keyboard on CBI
            """
        ),
        "out": [
            ("I2S_MCLK", 30, 65),
            ("I2S_BCLK", 30, 70),
            ("I2S_LRCLK", 30, 75),
            ("I2S_DOUT", 30, 80),
            ("I2S_DIN", 30, 85),
            ("IPC_TX", 30, 90),
            ("MIDI_TX", 30, 95),
            ("DEBUG_TX", 30, 100),
            ("+3V3", 30, 105),
            ("SPK_MUTE", 30, 110),
        ],
        "in": [
            ("VBAT", 180, 65),
            ("+5V", 180, 70),
            ("I2S_DIN", 180, 75),
            ("IPC_RX", 180, 80),
            ("MIDI_RX", 180, 85),
            ("DEBUG_RX", 180, 90),
            ("HP_DETECT", 180, 95),
            ("AUD_BOOT", 180, 100),
            ("GND", 180, 105),
        ],
    },
]

PERIPH_SHEETS = [
    {
        "name": "C6_MCU",
        "file": "periph_c6.kicad_sch",
        "x": 25,
        "y": 45,
        "w": 42,
        "h": 35,
        "desc": textwrap.dedent(
            """
            U1  ESP32-C6-MINI-1 (4MB flash)
            GPIO map: hardware/schematic/c6_gpio.csv

            IPC UART0: GPIO16 TX / GPIO17 RX
            I2C: GPIO6/7 → UI sheet
            8080 LCD: see periph_lcd sheet
            """
        ),
        "out": [
            ("IPC_TX", 180, 70),
            ("I2C_SDA", 180, 75),
            ("I2C_SCL", 180, 80),
            ("LCD_DB0", 180, 85),
            ("LCD_DB1", 180, 90),
            ("LCD_DB2", 180, 95),
            ("LCD_DB3", 180, 100),
            ("LCD_DB4", 180, 105),
            ("LCD_DB5", 180, 110),
            ("LCD_DB6", 180, 115),
            ("LCD_DB7", 180, 120),
            ("LCD_WR", 180, 125),
            ("LCD_RS", 180, 130),
            ("LCD_CS", 180, 135),
            ("LCD_RST", 180, 140),
            ("LCD_BL", 180, 145),
            ("+3V3", 180, 150),
            ("GND", 180, 155),
        ],
        "in": [
            ("IPC_RX", 30, 70),
            ("C6_BOOT", 30, 75),
            ("I2C_INT", 30, 80),
            ("ENC_A", 30, 85),
            ("ENC_B", 30, 90),
            ("ENC_SW", 30, 95),
            ("+3V3", 30, 100),
            ("GND", 30, 105),
        ],
    },
    {
        "name": "LCD",
        "file": "periph_lcd.kicad_sch",
        "x": 75,
        "y": 45,
        "w": 40,
        "h": 35,
        "desc": textwrap.dedent(
            """
            J-LCD  FPC for TFT020B107-C0 (JME-01)
            2" 240×320 ST7789P3 8080 8-bit

            RD → IOVCC (write-only)
            LEDA via PWM + limit resistor
            Keep FPC ≤15mm from C6
            """
        ),
        "out": [],
        "in": [
            ("LCD_DB0", 30, 70),
            ("LCD_DB1", 30, 75),
            ("LCD_DB2", 30, 80),
            ("LCD_DB3", 30, 85),
            ("LCD_DB4", 30, 90),
            ("LCD_DB5", 30, 95),
            ("LCD_DB6", 30, 100),
            ("LCD_DB7", 30, 105),
            ("LCD_WR", 30, 110),
            ("LCD_RS", 30, 115),
            ("LCD_CS", 30, 120),
            ("LCD_RST", 30, 125),
            ("LCD_BL", 30, 130),
            ("+3V3", 30, 135),
            ("GND", 30, 140),
        ],
    },
    {
        "name": "Audio",
        "file": "periph_audio.kicad_sch",
        "x": 25,
        "y": 90,
        "w": 45,
        "h": 40,
        "desc": textwrap.dedent(
            """
            U-ADC  MS1808  Mic/Line → I2S_DIN
            U-DAC  MS4344  I2S_DOUT → analog OUT
            VOL    10k log pot → Amp / TRS
            U-AMP  Class-D 5W + SPK_MUTE

            MS1808 analog 5V / digital 3.3V
            I2S bus shared MCLK/BCLK/LRCLK
            """
        ),
        "out": [
            ("I2S_DIN", 180, 70),
            ("HP_DETECT", 180, 75),
            ("LINE_OUT_L", 180, 80),
            ("LINE_OUT_R", 180, 85),
            ("SPK+", 180, 90),
            ("SPK-", 180, 95),
            ("GND", 180, 100),
        ],
        "in": [
            ("I2S_MCLK", 30, 65),
            ("I2S_BCLK", 30, 70),
            ("I2S_LRCLK", 30, 75),
            ("I2S_DOUT", 30, 80),
            ("SPK_MUTE", 30, 85),
            ("MIC_P", 30, 90),
            ("LINE_IN_L", 30, 95),
            ("LINE_IN_R", 30, 100),
            ("+3V3", 30, 105),
            ("+5V", 30, 110),
        ],
    },
    {
        "name": "UI",
        "file": "periph_ui.kicad_sch",
        "x": 80,
        "y": 90,
        "w": 38,
        "h": 35,
        "desc": textwrap.dedent(
            """
            U-KB   TCA8418 I2C keypad (0x34)
            U-LED  IS31FL3733 I2C LED (0x55)
            SW     Matrix pads + PWR via TCA
            ENC    Quadrature → C6 GPIO12/13/8

            All I2C board-only (not on CBI)
            """
        ),
        "out": [
            ("I2C_INT", 180, 70),
            ("ENC_A", 180, 75),
            ("ENC_B", 180, 80),
            ("ENC_SW", 180, 85),
            ("GND", 180, 90),
        ],
        "in": [
            ("I2C_SDA", 30, 70),
            ("I2C_SCL", 30, 75),
            ("+3V3", 30, 80),
        ],
    },
    {
        "name": "Power",
        "file": "periph_power.kicad_sch",
        "x": 125,
        "y": 45,
        "w": 38,
        "h": 35,
        "desc": textwrap.dedent(
            """
            BAT   Li-ion + charger (USB-C)
            PMIC  → VBAT to CBI
            Boost 5V for Amp / LEDA
            LDO 2.8/3.3 for LCD IOVCC if needed
            """
        ),
        "out": [
            ("VBAT", 180, 70),
            ("+5V", 180, 75),
            ("+3V3", 180, 80),
            ("GND", 180, 85),
        ],
        "in": [("GND", 30, 70)],
    },
    {
        "name": "Connectors",
        "file": "periph_conn.kicad_sch",
        "x": 125,
        "y": 90,
        "w": 38,
        "h": 35,
        "desc": textwrap.dedent(
            """
            J-MIDI  DIN-5 IN/OUT (opto)
            J-TRS   3.5mm IN/OUT
            J-MIC   ECM capsule
            J-SPK   Speaker pads

            MIDI UART ↔ CBI (Core RP2350)
            """
        ),
        "out": [
            ("MIDI_TX", 180, 70),
            ("MIDI_RX", 180, 75),
            ("HP_DETECT", 180, 80),
            ("MIC_P", 180, 85),
            ("LINE_IN_L", 180, 90),
            ("LINE_IN_R", 180, 95),
            ("GND", 180, 100),
        ],
        "in": [
            ("LINE_OUT_L", 30, 70),
            ("LINE_OUT_R", 30, 75),
            ("SPK+", 30, 80),
            ("SPK-", 30, 85),
        ],
    },
    {
        "name": "CBI40",
        "file": "periph_cbi.kicad_sch",
        "x": 170,
        "y": 45,
        "w": 45,
        "h": 70,
        "desc": textwrap.dedent(
            """
            J1  FEAHI-CBI-40 v0.3 (SMD pads top)
            mates CORE-B / CORE-A

            I2S + IPC + MIDI + power
            """
        ),
        "out": [
            ("VBAT", 30, 65),
            ("+5V", 30, 70),
            ("I2S_DIN", 30, 75),
            ("IPC_TX", 30, 80),
            ("MIDI_TX", 30, 85),
            ("HP_DETECT", 30, 90),
            ("GND", 30, 95),
        ],
        "in": [
            ("+3V3", 180, 65),
            ("I2S_MCLK", 180, 70),
            ("I2S_BCLK", 180, 75),
            ("I2S_LRCLK", 180, 80),
            ("I2S_DOUT", 180, 85),
            ("IPC_RX", 180, 90),
            ("C6_BOOT", 180, 95),
            ("MIDI_RX", 180, 100),
            ("DEBUG_TX", 180, 105),
            ("DEBUG_RX", 180, 110),
            ("SPK_MUTE", 180, 115),
            ("AUD_BOOT", 180, 120),
            ("GND", 180, 125),
        ],
    },
]


def write_project(
    slug: str,
    title: str,
    sheet_defs: list[dict],
) -> None:
    proj_dir = ROOT / slug
    sheets_dir = proj_dir / "sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)

    root_sheets = []
    for i, sd in enumerate(sheet_defs):
        sub_path = sheets_dir / sd["file"]
        sub_path.write_text(
            build_subsheet(
                f"{title} / {sd['name']}",
                sd["desc"],
                sd.get("out", []),
                sd.get("in", []),
                sd.get("bidir", []),
            ),
            encoding="utf-8",
        )
        rel_file = f"sheets/{sd['file']}"
        root_sheets.append(
            {
                "x": sd.get("root_x", 25 + (i % 3) * 55),
                "y": sd.get("root_y", 45 + (i // 3) * 50),
                "w": 38,
                "h": 28,
                "name": sd["name"],
                "file": rel_file,
                "pins": [],
            }
        )

    root_path = proj_dir / f"{slug}.kicad_sch"
    root_path.write_text(
        build_root(title, slug, root_sheets),
        encoding="utf-8",
    )

    pro_path = proj_dir / f"{slug}.kicad_pro"
    if pro_path.exists():
        pro = json.loads(pro_path.read_text(encoding="utf-8"))
    else:
        pro = {"meta": {"filename": f"{slug}.kicad_pro", "version": 3}}
    sch_uuid = pro.get("schematic", {}).get("top_level_sheets", [{}])[0].get(
        "uuid", uid()
    )
    pro["schematic"] = {
        "legacy_lib_dir": "",
        "legacy_lib_list": [],
        "meta": {"version": 1},
        "top_level_sheets": [
            {
                "filename": f"{slug}.kicad_sch",
                "name": slug,
                "uuid": sch_uuid,
            }
        ],
    }
    pro_path.write_text(json.dumps(pro, indent=2) + "\n", encoding="utf-8")
    print(f"  {slug}: root + {len(sheet_defs)} sub-sheets")


def main() -> None:
    print("Generating schematic framework...")
    write_project("feahi_cbi40_core", "CORE-B (RP2350)", CORE_SHEETS)
    write_project("feahi_cbi40_periph", "PERIPH-1 (C6+8080)", PERIPH_SHEETS)
    print(f"Netlists: {SCHEMATIC_DIR}")
    print("Done. Open .kicad_pro in KiCad 10 → import sheet pins on each block.")


if __name__ == "__main__":
    main()
