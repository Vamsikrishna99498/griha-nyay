# 21_promised_date_not_passed — Promised date is still in the future
Commit `not a git checkout` · run 2026-11-17 23:40 · as_of 2026-11-15 · answered by: `default:nvidia/nemotron-3.5-super-vl` · 4 model calls · 19904 input tokens (13152 from cache) · 6556 output tokens (5506 hidden reasoning) · 41s


## 🧑 User
Flat in Narsingi, Hyderabad, project Cedar Park by Lotus Infra, RERA registered. Possession is promised by 30 June 2027 and I have paid 30 lakh. Construction looks very slow and I am worried. I want the flat.

## 🤖 Griha Nyay
**Your case in short**
Lotus Infra is building Cedar Park in Narsingi. You have paid Rs 30,00,000 and possession is promised by 30 June 2027. My calculation shows 0 days (~0.0 months) of delay today.

**Where you stand**
The law helps only after the builder misses the promised date. [RERA-18-1] "by the date specified therein". Since that date has not passed, there is no delay to claim yet. Interest in Telangana is SBI's highest MCLR plus 2% a year [TS-R15].

**Your two choices**
(a) Withdraw: get your money back with interest and compensation. Refund interest and total are unknown; I need the date of each payment to work them out.
(b) Stay: get interest for every month of delay until handover. That is Rs 27,375 a month, and Rs 0 has accrued so far because the promised date has not passed.
Your goal is possession, so staying fits if you still want the flat. If unsure, ask yourself: do I still need this flat, and do I trust the builder to finish?

**What to do next**
1. Keep your agreement for sale, payment receipts, and any written updates from the builder ready.
2. Check Cedar Park's registration on the TG-RERA portal.
3. Come back if 30 June 2027 passes without possession; then we can look at your options.

**What I'm not sure about**
No assumptions were recorded. I do not have your agreement date, payment dates, total price, or RERA number. The final interest rate, period, and compensation are decided by TG-RERA or the adjudicating officer.

**When to get a real lawyer**
If the promised date passes without possession, or if you decide to withdraw, a lawyer can confirm the right forum and help you file.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[TS-R15]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 15 - _Interest rate in Telangana: highest SBI MCLR + 2%_ (PDF p. 13; https://rera.telangana.gov.in)

## 📄 Legal notice not generated
There is no delay to claim: the promised date has not passed, or possession was given by then.

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Narsingi",
 "builder_name": "Lotus Infra",
 "project_name": "Cedar Park",
 "flat_details": null,
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
- Retrieval (id: why): [{'RERA-18-1': 'index', 'TS-R15': 'index', 'TS-R34-1': 'case', 'FAQ-8': 'case', 'RERA-3-1': 'keyword', 'TS-R35-1': 'linked'}]
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 6, 'unsupported': 0, 'error': None}
  - [supported] The law helps only after the builder misses the promised date. (RERA-18-1)
  - [supported] Interest in Telangana is SBI's highest MCLR plus 2% a year. (TS-R15)
  - [supported] You can withdraw and get your money back with interest and compensation. (RERA-18-1)
  - [supported] You can stay and get interest for every month of delay until handover. (RERA-18-1)
  - [user_fact] Rs 27,375 a month of interest has accrued. (no tag)
  - [supported] The final interest rate, period, and compensation are decided by TG-RERA or the adjudicating officer. (TS-R34-1)
- Other log: [{'type': 'advice_cut_off'}]
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