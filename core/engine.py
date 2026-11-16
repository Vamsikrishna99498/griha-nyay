"""The conversation engine. Code owns the flow; the LLM only fills in language.

intake -> (escalate?) -> advise -> follow-up Q&A
Used by both the Streamlit app and run_tests.py, so tests exercise the real path.
"""
import json
import re
from datetime import date
from pathlib import Path

from . import guardrails, llm, retrieve
from .calculator import compute, inr
from .case import CaseFile

PROMPTS = Path(__file__).parent.parent / "prompts"
MAX_FOLLOWUPS = 2
HISTORY_WINDOW = 8
# After the first advice, a message matching this may change a fact -> re-run extraction.
FACT_HINT = re.compile(
    r"\d|lakh|lac|crore|actually|correction|mistake|wrong|typo|i meant|changed my mind|instead|"
    r"refund|possession|registered|rera|agreement|promised|లక్ష|लाख|करोड़", re.IGNORECASE)
TRACKED = {
    "state": "State", "builder_name": "Builder", "project_name": "Project", "rera_number": "RERA no.",
    "rera_registered": "RERA registered", "agreement_date": "Agreement date",
    "promised_possession_date": "Promised possession", "total_price_rupees": "Total price",
    "amount_paid_rupees": "Amount paid", "goal": "What you want", "payments": "Payments",
}
# Escalations after which the bot must not draft filings for the user.
DRAFT_BLOCKERS = {"insolvency", "already_in_court", "criminal", "title_dispute", "out_of_state", "unregistered"}
OFF_TOPIC_MSG = (
    "I'm built for only one kind of problem: **a builder delaying possession of a flat or house you bought "
    "in Telangana**. Your problem ({topic}) is outside what I cover, and I don't want to guess about law I "
    "haven't checked.\n\n**Where to get help:** free legal aid from the District Legal Services Authority "
    "(DLSA) at your district court, or the NALSA helpline **15100**.\n\nIf your problem *is* about a delayed "
    "flat from a builder, tell me more and I'll help."
)


def _p(name: str) -> str:
    return (PROMPTS / name).read_text()


class Session:
    def __init__(self, as_of: date | None = None, rate_pct: float | None = None):
        self.case = CaseFile()
        self.messages = []          # visible chat [{"role","content"}]
        self.stage = "intake"       # intake | advised
        self.followups = 0
        self.escalations = []       # [(id, msg)]
        self.cautions = []
        self.as_of = as_of
        self.rate_pct = rate_pct
        self.log = []               # audit trail: removed citations, unknown amounts, errors
        self._in_scope = None
        self._topic = ""

    # ---------- helpers ----------
    def user_text(self) -> str:
        return "\n".join(m["content"] for m in self.messages if m["role"] == "user")

    def calc(self):
        c = self.case
        return compute(c.promised_possession_date, c.amount_paid_rupees, c.payments,
                       as_of=self.as_of, rate_pct=self.rate_pct)

    def drafts_allowed(self) -> bool:
        return self.stage == "advised" and not ({i for i, _ in self.escalations} & DRAFT_BLOCKERS)

    def _history(self, n: int = HISTORY_WINDOW) -> list:
        """Recent chat for the model, minus the long 'Sources used' blocks (saves tokens)."""
        return [{"role": m["role"], "content": m["content"].split("\n\n---\n**Sources used**")[0]}
                for m in self.messages[-n:]]

    @staticmethod
    def _fmt(k, v):
        if v is None or v == []:
            return "—"
        if k.endswith("_rupees"):
            return inr(v)
        if k == "payments":
            return f"{len(v)} dated payment(s)"
        return str(v)

    def _diff_note(self, before: dict, after: dict) -> str:
        changes = [f"{label}: {self._fmt(k, before.get(k))} → {self._fmt(k, after.get(k))}"
                   for k, label in TRACKED.items() if before.get(k) != after.get(k)]
        if changes:
            self.log.append({"type": "case_updated", "items": changes})
            return "📝 **Updated your case file:** " + "; ".join(changes) + "\n\n"
        return ""

    def _guarded(self, text: str, entries: list, calc=None) -> str:
        clean, removed = guardrails.validate_citations(text, entries)
        if removed:
            self.log.append({"type": "citations_removed", "items": removed})
        if calc:
            allowed = calc.allowed_amount_strings() | {
                inr(x) for x in [self.case.amount_paid_rupees, self.case.total_price_rupees] if x
            } | {inr(p["amount_rupees"]) for p in self.case.payments}
            unk = guardrails.unknown_amounts(clean, allowed)
            if unk:
                self.log.append({"type": "amounts_not_from_calculator", "items": unk})
        ids = guardrails.cited_ids(clean)
        if ids:
            clean += "\n\n---\n**Sources used** (from my checked list — nothing else):\n" + retrieve.sources_block(ids)
        return clean

    # ---------- steps ----------
    def _intake(self) -> None:
        prompt = _p("intake.txt").format(
            missing=", ".join(self.case.missing_required().values()) or "nothing",
            case_json=json.dumps(self.case.to_dict(), ensure_ascii=False),
        )
        data = llm.chat_json([
            {"role": "system", "content": prompt},
            {"role": "user", "content": self.user_text()},
        ])
        asked_about = set(self.case.missing_required())
        self._in_scope = data.get("in_scope") if isinstance(data.get("in_scope"), bool) else None
        self._topic = str(data.get("topic") or "").strip()
        self.case.update_from(data)
        still_missing = self.case.missing_required()
        self._followup_q = (data.get("followup_question") or "").strip()
        # The model wrote its question before code filled in fields (e.g. Hyderabad -> Telangana).
        # If the missing set changed, don't let it re-ask known things: build the question in code.
        if set(still_missing) != asked_about or not self._followup_q:
            self._followup_q = ("Thanks, that helps. To work out your options I still need: "
                                + "; ".join(still_missing.values()) + "." if still_missing else "")

    def _advise(self, question: str | None = None) -> str:
        calc = self.calc()
        query = self.user_text() + " " + (question or "") + " " + " ".join(self.case.builder_excuses)
        entries = retrieve.retrieve(query)
        extra = []
        if "force_majeure" in self.cautions:
            extra.append("7. The builder is claiming force majeure / pandemic / extension. Explain [RERA-6] honestly: RERA describes force majeure as war, flood, drought, fire, cyclone, earthquake or other natural calamity; whether the builder's excuse counts is for TG-RERA to decide on the facts. Tell them to check the TG-RERA portal for any extension granted and that a lawyer should review if one was granted. Do NOT add conditions of your own (no 'only if').")
        if self.escalations:
            reasons = "; ".join(i for i, _ in self.escalations)
            extra.append(f"7. This case was flagged for a real lawyer ({reasons}). Do NOT tell them to file anything themselves. Only help them understand the situation and prepare for meeting a lawyer / DLSA.")
        system = _p("advisor.txt").format(
            language=self.case.language or "English",
            extra_rules="\n".join(extra),
            law=retrieve.format_for_prompt(entries),
            case_json=json.dumps(self.case.to_dict(), ensure_ascii=False),
            calc=json.dumps(calc.figures(), ensure_ascii=False, indent=1),
        )
        msgs = [{"role": "system", "content": system}]
        if question is None:
            msgs.append({"role": "user", "content": self.user_text() + "\n\n" + _p("first_advice.txt")})
        else:
            msgs += self._history()
        return self._guarded(llm.chat(msgs, temperature=0.2), entries, calc)

    def _escalation_reply(self) -> str:
        lines = ["**I need to be honest: this part needs a real lawyer.**", ""]
        lines += [f"- {msg}" for _, msg in self.escalations]
        lines += [
            "",
            "**Free legal help:** District Legal Services Authority (DLSA) at your district court, or call the NALSA helpline **15100**.",
            "",
            "**Take this case summary with you:**",
            self.case_summary_md(),
        ]
        return "\n".join(lines)

    # ---------- public ----------
    def handle(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        try:
            reply = self._handle()
        except Exception as e:
            self.log.append({"type": "error", "detail": str(e)})
            reply = f"Sorry, I had a technical problem ({e}). Please try again in a moment."
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def _handle(self) -> str:
        new_esc_from_text = guardrails.check_escalation(self.messages[-1]["content"], self.case)
        for c in guardrails.check_cautions(self.messages[-1]["content"]):
            if c not in self.cautions:
                self.cautions.append(c)

        if self.stage == "intake":
            self._intake()
            if self._in_scope is False:
                self.log.append({"type": "off_topic", "topic": self._topic})
                return OFF_TOPIC_MSG.format(topic=self._topic or "a different kind of legal problem")
            esc = guardrails.check_escalation(self.user_text(), self.case)
            newly = [e for e in esc if e[0] not in {i for i, _ in self.escalations}]
            self.escalations += newly
            if newly:
                self.stage = "advised"
                return self._escalation_reply()
            missing = self.case.missing_required()
            if missing and self.followups < MAX_FOLLOWUPS:
                self.followups += 1
                return self._followup_q or ("To help you properly I need: " + "; ".join(missing.values()) + ".")
            self.stage = "advised"
            return self._advise()

        # advised stage: free Q&A. If the message may change a fact, re-extract so the
        # calculator and drafts use the latest values, and tell the user what changed.
        text = self.messages[-1]["content"]
        prefix = ""
        # questions rarely carry new facts; anything else (or anything with numbers/fact words) might
        if FACT_HINT.search(text) or not text.strip().endswith("?"):
            before = self.case.to_dict()
            self._intake()
            prefix = self._diff_note(before, self.case.to_dict())
        esc = new_esc_from_text + guardrails.check_escalation("", self.case)  # text rules + re-checked case rules
        newly = [e for e in esc if e[0] not in {i for i, _ in self.escalations}]
        if newly:
            self.escalations += list(dict(newly).items())
            return prefix + self._escalation_reply()
        return prefix + self._advise(question=text)

    def case_summary_md(self) -> str:
        c, calc = self.case, self.calc()
        rows = [
            ("Buyer", c.buyer_name), ("Builder", c.builder_name), ("Project", c.project_name),
            ("Flat", c.flat_details), ("City / State", ", ".join(filter(None, [c.city, c.state]))),
            ("RERA no.", c.rera_number), ("Agreement date", c.agreement_date),
            ("Promised possession", c.promised_possession_date), ("Total price", inr(c.total_price_rupees) if c.total_price_rupees else None),
            ("Paid so far", inr(c.amount_paid_rupees) if c.amount_paid_rupees else None),
            ("Delay", f"{calc.delay_days} days" if c.promised_possession_date else None),
            ("Wants", c.goal), ("Builder's excuses", "; ".join(c.builder_excuses) or None),
            ("Proof they have", "; ".join(c.evidence) or None),
            ("Assumptions I made", "; ".join(c.assumptions) or None),
        ]
        out = "\n".join(f"- **{k}:** {v if v else '—'}" for k, v in rows)
        if c.timeline:
            out += "\n- **Timeline:**\n" + "\n".join(f"  - {t.get('date') or 'date not given'}: {t.get('event','')}" for t in c.timeline if isinstance(t, dict))
        return out
