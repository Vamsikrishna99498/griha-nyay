"""Delay/interest maths and the defect-window check. Pure Python on purpose: LLMs are bad at
arithmetic, and these numbers go into legal notices. Simple interest, per annum, 365-day year."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from dateutil.relativedelta import relativedelta

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


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


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
    handed_over: date | None = None
    undated: int = 0                      # part of the amount paid that has no payment date
    other_amounts: set = field(default_factory=set)   # figures named in the notes (so they are not flagged)

    def figures(self) -> dict:
        if self.handed_over:
            return {
                "as_of": self.as_of.isoformat(),
                "promised_possession_date": self.promised.isoformat() if self.promised else None,
                "possession_handed_over_date": self.handed_over.isoformat(),
                "delay": f"{self.delay_days} days (~{self.delay_months:.1f} months), from the promised date to the handover date",
                "interest_rate": f"{self.rate_pct:.2f}% per year ({TG['interest']['rule']})",
                "amount_paid": inr(self.amount_paid),
                "delay_interest_per_month": inr(self.monthly_interest),
                "delay_interest_for_the_whole_delay": inr(self.stay_interest_to_date),
                "refund_figures": "not calculated - possession has already been handed over; a lawyer can confirm what applies",
                "notes": self.notes,
            }
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

    def amounts(self) -> set:
        return {int(round(x)) for x in [self.amount_paid, self.monthly_interest, self.stay_interest_to_date,
                                         self.refund_interest_to_date, self.refund_total, *self.other_amounts] if x}


def compute(promised: date | None, amount_paid: int | None, payments: list | None = None,
            as_of: date | None = None, rate_pct: float | None = None, handed_over: date | None = None) -> DelayCalc:
    """Delay runs from the promised date to the handover date if possession was given, else to as_of."""
    as_of = as_of or date.today()
    if not promised:
        handed_over = None
    end = min(as_of, handed_over) if handed_over else as_of
    rate = rate_pct if rate_pct is not None else default_rate_pct()
    r = rate / 100
    notes = ["Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation."]
    delay_days = max(0, (end - promised).days) if promised else 0
    if promised and promised > as_of:
        notes.append("The promised date has not passed yet, so there is no delay to claim today.")
    if handed_over:
        notes.append(f"Possession was handed over on {handed_over.isoformat()}, so the delay is counted only up to that date.")

    monthly = stay = refund_int = refund_total = None
    payments = payments or []
    paid_sum = sum(p["amount_rupees"] for p in payments)
    other = set()
    if not amount_paid and paid_sum:
        amount_paid = paid_sum
        notes.append(f"No total was given, so the amount paid is taken as the sum of the dated payments ({inr(paid_sum)}).")
    undated = 0
    if amount_paid:
        # one basis for every figure, so the monthly, accrued and refund numbers agree with each other
        basis = amount_paid
        if payments and paid_sum > amount_paid:
            basis = paid_sum
            other.add(paid_sum)
            notes.append(f"The dated payments add up to {inr(paid_sum)}, which is more than the {inr(amount_paid)} you said you paid; "
                         "the figures use the dated payments. Please check which is right.")
        elif payments and paid_sum < amount_paid:
            undated = amount_paid - paid_sum
            other |= {paid_sum, undated}
        monthly = basis * r / 12
        if promised and payments:
            # each payment earns delay interest only from the later of (promised date, payment date);
            # money with no payment date is treated like the no-dates case: paid before the promised date
            stay = (sum(p["amount_rupees"] * r * max(0, (end - max(promised, p["date"])).days) / 365 for p in payments)
                    + undated * r * delay_days / 365)
            if undated:
                notes.append(f"{inr(undated)} of what you paid has no payment date; delay interest assumes it was paid before the "
                             "promised date. Give its payment dates for a more exact figure.")
        elif promised:
            stay = amount_paid * r * delay_days / 365
            notes.append("Delay interest assumes everything was paid before the promised date; give payment dates for a more exact figure.")
        if handed_over:
            notes.append("Refund figures are not calculated because possession has already been handed over; a lawyer can confirm what applies.")
        elif payments:
            refund_int = sum(p["amount_rupees"] * r * max(0, (as_of - p["date"]).days) / 365 for p in payments)
            refund_total = basis + refund_int
            if undated:
                notes.append(f"Refund interest is worked out only on the dated payments ({inr(paid_sum)}). Interest on the other "
                             f"{inr(undated)} is not included because its payment date is unknown, so the real figure is higher.")
        else:
            notes.append("Refund interest runs from the date of each payment; give payment dates for that estimate.")
    if not promised:
        notes.append("Promised possession date unknown, so delay cannot be calculated.")
    return DelayCalc(as_of, promised, delay_days, delay_days / 30.44, rate, amount_paid,
                     monthly, stay, refund_int, refund_total, notes, handed_over, undated, other)


@dataclass
class DefectCheck:
    as_of: date
    possession: date | None
    reported: date | None
    window_end: date | None
    within_window: bool | None
    fix_deadline: date | None
    overdue: bool | None
    notes: list

    def figures(self) -> dict:
        return {
            "as_of": self.as_of.isoformat(),
            "possession_handed_over": _iso(self.possession),
            "five_year_window_ends": _iso(self.window_end),
            "within_five_year_window": self.within_window,
            "defects_reported_to_builder_on": _iso(self.reported),
            "builder_30_day_fix_deadline": _iso(self.fix_deadline),
            "builder_past_30_days": self.overdue,
            "notes": self.notes,
        }


def defect_check(possession: date | None, reported: date | None = None, as_of: date | None = None) -> DefectCheck:
    """s.14(3): defects brought to the builder's notice within 5 years of handing over possession
    must be fixed free within 30 days. Compensation is decided by the adjudicating officer - no
    rupee figure is computed here on purpose."""
    as_of = as_of or date.today()
    notes = ["Compensation for unfixed defects is decided by the adjudicating officer; I don't estimate it."]
    if not possession:
        notes.append("Possession date unknown, so the 5-year window can't be checked.")
        return DefectCheck(as_of, None, reported, None, None, reported + timedelta(days=30) if reported else None,
                           (as_of > reported + timedelta(days=30)) if reported else None, notes)
    window_end = possession + relativedelta(years=5)
    if reported and reported < possession:
        # s.14(3) is about defects raised after handing over; a complaint dated earlier can't start the 30 days
        notes.append("The date you told the builder about the defects is before the possession date, so the 30 days are not "
                     "counted from it. Tell the builder again in writing, with a date.")
        return DefectCheck(as_of, possession, reported, window_end, as_of <= window_end, None, None, notes)
    within = (reported or as_of) <= window_end
    fix_deadline = reported + timedelta(days=30) if reported else None
    overdue = (as_of > fix_deadline) if fix_deadline else None
    if not reported:
        notes.append("You haven't told the builder in writing yet (or didn't give the date). Send a dated written notice first - the 30 days run from it.")
    elif not within:
        notes.append("The defects were reported after the 5-year window ended.")
    return DefectCheck(as_of, possession, reported, window_end, within, fix_deadline, overdue, notes)
