"""Document drafting. The LEGAL text is fixed in templates (written once, checked by a human);
the LLM only turns the user's story into numbered facts. Amounts come from the calculator."""
import json
import re
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from . import guardrails, llm
from .calculator import TG, inr

ROOT = Path(__file__).parent.parent
env = Environment(loader=FileSystemLoader(ROOT / "templates"), keep_trailing_newline=True)


def _facts(session) -> str:
    prompt = (ROOT / "prompts" / "notice_facts.txt").read_text().format(
        case_json=json.dumps(session.case.to_dict(), ensure_ascii=False)
    )
    text = llm.chat([{"role": "user", "content": prompt}], temperature=0.1)
    clean, removed = guardrails.validate_citations(text, [])  # facts may cite no law at all
    if removed:
        session.log.append({"type": "citations_removed_from_facts", "items": removed})
    return clean


def _ctx(session) -> dict:
    c, calc = session.case, session.calc()
    enclosures = "; ".join(c.evidence) if c.evidence else "[agreement for sale, payment receipts, builder's letters/emails]"
    return dict(
        today=date.today().strftime("%d %B %Y"),
        as_of=calc.as_of.strftime("%d %B %Y"),
        buyer=c.buyer_name, builder=c.builder_name, project=c.project_name, flat=c.flat_details,
        city=c.city, rera=c.rera_number,
        promised=c.promised_possession_date.strftime("%d %B %Y") if c.promised_possession_date else None,
        delay_days=calc.delay_days, goal=c.goal,
        paid=inr(c.amount_paid_rupees) if c.amount_paid_rupees else "[amount paid]",
        refund_interest=inr(calc.refund_interest_to_date) if calc.refund_interest_to_date else None,
        stay_interest=inr(calc.stay_interest_to_date) if calc.stay_interest_to_date else None,
        monthly=inr(calc.monthly_interest) if calc.monthly_interest else None,
        enclosures=enclosures, portal=TG["portal"],
        form_hint="Form M for the Authority; Form N for compensation before the Adjudicating Officer",
        **{f"n{i}": i for i in range(1, 10)},
    )


def legal_notice(session, facts: str | None = None) -> str:
    facts = facts or _facts(session)
    ctx = _ctx(session)
    # number legal paragraphs after the facts
    n_facts = sum(1 for line in facts.splitlines() if re.match(r"\s*\d+[.)]\s", line))
    for i in range(1, 7):
        ctx[f"n{i}"] = n_facts + i
    return env.get_template("legal_notice.md.j2").render(facts=facts, **ctx)


def rera_complaint(session, facts: str | None = None) -> str:
    facts = facts or _facts(session)
    return env.get_template("rera_complaint.md.j2").render(facts=facts, **_ctx(session))
