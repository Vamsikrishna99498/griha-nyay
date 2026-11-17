"""Remove clear ID numbers from user text BEFORE anything is stored or sent to a model.

Removed values are never kept and never re-inserted: the bot doesn't need them. Spaced-out round
figures and years ("paid 75000 50000", "in 2022 2023 2024") are left alone: they are facts. Names and
addresses are not detected (unreliable in Telugu/Hindi text); instead the Drafts tab collects
them in a local form that is never sent to the model. Amounts, dates and RERA numbers
(e.g. P02400003456) must survive untouched - tests check this.
"""
import re

_DIGIT_SEP = r"[ \-]?"
# not part of a longer number or an Indian-format amount like 14,20,000 / 4.5
NB = r"(?<!\d)(?<!\d[,.])"
NA = r"(?!\d)(?![,.]\d)"


def _groups(text: str) -> list:
    return [g for g in re.split(r"[\s-]+", text) if g]


def _round_or_years(groups: list) -> bool:
    """Spaced-out groups that are all round figures (75000 50000) or all years (2022 2023 2024) are
    amounts and dates the person is telling us, not an ID number."""
    return len(groups) > 1 and (all(g.endswith("00") for g in groups) or all(re.fullmatch(r"(?:19|20)\d\d", g) for g in groups))


def _not_aadhaar(m) -> bool:
    return _round_or_years(_groups(m.group(0)))


def _not_phone(m) -> bool:
    return _round_or_years(_groups(re.sub(r"^(?:\+91[\s-]?|0)", "", m.group(0))))


def _not_account(m) -> bool:
    digits = re.sub(r"\D", "", m.group(1))
    return len(digits) < 9 or _round_or_years(_groups(m.group(1)))   # "account on 15 03 2024" is a date


# (kind, pattern, optional test that says "this match is not an ID after all")
PATTERNS = [
    # e-mail
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b"), None),
    # PAN: 5 letters, 4 digits, 1 letter (people also type it in small letters)
    ("PAN", re.compile(r"(?i)\b[A-Z]{5}\d{4}[A-Z]\b"), None),
    # IFSC: 4 letters, 0, 6 alphanumerics
    ("IFSC", re.compile(r"(?i)\b[A-Z]{4}0[A-Z0-9]{6}\b"), None),
    # bank account: 9-18 digits only right after an account cue word
    ("bank account", re.compile(
        r"(?i)(?:a/c|acct|account|acc\.?\s*no|khata|खाता|ఖాతా)[^\d\n]{0,25}(\d[\d ]{7,20}\d)"), _not_account),
    # Aadhaar: 12 digits, first 2-9, optionally grouped 4-4-4
    ("Aadhaar", re.compile(NB + r"[2-9]\d{3}" + _DIGIT_SEP + r"\d{4}" + _DIGIT_SEP + r"\d{4}" + NA), _not_aadhaar),
    # Indian mobile: optional +91/0, 10 digits starting 6-9 (also 5-5 grouped)
    ("phone", re.compile(NB + r"(?:\+91[\s-]?|0)?[6-9]\d{4}[\s-]?\d{5}" + NA), _not_phone),
    # landline: STD code starting 0, a space or hyphen, then 6-8 digits (040-23456789)
    ("phone", re.compile(NB + r"0\d{2,4}[\s-]\d{6,8}" + NA), None),
]


def scrub(text: str) -> tuple[str, list[str]]:
    """Returns (clean_text, kinds_removed). Each match becomes '[removed: <kind>]'."""
    found = []
    for kind, rx, not_an_id in PATTERNS:
        def sub(m, kind=kind, not_an_id=not_an_id):
            if not_an_id and not_an_id(m):
                return m.group(0)
            found.append(kind)
            if m.lastindex:  # keep the cue word ("account no:"), drop only the number
                s, e = m.span(1)
                return m.group(0)[: s - m.start()] + f"[removed: {kind}]" + m.group(0)[e - m.start():]
            return f"[removed: {kind}]"
        text = rx.sub(sub, text)
    return text, sorted(set(found), key=found.index)
