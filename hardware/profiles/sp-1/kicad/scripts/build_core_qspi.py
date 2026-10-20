#!/usr/bin/env python3
"""Generate core.kicad_sch with U1 RP2350A and U4 W25Q32 on QMI/QSPI nets."""
from __future__ import annotations

import uuid
from pathlib import Path

CORE_SCH = Path(__file__).resolve().parent.parent / "core.kicad_sch"
SHEET_UUID = "40d7a410-5baa-4881-9a97-c817a97af2f2"
PROJECT_PATH = (
    "/9db6c40e-5a8d-45e3-b2cb-b13319d490f7/"
    "83ec0715-e78c-4f89-835e-302fe291db77"
)

U1_POS = (110.0, 130.0)
U4_POS = (165.0, 130.0)

# RP2350A left-side QSPI pins: (rel_x, rel_y, length) -> connection at (rel_x - L, rel_y)
RP2350_QSPI = {
    "60": (-25.4, 5.08, 3.81),   # ~{QSPI_SS}
    "56": (-25.4, 2.54, 3.81),   # QSPI_SCLK
    "57": (-25.4, 0.0, 3.81),    # QSPI_SD0
    "59": (-25.4, -2.54, 3.81),  # QSPI_SD1
    "58": (-25.4, -5.08, 3.81),  # QSPI_SD2
    "55": (-25.4, -7.62, 3.81),  # QSPI_SD3
}

# W25Q left-side pins
W25Q_PINS = {
    "1": (-10.16, 7.62, 2.54),   # ~{CS}
    "6": (-10.16, 5.08, 2.54),   # CLK
    "5": (-10.16, 2.54, 2.54),   # DI/IO0
    "2": (-10.16, 0.0, 2.54),    # DO/IO1
    "3": (-10.16, -2.54, 2.54),  # ~{WP}/IO2
    "7": (-10.16, -5.08, 2.54),  # ~{HOLD}/IO3
    "4": (0.0, -12.7, 2.54),     # GND (down)
    "8": (0.0, 12.7, 2.54),      # VCC (up, angle 270 in lib -> +Y)
}

# Pin mapping: RP2350 pin num -> W25Q pin num, net name
NETS = [
    ("60", "1", "QSPI_FLASH_CS"),
    ("56", "6", "QSPI_SCK"),
    ("57", "5", "QSPI_IO0"),
    ("59", "2", "QSPI_IO1"),
    ("58", "3", "QSPI_IO2"),
    ("55", "7", "QSPI_IO3"),
]


def uid() -> str:
    return str(uuid.uuid4())


def pin_abs(
    sym_pos: tuple[float, float],
    rel_x: float,
    rel_y: float,
    length: float,
    *,
    side: str = "left",
) -> tuple[float, float]:
    """Return electrical connection point at outward tip of pin stub."""
    sx, sy = sym_pos
    if side == "left":
        return (sx + rel_x - length, sy + rel_y)
    if side == "top":
        return (sx + rel_x, sy + rel_y - length)
    if side == "bottom":
        return (sx + rel_x, sy + rel_y + length)
    return (sx + rel_x, sy + rel_y)


def wire_segment(p1: tuple[float, float], p2: tuple[float, float]) -> str:
    x1, y1 = p1
    x2, y2 = p2
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def local_label(name: str, x: float, y: float, orient: int = 0) -> str:
    return f"""\t(label "{name}"
\t\t(at {x:.4f} {y:.4f} {orient})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def schematic_note(x: float, y: float, lines: list[str]) -> str:
    text = "\\n".join(lines)
    return f"""\t(text "{text}"
\t\t(exclude_from_sim yes)
\t\t(at {x} {y} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left top)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def power_symbol(lib_id: str, value: str, ref: str, x: float, y: float) -> str:
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x} {y + 3.81} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "{value}"
\t\t\t(at {x} {y - 5.08} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" ""
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(pin "1"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(instances
\t\t\t(project "sp-1"
\t\t\t\t(path "{PROJECT_PATH}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def rp2350_symbol() -> str:
    pins = list(RP2350_QSPI.keys())
    pin_lines = "\n".join(f'\t\t(pin "{p}"\n\t\t\t(uuid "{uid()}")\n\t\t)' for p in pins)
    return f"""\t(symbol
\t\t(lib_id "MCU_RaspberryPi:RP2350A")
\t\t(at {U1_POS[0]} {U1_POS[1]} 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "U1"
\t\t\t(at {U1_POS[0] - 5} {U1_POS[1] - 50} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "RP2350A"
\t\t\t(at {U1_POS[0] + 5} {U1_POS[1] - 50} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "Package_DFN_QFN:QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm"
\t\t\t(at {U1_POS[0]} {U1_POS[1]} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" "https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf"
\t\t\t(at {U1_POS[0]} {U1_POS[1]} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "CORE-B MCU, QFN-60"
\t\t\t(at {U1_POS[0]} {U1_POS[1]} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
{pin_lines}
\t\t(instances
\t\t\t(project "sp-1"
\t\t\t\t(path "{PROJECT_PATH}"
\t\t\t\t\t(reference "U1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def w25q_symbol() -> str:
    pins = ["1", "2", "3", "4", "5", "6", "7", "8"]
    pin_lines = "\n".join(f'\t\t(pin "{p}"\n\t\t\t(uuid "{uid()}")\n\t\t)' for p in pins)
    ux, uy = U4_POS
    return f"""\t(symbol
\t\t(lib_id "Integrated_circuits:W25Q32J(F)VSSIQ")
\t\t(at {ux} {uy} 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "U4"
\t\t\t(at {ux - 8} {uy + 14} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "W25Q32J(F)VSSIQ"
\t\t\t(at {ux + 2} {uy + 14} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "Connectors:SOP-8"
\t\t\t(at {ux} {uy} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "编码" "03000-08000-50520"
\t\t\t(at {ux} {uy} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "名称" "存储IC"
\t\t\t(at {ux} {uy} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "规格" "SPI Flash，W25Q32JVSSIQ（卷装），SOP-8 208mil，Winbond"
\t\t\t(at {ux} {uy} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
{pin_lines}
\t\t(instances
\t\t\t(project "sp-1"
\t\t\t\t(path "{PROJECT_PATH}"
\t\t\t\t\t(reference "U4")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def main() -> None:
    parts: list[str] = []
    bus_x = 127.0

    for mcu_pin, flash_pin, net in NETS:
        mx, my, ml = RP2350_QSPI[mcu_pin]
        fx, fy, fl = W25Q_PINS[flash_pin]
        p_mcu = pin_abs(U1_POS, mx, my, ml, side="left")
        p_flash = pin_abs(U4_POS, fx, fy, fl, side="left")
        y_bus = (p_mcu[1] + p_flash[1]) / 2.0
        parts.append(wire_segment(p_mcu, (bus_x, p_mcu[1])))
        parts.append(wire_segment((bus_x, p_mcu[1]), (bus_x, p_flash[1])))
        parts.append(wire_segment((bus_x, p_flash[1]), p_flash))
        parts.append(local_label(net, bus_x + 1.27, y_bus, 0))

    parts.append(
        schematic_note(
            25.4,
            50.8,
            [
                "QSPI XIP (U1 ↔ U4):",
                "~{QSPI_SS} → ~{CS}  (QSPI_FLASH_CS / BOOTSEL)",
                "QSPI_SCLK → CLK",
                "QSPI_SD0 → DI/IO0",
                "QSPI_SD1 → DO/IO1",
                "QSPI_SD2 → ~{WP}/IO2",
                "QSPI_SD3 → ~{HOLD}/IO3",
            ],
        )
    )

    # Flash power: VCC pin up (+Y), GND pin down
    vcc_pt = pin_abs(U4_POS, 0.0, 12.7, 2.54, side="top")
    gnd_pt = pin_abs(U4_POS, 0.0, -12.7, 2.54, side="bottom")

    parts.append(power_symbol("power:+3.3V", "+3.3V", "#PWR01", vcc_pt[0], vcc_pt[1] - 7.62))
    parts.append(
        wire_segment((vcc_pt[0], vcc_pt[1] - 5.08), vcc_pt)
    )
    parts.append(power_symbol("power:GNDD", "GNDD", "#PWR02", gnd_pt[0], gnd_pt[1] + 7.62))
    parts.append(wire_segment((gnd_pt[0], gnd_pt[1] + 5.08), gnd_pt))

    body = "\n".join(
        [
            "(kicad_sch",
            "\t(version 20260306)",
            '\t(generator "build_core_qspi.py")',
            '\t(generator_version "10.0")',
            f'\t(uuid "{SHEET_UUID}")',
            '\t(paper "A4")',
            "\t(title_block",
            '\t\t(title "CORE-B")',
            '\t\t(date "2026-09-18")',
            '\t\t(rev "V0.1")',
            '\t\t(comment 1 "RP2350A XIP Flash (W25Q32) QMI wiring")',
            "\t)",
            "\t(lib_symbols)",
            *parts,
            rp2350_symbol(),
            w25q_symbol(),
            "\t(sheet_instances",
            '\t\t(path "/"',
            '\t\t\t(page "3")',
            "\t\t)",
            "\t)",
            "\t(embedded_fonts no)",
            ")",
            "",
        ]
    )
    CORE_SCH.write_text(body, encoding="utf-8")
    print(f"Wrote {CORE_SCH}")


if __name__ == "__main__":
    main()
