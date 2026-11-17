"""Rule-based safety layer, applied in code to every model answer.

1. check_escalation()  - when to stop and send the user to a real lawyer / DLSA (keywords in
                         en/hi/te + structured case rules + intake flags, which can only escalate)
2. validate_citations() - citations only as verified tags; bare section/rule/article numbers are
                         turned into a tag if they match a retrieved entry, otherwise removed
3. mark_amounts()       - rupee figures not produced by the calculator get a visible warning
4. check_quotes()       - text in quotation marks next to a tag must be exact law text
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .calculator import compute, defect_check
from .case import CaseFile
from .i18n import T
from .lawtext import norm
from .retrieve import SUB_RE, sub_matches, sub_parts

ESC = json.loads((Path(__file__).parent.parent / "knowledge" / "escalation.json").read_text())
CAUTION_WORDS = {
    "force_majeure": ["force majeure", "covid", "pandemic", "lockdown", "extension granted", "act of god",
                      "కరోనా", "లాక్‌డౌన్", "कोरोना", "लॉकडाउन", "corona"],
}
FLAG_TO_RULE = {"insolvency": "insolvency", "court_case_pending": "already_in_court",
                "criminal_or_threat": "criminal", "title_dispute": "title_dispute"}


# ---------- keywords ----------
CASE_SENSITIVE = "cs:"   # "cs:FIR" matches FIR but not the Hinglish word "fir" (phir = then)


def _keyword_spans(t: str, k: str) -> list:
    if not k.isascii():
        return [(m.start(), m.end()) for m in re.finditer(re.escape(k.rstrip("*")), t)]
    # not inside a word, and not inside a number written with commas ('420' in '14,20,000');
    # a comma that is just punctuation ("in NCLT, what now?") must not hide the keyword
    if k.endswith("*"):
        rx = r"(?<!\w)(?<!\d,)" + re.escape(k[:-1]) + r"\w*"
    else:
        rx = r"(?<!\w)(?<!\d,)" + re.escape(k) + r"(?!\w)(?!,\d)"
    return [(m.start(), m.end()) for m in re.finditer(rx, t)]


def has_keyword(text: str, kw: str) -> bool:
    """ASCII keywords: whole word/phrase ('fir' never matches 'first', '420' never matches
    '14,20,000'); a trailing '*' allows any ending ('bankrupt*'). Non-ASCII (Hindi/Telugu)
    keywords are substring stems, because those languages attach suffixes to words."""
    return bool(_keyword_spans(text.lower(), kw.lower()))


_CLAUSE_BREAK = re.compile(r"[.!?;:,()\n—–]|\s-\s|\b(?:and|but|however|though|because)\b")
_FILLER = (r"(?:any|a|an|the|such|one|been|being|gone|going|in|into|under|filed|lodged|registered|received|got|get|"
           r"gotten|had|have|seen|heard|declared|as|yet|there|is|are|was|kind|sort|of|facing|made|given|sent|or)")
_NEG_BEFORE = re.compile(r"(?:\b(?:no|not|never|without|nor|neither|nobody|none)\b|n['’]t\b)(?:\s+" + _FILLER + r"){0,3}\s+$")
_NEG_AFTER = re.compile(r"\s+(?:is|are|was|were|has|have|had)\s+(?:not|never)\s+(?:been\s+)?"
                        r"(?:filed|lodged|registered|started|issued|received|sent|there|true|declared)\b"
                        r"|\s+(?:is|was|has|have)n['’]t\s+(?:been\s+)?(?:filed|lodged|registered|started|issued|received|sent)\b")


# A question about something that MIGHT happen is not a report that it has ("what if the builder goes
# bankrupt?", "should I file a police complaint?"). Intake's flags remain the second signal for real ones.
_MAYBE_BEFORE = re.compile(
    r"\b(?:if|whether|in case|suppose|supposing|unless|should i|shall i|can i|could i|may i|do i need|do i have|"
    r"how do i|how can i|how to|how long|how much time|when will|will there be|is it possible|agar|yadi)\b"
    r"|अगर|यदि|ఒకవేళ")
_MAYBE_AFTER = re.compile(r"\s+(?:if|in case)\b")


def _clause(t: str, start: int, end: int) -> tuple[str, str]:
    breaks = [m.end() for m in _CLAUSE_BREAK.finditer(t, 0, start)]
    nxt = _CLAUSE_BREAK.search(t, end)
    return t[breaks[-1] if breaks else 0: start], t[end: nxt.start() if nxt else len(t)]


def _negated(t: str, start: int, end: int) -> bool:
    before, after = _clause(t, start, end)
    return bool(_NEG_BEFORE.search(before + " ") or _NEG_AFTER.match(after))


def _only_a_possibility(t: str, start: int, end: int) -> bool:
    before, after = _clause(t, start, end)
    return bool(_MAYBE_BEFORE.search(before) or _MAYBE_AFTER.match(after))


def keyword_asserted(text: str, kw: str) -> bool:
    """has_keyword, minus English hits the user is denying ("no case pending") and hits that only ask about
    a possibility ("what if the builder goes bankrupt?"). Only tight patterns are skipped, since a missed
    escalation is worse than a false one; a Hindi/Telugu hit counts unless the clause opens with "if"."""
    t = text.lower()
    if kw.startswith(CASE_SENSITIVE):
        spans = _keyword_spans(text, kw[len(CASE_SENSITIVE):]) if len(t) == len(text) else []
    else:
        spans = _keyword_spans(t, kw.lower())
    spans = [(s, e) for s, e in spans if not _only_a_possibility(t, s, e)]
    if not kw.isascii():
        return bool(spans)
    return any(not _negated(t, s, e) for s, e in spans)


def check_escalation(user_text: str, case: CaseFile, flags: dict | None = None, defect_calc=None) -> list:
    """Returns rule ids. Keyword rules + intake flags + structured case rules."""
    hits = []
    for rule in ESC["rules"]:
        if any(keyword_asserted(user_text, kw) for kw in rule["keywords"]):
            hits.append(rule["id"])
    for f in (flags or {}):
        r = FLAG_TO_RULE.get(f)
        if r and r not in hits:
            hits.append(r)
    if case.state and case.state != "Telangana":
        hits.append("out_of_state")
    if case.rera_registered is False or case.permission_before_2017 is True:
        hits.append("unregistered")
    if (case.amount_paid_rupees or 0) > ESC["high_value_threshold_rupees"]:
        hits.append("high_value")
    if defect_calc is not None and case.categories == ["defects"] and defect_calc.within_window is False:
        hits.append("defect_window_passed")
    return hits


def escalation_message(rule_id: str, language: str) -> str:
    for r in ESC["rules"]:
        if r["id"] == rule_id:
            m = r["message"]
            break
    else:
        m = ESC["structured_rules"][rule_id]
    from .i18n import code_lang
    return m.get(code_lang(language), m["en"])


def check_cautions(user_text: str) -> list:
    """Soft flags: the bot still helps but says the outcome depends on facts it can't judge."""
    return [k for k, words in CAUTION_WORDS.items() if any(has_keyword(user_text, w) for w in words)]


# ---------- internal names ----------
BLOCK_NAMES = ["calculator", "calc", "case_file", "verified_law", "law_index", "defect_check", "notes", "user_message", "situation"]
BLOCK_LABEL_RE = re.compile(r"(?i)\s?(?:\[/?(?:%s)\]|</?(?:%s)>)" % (("|".join(BLOCK_NAMES).replace("_", "[ _]"),) * 2))


def leaked_names(text: str) -> list:
    """Names of prompt data blocks or calculator fields that show up in a reply the user reads."""
    fields = set(compute(None, None).figures()) | set(compute(date(2020, 1, 1), 1, handed_over=date(2020, 2, 1)).figures())
    fields |= set(defect_check(None).figures())
    names = sorted(n for n in fields | set(BLOCK_NAMES) if "_" in n)
    return [n for n in names if n in text] + BLOCK_LABEL_RE.findall(text)


# ---------- citations ----------
TAG_RE = re.compile(r"\[([A-Z]{2,6}(?:-[A-Z0-9]+)+)\]")
REF_RE = re.compile(
    r"(?i)\b(?P<w>sections?|secs?\.?|u/s\.?|s\.|rules?|r\.|articles?|art\.)\s*(?P<n>\d{1,3}[A-Z]?)(?P<sub>" + SUB_RE + r")"
    r"|(?P<wi>धाराओं|धारा|अनुच्छेद|नियम|సెక్షన్|నిబంధన|నియమం|ఆర్టికల్)\s*(?P<ni>\d{1,3})(?P<subi>" + SUB_RE + r")"
)
OTHER_LAW_RE = re.compile(r"(?i)\b(?:IPC|BNS|BNSS|CrPC|CPC)\b(?:\s*(?:s\.|sec\.?|section)?\s*\d+)?")
ACT_ALIASES = [   # Rules before Acts: the Telangana Rules' full title also contains "Real Estate"
    (re.compile(r"(?i)telangana.{0,60}rules|ts rera rules|\bTS\b.{0,10}rules|rera rules|real estate(?:(?!\bact\b).){0,45}rules"), "ts_rules"),
    (re.compile(r"(?i)consumer protection.{0,20}rules|jurisdiction.{0,40}rules"), "cpa_rules"),
    (re.compile(r"(?i)real estate|rera act|\bRERA\b"), "rera"),
    (re.compile(r"(?i)consumer protection|\bCPA\b"), "cpa"),
    (re.compile(r"(?i)legal services"), "lsa"),
    (re.compile(r"(?i)penal code|nyaya sanhita|contract act|evidence act|transfer of property|specific relief|"
                r"income tax|companies act|insolvency|\bIBC\b|limitation act|registration act|constitution"), "other"),
]
CASE_RES = [
    re.compile(r"\b[A-Z][\w.&']*(?:\s+(?:[A-Z][\w.&']*|of|and|&))*\s+(?:v\.|vs\.?|versus)\s+[A-Z][\w.&']*(?:\s+(?:[A-Z][\w.&']*|of|and|&))*"),
    re.compile(r"\(\s*\d{4}\s*\)\s*\d+\s*SCC\s*\d+"),
    re.compile(r"\bAIR\s*\d{4}\s*(?:SC|[A-Z]{2,4})\s*\d+"),
    re.compile(r"\b\d{4}\s*SCC\s*OnLine\s*\w+\s*\d+", re.IGNORECASE),
]
# "Refund vs Possession" compares two choices; it is not a case name
PLAIN_WORDS = {"refund", "possession", "interest", "stay", "staying", "wait", "waiting", "withdraw", "withdrawing", "option",
               "choice", "a", "b", "c", "one", "two", "compensation", "repair", "notice", "complaint", "rera", "consumer",
               "commission", "court", "authority", "builder", "buyer", "flat", "money", "delay", "defects", "exit", "continue",
               "keep", "leave", "the", "of", "and", "your", "you", "tg", "route", "civil", "forum", "form", "m", "n"}


def _is_case_name(text: str) -> bool:
    words = [w.lower() for w in re.findall(r"[A-Za-z]+", text) if w.lower() not in ("v", "vs", "versus")]
    return not all(w in PLAIN_WORDS for w in words)


CASE_PLACEHOLDER = "[court case reference removed - I don't cite judgments]"
SECTION_PLACEHOLDER = "[unverified legal reference removed]"


# "the Negotiable Instruments Act", "Indian Penal Code" - but not "the Act", "the said Act", "these Rules"
_SOME_NAMED_LAW = re.compile(r"(?i)\b(?!(?:the|said|this|that|same|above|these|those|such|aforesaid)\s)[\w&]+\s+"
                             r"(?:act|code|sanhita|adhiniyam|rules|regulations)\b")


def _act_named(after: str) -> str | None:
    """Which law the words after a bare reference name: a known key, "other" for a law we don't hold,
    or None when no law is named ("Section 18 of the Act", "Section 18 in plain words")."""
    m = re.match(r"\s*(?:\(\s*\w+\s*\)\s*)*(?:of|under|in)\s+(?:the\s+)?(.{0,70})", after, re.I)
    if not m:
        return None
    named = re.split(r"[.;\n]", m.group(1))[0]   # stay inside this sentence
    for rx, key in ACT_ALIASES:
        if rx.search(named):
            return key
    return "other" if _SOME_NAMED_LAW.search(named) else None


def validate_citations(text: str, entries: list) -> tuple[str, list]:
    """Returns (clean_text, removed). Allowed: tags of this turn's entries. A bare 'Section 18'
    becomes '[RERA-18-1]' only if it matches a retrieved entry (same Act if an Act is named);
    anything else - other Acts, Articles, IPC/BNS, case law, unknown tags - is removed."""
    allowed = {e["id"]: e for e in entries}
    removed = []

    def tag_sub(m):
        if m.group(1) in allowed:
            return m.group(0)
        removed.append(("unknown_tag", m.group(0)))
        return ""

    text = TAG_RE.sub(tag_sub, text)
    text = BLOCK_LABEL_RE.sub("", text)

    def ref_sub(m):
        word = (m.group("w") or m.group("wi") or "").lower()
        num = m.group("n") or m.group("ni")
        if word.startswith(("art", "अनुच्छेद", "ఆర్టికల్")):
            removed.append(("article", m.group(0)))
            return SECTION_PLACEHOLDER
        kind = "rule" if word.startswith(("rule", "r.", "नियम", "నియమం", "నిబంధన")) else "section"
        act = _act_named(text[m.end(): m.end() + 90])
        sub = sub_parts(m.group("sub") or m.group("subi"))
        cands = [e for e in allowed.values() if e.get("ref_kind") == kind and e.get("ref_num") == num.rstrip("ABCDEFGHabcdefgh")
                 and e.get("kind") == "law" and (act is None or act == e.get("act_key")) and sub_matches(sub, e)]
        if cands:
            return f"[{cands[0]['id']}]"
        removed.append(("unverified_section", m.group(0)))
        return SECTION_PLACEHOLDER

    text = REF_RE.sub(ref_sub, text)

    def other_sub(m):
        removed.append(("other_law", m.group(0)))
        return SECTION_PLACEHOLDER

    text = OTHER_LAW_RE.sub(other_sub, text)
    for rx in CASE_RES:
        def case_sub(m, rx=rx):
            if rx is CASE_RES[0] and not _is_case_name(m.group(0)):
                return m.group(0)
            removed.append(("case_law", m.group(0)))
            return CASE_PLACEHOLDER
        text = rx.sub(case_sub, text)
    # collapse "[RERA-18-1] [RERA-18-1]" created by tag + converted bare reference
    text = re.sub(r"(\[[A-Z0-9-]+\])(\s*\1)+", r"\1", text)
    text = re.sub(re.escape(SECTION_PLACEHOLDER) + r"(?:\s*" + re.escape(SECTION_PLACEHOLDER) + r")+", SECTION_PLACEHOLDER, text)
    return text, removed


_TAG = r"[A-Z]{2,6}(?:-[A-Z0-9]+)+"
TAG_LIST_RE = re.compile(r"\[(" + _TAG + r"(?:\s*(?:,|;|and|&)\s*" + _TAG + r")+)\]")


def split_tag_lists(text: str) -> str:
    """Some models put several tags in one bracket: [RERA-18-1, RERA-19-4] -> [RERA-18-1] [RERA-19-4],
    so each one is checked and listed under the sources like any other tag."""
    return TAG_LIST_RE.sub(lambda m: " ".join(f"[{t}]" for t in re.findall(_TAG, m.group(1))), text)


def cited_ids(text: str) -> list:
    seen = []
    for m in TAG_RE.finditer(text):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


# ---------- amounts ----------
AMOUNT_RE = re.compile(
    r"(?i)(?P<cur>(?<![A-Za-z])Rs\.?|₹|(?<![A-Za-z])INR|रु\.?|रुपये|రూ\.?)?\s?(?P<num>\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?:\s?(?P<unit>lakhs?|lacs?|lakh|crores?|cr\b|లక్షలు|లక్షల|లక్ష|కోట్లు|కోటి|लाख|करोड़))?"
    r"(?P<cur2>\s?(?:rupees|रुपये|రూపాయలు))?"
)
UNITS = {"lakh": 10**5, "lakhs": 10**5, "lac": 10**5, "lacs": 10**5, "crore": 10**7, "crores": 10**7, "cr": 10**7,
         "లక్షలు": 10**5, "లక్షల": 10**5, "లక్ష": 10**5, "కోట్లు": 10**7, "కోటి": 10**7, "लाख": 10**5, "करोड़": 10**7}


def find_amounts(text: str) -> list:
    """[(start, end, value)] for money mentions: needs a currency marker or a lakh/crore unit."""
    out = []
    for m in AMOUNT_RE.finditer(text):
        if not (m.group("cur") or m.group("unit") or m.group("cur2")):
            continue
        n = float(m.group("num").replace(",", ""))
        unit = (m.group("unit") or "").lower()
        out.append((m.start("num") if not m.group("cur") else m.start(), m.end(), n * UNITS.get(unit, 1)))
    return out


def unknown_amounts(text: str, allowed: set) -> list:
    return [text[s:e] for s, e, v in find_amounts(text) if not _amount_ok(v, allowed)]


# amounts that appear in the verified law entries (fee, consumer-commission limits, legal-aid income)
LAW_AMOUNTS = {1000, 9000, 12000, 50 * 10**5, 2 * 10**7}


def _amount_ok(v: float, allowed: set) -> bool:
    if v < 1000:  # small figures (percentages, fees like 1000 are allowed separately) aren't checked
        return True
    return any(abs(v - a) <= max(1, 0.006 * a) for a in set(allowed) | LAW_AMOUNTS)  # tolerate rounding like "25.2 lakh"


def mark_amounts(text: str, allowed: set, language: str = "English") -> tuple[str, list]:
    """Keep figures, but flag any not produced by code (calculator, case file, law entries)."""
    flagged = []
    for s, e, v in reversed(find_amounts(text)):
        if not _amount_ok(v, allowed):
            flagged.append(text[s:e])
            text = text[:e] + f" ({T('unverified_amount', language)})" + text[e:]
    return text, flagged[::-1]


# ---------- quotes ----------
QUOTE_RE = re.compile(r"[\"“”]([^\"“”]{12,600})[\"“”]")


def check_quotes(text: str, entries: list, language: str = "English") -> tuple[str, list]:
    """A quoted span within 60 chars of a tag must appear verbatim (after norm) in that tag's
    exact text. Otherwise its quotation marks are dropped and it's marked 'not exact law text'."""
    by_id = {e["id"]: norm(e["quote_text"]).lower() for e in entries}
    bad = []

    def sub(m):
        span = m.group(1)
        window = text[max(0, m.start() - 60): m.end() + 60]
        tags = [t for t in TAG_RE.findall(window) if t in by_id]
        if not tags:
            return m.group(0)  # not presented as law (e.g. quoting the user) - leave alone
        q = norm(span).lower().strip(" .,;:…").replace("...", "…")
        parts = [p.strip() for p in q.split("…") if p.strip()]
        if parts and all(any(p in by_id[t] for t in tags) for p in parts):
            return m.group(0)
        bad.append(span[:80])
        return f"{span} ({T('not_exact_law', language)})"

    return QUOTE_RE.sub(sub, text), bad
