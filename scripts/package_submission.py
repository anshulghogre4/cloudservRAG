"""Build the submission package (Submission Guide: four folders, one archive).

    python scripts/package_submission.py            # build the folder and the zip
    python scripts/package_submission.py --no-zip   # folder only

What it does, in order:
  02_Report       copies report/AnshulGhogre_Capstone_Report.pdf (build it first with
                  report/make_figures.py and report/build_report.py)
  03_Workbooks    copies the five stage workbooks from Docs/Capstone_Project/02_Stage_Workbooks
                  renamed AnshulGhogre_Stage_N_*.docx, and the effort log: the filled
                  03_Workbooks/AnshulGhogre_Effort_Log.docx if present (else the DRAFT), converted
                  to PDF with Word when Word is available
  04_Source_Code  fresh `git clone` of this repository's HEAD (history included, no .env, no
                  storage/, no submission/), then a credential scan over the clone's history
  01_Video        left as is; writes a README if no .mp4 or link file is present
  zip             submission/AnshulGhogre_Capstone_Submission.zip with the four folders at the root

Everything under submission/ is gitignored; nothing here pushes or commits.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "submission"
PKG = SUB / "AnshulGhogre_Capstone_Submission"
NAME = "AnshulGhogre"
WORKBOOKS = ROOT / "Docs" / "Capstone_Project" / "02_Stage_Workbooks"
KEY_PATTERNS = [r"sk-or-v1-[0-9a-f]{20,}", r"sk-[A-Za-z0-9]{32,}", r"OPENROUTER_API_KEY\s*=\s*['\"]?sk-",
                r"AKIA[0-9A-Z]{16}", r"ghp_[A-Za-z0-9]{30,}"]


def log(msg: str) -> None:
    print(f"  {msg}")


def report() -> None:
    src = ROOT / "report" / f"{NAME}_Capstone_Report.pdf"
    dst = PKG / "02_Report" / f"{NAME}_Capstone_Report.pdf"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        log("WARNING: report PDF missing; run report/make_figures.py then report/build_report.py")
        return
    shutil.copy2(src, dst)
    log(f"report -> {dst.relative_to(SUB)}")


def docx_to_pdf(src: Path, dst: Path) -> bool:
    try:
        import win32com.client  # type: ignore
    except ImportError:
        return False
    word = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(str(src.resolve()), ReadOnly=True)
        doc.SaveAs2(str(dst.resolve()), FileFormat=17)  # wdFormatPDF
        doc.Close(False)
        return True
    except Exception as exc:  # noqa: BLE001
        log(f"Word conversion failed for {src.name}: {exc}")
        return False
    finally:
        if word is not None:
            try:
                word.Quit()
            except Exception:  # noqa: BLE001
                pass


def workbooks() -> None:
    out = PKG / "03_Workbooks"
    out.mkdir(parents=True, exist_ok=True)
    for i in range(1, 6):
        matches = sorted(WORKBOOKS.glob(f"Stage_{i}_*.docx"))
        matches = [m for m in matches if not m.name.startswith("~")]
        if not matches:
            log(f"WARNING: Stage {i} workbook not found")
            continue
        dst = out / f"{NAME}_{matches[0].name}"
        shutil.copy2(matches[0], dst)
        log(f"workbook -> {dst.name}")
    filled = out / f"{NAME}_Effort_Log.docx"
    draft = out / f"{NAME}_Effort_Log_DRAFT.docx"
    src = filled if filled.exists() else draft
    if not src.exists():
        log("WARNING: no effort log found in 03_Workbooks")
        return
    pdf = out / f"{NAME}_Effort_Log.pdf"
    if docx_to_pdf(src, pdf):
        log(f"effort log {src.name} -> {pdf.name}" + ("" if src is filled else "  (DRAFT: hours still to be filled by the author)"))
    else:
        log(f"effort log kept as {src.name} (Word not available for PDF conversion)")
    if src is draft:
        log("REMINDER: the Submission Guide requires the effort log as a PDF with actual hours; fill the DRAFT, save it as "
            f"{filled.name}, and re-run this script")


def source_code() -> None:
    out = PKG / "04_Source_Code"
    if out.exists():
        shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    clone = out / "cloudservRAG"
    subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(ROOT), str(clone)], check=True)
    head = subprocess.run(["git", "-C", str(clone), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    log(f"source -> {clone.relative_to(SUB)} at {head}")
    if dirty:
        log("WARNING: the working tree has uncommitted changes; the clone contains only committed work:")
        for line in dirty.splitlines()[:15]:
            log("    " + line)
    for forbidden in (".env", "storage"):
        if (clone / forbidden).exists():
            log(f"ERROR: {forbidden} present in the clone")
    # credential scan over the whole history
    hits = []
    log_all = subprocess.run(["git", "-C", str(clone), "log", "-p", "--all"], capture_output=True, text=True, errors="ignore").stdout
    for pat in KEY_PATTERNS:
        for m in re.finditer(pat, log_all):
            hits.append(m.group(0)[:12] + "...")
    if hits:
        log(f"ERROR: {len(hits)} credential-like strings found in history: {sorted(set(hits))}")
    else:
        log("credential scan over the clone's full history: nothing found")
    (out / "README_FIRST.txt").write_text(
        "The repository is in cloudservRAG/ (a full git clone with history). Open cloudservRAG/README.md and follow it\n"
        f"from the first line. Packaged from commit {head}.\n", encoding="utf-8")


def video() -> None:
    out = PKG / "01_Video"
    out.mkdir(parents=True, exist_ok=True)
    have = [p for p in out.iterdir() if p.suffix.lower() in (".mp4", ".txt", ".md") and not p.name.startswith("README")]
    if not have:
        (out / "README.txt").write_text(
            f"Place {NAME}_Capstone_Video.mp4 here (MP4, 1080p, 18 to 22 minutes), or a text file containing a shareable link.\n"
            "The recording plan is in video_plan.md next to this file.\n", encoding="utf-8")
        log("video: not present; README.txt written")
    else:
        log("video: " + ", ".join(p.name for p in have))


def make_zip() -> None:
    dst = SUB / f"{NAME}_Capstone_Submission.zip"
    if dst.exists():
        dst.unlink()
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for p in PKG.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(PKG))
    log(f"archive -> {dst.relative_to(SUB)} ({dst.stat().st_size / 1e6:.1f} MB); top level: "
        + ", ".join(sorted(x.name for x in PKG.iterdir())))


if __name__ == "__main__":
    print("Packaging submission")
    report()
    workbooks()
    source_code()
    video()
    if "--no-zip" not in sys.argv:
        make_zip()
    print("done")
