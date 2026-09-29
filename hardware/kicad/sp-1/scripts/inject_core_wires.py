#!/usr/bin/env python3
"""Insert QSPI wires between U6 (W25Q) and U7 (RP2350A) in core.kicad_sch."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent / "core.kicad_sch"

U7_POS = (111.76, 98.552)
U6_POS = (52.832, 100.33)

RP2350_QSPI = {
    "60": (-25.4, 5.08, 3.81),
    "56": (-25.4, 2.54, 3.81),
    "57": (-25.4, 0.0, 3.81),
    "59": (-25.4, -2.54, 3.81),
    "58": (-25.4, -5.08, 3.81),
    "55": (-25.4, -7.62, 3.81),
}
W25Q = {
    "1": (-10.16, 7.62, 2.54),
    "6": (-10.16, 5.08, 2.54),
    "5": (-10.16, 2.54, 2.54),
    "2": (-10.16, 0.0, 2.54),
    "3": (-10.16, -2.54, 2.54),
    "7": (-10.16, -5.08, 2.54),
}
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


def pin_connect(sym: tuple[float, float], rel_x: float, rel_y: float, length: float) -> tuple[float, float]:
    """Eeschema connection point is the pin (at) anchor for line pins."""
    sx, sy = sym
    del length
    return (round(sx + rel_x, 4), round(sy + rel_y, 4))


def wire(p1: tuple[float, float], p2: tuple[float, float]) -> str:
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {p1[0]} {p1[1]}) (xy {p2[0]} {p2[1]})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def label(name: str, x: float, y: float) -> str:
    return f"""\t(label "{name}"
\t\t(at {x:.4f} {y:.4f} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def main() -> None:
    text = CORE.read_text(encoding="utf-8")
    if "(wire" in text:
        text = re.sub(r"\t\(wire[\s\S]*?\n\t\)\n", "", text)
        text = re.sub(r"\t\(label \"QSPI_[^\"]+\"[\s\S]*?\n\t\)\n", "", text)
        text = re.sub(r"\t\(junction[\s\S]*?\n\t\)\n", "", text)

    blocks: list[str] = []
    bus_x = 72.0

    for mcu_p, flash_p, net in NETS:
        mx, my, ml = RP2350_QSPI[mcu_p]
        fx, fy, fl = W25Q[flash_p]
        p7 = pin_connect(U7_POS, mx, my, ml)
        p6 = pin_connect(U6_POS, fx, fy, fl)
        # U6 west of U7: route U6 pin -> east -> bus -> U7 pin
        blocks.append(wire(p6, (bus_x, p6[1])))
        blocks.append(wire((bus_x, p6[1]), (bus_x, p7[1])))
        blocks.append(wire((bus_x, p7[1]), p7))
        blocks.append(label(net, bus_x + 1.27, (p6[1] + p7[1]) / 2))

    insert = "\n".join(blocks) + "\n"
    marker = '\t(symbol\n\t\t(lib_id "MCU_RaspberryPi:RP2350A")'
    if marker not in text:
        raise SystemExit("U7 symbol anchor not found")
    text = text.replace(marker, insert + marker, 1)

    if "(sheet_instances" not in text:
        text = text.rstrip()
        if text.endswith(")"):
            text = text[:-1]
        text += """
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "3")
\t\t)
\t)
\t(embedded_fonts no)
)
"""

    CORE.write_text(text, encoding="utf-8")
    print(f"Injected {len(NETS) * 3} wire segments into {CORE}")


if __name__ == "__main__":
    main()
