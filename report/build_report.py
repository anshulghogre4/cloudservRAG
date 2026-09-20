"""Build the report PDF: fill the table fragments into report.html, render with headless Edge,
stamp page numbers, and report where each section starts.

    python report/make_figures.py
    python report/build_report.py

Output: report/AnshulGhogre_Capstone_Report.pdf
"""
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "report"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
OUT = REP / "AnshulGhogre_Capstone_Report.pdf"


def fill_html() -> Path:
    html = (REP / "report.html").read_text(encoding="utf-8")
    for key in ("PERCLASS", "SEGMENTS", "FILES"):
        frag = (REP / f"_{key.lower()}.html").read_text(encoding="utf-8")
        html = html.replace("{{" + key + "}}", frag)
    out = REP / "_report_filled.html"
    out.write_text(html, encoding="utf-8")
    return out


def render(html: Path, pdf: Path) -> None:
    url = "file:///" + str(html).replace("\\", "/")
    cmd = [str(EDGE), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf}", url]
    subprocess.run(cmd, check=True, capture_output=True, timeout=180)


def stamp_page_numbers(src: Path, dst: Path) -> int:
    from pypdf import PdfReader, PdfWriter
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    reader = PdfReader(str(src))
    writer = PdfWriter()
    n = len(reader.pages)
    for i, page in enumerate(reader.pages):
        if i >= 1:  # no number on the cover
            w = float(page.mediabox.width)
            h = float(page.mediabox.height)
            fig = plt.figure(figsize=(w / 72, h / 72))
            fig.text(0.5, 0.017, f"{i + 1}", ha="center", va="bottom", fontsize=8.5, family="DejaVu Sans", color="#52514e")
            fig.text(0.94, 0.017, "Anshul Ghogre, Capstone Report", ha="right", va="bottom", fontsize=7, family="DejaVu Sans", color="#8a8985")
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf", transparent=True)
            plt.close(fig)
            buf.seek(0)
            overlay = PdfReader(buf).pages[0]
            page.merge_page(overlay)
        writer.add_page(page)
    with open(dst, "wb") as f:
        writer.write(f)
    return n


def section_pages(pdf: Path) -> None:
    from pypdf import PdfReader
    reader = PdfReader(str(pdf))
    marks = ["1. Executive summary", "2. The problem", "3. Discovery findings", "4. Requirements", "5. Architecture and design",
             "6. Implementation", "7. Evaluation", "8. Governance and risk", "9. The requirements revision", "10. Conclusions",
             "Declaration of AI tool use", "Appendix A"]
    found = {}
    for i, p in enumerate(reader.pages):
        text = p.extract_text() or ""
        head = text[:120]
        for m in marks:
            if m not in found and head.startswith(m):
                found[m] = i + 1
    for m in marks:
        print(f"  p.{found.get(m, '?'):>3}  {m}")
    print(f"  total pages: {len(reader.pages)}")


if __name__ == "__main__":
    html = fill_html()
    raw = REP / "_report_raw.pdf"
    render(html, raw)
    n = stamp_page_numbers(raw, OUT)
    print("wrote", OUT, "pages", n)
    section_pages(OUT)
    sys.exit(0)
