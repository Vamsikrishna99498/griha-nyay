"""Tests for the code-only parts (no API key needed). Run: python -m tests.test_offline"""
from datetime import date

from core import guardrails, retrieve
from core.calculator import compute, inr
from core.case import CaseFile


def test_inr():
    assert inr(4500000) == "Rs 45,00,000"
    assert inr(12345678) == "Rs 1,23,45,678"
    assert inr(999) == "Rs 999"


def test_calculator():
    c = compute(date(2024, 1, 1), 4_000_000, as_of=date(2025, 1, 1), rate_pct=10.0)
    assert c.delay_days == 366
    assert round(c.monthly_interest) == 33333  # 40L * 10% / 12
    assert round(c.stay_interest_to_date) == round(4_000_000 * 0.10 * 366 / 365)
    pays = [{"date": date(2023, 1, 1), "amount_rupees": 1_000_000}, {"date": date(2024, 1, 1), "amount_rupees": 3_000_000}]
    c2 = compute(date(2024, 1, 1), 4_000_000, pays, as_of=date(2025, 1, 1), rate_pct=10.0)
    exp = 1_000_000 * 0.1 * 731 / 365 + 3_000_000 * 0.1 * 366 / 365
    assert abs(c2.refund_interest_to_date - exp) < 1
    future = compute(date(2030, 1, 1), 100, as_of=date(2025, 1, 1))
    assert future.delay_days == 0


def test_case_normalisation():
    c = CaseFile()
    c.update_from({"city": "Gachibowli, Hyderabad", "amount_paid_rupees": "45,00,000",
                   "promised_possession_date": "2023-12-01", "rera_number": "P02400001234"})
    assert c.state == "Telangana" and c.amount_paid_rupees == 4500000 and c.rera_registered is True
    c.update_from({"amount_paid_rupees": None, "state": None})  # nulls never erase facts
    assert c.amount_paid_rupees == 4500000 and c.state == "Telangana"


def test_iso_dates_not_flipped():
    c = CaseFile()
    c.update_from({"agreement_date": "2021-03-10", "promised_possession_date": "31/12/2023",
                   "payments": [{"date": "2021-09-01", "amount_rupees": 1}]})
    assert c.agreement_date == date(2021, 3, 10)  # was parsed as 3 Oct 2021 before the fix
    assert c.promised_possession_date == date(2023, 12, 31)
    assert c.payments[0]["date"] == date(2021, 9, 1)


def test_dedupe():
    from core.llm import _dedupe
    a = "Your case in short. Delay is 10 days."
    assert _dedupe(a + a) == a and _dedupe(a + "\n\n" + a) == a and _dedupe(a) == a


def test_escalation():
    c = CaseFile(state="Telangana")
    assert [i for i, _ in guardrails.check_escalation("the builder is now in NCLT insolvency", c)] == ["insolvency"]
    assert guardrails.check_escalation("I paid 14,20,000 first", c) == []  # no false '420' / 'fir'
    assert "out_of_state" in [i for i, _ in guardrails.check_escalation("", CaseFile(state="Maharashtra"))]
    assert "unregistered" in [i for i, _ in guardrails.check_escalation("", CaseFile(rera_registered=False))]


def test_citation_validator():
    entries = [retrieve.KB["RERA-18-1"], retrieve.KB["RERA-31"]]
    text = ("You can claim under Section 18 [RERA-18-1] and complain under s. 31 [RERA-31]. "
            "Also Section 73 of the Contract Act [ICA-73]. See Imperia Structures Ltd. v. Anil Patni, (2020) 10 SCC 783.")
    clean, removed = guardrails.validate_citations(text, entries)
    assert "Section 18" in clean and "s. 31" in clean and "[RERA-18-1]" in clean
    assert "Section 73" not in clean and "[ICA-73]" not in clean
    assert "Imperia" not in clean and "SCC" not in clean
    kinds = {k for k, _ in removed}
    assert kinds == {"unknown_tag", "unverified_section", "case_law"}
    assert "Rs." not in "".join(x for _, x in removed)


def test_retrieval():
    ids = [e["id"] for e in retrieve.retrieve("builder says force majeure covid, can I go to consumer court?")]
    assert "RERA-6" in ids and "CPA-JURIS" in ids and ids[0] == "RERA-18-1"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
