"""The structured case file. Filled by the LLM (intake), validated by code."""
from dataclasses import asdict, dataclass, field
from datetime import date

from dateutil import parser as dparser

TELANGANA_PLACES = [
    "telangana", "hyderabad", "secunderabad", "gachibowli", "kokapet", "kondapur", "hitec city",
    "madhapur", "kukatpally", "miyapur", "shamshabad", "warangal", "karimnagar", "nizamabad",
    "medchal", "rangareddy", "ranga reddy", "sangareddy", "tellapur", "narsingi", "kompally",
    "uppal", "lb nagar", "manikonda", "bachupally", "adibatla", "patancheru", "ghatkesar",
]

REQUIRED = {
    "state": "which state the flat is in",
    "promised_possession_date": "the possession date promised in your agreement",
    "amount_paid_rupees": "how much you have paid the builder so far",
}


def _to_date(v):
    if not v:
        return None
    if isinstance(v, date):
        return v
    try:  # the prompt asks for ISO dates; parse those strictly (dayfirst would flip 2021-03-10 to 3 Oct)
        return date.fromisoformat(str(v).strip()[:10])
    except ValueError:
        pass
    try:
        d = dparser.parse(str(v), dayfirst=True, default=dparser.parse("2000-01-01")).date()
        return d if 1990 < d.year < 2100 else None
    except (ValueError, OverflowError):
        return None


def _to_amount(v):
    try:
        n = int(float(str(v).replace(",", "")))
        return n if n > 0 else None
    except (TypeError, ValueError):
        return None


@dataclass
class CaseFile:
    language: str = "English"
    state: str | None = None
    city: str | None = None
    buyer_name: str | None = None
    builder_name: str | None = None
    project_name: str | None = None
    flat_details: str | None = None
    rera_number: str | None = None
    rera_registered: bool | None = None
    agreement_date: date | None = None
    promised_possession_date: date | None = None
    total_price_rupees: int | None = None
    amount_paid_rupees: int | None = None
    payments: list = field(default_factory=list)  # [{"date": date, "amount_rupees": int}]
    evidence: list = field(default_factory=list)
    goal: str | None = None  # refund | possession | unsure
    builder_excuses: list = field(default_factory=list)
    timeline: list = field(default_factory=list)  # [{"date": str, "event": str}]
    assumptions: list = field(default_factory=list)  # guesses made while reading the story

    def update_from(self, d: dict) -> None:
        """Merge LLM-extracted values; code validates types. Never erase known facts with nulls."""
        for k in ["language", "state", "city", "buyer_name", "builder_name", "project_name",
                  "flat_details", "rera_number"]:
            if d.get(k):
                setattr(self, k, str(d[k]).strip())
        if isinstance(d.get("rera_registered"), bool):
            self.rera_registered = d["rera_registered"]
        if self.rera_number:
            self.rera_registered = True if self.rera_registered is None else self.rera_registered
        for k in ["agreement_date", "promised_possession_date"]:
            v = _to_date(d.get(k))
            if v:
                setattr(self, k, v)
        for k in ["total_price_rupees", "amount_paid_rupees"]:
            v = _to_amount(d.get(k))
            if v:
                setattr(self, k, v)
        pays = []
        for p in d.get("payments") or []:
            if isinstance(p, dict):
                pd, pa = _to_date(p.get("date")), _to_amount(p.get("amount_rupees"))
                if pd and pa:
                    pays.append({"date": pd, "amount_rupees": pa})
        if pays:
            self.payments = sorted(pays, key=lambda x: x["date"])
        for k in ["evidence", "builder_excuses", "timeline", "assumptions"]:
            if d.get(k):
                setattr(self, k, list(d[k]))
        if d.get("goal") in ("refund", "possession", "unsure"):
            self.goal = d["goal"]
        self._normalise_state()

    def _normalise_state(self) -> None:
        """Infer Telangana from a Telangana place name, but never override another state the user gave."""
        if self.state and not any(p in self.state.lower() for p in TELANGANA_PLACES):
            return
        blob = " ".join(filter(None, [self.state, self.city, self.project_name])).lower()
        if any(p in blob for p in TELANGANA_PLACES):
            self.state = "Telangana"

    def missing_required(self) -> dict:
        return {k: v for k, v in REQUIRED.items() if not getattr(self, k)}

    def missing_proof(self) -> list:
        tips = []
        ev = " ".join(self.evidence).lower()
        if "agreement" not in ev:
            tips.append("Copy of the agreement for sale (shows the promised date)")
        if not any(w in ev for w in ["receipt", "bank", "statement", "payment"]):
            tips.append("Payment receipts / bank statements for every instalment")
        if not self.rera_number:
            tips.append("Project's RERA registration number (search on rera.telangana.gov.in)")
        if not any(w in ev for w in ["email", "letter", "whatsapp", "message", "notice"]):
            tips.append("Emails/letters/WhatsApp from the builder about the delay")
        return tips

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ["agreement_date", "promised_possession_date"]:
            d[k] = d[k].isoformat() if d[k] else None
        d["payments"] = [{"date": p["date"].isoformat(), "amount_rupees": p["amount_rupees"]} for p in self.payments]
        return d
