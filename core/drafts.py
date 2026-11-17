"""Document drafting with NO model call. The numbered facts are built by code from the case file
(so dates and amounts are exact), the legal paragraphs quote the verified law entries, and the
buyer's name/address come from the local Drafts form (never sent to a model)."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .calculator import TG, inr
from .retrieve import KB

ROOT = Path(__file__).parent.parent
env = Environment(loader=FileSystemLoader(ROOT / "templates"), keep_trailing_newline=True)


def _d(x) -> str | None:
    return x.strftime("%d %B %Y") if x else None


def _q(s: str | None) -> str | None:
    """Text that goes inside the draft's own double quotes must not carry double quotes itself."""
    return re.sub(r'["“”]', "'", s) if s else s


def _end(s: str) -> str:
    """Drop the full stop (or other closing mark) a phrase already ends with; the sentence adds its own."""
    return s.rstrip(" .;,।")


def _join(items: list) -> str:
    return "; ".join(_end(x) for x in items)


def _has_indic(texts: list) -> bool:
    return any("\u0900" <= ch <= "\u0d7f" for t in texts for ch in t or "")


def facts(session) -> list[str]:
    """Numbered facts in the first person, only from the case file. Gaps become [brackets]."""
    c, out = session.case, []
    proj = f"the project \"{_q(c.project_name) or '[project name]'}\""
    where = f" at {c.city}" if c.city else ""
    flat = c.flat_details or "[flat number]"
    if c.agreement_date:
        out.append(f"I entered into an agreement for sale with you dated {_d(c.agreement_date)} for {flat} in {proj}{where}.")
    else:
        out.append(f"I booked {flat} in {proj}{where} and entered into an agreement for sale with you dated [date of agreement].")
    if c.rera_number:
        out.append(f"The project is registered with TG-RERA under registration number {c.rera_number}.")
    if c.total_price_rupees:
        out.append(f"The total price agreed for the flat is {inr(c.total_price_rupees)}.")
    if c.payments:
        pays = "; ".join(f"{inr(p['amount_rupees'])} on {_d(p['date'])}" for p in c.payments)
        out.append(f"I have made the following payments to you: {pays}.")
    paid = c.amount_paid_rupees or sum(p["amount_rupees"] for p in c.payments)
    if paid:
        out.append(f"In all, I have paid you {inr(paid)} so far.")
    else:
        out.append("In all, I have paid you [total amount paid] so far.")
    if "delay" in c.categories or not c.categories:
        out.append(f"Under the agreement, you were to hand over possession of the flat by {_d(c.promised_possession_date) or '[promised possession date]'}.")
        if c.possession_handed_over_date:
            out.append(f"You handed over possession of the flat to me on {_d(c.possession_handed_over_date)}.")
        else:
            out.append("As on date, you have not handed over possession of the flat to me.")
        if c.builder_excuses:
            out.append("The reasons you have given for the delay are: " + _join(c.builder_excuses) + ".")
    if "defects" in c.categories:
        handover = f"You handed over possession of the flat to me on {_d(c.possession_handed_over_date) or '[date of possession]'}."
        if handover not in out:
            out.append(handover)
        if c.defects:
            out.append("The flat has the following defects: " + _join(c.defects) + ".")
        if c.defect_reported_date:
            out.append(f"I brought these defects to your notice in writing on {_d(c.defect_reported_date)}.")
        if c.builder_response:
            out.append(f"Your response so far: {_end(c.builder_response)}.")
    return out


def _ctx(session) -> dict:
    c, calc, dc, party = session.case, session.calc(), session.defect_calc(), session.party
    plan = session.draft_plan()
    enclosures = _join(c.evidence) if c.evidence else "[agreement for sale, payment receipts, builder's letters/emails]"
    listed = facts(session)
    # the builder's 30 days count only from a dated report made after possession (see calculator.defect_check)
    reported = _d(c.defect_reported_date) if dc.fix_deadline else None
    return dict(
        defect_reported=reported, defect_fix_deadline=_d(dc.fix_deadline), defect_overdue=bool(dc.overdue),
        non_english=_has_indic(listed + c.defects + c.evidence),
        today=date.today().strftime("%d %B %Y"), as_of=calc.as_of.strftime("%d %B %Y"),
        buyer=party.get("name"), buyer_address=party.get("address"), buyer_contact=party.get("contact"),
        builder=c.builder_name, builder_address=party.get("builder_address"),
        project=_q(c.project_name), flat=c.flat_details, city=c.city, rera=c.rera_number,
        promised=_d(c.promised_possession_date), possession=_d(c.possession_handed_over_date),
        delay_days=calc.delay_days if c.promised_possession_date else "[number of]", demand=plan["demand"],
        defects=[_end(x) for x in c.defects],
        categories=[k for k in ("delay", "defects") if plan[k]],
        paid=inr(calc.amount_paid) if calc.amount_paid else "[amount paid]", undated=calc.undated,
        refund_interest=inr(calc.refund_interest_to_date) if calc.refund_interest_to_date else None,
        stay_interest=inr(calc.stay_interest_to_date) if calc.stay_interest_to_date else None,
        monthly=inr(calc.monthly_interest) if calc.monthly_interest else None,
        window_end=_d(dc.window_end), enclosures=enclosures, portal=TG["portal"], law=KB,
        facts=listed,
    )


class DraftNotReady(ValueError):
    pass


def legal_notice(session) -> str:
    """Delay notice: refund, possession with delay interest, or delay interest only after a late handover."""
    if not session.draft_plan()["notice"]:
        raise DraftNotReady("no delay to claim yet, or the buyer has not chosen refund or possession")
    return env.get_template("legal_notice.md.j2").render(**_ctx(session))


def rera_complaint(session) -> str:
    if not session.draft_plan()["complaint"]:
        raise DraftNotReady("nothing to complain about yet, or the buyer has not chosen refund or possession")
    return env.get_template("rera_complaint.md.j2").render(**_ctx(session))


def defect_notice(session) -> str:
    """s.14(3) notice: lists the defects and starts the builder's 30 days."""
    if not session.draft_plan()["defect_notice"]:
        raise DraftNotReady("no defect case, or the five-year period for defects has passed")
    return env.get_template("defect_notice.md.j2").render(**_ctx(session))
