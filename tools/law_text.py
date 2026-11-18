"""Build and search the official law text. Needs `pdftotext` (poppler-utils) only for `extract`.

  python -m tools.law_text extract            # PDFs -> data/laws/text/<DOC>.pages.json + sha256 in sources.json
  python -m tools.law_text find DOC "start words" ["end words"]
                                              # print the exact official span + PDF page, to copy into law.json

Quotes in knowledge/law.json are copied from `find` output, never typed from memory.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys

from core.lawtext import ROOT, TEXT_DIR, norm

SOURCES_PATH = ROOT / "knowledge" / "sources.json"


def extract() -> None:
    src = json.loads(SOURCES_PATH.read_text())
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    for doc, meta in src["docs"].items():
        pdf = ROOT / meta["file"]
        out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
        pages = out.split("\f")
        if pages and not pages[-1].strip():
            pages = pages[:-1]
        (TEXT_DIR / f"{doc}.pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=0))
        meta["sha256"] = hashlib.sha256(pdf.read_bytes()).hexdigest()
        meta["pdf_pages"] = len(pages)
        print(f"{doc}: {len(pages)} pages")
    SOURCES_PATH.write_text(json.dumps(src, ensure_ascii=False, indent=1) + "\n")


def find(doc: str, start: str, end: str | None = None) -> None:
    from core.lawtext import pages
    ps = pages(doc)
    joined, offsets = "", []
    for i, p in enumerate(ps, 1):
        offsets.append((len(joined), i))
        joined += norm(p) + " "
    s = joined.find(norm(start))
    if s < 0:
        sys.exit(f"not found: {start!r}")
    e = joined.find(norm(end), s) + len(norm(end)) if end else s + 400
    if end and e < len(norm(end)):
        sys.exit(f"end not found after start: {end!r}")
    starts = [off for off, _ in offsets] + [len(joined)]
    pg = [n for k, (off, n) in enumerate(offsets) if off < e and starts[k + 1] > s]
    print(f"pdf_pages: {pg}\n---\n{joined[s:e]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "extract":
        extract()
    elif cmd == "find" and len(sys.argv) >= 4:
        find(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        print(__doc__)
