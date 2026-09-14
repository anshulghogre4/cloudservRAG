"""Extract every .docx in Docs/Capstone_Project to plain markdown under Docs/Capstone_Project_text.

Run:  python scripts/extract_pack.py
Re-run whenever a workbook .docx is edited so the text mirror stays current.
Tables are rendered as pipe rows; paragraphs are kept in document order.
"""
from __future__ import annotations

import html
import re
import sys
import zipfile
from pathlib import Path

SRC = Path("Docs/Capstone_Project")
DST = Path("Docs/Capstone_Project_text")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _text_of(el) -> str:
    parts = []
    for node in el.iter():
        tag = node.tag
        if tag == W + "t":
            parts.append(node.text or "")
        elif tag == W + "tab":
            parts.append("\t")
        elif tag == W + "br":
            parts.append("\n")
    return "".join(parts)


def docx_to_markdown(path: Path) -> str:
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    out: list[str] = []
    for child in body:
        if child.tag == W + "p":
            style = child.find(f"{W}pPr/{W}pStyle")
            sval = style.get(W + "val", "") if style is not None else ""
            t = _text_of(child).strip()
            if not t:
                continue
            if sval.lower().startswith("heading"):
                level = re.sub(r"\D", "", sval) or "2"
                out.append("#" * min(int(level), 4) + " " + t)
            elif sval.lower() == "title":
                out.append("# " + t)
            else:
                out.append(t)
            out.append("")
        elif child.tag == W + "tbl":
            rows = []
            for tr in child.iter(W + "tr"):
                cells = [
                    " ".join(_text_of(tc).split()) for tc in tr.findall(W + "tc")
                ]
                rows.append(cells)
            if not rows:
                continue
            width = max(len(r) for r in rows)
            rows = [r + [""] * (width - len(r)) for r in rows]
            out.append("| " + " | ".join(rows[0]) + " |")
            out.append("|" + "---|" * width)
            for r in rows[1:]:
                out.append("| " + " | ".join(r) + " |")
            out.append("")
    text = "\n".join(out)
    return html.unescape(re.sub(r"\n{3,}", "\n\n", text)).strip() + "\n"


def main() -> int:
    if not SRC.is_dir():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    count = 0
    for docx in sorted(SRC.rglob("*.docx")):
        if docx.name.startswith("~$"):
            continue
        rel = docx.relative_to(SRC).with_suffix(".md")
        target = DST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(docx_to_markdown(docx), encoding="utf-8")
        print(f"{docx} -> {target}")
        count += 1
    # Copy the one markdown file in the pack as-is
    readme = SRC / "01_Read_First" / "README.md"
    if readme.exists():
        (DST / "01_Read_First").mkdir(parents=True, exist_ok=True)
        (DST / "01_Read_First" / "README.md").write_text(
            readme.read_text(encoding="utf-8"), encoding="utf-8"
        )
        count += 1
    print(f"{count} files written under {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
