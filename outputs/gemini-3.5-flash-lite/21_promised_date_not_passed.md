# 21_promised_date_not_passed — Promised date is still in the future
Commit `not a git checkout` · run 2026-11-18 03:09 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 3 model calls · 14072 input tokens (cached not reported) · 935 output tokens · 165s


## 🧑 User
Flat in Narsingi, Hyderabad, project Cedar Park by Lotus Infra, RERA registered. Possession is promised by 30 June 2027 and I have paid 30 lakh. Construction looks very slow and I am worried. I want the flat.

## 🤖 Griha Nyay
**Your case in short**
You have paid Rs 30,00,000 for a flat in Cedar Park by Lotus Infra in Hyderabad. The promised possession date is 30 June 2027, so there is no delay to claim today as that date has not passed yet.

**Where you stand**
The law requires the builder to give possession by the agreed date. If there is a delay, you have protections under the law [RERA-18-1] "interest for every month of delay". TG-RERA's FAQ says that delay interest should be paid automatically under your agreement [FAQ-8].

**Your two choices**
Because your promised date has not passed yet, neither choice applies right now. If a delay happens later, your choices under [RERA-18-1] are: (a) withdraw from the project and get your money back with interest and compensation, or (b) stay in the project and get monthly interest until handover. Your goal is to keep the flat, which fits choice (b) if a delay occurs in the future.

**What to do next**
1. Keep your agreement for sale, payment receipts, and any written updates from the builder safe.
2. Check the project registration status on the TG-RERA website [FAQ-3].
3. Wait and watch the construction progress. You can return if the promised date passes without possession.

**What I'm not sure about**
I am not sure about individual payment dates, the exact total price, or when your agreement was signed, as those details are missing. The authority decides the final interest rate, period, and compensation.

**When to get a real lawyer**
Consult a lawyer or reach out to the District Legal Services Authority (DLSA) under [LSA-12] if you need formal legal advice or if disputes arise later.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[FAQ-8]** TG-RERA Frequently Asked Questions (07.07.2023), FAQ 8(ii) (guidance, not law) - _Delay interest should be paid automatically_ (PDF p. 2; https://rera.telangana.gov.in)
- **[FAQ-3]** TG-RERA Frequently Asked Questions (07.07.2023), FAQ 3 (guidance, not law) - _How to check if a project is registered_ (PDF p. 2; https://rera.telangana.gov.in)
- **[LSA-12]** Legal Services Authorities Act, 1987, Section 12 - _Who gets free legal services_ (PDF p. 11, 12; https://www.jhalsa.org/pdfs/LSA_1987.pdf)

## 📄 Legal notice not generated
There is no delay to claim: the promised date has not passed, or possession was given by then.

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Hyderabad",
 "builder_name": "Lotus Infra",
 "project_name": "Cedar Park",
 "flat_details": "Flat in Narsingi",
 "rera_number": null,
 "rera_registered": true,
 "permission_before_2017": null,
 "categories": [
  "delay"
 ],
 "agreement_date": null,
 "promised_possession_date": "2027-06-30",
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": 3000000,
 "payments": [],
 "goal": "possession",
 "defects": [],
 "defect_reported_date": null,
 "builder_response": null,
 "evidence": [],
 "builder_excuses": [
  "Construction looks very slow"
 ],
 "timeline": [],
 "assumptions": []
}
```
## 🧮 Calculator
```json
{
 "as_of": "2026-11-15",
 "promised_possession_date": "2027-06-30",
 "delay": "0 days (~0.0 months)",
 "interest_rate": "10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, Rule 15))",
 "amount_paid": "Rs 30,00,000",
 "option_stay_monthly_interest": "Rs 27,375",
 "option_stay_interest_accrued_so_far": "Rs 0",
 "option_refund_interest_so_far": "unknown",
 "option_refund_total_so_far": "unknown",
 "notes": [
  "Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation.",
  "The promised date has not passed yet, so there is no delay to claim today.",
  "Delay interest assumes everything was paid before the promised date; give payment dates for a more exact figure.",
  "Refund interest runs from the date of each payment; give payment dates for that estimate."
 ]
}
```
## 🛡️ Guardrail log
- Escalations: none
- Cautions: none
- Retrieval (id: why): [{'RERA-18-1': 'index', 'RERA-19-4': 'index', 'TS-R15': 'case', 'TS-R34-1': 'case', 'FAQ-8': 'case', 'RERA-3-1': 'keyword'}]
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 5, 'unsupported': 0, 'error': None}
  - [supported] If there is a delay, you have protections under the law for interest for every month of delay. (RERA-18-1)
  - [supported] TG-RERA's FAQ says that delay interest should be paid automatically under your agreement. (FAQ-8)
  - [supported] Your choices under RERA are to withdraw and get money back or stay and get monthly interest. (RERA-18-1)
  - [supported] Check the project registration status on the TG-RERA website. (FAQ-3)
  - [supported] Reach out to the District Legal Services Authority (DLSA) under the Legal Services Authorities Act. (LSA-12)
- Other log: [{'type': 'index_tags_added', 'ids': ['FAQ-3', 'LSA-12']}]
## ✅ Checks
- PASS no_false_escalation
- PASS reached_advice
- PASS not_in_reply:I can draft
- PASS field_promised_possession_date
- PASS field_amount_paid_rupees
- PASS delay_notice_blocked
- PASS calc_delay_days
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer