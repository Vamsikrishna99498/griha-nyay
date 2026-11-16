"""Rule-based safety layer. None of this is decided by the LLM.

1. check_escalation(): when to stop and send the user to a real lawyer / DLSA.
2. validate_citations(): strip any law/section/case the model mentions that is not in the
   retrieved, verified knowledge entries for this turn.
"""
import json
import re
from pathlib import Path

from .case import CaseFile

ESC = json.loads((Path(__file__).parent.parent / "knowledge" / "escalation.json").read_text())

CAUTION_WORDS = {
    "force_majeure": ["force majeure", "covid", "pandemic", "lockdown", "extension granted", "act of god"],
}


def _has_keyword(text: str, kw: str) -> bool:
    # word boundaries so "fir" doesn't match "first" and "420" doesn't match "14,20,000"
    return re.search(r"(?<![\w,])" + re.escape(kw.lower()) + r"(?![\w,])", text.lower()) is not None


def check_escalation(user_text: str, case: CaseFile) -> list:
    """Returns [(rule_id, message)]. Non-empty => tell the user to get a real lawyer."""
    hits = []
    for rule in ESC["rules"]:
        if any(_has_keyword(user_text, kw) for kw in rule["keywords"]):
            hits.append((rule["id"], rule["message"]))
    s = ESC["structured_rules"]
    if case.state and case.state.lower() != "telangana":
        hits.append(("out_of_state", s["out_of_state"]))
    if case.rera_registered is False:
        hits.append(("unregistered", s["unregistered"]))
    if (case.amount_paid_rupees or 0) > ESC["high_value_threshold_rupees"]:
        hits.append(("high_value", s["high_value"]))
    return hits


def check_cautions(user_text: str) -> list:
    """Soft flags: the bot still helps but says the outcome depends on facts it can't judge."""
    return [k for k, words in CAUTION_WORDS.items() if any(_has_keyword(user_text, w) for w in words)]


# ---------- citation validation ----------

TAG_RE = re.compile(r"\[([A-Z]{2,4}(?:-[A-Z0-9]+)+)\]")
SECTION_RE = re.compile(
    r"(?:\bsections?|\bsecs?\.?|\bu/s\.?|\bs\.|\brules?|धारा|धाराओं|సెక్షన్|నిబంధన)\s*(\d+[A-Z]?)(?:\s*\(\s*\w+\s*\))*",
    re.IGNORECASE,
)
CASE_RES = [
    re.compile(r"\b[A-Z][\w.&']*(?:\s+(?:[A-Z][\w.&']*|of|and|&))*\s+(?:v\.|vs\.?|versus)\s+[A-Z][\w.&']*(?:\s+(?:[A-Z][\w.&']*|of|and|&))*"),
    re.compile(r"\(\s*\d{4}\s*\)\s*\d+\s*SCC\s*\d+"),
    re.compile(r"\bAIR\s*\d{4}\s*(?:SC|[A-Z]{2,4})\s*\d+"),
    re.compile(r"\b\d{4}\s*SCC\s*OnLine\s*\w+\s*\d+", re.IGNORECASE),
]
CASE_PLACEHOLDER = "[court case reference removed — I don't cite judgments]"
SECTION_PLACEHOLDER = "[unverified legal reference removed]"


def _allowed_numbers(entries: list) -> set:
    nums = set()
    for e in entries:
        nums |= set(re.findall(r"\d+", e["section"]))
    return nums


def validate_citations(text: str, entries: list) -> tuple[str, list]:
    """Returns (clean_text, removed_items). Entries = the KB entries given to the model this turn."""
    allowed_ids = {e["id"] for e in entries}
    allowed_nums = _allowed_numbers(entries)
    removed = []

    def tag_sub(m):
        if m.group(1) in allowed_ids:
            return m.group(0)
        removed.append(("unknown_tag", m.group(0)))
        return ""

    text = TAG_RE.sub(tag_sub, text)
    # models sometimes "cite" the prompt's own section names, e.g. [CALCULATOR]; not law, drop quietly
    text = re.sub(r"\s?\[(?:CALCULATOR|CALC|CASE FILE|CASE_FILE|VERIFIED LAW)\]", "", text)

    def sec_sub(m):
        if m.group(1).rstrip("ABCDEFGH") in allowed_nums:
            return m.group(0)
        removed.append(("unverified_section", m.group(0)))
        return SECTION_PLACEHOLDER

    text = SECTION_RE.sub(sec_sub, text)

    for rx in CASE_RES:
        def case_sub(m):
            removed.append(("case_law", m.group(0)))
            return CASE_PLACEHOLDER
        text = rx.sub(case_sub, text)
    return text, removed


def cited_ids(text: str) -> list:
    seen = []
    for m in TAG_RE.finditer(text):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


def unknown_amounts(text: str, allowed: set) -> list:
    """Rupee figures in the answer that the calculator did not produce (LLM did its own maths)."""
    found = re.findall(r"(?:Rs\.?|₹|INR)\s?[\d,]+(?:\.\d+)?", text)
    norm_allowed = {a.replace("Rs ", "").replace(",", "") for a in allowed}
    out = []
    for f in found:
        digits = re.sub(r"[^\d]", "", f.split(".")[0])
        if len(digits) >= 4 and digits not in norm_allowed:  # ignore "Rs 50 lakh"-style thresholds
            out.append(f)
    return out
