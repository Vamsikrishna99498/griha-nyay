"""Structured retrieval over the verified law entries. No vectors.

Order of preference (each step adds entries, capped at MAX_ENTRIES):
  1. exact lookup   - the user names "section 19" / "rule 15" / "धारा 18" / "సెక్షన్ 18"
  2. index picks    - intake reads the compact LAW INDEX and returns up to 4 law_ids
  3. case rules     - knowledge/retrieval_map.json: category, goal, cautions, escalations
  4. keywords       - multilingual tags + synonyms, generic words ignored
  5. see_also links - e.g. s.18(1) pulls Rule 15 (rate) and Rules 34/35 (forms)
Nothing relevant -> empty list (the advisor must then say it has no verified law), never padding.
"""
import json
import re
from pathlib import Path

from .lawtext import norm, sources

KB_DIR = Path(__file__).parent.parent / "knowledge"
MAX_ENTRIES = 6
BOTH_PROBLEMS_EXTRA = 2
GENERIC = {"builder", "flat", "house", "home", "project", "apartment", "rera", "the", "my", "law", "legal"}


SUB_RE = r"(?:\s*\(\s*(?:\d{1,3}[A-Za-z]?|[A-Za-z]|[ivxIVX]{1,4})\s*\))*"   # (1), (4)(a), (ii)


def sub_parts(text: str) -> list:
    return [x.lower() for x in re.findall(r"\(\s*(\w+)\s*\)", text or "")]


def sub_matches(named: list, entry: dict) -> bool:
    """'Section 19(7)' is not the verified 'Section 19(4)'. A reference with no sub-section, or an entry
    that covers the whole provision, matches; otherwise one must be the start of the other."""
    have = entry.get("ref_sub") or []
    n = min(len(named), len(have))
    return named[:n] == have[:n]


def _load():
    src = sources()
    entries = json.loads((KB_DIR / "law.json").read_text())["entries"]
    for e in entries:
        meta = src[e["doc"]]
        e["act"] = meta["title"]
        e["act_short"] = meta["short"]
        e["act_key"] = meta["act_key"]
        e["kind"] = meta["kind"]
        e["url"] = meta["url"]
        e["quote_text"] = " … ".join(e["quote"])
        m = re.match(r"(Section|Rule)s?\s+(\d+)((?:\(\w+\))*)", e["section"])
        e["ref_kind"], e["ref_num"] = (m.group(1).lower(), m.group(2)) if m else (None, None)
        e["ref_sub"] = sub_parts(m.group(3)) if m else []   # "Section 19(4)" -> ["4"]
    return {e["id"]: e for e in entries}


KB = _load()
RMAP = json.loads((KB_DIR / "retrieval_map.json").read_text())


def law_index() -> str:
    """Compact table of contents of everything verified (~1.5k tokens): id, place, title, gist."""
    lines, last = [], None
    for e in KB.values():
        head = f"{e['act_short']} › {e['chapter']}"
        if head != last:
            lines.append(f"## {head}")
            last = head
        lines.append(f"[{e['id']}] {e['section']} - {e['title']}: {e['gist']}")
    return "\n".join(lines)


# ---------- 1. exact lookup ----------
REF_RE = re.compile(r"(?i)\b(section|sec\.?|s\.|u/s|rule|r\.)\s*(\d{1,3})(?!\d)(" + SUB_RE + r")"
                    r"|(धारा|सेक्शन|नियम|నియమం|సెక్షన్|రూల్)\s*(\d{1,3})(?!\d)(" + SUB_RE + r")")


def lookup(text: str) -> tuple[list, list]:
    """Returns (entry_ids, unknown_refs) for provisions the user names explicitly."""
    ids, unknown = [], []
    for m in REF_RE.finditer(text or ""):
        word = (m.group(1) or m.group(4) or "").lower()
        num = m.group(2) or m.group(5)
        sub = sub_parts(m.group(3) or m.group(6))
        kind = "rule" if word.startswith(("rule", "r.", "नियम", "నియమం", "రూల్")) else "section"
        hits = [e["id"] for e in KB.values() if e["ref_kind"] == kind and e["ref_num"] == num and e["kind"] == "law"
                and (kind == "rule" or e["act_key"] == "rera") and sub_matches(sub, e)]
        if hits:
            ids += [h for h in hits if h not in ids]
        else:
            unknown.append(f"{kind.title()} {num}" + "".join(f"({s})" for s in sub))
    return ids, unknown


# ---------- 4. keywords ----------
def _has(text: str, tag: str) -> bool:
    if not tag.isascii():
        return tag in text                       # Indic scripts: substring (suffixes attach to words)
    return re.search(r"(?<![a-z0-9])" + re.escape(tag) + r"(?![a-z0-9])", text) is not None


def keyword_scores(text: str) -> list:
    t = norm(text or "").lower()
    scored = []
    for e in KB.values():
        s = sum(3 if " " in tag or not tag.isascii() else 2
                for tag in e["tags"] if tag.lower() not in GENERIC and _has(t, tag.lower()))
        if s:
            scored.append((s, e["id"]))
    scored.sort(key=lambda x: -x[0])
    return [i for s, i in scored if s >= 2]


def retrieve(case=None, message: str = "", law_ids=None, cautions=(), escalations=()) -> tuple[list, dict]:
    """Returns (entries, why) where why[id] = 'lookup' | 'index' | 'case' | 'keyword' | 'linked'."""
    why = {}
    # a case with both problems needs both sets of core entries AND room for the goal / caution ones
    cap = MAX_ENTRIES + BOTH_PROBLEMS_EXTRA if case is not None and len(set(case.categories or [])) > 1 else MAX_ENTRIES

    def add(ids, reason):
        for i in ids:
            if i in KB and i not in why and len(why) < cap:
                why[i] = reason

    found, _ = lookup(message)
    add(found, "lookup")
    add(law_ids or [], "index")
    if case is not None:
        for c in case.categories or []:
            add(RMAP["category"].get(c, []), "case")
        if case.goal:
            add(RMAP["goal"].get(case.goal, []), "case")
    for c in cautions:
        add(RMAP["caution"].get(c, []), "case")
    for x in escalations:
        add(RMAP["escalation"].get(x, []), "case")
    add(keyword_scores(message), "keyword")
    for i in list(why):
        add(KB[i]["see_also"], "linked")
    return [KB[i] for i in why], why


def format_for_prompt(entries: list) -> str:
    out = []
    for e in entries:
        label = "GUIDANCE (not law)" if e["kind"] == "guidance" else "LAW"
        s = f"[{e['id']}] {label} - {e['act']}, {e['section']}: {e['title']}\nExact text: \"{e['quote_text']}\"\nPlain meaning: {e['gist']}"
        if e.get("practice_note"):
            s += f"\nPractice note: {e['practice_note']}"
        out.append(s)
    return "\n\n".join(out)


def sources_block(ids: list) -> str:
    lines = []
    for i in ids:
        e = KB.get(i)
        if e:
            tag = " (guidance, not law)" if e["kind"] == "guidance" else ""
            pages = ", ".join(str(p) for p in e["pdf_pages"])
            lines.append(f"- **[{i}]** {e['act']}, {e['section']}{tag} - _{e['title']}_ (PDF p. {pages}; {e['url']})")
    return "\n".join(lines)
