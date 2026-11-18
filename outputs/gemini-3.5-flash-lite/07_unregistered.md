# 07_unregistered — Project not registered with RERA
Commit `not a git checkout` · run 2026-11-18 15:02 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 1 model calls · 5647 input tokens (cached not reported) · 197 output tokens · 6s


## 🧑 User
I booked a villa in a gated project near Shamshabad by a small developer, Om Sai Builders. They said the project is not registered with RERA because approvals were pending. Possession was promised in January 2024, I paid 22 lakh in cash and cheque. Nothing built yet.

## 🤖 Griha Nyay
**I need to be honest: this part needs a real lawyer.**

- The project seems not to be registered with RERA (or its building permission came before 01.01.2017, which TS rules exclude from 'ongoing projects'). RERA may not cover it; your remedy may be a consumer commission or a civil court instead. This choice is tricky - please consult a lawyer or the DLSA.

**Where to get help:**
- Consumer commission: a homebuyer can complain about deficient service (Consumer Protection Act 2019). Ask the National Consumer Helpline 1915 how to file.
- Free legal advice: District Legal Services Authority (DLSA) at your district court, or the NALSA legal aid helpline 15100. A free lawyer if you are eligible (Legal Services Authorities Act, s.12).

**Take this case summary with you:**
- **Problem:** delay
- **Builder:** Om Sai Builders
- **Project:** —
- **Flat:** Villa
- **City / State:** Shamshabad, Telangana
- **RERA no.:** —
- **Agreement date:** —
- **Promised possession:** 2024-01-31
- **Possession received:** —
- **Total price:** —
- **Paid so far:** Rs 22,00,000
- **Delay:** 1019 days
- **Defects:** —
- **Defects reported on:** —
- **Wants:** possession
- **Builder's excuses / response:** —
- **Proof they have:** —
- **Assumptions I made:** Only the month was given for the promised possession date, so the delay is counted from the last day of that month (31 January 2024).
- **Flagged for a lawyer:** project not under RERA

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Shamshabad",
 "builder_name": "Om Sai Builders",
 "project_name": null,
 "flat_details": "Villa",
 "rera_number": null,
 "rera_registered": false,
 "permission_before_2017": null,
 "categories": [
  "delay"
 ],
 "agreement_date": null,
 "promised_possession_date": "2024-01-31",
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": 2200000,
 "payments": [
  {
   "date": "2024-01-01",
   "amount_rupees": 2200000
  }
 ],
 "goal": "possession",
 "defects": [],
 "defect_reported_date": null,
 "builder_response": null,
 "evidence": [],
 "builder_excuses": [],
 "timeline": [],
 "assumptions": [
  "Only the month was given for the promised possession date, so the delay is counted from the last day of that month (31 January 2024)."
 ]
}
```
## 🧮 Calculator
```json
{
 "as_of": "2026-11-15",
 "promised_possession_date": "2024-01-31",
 "delay": "1019 days (~33.5 months)",
 "interest_rate": "10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, Rule 15))",
 "amount_paid": "Rs 22,00,000",
 "option_stay_monthly_interest": "Rs 20,075",
 "option_stay_interest_accrued_so_far": "Rs 6,72,540",
 "option_refund_interest_so_far": "Rs 6,92,340",
 "option_refund_total_so_far": "Rs 28,92,340",
 "notes": [
  "Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation."
 ]
}
```
## 🛡️ Guardrail log
- Escalations: ['unregistered']
- Cautions: none
- Retrieval (id: why): none
- Other log: none
## ✅ Checks
- PASS escalated_correctly
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer