# 21_promised_date_not_passed — Promised date is still in the future
Commit `not a git checkout` · run 2026-11-18 15:40 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 3 model calls · 14147 input tokens (cached not reported) · 726 output tokens · 25s


## 🧑 User
Flat in Narsingi, Hyderabad, project Cedar Park by Lotus Infra, RERA registered. Possession is promised by 30 June 2027 and I have paid 30 lakh. Construction looks very slow and I am worried. I want the flat.

## 🤖 Griha Nyay
**Your case in short**
The delay is 0 days (~0.0 months) as the promised date is in the future.

**Where you stand**
Under [RERA-18-1] "interest for every month of delay, till the handing over of the possession", if a builder fails to give possession by the agreed date, an allottee who stays in the project is owed interest for every month of delay. However, your promised date has not arrived yet.

**Your two choices**
(a) Withdraw from the project and get your money back with interest (refund interest and total amounts are currently unknown because payment dates are missing). (b) Stay in the project and get interest for every month of delay until handover, calculated on Rs 30,00,000 at an estimated monthly interest of Rs 27,375. Since you want to keep the flat, staying fits your goal.

**What to do next**
1. Keep your agreement for sale, payment receipts, and any written updates from the builder safely ready.
2. Check the project's registration on the TG-RERA portal [FAQ-3].
3. You can come back if the promised date passes without possession.

**What I'm not sure about**
I do not know the exact payment dates, which are needed for precise refund calculations. The final interest rate, period, and compensation are decided by the authority.

**When to get a real lawyer**
Consult a lawyer or free legal aid if disputes arise or if the builder fails to deliver by the promised date.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[FAQ-3]** TG-RERA Frequently Asked Questions (07.07.2023), FAQ 3 (guidance, not law) - _How to check if a project is registered_ (PDF p. 2; https://rera.telangana.gov.in)

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
 "builder_excuses": [],
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
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 3, 'unsupported': 0, 'error': None}
  - [supported] An allottee who stays in the project is owed interest for every month of delay if the builder fails to give possession by the agreed date. (RERA-18-1)
  - [supported] Check the project's registration on the TG-RERA portal. (FAQ-3)
  - [user_fact] Amount paid is Rs 30,00,000. (no tag)
- Other log: [{'type': 'index_tags_added', 'ids': ['FAQ-3']}]
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