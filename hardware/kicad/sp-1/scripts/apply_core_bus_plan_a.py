#!/usr/bin/env python3
"""Plan A: QMI bus_alias + {QMI} label; FLASH_CS off bus (core.kicad_sch)."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent / "core.kicad_sch"

BUS_ALIAS_BLOCK = """\t(bus_alias "QMI"
\t\t(members "QSPI_SCLK" "QSPI_SD0" "QSPI_SD1" "QSPI_SD2" "QSPI_SD3")
\t)
"""

# Horizontal QMI trunk in current core layout (KiCad grid 2.54 mm).
BUS_H_Y = 88.9
BUS_H_X0 = 85.09
BUS_H_X1 = 120.65
BUS_LABEL_X = (BUS_H_X0 + BUS_H_X1) / 2.0

BUS_LABEL = """\t(label "{{QMI}}"
\t\t(at {x:.4f} {y:.4f} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uuid}")
\t)"""

CS_BUS_ENTRIES = frozenset({(84.836, 94.488), (84.836, 97.028), (121.158, 93.726)})

CS_WIRE_UUIDS = frozenset(
    {
        "24ad6d66-7ffd-4be0-8b8e-321d4a02af30",
        "90382c6a-58d1-40ab-a2b1-7a4dca7b072f",
    }
)

BUS_ENTRY_BLOCK = re.compile(
    r"\t\(bus_entry\n"
    r"\t\t\(at (?P<x>[-0-9.]+) (?P<y>[-0-9.]+)\)\n"
    r"\t\t\(size [^\n]+\n"
    r"\t\t\(stroke\n"
    r"\t\t\t\(width 0\)\n"
    r"\t\t\t\(type default\)\n"
    r"\t\t\)\n"
    r"\t\t\(uuid \"[a-f0-9-]+\"\)\n"
    r"\t\)\n",
    re.MULTILINE,
)

WIRE_BLOCK = re.compile(
    r"\t\(wire\n"
    r"(?:.*?\n)*?"
    r"\t\t\(uuid \"(?P<u>[a-f0-9-]+)\"\)\n"
    r"\t\)\n",
    re.MULTILINE,
)

LABEL_FLASH = re.compile(
    r"\t\(label \"FLASH_CS\"\n"
    r"\t\t\(at (?P<x>[-0-9.]+) (?P<y>[-0-9.]+)[^\n]*\n"
    r"(?:.*?\n)*?"
    r"\t\t\(uuid \"[a-f0-9-]+\"\)\n"
    r"\t\)\n",
    re.MULTILINE,
)


def uid() -> str:
    return str(uuid.uuid4())


def flash_cs_wires() -> str:
    return f"""\t(wire
\t\t(pts
\t\t\t(xy 72.3900 97.0280) (xy 128.0000 97.0280)
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)
\t(wire
\t\t(pts
\t\t\t(xy 128.0000 97.0280) (xy 128.0000 93.7260)
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)
\t(wire
\t\t(pts
\t\t\t(xy 128.0000 93.7260) (xy 133.6040 93.7260)
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)
\t(label "FLASH_CS"
\t\t(at 100.0000 97.0280 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def add_bus_alias(text: str) -> str:
    if '(bus_alias "QMI"' in text:
        return text
    anchor = "\t(embedded_fonts no)\n\t\t)\n\t)\n"
    idx = text.find(anchor)
    if idx < 0:
        raise SystemExit("lib_symbols end not found.")
    insert_at = idx + len(anchor)
    return text[:insert_at] + BUS_ALIAS_BLOCK + text[insert_at:]


def ensure_bus_label(text: str) -> str:
    lbl = BUS_LABEL.format(x=BUS_LABEL_X, y=BUS_H_Y, uuid=uid())
    if '(label "{QMI}"' in text:
        text = re.sub(
            r'\(label "\{QMI\}"\n\t\t\(at [^\n]+\n',
            f'(label "{{QMI}}"\n\t\t(at {BUS_LABEL_X:.4f} {BUS_H_Y:.4f} 0)\n',
            text,
            count=1,
        )
        return text
    # Replace legacy inline group label if present.
    text = re.sub(
        r'\t\(label "\{QSPI_SCLK QSPI_SD0 QSPI_SD1 QSPI_SD2 QSPI_SD3\}"\n'
        r"\t\t\(at [^\n]+\n"
        r"\t\t\(effects\n"
        r"\t\t\t\(font\n"
        r"\t\t\t\t\(size 1\.27 1\.27\)\n"
        r"\t\t\t\)\n"
        r"\t\t\t\(justify left bottom\)\n"
        r"\t\t\)\n"
        r'\t\t\(uuid "[a-f0-9-]+"\)\n'
        r"\t\)\n",
        lbl + "\n",
        text,
        count=1,
    )
    if '(label "{QMI}"' not in text:
        m = re.search(
            rf"(\t\(bus\n\t\t\(pts\n\t\t\t\(xy {BUS_H_X0:g} {BUS_H_Y:g}\) \(xy {BUS_H_X1:g} {BUS_H_Y:g}\)\n"
            r"\t\t\)\n\t\t\(stroke\n\t\t\t\(width 0\)\n\t\t\t\(type default\)\n"
            r"\t\t\)\n\t\t\(uuid \"[a-f0-9-]+\"\)\n\t\)\n)",
            text,
        )
        if not m:
            raise SystemExit("Horizontal QMI bus not found.")
        text = text[: m.end()] + "\n" + lbl + "\n" + text[m.end() :]
    return text


def remove_all_bus_entries(text: str) -> str:
    """Bus entries are optional; removing them avoids 'wire not at entry' ERC."""
    return BUS_ENTRY_BLOCK.sub("", text)


def remove_cs_bus_entries(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        x, y = float(m.group("x")), float(m.group("y"))
        for cx, cy in CS_BUS_ENTRIES:
            if abs(x - cx) < 0.001 and abs(y - cy) < 0.001:
                return ""
        return m.group(0)

    return BUS_ENTRY_BLOCK.sub(repl, text)


def extend_left_bus_for_u8_sclk(text: str) -> str:
    return text.replace(
        f"(xy {BUS_H_X0:g} 68.58) (xy {BUS_H_X0:g} {BUS_H_Y:g})",
        f"(xy {BUS_H_X0:g} 66.04) (xy {BUS_H_X0:g} {BUS_H_Y:g})",
        1,
    )


def remove_cs_wires(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return "" if m.group("u") in CS_WIRE_UUIDS else m.group(0)

    return WIRE_BLOCK.sub(repl, text)


def remove_cs_stub_labels(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        x, y = float(m.group("x")), float(m.group("y"))
        if (abs(x - 82.296) < 0.001 and abs(y - 97.028) < 0.001) or (
            abs(x - 123.698) < 0.001 and abs(y - 93.726) < 0.001
        ):
            return ""
        return m.group(0)

    return LABEL_FLASH.sub(repl, text)


def trim_right_bus(text: str) -> str:
    seg = re.compile(
        r"\t\(bus\n"
        r"\t\t\(pts\n"
        r"\t\t\t\(xy 121\.158 88\.9\) \(xy 121\.158 93\.726\)\n"
        r"\t\t\)\n"
        r"\t\t\(stroke\n"
        r"\t\t\t\(width 0\)\n"
        r"\t\t\t\(type default\)\n"
        r"\t\t\)\n"
        r"\t\t\(uuid \"[a-f0-9-]+\"\)\n"
        r"\t\)\n",
        re.MULTILINE,
    )
    text, _ = seg.subn("", text, count=1)
    return text.replace(
        "(xy 121.158 93.726) (xy 121.158 98.806)",
        "(xy 121.158 96.266) (xy 121.158 98.806)",
        1,
    )


def add_flash_cs_route(text: str) -> str:
    if "128.0000 97.0280" in text:
        return text
    m = re.search(r"\n\t\(label \"PSRAM_CS\"", text)
    if not m:
        raise SystemExit("Insert point for FLASH_CS not found.")
    return text[: m.start()] + "\n" + flash_cs_wires() + text[m.start() :]


def main() -> None:
    text = CORE.read_text(encoding="utf-8")
    text = add_bus_alias(text)
    text = ensure_bus_label(text)
    text = remove_cs_bus_entries(text)
    text = trim_right_bus(text)
    text = remove_cs_wires(text)
    text = remove_cs_stub_labels(text)
    text = add_flash_cs_route(text)
    text = extend_left_bus_for_u8_sclk(text)
    text = remove_all_bus_entries(text)
    CORE.write_text(text, encoding="utf-8")
    print(f"Applied Plan A to {CORE}")


if __name__ == "__main__":
    main()
