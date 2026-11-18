# 06_insolvency — Builder under insolvency
Commit `not a git checkout` · run 2026-11-18 15:02 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 1 model calls · 5649 input tokens (cached not reported) · 158 output tokens · 6s


## 🧑 User
My builder Horizon Infra in Kompally stopped work in 2023. Possession was promised in March 2023, I paid 28 lakh. Now I got an email that NCLT has admitted insolvency against them and an IRP is appointed. Can I file a RERA complaint?

## 🤖 Griha Nyay
**I need to be honest: this part needs a real lawyer.**

- Your builder appears to be in insolvency proceedings (NCLT/IBC). Once insolvency starts, a moratorium usually stops RERA and consumer cases against the company, and homebuyers have to file claims with the resolution professional instead. This is time-sensitive and technical - please see a lawyer or the DLSA soon.

**Where to get help:**
- Free legal advice: District Legal Services Authority (DLSA) at your district court, or the NALSA legal aid helpline 15100. A free lawyer if you are eligible (Legal Services Authorities Act, s.12).

**Take this case summary with you:**
- **Problem:** delay
- **Builder:** Horizon Infra
- **Project:** —
- **Flat:** —
- **City / State:** Kompally, Telangana
- **RERA no.:** —
- **Agreement date:** —
- **Promised possession:** 2023-03-31
- **Possession received:** —
- **Total price:** —
- **Paid so far:** Rs 28,00,000
- **Delay:** 1325 days
- **Defects:** —
- **Defects reported on:** —
- **Wants:** unsure
- **Builder's excuses / response:** —
- **Proof they have:** —
- **Assumptions I made:** Only the month was given for the promised possession date, so the delay is counted from the last day of that month (31 March 2023).
- **Flagged for a lawyer:** builder insolvency

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Kompally",
 "builder_name": "Horizon Infra",
 "project_name": null,
 "flat_details": null,
 "rera_number": null,
 "rera_registered": null,
 "permission_before_2017": null,
 "categories": [
  "delay"
 ],
 "agreement_date": null,
 "promised_possession_date": "2023-03-31",
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": 2800000,
 "payments": [],
 "goal": "unsure",
 "defects": [],
 "defect_reported_date": null,
 "builder_response": null,
 "evidence": [],
 "builder_excuses": [],
 "timeline": [],
 "assumptions": [
  "Only the month was given for the promised possession date, so the delay is counted from the last day of that month (31 March 2023)."
 ]
}
```
## 🧮 Calculator
```json
{
 "as_of": "2026-11-15",
 "promised_possession_date": "2023-03-31",
 "delay": "1325 days (~43.5 months)",
 "interest_rate": "10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, Rule 15))",
 "amount_paid": "Rs 28,00,000",
 "option_stay_monthly_interest": "Rs 25,550",
 "option_stay_interest_accrued_so_far": "Rs 11,13,000",
 "option_refund_interest_so_far": "unknown",
 "option_refund_total_so_far": "unknown",
 "notes": [
  "Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation.",
  "Delay interest assumes everything was paid before the promised date; give payment dates for a more exact figure.",
  "Refund interest runs from the date of each payment; give payment dates for that estimate."
 ]
}
```
## 🛡️ Guardrail log
- Escalations: ['insolvency']
- Cautions: none
- Retrieval (id: why): none
- Other log: none
## ✅ Checks
- PASS escalated_correctly
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer