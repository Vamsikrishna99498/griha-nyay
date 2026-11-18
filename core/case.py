"""The structured case file = the bot's memory. Filled from intake JSON, but every value is
cleaned and validated by code (whitelist, types, enums, lengths) before it is merged."""
from __future__ import annotations

import calendar
import re
from dataclasses import asdict, dataclass, field
from datetime import date

from dateutil import parser as dparser

TELANGANA_PLACES = [
    "telangana", "hyderabad", "secunderabad", "gachibowli", "kokapet", "kondapur", "hitec city", "hitech city",
    "madhapur", "kukatpally", "miyapur", "shamshabad", "warangal", "karimnagar", "nizamabad", "medchal",
    "rangareddy", "ranga reddy", "sangareddy", "tellapur", "narsingi", "kompally", "uppal", "lb nagar",
    "manikonda", "bachupally", "adibatla", "patancheru", "ghatkesar", "nallagandla", "puppalaguda",
    "హైదరాబాద్", "సికింద్రాబాద్", "గచ్చిబౌలి", "కొండాపూర్", "బాచుపల్లి", "కూకట్‌పల్లి", "మియాపూర్",
    "తెలంగాణ", "వరంగల్", "हैदराबाद", "सिकंदराबाद", "तेलंगाना",
]
TELANGANA_ALIASES = {"telangana", "ts", "tg", "t.s.", "t.g.", "t.s", "t.g", "telangana state", "telengana",
                     "telangana, india", "తెలంగాణ", "तेलंगाना"}
TELANGANA_NAMES = ("telangana", "telengana", "తెలంగాణ", "तेलंगाना")
ANDHRA_ALIASES = {"andhra pradesh", "ap", "a.p.", "a.p", "andhra"}

DATE_FIELDS = ["agreement_date", "promised_possession_date", "possession_handed_over_date", "defect_reported_date"]
AMOUNT_FIELDS = ["total_price_rupees", "amount_paid_rupees"]
STR_FIELDS = {"state": 60, "city": 80, "builder_name": 80, "project_name": 80, "flat_details": 120,
              "rera_number": 40, "builder_response": 300}
LIST_FIELDS = ["evidence", "builder_excuses", "defects", "assumptions"]
BOOL_FIELDS = ["rera_registered", "permission_before_2017"]
CATEGORIES = {"delay", "defects"}
GOALS = {"refund", "possession", "unsure", "repair", "compensation"}
MESSAGE_KINDS = {"facts", "correction", "question", "hypothetical", "remove", "chat", "other"}
FLAG_KEYS = {"insolvency", "court_case_pending", "criminal_or_threat", "title_dispute"}
REMOVABLE = (set(STR_FIELDS) | set(DATE_FIELDS) | set(AMOUNT_FIELDS) | set(BOOL_FIELDS) | {"goal", "payments", "categories"}
             | set(LIST_FIELDS))
LANG_WORDS = {"telugu": "Telugu", "hindi": "Hindi", "tenglish": "Tenglish", "hinglish": "Hinglish", "english": "English"}

MONTH_ONLY_RE = re.compile(r"^(\d{4})-(\d{1,2})$")
YMD_RE = re.compile(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})(?!\d)")
STATE_ASSUMED_NOTE = ("No place was mentioned, so I assumed the flat is in Telangana (the only state I cover in detail). "
                      "Tell me if it is somewhere else.")
MONTH_END_NOTE = "Only the month was given for the promised possession date, so the delay is counted from the last day of that month"

REQUIRED = {
    "delay": ["state", "promised_possession_date", "amount_paid_rupees"],
    "defects": ["state", "possession_handed_over_date", "defects"],
}


def _to_date(v):
    if not v:
        return None
    if isinstance(v, date):
        return v
    s = str(v).strip()
    if re.fullmatch(r"\d{4}", s):
        return None  # a year alone is not a date (dateutil would make it 1 January)
    m = YMD_RE.match(s)
    try:  # the prompt asks for ISO dates; year-first is read strictly, padded or not (dayfirst would flip 2021-3-10 to 3 Oct)
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else date.fromisoformat(s[:10])
    except ValueError:
        if m:
            return None
        try:
            d = dparser.parse(s, dayfirst=True, default=dparser.parse("2000-01-01")).date()
        except (ValueError, OverflowError):
            return None
    return d if 1990 < d.year < 2100 else None


def _month_end(v) -> date | None:
    """'2024-12' -> 31 Dec 2024. A promise "by December" is not broken until the month ends."""
    m = MONTH_ONLY_RE.match(str(v or "").strip())
    if not m or not 1 <= int(m.group(2)) <= 12 or not 1990 < int(m.group(1)) < 2100:
        return None
    y, mo = int(m.group(1)), int(m.group(2))
    return date(y, mo, calendar.monthrange(y, mo)[1])


def _first_of_month_line(text: str, d: date) -> bool:
    t = text.lower()
    return bool(re.search(r"\b(1st|first)\b", t)) and str(d.year) in t and d.strftime("%b").lower() in t


def _to_amount(v):
    try:
        n = int(float(str(v).replace(",", "")))
        return n if 0 < n < 10**11 else None
    except (TypeError, ValueError, OverflowError):
        return None


def _clean_str(v, n: int = 200) -> str | None:
    if v is None or isinstance(v, (dict, list)):
        return None
    s = re.sub(r"[\x00-\x1f\x7f]+", " ", str(v)).strip()
    return s[:n] or None


def clean_extraction(d) -> tuple[dict, list]:
    """Whitelist + type/enum/length checks on the model's JSON. Returns (clean, dropped_keys).
    Anything odd is dropped, never trusted: this is the schema guard against injection."""
    if not isinstance(d, dict):
        return {}, ["<not an object>"]
    out, dropped = {}, []
    for k, v in d.items():
        if k in STR_FIELDS:
            s = _clean_str(v, STR_FIELDS[k])
            if s:
                out[k] = s
        elif k in DATE_FIELDS:
            end = _month_end(v) if k == "promised_possession_date" else None
            dt = end or _to_date(_clean_str(v, 40))
            if dt:
                out[k] = dt
            if end:
                out["promised_month_only"] = True
        elif k in AMOUNT_FIELDS:
            a = _to_amount(v)
            if a:
                out[k] = a
        elif k in BOOL_FIELDS or k == "in_scope":
            if isinstance(v, bool):
                out[k] = v
        elif k in LIST_FIELDS:
            if isinstance(v, list):
                out[k] = [s for s in (_clean_str(x, 200) for x in v[:20]) if s]
        elif k == "payments":
            if isinstance(v, list):
                pays = []
                for p in v[:40]:
                    if isinstance(p, dict):
                        pd, pa = _to_date(_clean_str(p.get("date"), 40)), _to_amount(p.get("amount_rupees"))
                        if pd and pa:
                            pays.append({"date": pd, "amount_rupees": pa})
                out[k] = pays
        elif k == "timeline":
            if isinstance(v, list):
                out[k] = [{"date": _clean_str(t.get("date"), 40), "event": _clean_str(t.get("event"), 200)}
                          for t in v[:20] if isinstance(t, dict) and _clean_str(t.get("event"))]
        elif k == "categories":
            if isinstance(v, list):
                out[k] = [c for c in v if isinstance(c, str) and c in CATEGORIES]
        elif k == "goal":
            if isinstance(v, str) and v in GOALS:
                out[k] = v
        elif k == "message_kind":
            if isinstance(v, str) and v in MESSAGE_KINDS:
                out[k] = v
        elif k == "remove_fields":
            if isinstance(v, list):
                out[k] = [f for f in v if isinstance(f, str) and f in REMOVABLE]
        elif k == "flags":
            if isinstance(v, dict):
                out[k] = {f: True for f, b in v.items() if f in FLAG_KEYS and b is True}
        elif k == "law_ids":
            if isinstance(v, list):
                out[k] = [s for s in (_clean_str(x, 30) for x in v[:4]) if s]
        elif k == "language":
            lang = LANG_WORDS.get(str(v).strip().lower().split(" ")[0]) if isinstance(v, str) else None
            if lang:
                out[k] = lang
            else:
                dropped.append(k)
        elif k in ("topic", "followup_question"):
            s = _clean_str(v, 60 if k == "topic" else 300)
            if s:
                out[k] = s
        else:
            dropped.append(k)
    if out.get("promised_month_only") and out.get("assumptions"):
        out["assumptions"] = [a for a in out["assumptions"] if not _first_of_month_line(a, out["promised_possession_date"])]
    return out, dropped


@dataclass
class CaseFile:
    language: str = "English"
    state: str | None = None
    city: str | None = None
    builder_name: str | None = None
    project_name: str | None = None
    flat_details: str | None = None
    rera_number: str | None = None
    rera_registered: bool | None = None
    permission_before_2017: bool | None = None
    categories: list = field(default_factory=list)   # delay | defects
    agreement_date: date | None = None
    promised_possession_date: date | None = None
    possession_handed_over_date: date | None = None
    total_price_rupees: int | None = None
    amount_paid_rupees: int | None = None
    payments: list = field(default_factory=list)      # [{"date": date, "amount_rupees": int}]
    goal: str | None = None
    defects: list = field(default_factory=list)
    defect_reported_date: date | None = None
    builder_response: str | None = None
    evidence: list = field(default_factory=list)
    builder_excuses: list = field(default_factory=list)
    timeline: list = field(default_factory=list)      # [{"date": str, "event": str}]
    assumptions: list = field(default_factory=list)

    @property
    def state_assumed(self) -> bool:
        return STATE_ASSUMED_NOTE in self.assumptions

    def assume_telangana(self) -> None:
        """The scope is stated up front, so a person who names no place is taken to be in Telangana. It is
        recorded as an assumption (shown in the advice and the case summary) and dropped once a place is given."""
        if not self.state:
            self.state = "Telangana"
            self.assumptions.append(STATE_ASSUMED_NOTE)

    def update_from(self, d: dict) -> None:
        """Merge CLEANED values (see clean_extraction). Nulls never erase; lists are unions."""
        if d.get("state") or d.get("city"):   # a real place replaces the assumption (and may turn out to be elsewhere)
            if self.state_assumed:
                self.assumptions.remove(STATE_ASSUMED_NOTE)
                self.state = None
        for k in STR_FIELDS:
            if d.get(k):
                setattr(self, k, d[k])
        for k in BOOL_FIELDS:
            if isinstance(d.get(k), bool):
                setattr(self, k, d[k])
        if self.rera_number and self.rera_registered is None:
            self.rera_registered = True
        for k in DATE_FIELDS + AMOUNT_FIELDS:
            if d.get(k):
                setattr(self, k, d[k])
        if d.get("promised_possession_date"):
            self.assumptions = [a for a in self.assumptions if not a.startswith(MONTH_END_NOTE)]
            if d.get("promised_month_only"):
                self.assumptions.append(f"{MONTH_END_NOTE} ({self.promised_possession_date.strftime('%d %B %Y')}).")
        for k in LIST_FIELDS:
            for x in d.get(k) or []:
                if x not in getattr(self, k):
                    getattr(self, k).append(x)
        seen = {(p["date"], p["amount_rupees"]) for p in self.payments}
        for p in d.get("payments") or []:
            if d.get("message_kind") == "correction" and (p["date"], p["amount_rupees"]) not in seen:
                # a correction replaces the payment it fixes (same date, or the only one of that amount)
                same_date = [q for q in self.payments if q["date"] == p["date"]]
                same_amount = [q for q in self.payments if q["amount_rupees"] == p["amount_rupees"]]
                old = same_date[0] if len(same_date) == 1 else same_amount[0] if len(same_amount) == 1 and not same_date else None
                if old:
                    seen.discard((old["date"], old["amount_rupees"]))
                    self.payments.remove(old)
            if (p["date"], p["amount_rupees"]) not in seen:
                self.payments.append(p)
                seen.add((p["date"], p["amount_rupees"]))
        self.payments.sort(key=lambda x: x["date"])
        tl = {(t.get("date"), t.get("event")) for t in self.timeline}
        for t in d.get("timeline") or []:
            if (t.get("date"), t.get("event")) not in tl:
                self.timeline.append(t)
        for c in d.get("categories") or []:
            if c not in self.categories:
                self.categories.append(c)
        if d.get("goal"):
            self.goal = d["goal"]
        self._normalise_state()

    def remove(self, fields: list) -> None:
        for f in fields:
            if f in REMOVABLE:
                setattr(self, f, [] if isinstance(getattr(self, f), list) else None)
        if "promised_possession_date" in fields:
            self.assumptions = [a for a in self.assumptions if not a.startswith(MONTH_END_NOTE)]

    def _normalise_state(self) -> None:
        """TS/TG/తెలంగాణ -> Telangana; infer Telangana from a Hyderabad-area place; an old
        'Andhra Pradesh' agreement for a Hyderabad-area flat is Telangana today (since 2014)."""
        st = (self.state or "").strip().lower()
        place = " ".join(filter(None, [self.city, self.project_name])).lower()
        in_tg_place = any(p in place for p in TELANGANA_PLACES)
        loose = " ".join(re.sub(r"[.,;:()\[\]/|-]+", " ", st).split())   # "Telangana.", "Hyderabad, Telangana"
        named = any(n in loose for n in TELANGANA_NAMES) or any(p in loose for p in TELANGANA_PLACES)
        if st in TELANGANA_ALIASES or loose in TELANGANA_ALIASES or named:
            self.state = "Telangana"
        elif st in ANDHRA_ALIASES and in_tg_place:
            self.state = "Telangana"
            note = "Agreement says Andhra Pradesh, but the place is in Telangana (state formed 2014) - treated as Telangana."
            if note not in self.assumptions:
                self.assumptions.append(note)
        elif not st and in_tg_place:
            self.state = "Telangana"

    def missing_required(self) -> list:
        cats = self.categories or ["delay"]
        need = []
        for c in cats:
            for f in REQUIRED[c]:
                if f == "amount_paid_rupees" and self.payments:
                    continue  # dated payments already say how much was paid
                if f not in need and not getattr(self, f):
                    need.append(f)
        return need

    def missing_proof(self) -> list:
        tips = []
        ev = " ".join(self.evidence).lower()
        if "agreement" not in ev:
            tips.append("Copy of the agreement for sale (shows the promised date and defect clause)")
        if not any(w in ev for w in ["receipt", "bank", "statement", "payment"]):
            tips.append("Payment receipts / bank statements for every instalment")
        if not self.rera_number:
            tips.append("Project's RERA registration number (search on rera.telangana.gov.in)")
        if not any(w in ev for w in ["email", "letter", "whatsapp", "message", "notice"]):
            tips.append("Emails/letters/WhatsApp from the builder")
        if "defects" in self.categories:
            if not any(w in ev for w in ["photo", "video"]):
                tips.append("Dated photos/videos of each defect")
            if not self.defect_reported_date:
                tips.append("A written, dated complaint about the defects sent to the builder (keep proof of delivery)")
            if not any(w in ev for w in ["possession letter", "handover", "possession"]):
                tips.append("Possession / handover letter (proves when the 5-year window started)")
        return tips

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in DATE_FIELDS:
            d[k] = d[k].isoformat() if d[k] else None
        d["payments"] = [{"date": p["date"].isoformat(), "amount_rupees": p["amount_rupees"]} for p in self.payments]
        return d
