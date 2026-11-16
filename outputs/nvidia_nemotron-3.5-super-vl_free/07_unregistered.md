# 07_unregistered — Project not registered with RERA
Model: `nvidia/nemotron-3.5-super-vl:free` · as_of: 2026-11-15

## 🧑 User
I booked a villa in a gated project near Shamshabad by a small developer, Om Sai Builders. They said the project is not registered with RERA because approvals were pending. Possession was promised in January 2024, I paid 22 lakh in cash and cheque. Nothing built yet.

## 🤖 Griha Nyay
**I need to be honest: this part needs a real lawyer.**

- You said the project is not registered with RERA. RERA protection mainly applies to registered (or registrable) projects; an unregistered project may itself be a violation, but your remedy may be a consumer commission or civil court instead. This choice is tricky — please consult a lawyer or the DLSA.

**Free legal help:** District Legal Services Authority (DLSA) at your district court, or call the NALSA helpline **15100**.

**Take this case summary with you:**
- **Buyer:** —
- **Builder:** Om Sai Builders
- **Project:** —
- **Flat:** villa in a gated project near Shamshabad
- **City / State:** Shamshabad, Telangana
- **RERA no.:** —
- **Agreement date:** —
- **Promised possession:** 2024-01-01
- **Total price:** —
- **Paid so far:** Rs 22,00,000
- **Delay:** 1049 days
- **Wants:** —
- **Builder's excuses:** Project not registered with RERA because approvals were pending
- **Proof they have:** —
- **Timeline:**
  - 2024-01-01: Possession promised by builder

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Shamshabad",
 "buyer_name": null,
 "builder_name": "Om Sai Builders",
 "project_name": null,
 "flat_details": "villa in a gated project near Shamshabad",
 "rera_number": null,
 "rera_registered": false,
 "agreement_date": null,
 "promised_possession_date": "2024-01-01",
 "total_price_rupees": null,
 "amount_paid_rupees": 2200000,
 "payments": [],
 "evidence": [],
 "goal": null,
 "builder_excuses": [
  "Project not registered with RERA because approvals were pending"
 ],
 "timeline": [
  {
   "date": "2024-01-01",
   "event": "Possession promised by builder"
  }
 ]
}
```
## 🧮 Calculator
```json
{
 "as_of": "2026-11-15",
 "promised_possession_date": "2024-01-01",
 "delay": "1049 days (~34.5 months)",
 "interest_rate": "10.70% per year (SBI Marginal Cost of Lending Rate (MCLR) + 2% per annum)",
 "amount_paid": "Rs 22,00,000",
 "option_stay_monthly_interest": "Rs 19,617",
 "option_stay_interest_accrued_so_far": "Rs 6,76,533",
 "option_refund_interest_so_far": "unknown",
 "option_refund_total_so_far": "unknown",
 "notes": [
  "Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation.",
  "Refund interest normally runs from the date of each payment; give payment dates for that estimate."
 ]
}
```
## 🛡️ Guardrail log
- Escalations: ['unregistered']
- Cautions: none
- Citations/references removed by validator: none
- Other log: none
## ✅ Checks
- PASS escalated_correctly
- PASS no_llm_errors
- PASS no_duplicated_answer

_Time: 29.7s_