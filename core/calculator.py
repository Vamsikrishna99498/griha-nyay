"""Delay and interest maths. Pure Python on purpose: LLMs are bad at arithmetic,
and these numbers go into legal notices. Simple interest, per annum, 365-day year."""
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

TG = json.loads((Path(__file__).parent.parent / "knowledge" / "telangana.json").read_text())


def inr(n: float | int | None) -> str:
    """Indian digit grouping: 4500000 -> Rs 45,00,000."""
    if n is None:
        return "unknown"
    n = int(round(n))
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        s = ",".join(groups) + "," + tail
    return ("-" if n < 0 else "") + "Rs " + s


def default_rate_pct() -> float:
    return TG["interest"]["base_rate_pct"] + TG["interest"]["markup_pct"]


@dataclass
class DelayCalc:
    as_of: date
    promised: date | None
    delay_days: int
    delay_months: float
    rate_pct: float
    amount_paid: int | None
    monthly_interest: float | None        # option (b): stay, per month of delay
    stay_interest_to_date: float | None   # option (b): accrued so far
    refund_interest_to_date: float | None  # option (a): interest from each payment date
    refund_total: float | None
    notes: list

    def figures(self) -> dict:
        return {
            "as_of": self.as_of.isoformat(),
            "promised_possession_date": self.promised.isoformat() if self.promised else None,
            "delay": f"{self.delay_days} days (~{self.delay_months:.1f} months)",
            "interest_rate": f"{self.rate_pct:.2f}% per year ({TG['interest']['rule']})",
            "amount_paid": inr(self.amount_paid),
            "option_stay_monthly_interest": inr(self.monthly_interest),
            "option_stay_interest_accrued_so_far": inr(self.stay_interest_to_date),
            "option_refund_interest_so_far": inr(self.refund_interest_to_date),
            "option_refund_total_so_far": inr(self.refund_total),
            "notes": self.notes,
        }

    def allowed_amount_strings(self) -> set:
        return {v for k, v in self.figures().items() if isinstance(v, str) and v.startswith("Rs ")}


def compute(promised: date | None, amount_paid: int | None, payments: list | None = None,
            as_of: date | None = None, rate_pct: float | None = None) -> DelayCalc:
    as_of = as_of or date.today()
    rate = rate_pct if rate_pct is not None else default_rate_pct()
    r = rate / 100
    notes = [
        "Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation.",
    ]
    delay_days = max(0, (as_of - promised).days) if promised else 0
    if promised and promised > as_of:
        notes.append("The promised date has not passed yet, so there is no delay to claim today.")

    monthly = stay = refund_int = refund_total = None
    if amount_paid:
        monthly = amount_paid * r / 12
        stay = amount_paid * r * delay_days / 365 if promised else None
        if payments:
            refund_int = sum(p["amount_rupees"] * r * max(0, (as_of - p["date"]).days) / 365 for p in payments)
            paid_sum = sum(p["amount_rupees"] for p in payments)
            if paid_sum != amount_paid:
                notes.append(f"Payment list adds up to {inr(paid_sum)} but you said you paid {inr(amount_paid)}; refund interest uses the dated payments only.")
            refund_total = paid_sum + refund_int
        else:
            notes.append("Refund interest normally runs from the date of each payment; give payment dates for that estimate.")
    if not promised:
        notes.append("Promised possession date unknown, so delay cannot be calculated.")
    return DelayCalc(as_of, promised, delay_days, delay_days / 30.44, rate, amount_paid,
                     monthly, stay, refund_int, refund_total, notes)
