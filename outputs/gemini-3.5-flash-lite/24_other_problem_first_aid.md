# 24_other_problem_first_aid — Unpaid salary: first aid, no law stated
Commit `not a git checkout` · run 2026-11-18 15:17 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 3 model calls · 8152 input tokens (cached not reported) · 336 output tokens · 17s


## 🧑 User
My employer ABC Tech in Hyderabad has not paid my salary for the last three months, about 90,000 rupees in total. I have my offer letter and bank statements. What can I do?

## 🤖 Griha Nyay
I'm sorry you're dealing with this. Your problem (unpaid salary or dues from an employer) is outside what I cover: I have checked the law only for builder delays and flat defects in Telangana, so I won't tell you what the law says here. What I can do is help you get ready for someone who can - put your story in order, list what to collect, and point you to free help.

**Your case so far**
- **Problem:** unpaid salary or dues from an employer
- **Who it is with:** ABC Tech
- **What happened:** Salary has not been paid for the last three months by the employer ABC Tech in Hyderabad, amounting to about 90,000 rupees.
- **Money involved:** Rs 90,000
- **What you want:** unpaid salary
- **Proof you have:** offer letter; bank statements
- **Timeline:**
  - last three months: salary not paid

**Collect these**
- Appointment or offer letter (or any message that shows your pay)
- Salary slips and bank statements showing what was paid and when it stopped
- Proof you worked in the unpaid months (attendance, emails, ID card)
- Any resignation, termination or warning letter
- Your written requests for the salary and the employer's replies

**Where to get help:**
- Free legal advice: District Legal Services Authority (DLSA) at your district court, or the NALSA legal aid helpline 15100. A free lawyer if you are eligible (Legal Services Authorities Act, s.12).

Have you raised this issue with your HR or manager in writing, such as through email?

_You can download this case note from the sidebar and take it with you._

## 🧑 User
They stopped paying from August 2026 and HR is not replying to my emails.

## 🤖 Griha Nyay
I've added that to your case note.

**Your case so far**
- **Problem:** unpaid salary or dues from an employer
- **Who it is with:** ABC Tech
- **What happened:** Salary has not been paid by ABC Tech since August 2026, amounting to about 90,000 rupees. HR is not replying to emails.
- **Money involved:** Rs 90,000
- **What you want:** unpaid salary
- **Proof you have:** offer letter; bank statements; emails to HR
- **Timeline:**
  - last three months: salary not paid
  - August 2026: salary stopped

Do you have any written communication from HR or management regarding the delayed salary before they stopped replying?

_You can download this case note from the sidebar and take it with you._

## 📝 Case note (first aid - a problem outside the verified law)
```json
{
 "category": "salary",
 "other_party": "ABC Tech",
 "summary": "Salary has not been paid by ABC Tech since August 2026, amounting to about 90,000 rupees. HR is not replying to emails.",
 "amount_rupees": 90000,
 "wants": "unpaid salary",
 "timeline": [
  {
   "date": "last three months",
   "event": "salary not paid"
  },
  {
   "date": "August 2026",
   "event": "salary stopped"
  }
 ],
 "evidence": [
  "offer letter",
  "bank statements",
  "emails to HR"
 ],
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
- Other log: [{'type': 'off_topic'}, {'type': 'first_aid', 'category': 'salary'}]
## ✅ Checks
- PASS reply0_has:outside what I cover
- PASS reply0_has:15100
- PASS reply0_has:Collect these
- PASS reply0_lacks:Payment of Wages
- PASS reply0_lacks:Industrial Disputes
- PASS reply0_lacks:Labour Court
- PASS reply0_lacks:[RERA
- PASS reply1_lacks:Payment of Wages
- PASS reply1_lacks:Industrial Disputes
- PASS reply1_lacks:Labour Court
- PASS reply1_lacks:[RERA
- PASS first_aid_mode
- PASS general_category
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer