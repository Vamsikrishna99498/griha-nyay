# 21_promised_date_not_passed — Promised date is still in the future
Commit `not a git checkout` · run 2026-11-18 02:04 · as_of 2026-11-15 · answered by: `none (no model call)` · 0 model calls · tokens not reported · output tokens not reported · 13s


## 🧑 User
Flat in Narsingi, Hyderabad, project Cedar Park by Lotus Infra, RERA registered. Possession is promised by 30 June 2027 and I have paid 30 lakh. Construction looks very slow and I am worried. I want the flat.

## 🤖 Griha Nyay
Sorry, I had a technical problem reaching the AI service. Please try again in a moment.

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
- Other log: [{'type': 'error', 'detail': 'LLMError: all providers failed: default: RateLimitError 429 Error code: 429 - Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day: https://openrouter.ai/settings/'}]
## ✅ Checks
- PASS no_false_escalation
- FAIL reached_advice
- PASS not_in_reply:I can draft
- FAIL field_promised_possession_date
- FAIL field_amount_paid_rupees
- PASS delay_notice_blocked
- PASS calc_delay_days
- FAIL no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer