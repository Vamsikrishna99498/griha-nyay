"""Tiny keyword/tag retrieval over the verified knowledge base.
~25 entries don't need a vector DB; this is transparent and easy to debug."""
import json
import re
from pathlib import Path

KB_DIR = Path(__file__).parent.parent / "knowledge"


def load_kb() -> dict:
    entries = json.loads((KB_DIR / "rera_central.json").read_text())["entries"]
    entries += json.loads((KB_DIR / "telangana.json").read_text())["entries"]
    return {e["id"]: e for e in entries}


KB = load_kb()

# Always relevant to a delayed-possession case in Telangana.
CORE_IDS = ["RERA-18-1", "TG-INTEREST", "RERA-31", "TG-FORMS"]


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def retrieve(query: str, k: int = 6, include_core: bool = True) -> list:
    q = query.lower()
    qt = _tokens(q)
    scored = []
    for e in KB.values():
        score = 0.0
        for tag in e["tags"]:
            if tag in q:
                score += 3  # phrase hit
            score += 0.5 * len(_tokens(tag) & qt)
        score += 0.2 * len(_tokens(e["title"] + " " + e["summary"]) & qt)
        scored.append((score, e["id"]))
    scored.sort(reverse=True)
    ids = [i for s, i in scored[:k] if s > 1.0]
    if include_core:
        ids = CORE_IDS + [i for i in ids if i not in CORE_IDS]
    return [KB[i] for i in ids]


def format_for_prompt(entries: list) -> str:
    return "\n\n".join(
        f"[{e['id']}] {e['act']} — {e['section']}: {e['title']}\n{e['summary']}" for e in entries
    )


def sources_block(ids: list) -> str:
    lines = []
    for i in ids:
        e = KB.get(i)
        if e:
            lines.append(f"- **[{i}]** {e['act']}, {e['section']} — _{e['title']}_ (source: {e['source']}; check status: {e['verification']})")
    return "\n".join(lines)
