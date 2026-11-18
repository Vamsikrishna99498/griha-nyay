"""First aid for everyday problems OUTSIDE the verified law (anything that is not a builder delay or defect).

No law is stated for these. The model only turns the story into a short case note; code validates it,
adds a practical list of papers to collect (knowledge/first_aid.json) and help pointers from
helplines.json, and offers the note as a download to take to a lawyer or free legal aid."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .calculator import inr
from .case import LANG_WORDS, _clean_str, _to_amount
from .i18n import code_lang

# A sentence that names a law does not belong in a note for a problem whose law was never checked.
LAW_TALK = re.compile(r"(?i:\bsections?\b|\bsec\.|\bu/s\b|\bstatute|\bjudg(?:e)?ment|\bsupreme court\b|\bhigh court\b|\bipc\b|\bbns\b|\bcrpc\b)"
                      r"|\bAct\b|धारा|अधिनियम|సెక్షన్|చట్టం ప్రకారం")


def without_law_talk(text: str | None) -> str | None:
    """Drop every sentence that mentions a section, an Act, a code or a court ruling."""
    if not text:
        return text
    kept = [s for s in re.split(r"(?<=[.!?।])\s+", text) if not LAW_TALK.search(s)]
    return " ".join(kept).strip() or None


FIRST_AID = json.loads((Path(__file__).parent.parent / "knowledge" / "first_aid.json").read_text())["categories"]
CATEGORIES = set(FIRST_AID)
MAX_ASKS = 3   # follow-up questions before the note is simply kept as it is
ROW_LABELS = {   # the note's headings; the downloaded copy is always English, for the lawyer who reads it
    "en": ["Problem", "Who it is with", "What happened", "Money involved", "What you want", "Proof you have", "Timeline", "date not given"],
    "hi": ["समस्या", "किसके साथ", "क्या हुआ", "कितनी रक़म", "आप क्या चाहते हैं", "आपके पास सबूत", "घटनाक्रम", "तारीख़ नहीं दी"],
    "te": ["సమస్య", "ఎవరితో", "ఏం జరిగింది", "ఎంత డబ్బు", "మీకు ఏం కావాలి", "మీ దగ్గర ఉన్న రుజువులు", "ఘటనల క్రమం", "తేదీ ఇవ్వలేదు"],
}


def clean_general(d) -> tuple[dict, list]:
    """Whitelist + type/length checks on the model's JSON, like case.clean_extraction. Returns (clean, dropped_keys)."""
    if not isinstance(d, dict):
        return {}, ["<not an object>"]
    out, dropped = {}, []
    for k, v in d.items():
        if k in ("builder_problem", "urgent"):
            if isinstance(v, bool):
                out[k] = v
        elif k == "category":
            if isinstance(v, str) and v in CATEGORIES:
                out[k] = v
        elif k in ("other_party", "wants"):
            s = _clean_str(v, 100)
            if s:
                out[k] = s
        elif k == "summary":
            s = without_law_talk(_clean_str(v, 500))
            if s:
                out[k] = s
        elif k == "amount_rupees":
            a = _to_amount(v)
            if a:
                out[k] = a
        elif k == "timeline":
            if isinstance(v, list):
                out[k] = [{"date": _clean_str(t.get("date"), 40), "event": _clean_str(t.get("event"), 160)}
                          for t in v[:10] if isinstance(t, dict) and _clean_str(t.get("event"))]
        elif k == "evidence":
            if isinstance(v, list):
                out[k] = [s for s in (_clean_str(x, 120) for x in v[:10]) if s]
        elif k == "language":
            lang = LANG_WORDS.get(str(v).strip().lower().split(" ")[0]) if isinstance(v, str) else None
            if lang:
                out[k] = lang
        elif k == "followup_question":
            s = _clean_str(v, 300)
            if s and not LAW_TALK.search(s):   # a question that brings up law is not asked at all
                out[k] = s
        else:
            dropped.append(k)
    return out, dropped


@dataclass
class GeneralCase:
    category: str = "other"
    other_party: str | None = None
    summary: str | None = None
    amount_rupees: int | None = None
    wants: str | None = None
    timeline: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    urgent: bool = False

    def update_from(self, d: dict) -> None:
        """Merge CLEANED values. Nulls never erase; lists are unions; urgent only ever switches on."""
        for k in ("category", "other_party", "summary", "amount_rupees", "wants"):
            if d.get(k):
                setattr(self, k, d[k])
        self.urgent = self.urgent or d.get("urgent") is True
        seen = {(t.get("date"), t.get("event")) for t in self.timeline}
        for t in d.get("timeline") or []:
            if (t.get("date"), t.get("event")) not in seen:
                self.timeline.append(t)
                seen.add((t.get("date"), t.get("event")))
        for e in d.get("evidence") or []:
            if e not in self.evidence:
                self.evidence.append(e)

    def has_facts(self) -> bool:
        return bool(self.summary or self.other_party or self.amount_rupees or self.wants or self.timeline or self.evidence)

    def label(self, language: str | None) -> str:
        lab = FIRST_AID[self.category]["label"]
        return lab.get(code_lang(language), lab["en"])

    def collect(self, language: str | None) -> list:
        lc = code_lang(language)
        return [item.get(lc, item["en"]) for item in FIRST_AID[self.category]["collect"]]

    def help_ids(self) -> list:
        return (["police"] if self.urgent else []) + FIRST_AID[self.category]["help"]

    def to_dict(self) -> dict:
        return {"category": self.category, "other_party": self.other_party, "summary": self.summary,
                "amount_rupees": self.amount_rupees, "wants": self.wants, "timeline": [dict(t) for t in self.timeline],
                "evidence": list(self.evidence), "urgent": self.urgent}   # copies: a snapshot must not change later

    def summary_md(self, language: str | None = "English") -> str:
        names = ROW_LABELS[code_lang(language)]
        values = [self.label(language), self.other_party, self.summary, inr(self.amount_rupees) if self.amount_rupees else None,
                  self.wants, "; ".join(self.evidence) or None]
        out = "\n".join(f"- **{k}:** {v if v else '—'}" for k, v in zip(names, values))
        if self.timeline:
            out += f"\n- **{names[6]}:**\n" + "\n".join(f"  - {t.get('date') or names[7]}: {t.get('event', '')}" for t in self.timeline)
        return out
