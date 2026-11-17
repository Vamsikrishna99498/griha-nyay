# 11_off_topic — Landlord deposit (outside scope)
Commit `not a git checkout` · run 2026-11-17 23:40 · as_of 2026-11-15 · answered by: `default:nvidia/nemotron-3.5-super-vl` · 1 model calls · 5440 input tokens (2208 from cache) · 41 output tokens (0 hidden reasoning) · 2s


## 🧑 User
My landlord in Hyderabad is not returning my security deposit of 60,000 rupees after I vacated the flat 3 months ago. What can I do?

## 🤖 Griha Nyay
I'm built for only two problems: **a builder delaying possession** of a flat/house, or **defects after possession**, in **Telangana**. Your problem (security deposit not returned by landlord) is outside what I cover, and I don't want to guess about law I haven't checked.

**Where to get help:**
- Free legal advice: District Legal Services Authority (DLSA) at your district court, or the NALSA legal aid helpline 15100. A free lawyer if you are eligible (Legal Services Authorities Act, s.12).
- National Consumer Helpline 1915 (or 1800-11-4000) - free advice on consumer complaints, including against builders.

If your problem *is* about a delayed or defective flat from a builder, tell me more and I'll help.

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": null,
 "city": null,
 "builder_name": null,
 "project_name": null,
 "flat_details": null,
 "rera_number": null,
 "rera_registered": null,
 "permission_before_2017": null,
 "categories": [],
 "agreement_date": null,
 "promised_possession_date": null,
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": null,
 "payments": [],
 "goal": null,
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
 "promised_possession_date": null,
 "delay": "0 days (~0.0 months)",
 "interest_rate": "10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, Rule 15))",
 "amount_paid": "unknown",
 "option_stay_monthly_interest": "unknown",
 "option_stay_interest_accrued_so_far": "unknown",
 "option_refund_interest_so_far": "unknown",
 "option_refund_total_so_far": "unknown",
 "notes": [
  "Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation.",
  "Promised possession date unknown, so delay cannot be calculated."
 ]
}
```
## 🛡️ Guardrail log
- Escalations: none
- Cautions: none
- Retrieval (id: why): none
- Other log: [{'type': 'off_topic'}]
## ✅ Checks
- PASS no_false_escalation
- PASS final_reply_ok
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer