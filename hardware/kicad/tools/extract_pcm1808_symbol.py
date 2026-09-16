#!/usr/bin/env python3
"""Extract PCM1808 symbol into project feahi.kicad_sym."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBS = ROOT / "libs" / "symbols"
OUT = LIBS / "feahi.kicad_sym"

SCH_CANDIDATES = [
    Path(r"C:\Users\guthm\Downloads\stereo-audio-adc-interface-pcm1808-smalldsp.kicad_sch"),
    Path(r"C:\Users\guthm\Downloads\1_Project_Symbols.kicad_sym"),
]


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


def from_sch(sch_path: Path) -> str:
    text = sch_path.read_text(encoding="utf-8")
    marker = '(symbol "1_Project_Symbols:PCM1808"'
    idx = text.find(marker)
    if idx < 0:
        marker = '(symbol "PCM1808"'
        idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f"PCM1808 not found in {sch_path}")
    block = extract_sexpr_block(text, idx)
    # Drop library prefix for project-local symbol name
    block = block.replace('"1_Project_Symbols:PCM1808"', '"PCM1808"', 1)
    block = block.replace('"PCM1808_0_1"', '"PCM1808_0_1"', 1)
    return block


def from_html_blob(html_path: Path) -> str:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    if not html.lstrip().startswith("<!DOCTYPE") and "(kicad_symbol_lib" in html[:200]:
        # Already a real sym file
        idx = html.find('(symbol "PCM1808"')
        if idx < 0:
            idx = html.find('(symbol "1_Project_Symbols:PCM1808"')
        if idx < 0:
            raise SystemExit("PCM1808 not in sym file")
        return from_sch(html_path)

    # GitHub HTML wrapper with escaped JSON lines
    m = re.search(r'\\"\(symbol \\"PCM1808\\"', html)
    if not m:
        m = re.search(r'\\"\(symbol \\"1_Project_Symbols:PCM1808\\"', html)
    if not m:
        raise SystemExit(
            f"{html_path} is HTML, not a valid .kicad_sym; use the .kicad_sch reference instead"
        )
    # Rebuild from sch is more reliable
    raise SystemExit("HTML blob detected — extract from .kicad_sch instead")


def build_lib(symbol_body: str, add_ms1808_alias: bool = True) -> str:
    ms1808 = ""
    if add_ms1808_alias:
        ms1808 = symbol_body.replace('"PCM1808"', '"MS1808"', 1)
        ms1808 = re.sub(r'"Value" "PCM1808"', '"Value" "MS1808"', ms1808, count=1)
        ms1808 = ms1808.replace('"PCM1808_0_1"', '"MS1808_0_1"')
        ms1808 = ms1808.replace('"PCM1808_1_1"', '"MS1808_1_1"')
        ms1808 = f"\n{ms1808}\n"

    return f"""(kicad_symbol_lib
\t(version 20231120)
\t(generator "feahi_extract_pcm1808")
\t(generator_version "1.0")
{symbol_body}
{ms1808})
"""


def write_sym_lib_table(project_dir: Path) -> None:
    rel = "${KIPRJMOD}/../libs/symbols/feahi.kicad_sym"
    table = f"""(sym_lib_table
  (version 7)
  (lib (name "feahi") (type "KiCad") (uri "{rel}") (options "") (descr "FEAHI SP-1 project symbols"))
)
"""
    (project_dir / "sym-lib-table").write_text(table, encoding="utf-8")


def main() -> None:
    sch_path = next((p for p in SCH_CANDIDATES if p.exists()), None)
    if sch_path is None:
        raise SystemExit("No source schematic found in Downloads")

    if sch_path.suffix == ".kicad_sch":
        symbol_body = from_sch(sch_path)
        source = sch_path.name
    else:
        symbol_body = from_html_blob(sch_path)
        source = sch_path.name

    LIBS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_lib(symbol_body), encoding="utf-8")

    for proj in ("feahi_cbi40_core", "feahi_cbi40_periph"):
        write_sym_lib_table(ROOT / proj)

    print(f"Created {OUT}")
    print(f"  Source: {source}")
    print("  Symbols: PCM1808, MS1808 (alias)")
    print("  sym-lib-table updated for core + periph projects")


if __name__ == "__main__":
    main()
