# 21_promised_date_not_passed — Promised date is still in the future
Commit `not a git checkout` · run 2026-11-18 15:14 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 3 model calls · 14270 input tokens (cached not reported) · 995 output tokens · 33s


## 🧑 User
Flat in Narsingi, Hyderabad, project Cedar Park by Lotus Infra, RERA registered. Possession is promised by 30 June 2027 and I have paid 30 lakh. Construction looks very slow and I am worried. I want the flat.

## 🤖 Griha Nyay
**Your case in short**
By my calculation, your delay is 0 days (~0.0 months) as the promised date has not passed yet.

**Where you stand**
The law gives rights to buyers once the promised possession date arrives [RERA-18-1] "If the promoter fails to complete or is unable to give possession". You can also claim a refund with interest and compensation if the builder fails to give possession as agreed [RERA-19-4].

**Your two choices**
(a) Withdraw from the project and get your money back with interest (plus compensation), or (b) stay in the project and get interest for every month of delay until handover [RERA-18-1]. For staying in the project with an amount paid of Rs 30,00,000, the estimated monthly interest is Rs 27,375 at the rate of 10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, [TS-R15])). For a refund, the total interest and total amount so far are unknown because payment dates are missing. Since your goal is to get the flat, staying in the project fits your choice.

**What to do next**
1. Keep your agreement for sale, payment receipts, and any written updates from the builder ready.
2. Check the project's registration on the TG-RERA portal as explained in FAQ 3 [FAQ-3] Check the TG-RERA website for the project; its ads must show the TG-RERA registration number.
3. You can come back if the promised date passes without possession.

**What I'm not sure about**
My calculations assume simple interest only. The final rate, period, and compensation are decided by the TG-RERA order. I am also missing exact payment dates and a copy of your agreement for sale.

**When to get a real lawyer**
Consult a qualified lawyer or free legal aid if you need help reviewing your builder agreement or if the builder fails to give possession by the promised date.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[RERA-19-4]** Real Estate (Regulation and Development) Act, 2016, Section 19(4) - _Buyer's right to refund with interest and compensation_ (PDF p. 17; https://rera.telangana.gov.in)
- **[TS-R15]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 15 - _Interest rate in Telangana: highest SBI MCLR + 2%_ (PDF p. 13; https://rera.telangana.gov.in)
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
- Answer check: citations removed none; quotes not exact: 1; amounts unverified: 0; grounding: {'claims': 5, 'unsupported': 0, 'error': None}
  - [supported] The law gives rights to buyers once the promised possession date arrives. (RERA-18-1)
  - [supported] You can also claim a refund with interest and compensation if the builder fails to give possession as agreed. (RERA-19-4)
  - [supported] Withdraw from the project and get your money back with interest or stay in the project and get interest for every month of delay. (RERA-18-1)
  - [supported] Interest rate is highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year. (TS-R15)
  - [supported] Check the project's registration on the TG-RERA portal. (FAQ-3)
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