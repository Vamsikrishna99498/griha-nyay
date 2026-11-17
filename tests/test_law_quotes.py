"""Every piece of law text the bot can show must be exact official text.
- each knowledge entry's quote appears verbatim (after normalising spaces/quotes) on its PDF page(s)
- each PDF's sha256 matches sources.json (the text was extracted from these exact files)
- every quoted phrase and every Section/Rule named in templates/*.j2 exists in the official text / KB
- every helpline has an official source and a check date
Run: python -m tests.test_law_quotes"""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from core.lawtext import norm, page_text, pages, sources
from core.retrieve import KB

ROOT = Path(__file__).parent.parent


def test_every_quote_is_on_its_pages():
    for e in KB.values():
        page = norm(page_text(e["doc"], e["pdf_pages"]))
        for q in e["quote"]:
            assert norm(q) in page, f"{e['id']}: quote not found on PDF pages {e['pdf_pages']}"


def test_pdf_hashes_match_sources():
    for doc, meta in sources().items():
        h = hashlib.sha256((ROOT / meta["file"]).read_bytes()).hexdigest()
        assert h == meta["sha256"], doc
        assert meta.get("url") and meta.get("retrieved") and meta.get("publisher"), doc


def test_pages_json_matches_pdf_if_poppler_available():
    if not shutil.which("pdftotext"):
        print("  (skipped: pdftotext not installed)")
        return
    for doc, meta in sources().items():
        out = subprocess.run(["pdftotext", "-f", "1", "-l", "1", str(ROOT / meta["file"]), "-"],
                             capture_output=True, text=True, check=True).stdout
        assert norm(out) == norm(pages(doc)[0]), doc


def test_templates_quote_only_official_text():
    official = " ".join(norm(" ".join(pages(d))) for d in sources())
    for t in (ROOT / "templates").glob("*.j2"):
        src = re.sub(r'"\{\{.*?\}\}"', "", t.read_text())              # quoted Jinja values (KB quotes)
        src = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", "", src)              # other Jinja expressions
        for q in re.findall(r'"([^"{}\n]{20,})"', src):                # literal quoted phrases on one line
            assert norm(q) in official, f"{t.name}: '{q[:60]}' is not official text"
        for kind, num in re.findall(r"\b(Section|Rule)\s+(\d+)", src):
            hit = any(e["ref_kind"] == kind.lower() and e["ref_num"] == num for e in KB.values())
            assert hit, f"{t.name}: {kind} {num} is not a verified entry"


def test_helplines_have_sources():
    h = json.loads((ROOT / "knowledge" / "helplines.json").read_text())
    for k, p in h["pointers"].items():
        assert p["source_url"].startswith("https://") and p["verified_on"], k
        assert {"en", "hi", "te"} <= set(p["label"]), k
    for state, p in h["state_rera_portals"].items():
        assert p["url"].startswith("https://") and p["verified_on"], state
    for situation, keys in h["when"].items():
        assert all(k in h["pointers"] for k in keys), situation


def test_faq_is_marked_guidance():
    for e in KB.values():
        if e["doc"] == "TG_FAQ":
            assert e["kind"] == "guidance" and e["ref_kind"] is None, e["id"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
