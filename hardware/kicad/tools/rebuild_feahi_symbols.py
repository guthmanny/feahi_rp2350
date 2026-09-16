#!/usr/bin/env python3
"""Rebuild feahi.kicad_sym with PCM1808, MS1808, and OR-M611."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBS = ROOT / "libs" / "symbols"
OUT = LIBS / "feahi.kicad_sym"
SCH = ROOT / "feahi_cbi40_periph" / "sheets" / "periph_conn.kicad_sch"

SCH_CANDIDATES = [
    Path(r"C:\Users\guthm\Downloads\stereo-audio-adc-interface-pcm1808-smalldsp.kicad_sch"),
    Path(r"C:\Users\guthm\Downloads\1_Project_Symbols.kicad_sym"),
]

WEIKE_OR_M611 = "03000-06000-04320"
PART_OR_M611 = "OR-M611-TP-G-(HB)"


def extract_sexpr_block(text: str, start: int) -> str:
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise ValueError("unbalanced parentheses")


def normalize_library_symbol(block: str, name: str) -> str:
    block = re.sub(r'^\(symbol "[^"]+"', f'(symbol "{name}"', block, count=1)
    lines = block.splitlines()
    lines[0] = "\t" + lines[0].lstrip()
    for i in range(1, len(lines)):
        if lines[i].startswith("\t"):
            lines[i] = lines[i][1:]
    return "\n".join(lines)


def from_sch(sch_path: Path) -> str:
    text = sch_path.read_text(encoding="utf-8")
    marker = '(symbol "1_Project_Symbols:PCM1808"'
    idx = text.find(marker)
    if idx < 0:
        marker = '(symbol "PCM1808"'
        idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f"PCM1808 not found in {sch_path}")
    return normalize_library_symbol(extract_sexpr_block(text, idx), "PCM1808")


def ms1808_alias(pcm1808: str) -> str:
    block = pcm1808.replace('"PCM1808"', '"MS1808"', 1)
    block = re.sub(r'"Value" "PCM1808"', '"Value" "MS1808"', block, count=1)
    block = block.replace('"PCM1808_0_1"', '"MS1808_0_1"')
    block = block.replace('"PCM1808_1_1"', '"MS1808_1_1"')
    return block


def or_m611_from_periph() -> str:
    text = SCH.read_text(encoding="utf-8")
    marker = '(symbol "feahi:OR-M611"'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit("embedded feahi:OR-M611 not found")
    block = extract_sexpr_block(text, idx)
    block = block.replace('"feahi:OR-M611"', '"OR-M611"', 1)
    block = block.replace('"Part Number" "OR-M611"', f'"Part Number" "{PART_OR_M611}"', 1)
    if "Weike Code" not in block:
        insert_at = block.find('\t\t\t(symbol "OR-M611_0_1"')
        if insert_at < 0:
            raise SystemExit("OR-M611 graphic sub-symbol not found")
        prop = (
            '\t\t\t(property "Weike Code" "' + WEIKE_OR_M611 + '"\n'
            "\t\t\t\t(at 0 40.64 0)\n"
            "\t\t\t\t(show_name no)\n"
            "\t\t\t\t(do_not_autoplace no)\n"
            "\t\t\t\t(hide yes)\n"
            "\t\t\t\t(effects\n"
            "\t\t\t\t\t(font\n"
            "\t\t\t\t\t\t(size 1.27 1.27)\n"
            "\t\t\t\t\t)\n"
            "\t\t\t\t)\n"
            "\t\t\t)\n"
        )
        block = block[:insert_at] + prop + block[insert_at:]
    return normalize_library_symbol(block, "OR-M611")


def build_lib(*symbols: str) -> str:
    body = "\n".join(symbols)
    return (
        "(kicad_symbol_lib\n"
        "\t(version 20231120)\n"
        '\t(generator "feahi_rebuild_symbols")\n'
        '\t(generator_version "1.0")\n'
        f"{body}\n"
        ")\n"
    )


def main() -> None:
    sch_path = next((p for p in SCH_CANDIDATES if p.exists()), None)
    if sch_path is None:
        raise SystemExit("No PCM1808 source found in Downloads")

    pcm1808 = from_sch(sch_path)
    ms1808 = ms1808_alias(pcm1808)
    or_m611 = or_m611_from_periph()

    LIBS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_lib(pcm1808, ms1808, or_m611), encoding="utf-8")
    print(f"Rebuilt {OUT}")
    print("  Symbols: PCM1808, MS1808, OR-M611")


if __name__ == "__main__":
    main()
