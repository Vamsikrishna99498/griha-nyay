# 01_clean_refund — Clean Hyderabad delay, wants refund
Commit `6bb8991` · run 2026-11-17 18:55 · as_of 2026-11-15 · answered by: `openrouter:nvidia/nemotron-3.5-super-vl:free` · 2 model calls · 36s


## 🧑 User
My name is Ravi Kumar. I booked a 2BHK (Flat 504, Tower B) in Skyline Heights, Kokapet, Hyderabad by Sunrise Constructions Pvt Ltd. Agreement for sale signed on 10 March 2021, possession promised by 31 December 2023. Total price 62 lakh, I have paid 48 lakh: 6 lakh on 10 March 2021, 20 lakh on 1 Sept 2021, 22 lakh on 15 June 2022. RERA number P02400003456. Still no flat, builder keeps saying 'next quarter'. I have the agreement, bank statements and their emails. I've lost trust, I just want my money back.

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
- Other log: [{'type': 'error', 'detail': 'ValueError: unbalanced JSON in model output'}]
## ✅ Checks
- PASS no_false_escalation
- FAIL reached_advice
- FAIL field_agreement_date
- FAIL field_promised_possession_date
- FAIL field_amount_paid_rupees
- FAIL field_total_price_rupees
- FAIL field_goal
- FAIL field_payments
- FAIL no_llm_errors
- PASS no_duplicated_answer