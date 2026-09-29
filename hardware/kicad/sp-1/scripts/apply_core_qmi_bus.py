#!/usr/bin/env python3
"""Replace parallel QSPI wires on core.kicad_sch with a KiCad group bus (U6/U7/U8)."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent / "core.kicad_sch"

BUS_X = 77.0
BUS_TAP_L = 74.46  # wire ends here; bus_entry bridges to vertical bus at BUS_X
BUS_TAP_R = 79.54
BUS_Y0 = 50.546
BUS_Y1 = 106.172

U8_LINES = [
    ("QSPI_SCK", 50.546, 58.42),
    ("QSPI_IO0", 53.086, 58.42),
    ("QSPI_IO1", 55.626, 58.42),
    ("QSPI_IO2", 58.166, 58.42),
    ("QSPI_IO3", 60.706, 58.42),
]

U6_LINES = [
    ("QSPI_SCK", 96.012, 60.706),
    ("QSPI_IO0", 98.552, 60.706),
    ("QSPI_IO1", 101.092, 60.706),
    ("QSPI_IO2", 103.632, 60.706),
    ("QSPI_IO3", 106.172, 60.706),
]

U7_LINES = [
    ("QSPI_SCK", 96.012, 86.36),
    ("QSPI_IO0", 98.552, 86.36),
    ("QSPI_IO1", 101.092, 86.36),
    ("QSPI_IO2", 103.632, 86.36),
    ("QSPI_IO3", 106.172, 86.36),
]

GROUP_BUS = "{QSPI_SCK QSPI_IO0 QSPI_IO1 QSPI_IO2 QSPI_IO3}"


def uid() -> str:
    return str(uuid.uuid4())


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
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


def bus_seg(x1: float, y1: float, x2: float, y2: float) -> str:
    return f"""\t(bus
\t\t(pts
\t\t\t(xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def bus_entry(x: float, y: float, sx: float, sy: float) -> str:
    return f"""\t(bus_entry
\t\t(at {x:.4f} {y:.4f})
\t\t(size {sx:.4f} {sy:.4f})
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def junction(x: float, y: float) -> str:
    return f"""\t(junction
\t\t(at {x:.4f} {y:.4f})
\t\t(diameter 0)
\t\t(color 0 0 0 0)
\t\t(uuid "{uid()}")
\t)"""


def label(name: str, x: float, y: float, orient: int = 0) -> str:
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


def build_qmi_graphics() -> str:
    chunks: list[str] = []

    chunks.append(
        "\t(text \"QMI XIP: group bus U6 Flash + U8 PSRAM + U7 RP2350; CS0/CS1 separate\""
        "\n\t\t(exclude_from_sim yes)"
        f"\n\t\t(at 25.4 38.1 0)"
        "\n\t\t(effects"
        "\n\t\t\t(font"
        "\n\t\t\t\t(size 1.27 1.27)"
        "\n\t\t\t)"
        "\n\t\t\t(justify left top)"
        "\n\t\t)"
        f'\n\t\t(uuid "{uid()}")'
        "\n\t)"
    )

    chunks.append(bus_seg(BUS_X, BUS_Y0, BUS_X, BUS_Y1))
    chunks.append(label(GROUP_BUS, BUS_X + 1.27, 72.0, 90))

    def add_chip(lines: list[tuple[str, float, float]], side: str) -> None:
        for net, y, pin_x in lines:
            if side == "left":
                chunks.append(wire(pin_x, y, BUS_TAP_L, y))
                chunks.append(bus_entry(BUS_TAP_L, y, 2.54, 0))
                chunks.append(label(net, (pin_x + BUS_TAP_L) / 2.0, y))
            else:
                chunks.append(wire(BUS_TAP_R, y, pin_x, y))
                chunks.append(bus_entry(BUS_TAP_R, y, -2.54, 0))
                chunks.append(label(net, (BUS_TAP_R + pin_x) / 2.0, y))

    add_chip(U8_LINES, "left")
    add_chip(U6_LINES, "left")
    add_chip(U7_LINES, "right")

    # Flash CS0 (not on shared data bus)
    chunks.append(wire(60.706, 93.472, 86.36, 93.472))
    chunks.append(label("QSPI_FLASH_CS", 73.533, 93.472))

    # PSRAM_CS: U8 CE -> U7 GPIO8
    chunks.append(junction(137.16, 80.772))
    chunks.append(wire(58.42, 48.006, 72.0, 48.006))
    chunks.append(wire(72.0, 48.006, 72.0, 80.772))
    chunks.append(wire(72.0, 80.772, 137.16, 80.772))
    chunks.append(wire(137.16, 80.772, 139.7, 80.772))
    chunks.append(label("PSRAM_CS", 58.42, 48.006))
    chunks.append(label("PSRAM_CS", 139.7, 80.772))

    return "\n".join(chunks) + "\n"


def strip_old_connectivity(text: str) -> str:
    """Remove wires/junctions/labels between lib_symbols end and first symbol instance."""
    m = re.search(
        r"\n\t\)\n\t\((?:junction|wire|label|bus|bus_entry|text)\b",
        text,
    )
    if not m:
        raise SystemExit("Could not find connectivity section in core.kicad_sch")
    start = m.start() + len("\n\t)\n")

    sym = re.search(r"\n\t\(symbol\n\t\t\(lib_id", text[start:])
    if not sym:
        raise SystemExit("Could not find symbol section")
    end = start + sym.start()

    return text[:start] + build_qmi_graphics() + text[end:]


def main() -> None:
    text = CORE.read_text(encoding="utf-8")
    out = strip_old_connectivity(text)
    CORE.write_text(out, encoding="utf-8")
    print(f"Updated {CORE} with QMI group bus.")


if __name__ == "__main__":
    main()
