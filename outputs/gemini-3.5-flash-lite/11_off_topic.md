# 11_off_topic — Landlord deposit (outside scope)
Commit `not a git checkout` · run 2026-11-18 15:07 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 2 model calls · 6853 input tokens (cached not reported) · 172 output tokens · 12s


## 🧑 User
My landlord in Hyderabad is not returning my security deposit of 60,000 rupees after I vacated the flat 3 months ago. What can I do?

## 🤖 Griha Nyay
I'm sorry you're dealing with this. Your problem (rent or deposit dispute with a landlord) is outside what I cover: I have checked the law only for builder delays and flat defects in Telangana, so I won't tell you what the law says here. What I can do is help you get ready for someone who can - put your story in order, list what to collect, and point you to free help.

**Your case so far**
- **Problem:** rent or deposit dispute with a landlord
- **Who it is with:** landlord
- **What happened:** Vacated the flat 3 months ago in Hyderabad. The landlord has not returned the security deposit of 60,000 rupees.
- **Money involved:** Rs 60,000
- **What you want:** security deposit back
- **Proof you have:** —
- **Timeline:**
  - 3 months ago: vacated the flat

**Collect these**
- Rent agreement (or any written terms, even WhatsApp)
- Proof you paid the deposit and the rent (receipts, bank or UPI records)
- Proof of the date you moved out and returned the keys
- Photos or videos of the house when you left
- Every message, call record or letter with the landlord about the money

**Where to get help:**
- Free legal advice: District Legal Services Authority (DLSA) at your district court, or the NALSA legal aid helpline 15100. A free lawyer if you are eligible (Legal Services Authorities Act, s.12).

Do you have a written rent agreement or any messages with the landlord about the deposit?

_You can download this case note from the sidebar and take it with you._

## 📝 Case note (first aid - a problem outside the verified law)
```json
{
 "category": "rent_deposit",
 "other_party": "landlord",
 "summary": "Vacated the flat 3 months ago in Hyderabad. The landlord has not returned the security deposit of 60,000 rupees.",
 "amount_rupees": 60000,
 "wants": "security deposit back",
 "timeline": [
  {
   "date": "3 months ago",
   "event": "vacated the flat"
  }
 ],
 "evidence": [],
 "urgent": false
}
```
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
- Other log: [{'type': 'off_topic'}, {'type': 'first_aid', 'category': 'rent_deposit'}]
## ✅ Checks
- PASS no_false_escalation
- PASS final_reply_ok
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer