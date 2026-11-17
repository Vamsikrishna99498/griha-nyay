"""Official law text: page text extracted from the PDFs in data/laws/, and the one
normaliser used everywhere a quote is compared with that text (tests, quote checks)."""
import json
import re
import unicodedata
from functools import cache, lru_cache
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEXT_DIR = ROOT / "data" / "laws" / "text"

_QUOTES = {"‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'",
           "“": '"', "”": '"', "„": '"', "″": '"',
           "–": "-", "—": "-", "‒": "-", "−": "-", "­": ""}


def norm(text: str) -> str:
    """Make PDF text and typed quotes comparable: same quotes/dashes, no page-number lines,
    no private-use glyphs, hyphenated line breaks joined, all whitespace collapsed."""
    t = unicodedata.normalize("NFKC", text)
    t = "".join(_QUOTES.get(ch, ch) for ch in t)
    t = re.sub(r"[-]", " ", t)                 # private-use bullets in the FAQ
    t = re.sub(r"(?m)^\s*\d{1,3}\s*$", " ", t)              # lines that are only a page number
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)            # hyphen + line break
    t = re.sub(r"\s+", " ", t)
    return t.strip()


@lru_cache(maxsize=1)
def sources() -> dict:
    return json.loads((ROOT / "knowledge" / "sources.json").read_text())["docs"]


@cache
def pages(doc: str) -> list[str]:
    return json.loads((TEXT_DIR / f"{doc}.pages.json").read_text())


def page_text(doc: str, pdf_pages: list[int]) -> str:
    p = pages(doc)
    return "\n".join(p[i - 1] for i in pdf_pages if 0 < i <= len(p))
