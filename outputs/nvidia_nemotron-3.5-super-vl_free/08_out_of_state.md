# 08_out_of_state — Maharashtra project
Model: `nvidia/nemotron-3.5-super-vl:free` · as_of: 2026-11-15

## 🧑 User
My flat in Pune, Maharashtra (Kalpataru Gardens by ABC Developers) was supposed to be handed over in December 2023. I paid 70 lakh. Can you help me file a complaint?

## 🤖 Griha Nyay
**I need to be honest: this part needs a real lawyer.**

- I only cover Telangana projects right now. RERA (the central Act) applies across India, but interest rates, forms and procedure differ by state. Please check your state's RERA portal or get local legal advice.

**Free legal help:** District Legal Services Authority (DLSA) at your district court, or call the NALSA helpline **15100**.

**Take this case summary with you:**
- **Buyer:** —
- **Builder:** ABC Developers
- **Project:** Kalpataru Gardens
- **Flat:** —
- **City / State:** Pune, Maharashtra
- **RERA no.:** —
- **Agreement date:** —
- **Promised possession:** 2023-12-01
- **Total price:** —
- **Paid so far:** Rs 70,00,000
- **Delay:** 1080 days
- **Wants:** —
- **Builder's excuses:** —
- **Proof they have:** —
- **Timeline:**
  - 2023-12-01: Promised possession date

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Maharashtra",
 "city": "Pune",
 "buyer_name": null,
 "builder_name": "ABC Developers",
 "project_name": "Kalpataru Gardens",
 "flat_details": null,
 "rera_number": null,
 "rera_registered": null,
 "agreement_date": null,
 "promised_possession_date": "2023-12-01",
 "total_price_rupees": null,
 "amount_paid_rupees": 7000000,
 "payments": [],
 "evidence": [],
 "goal": null,
 "builder_excuses": [],
 "timeline": [
  {
   "date": "2023-12-01",
   "event": "Promised possession date"
  }
 ]
}
```
## 🧮 Calculator
```json
{
 "as_of": "2026-11-15",
 "promised_possession_date": "2023-12-01",
 "delay": "1080 days (~35.5 months)",
 "interest_rate": "10.70% per year (SBI Marginal Cost of Lending Rate (MCLR) + 2% per annum)",
 "amount_paid": "Rs 70,00,000",
 "option_stay_monthly_interest": "Rs 62,417",
 "option_stay_interest_accrued_so_far": "Rs 22,16,219",
 "option_refund_interest_so_far": "unknown",
 "option_refund_total_so_far": "unknown",
 "notes": [
  "Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation.",
  "Refund interest normally runs from the date of each payment; give payment dates for that estimate."
 ]
}
```
## 🛡️ Guardrail log
- Escalations: ['out_of_state']
- Cautions: none
- Citations/references removed by validator: none
- Other log: none
## ✅ Checks
- PASS escalated_correctly
- PASS no_llm_errors
- PASS no_duplicated_answer

_Time: 23.8s_