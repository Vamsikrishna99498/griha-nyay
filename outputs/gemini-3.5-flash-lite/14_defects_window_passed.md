# 14_defects_window_passed — Defects reported more than 5 years after possession
Commit `not a git checkout` · run 2026-11-18 15:08 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 1 model calls · 5656 input tokens (cached not reported) · 166 output tokens · 6s


## 🧑 User
I live in Miyapur, Hyderabad. Possession of my flat in Green Valley Apartments by Ramky Homes was handed over on 15 March 2019. Now in 2026 there are big cracks in the walls and seepage in two rooms. I have not complained to the builder yet. Can I make them repair it free?

## 🤖 Griha Nyay
**I need to be honest: this part needs a real lawyer.**

- Section 14(3) covers defects brought to the builder's notice within 5 years of getting possession. From the dates you gave, that window seems to have passed. Other remedies may still exist (for example a consumer commission), but this needs a lawyer or the DLSA to check.

**Where to get help:**
- Consumer commission: a homebuyer can complain about deficient service (Consumer Protection Act 2019). Ask the National Consumer Helpline 1915 how to file.
- Free legal advice: District Legal Services Authority (DLSA) at your district court, or the NALSA legal aid helpline 15100. A free lawyer if you are eligible (Legal Services Authorities Act, s.12).

**Take this case summary with you:**
- **Problem:** defects
- **Builder:** Ramky Homes
- **Project:** Green Valley Apartments
- **Flat:** flat in Green Valley Apartments
- **City / State:** Hyderabad, Telangana
- **RERA no.:** —
- **Agreement date:** —
- **Promised possession:** —
- **Possession received:** 2019-03-15
- **Total price:** —
- **Paid so far:** —
- **Delay:** —
- **Defects:** big cracks in the walls; seepage in two rooms
- **Defects reported on:** —
- **Wants:** repair
- **Builder's excuses / response:** —
- **Proof they have:** —
- **Assumptions I made:** —
- **Flagged for a lawyer:** 5-year defect window passed

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Hyderabad",
 "builder_name": "Ramky Homes",
 "project_name": "Green Valley Apartments",
 "flat_details": "flat in Green Valley Apartments",
 "rera_number": null,
 "rera_registered": null,
 "permission_before_2017": null,
 "categories": [
  "defects"
 ],
 "agreement_date": null,
 "promised_possession_date": null,
 "possession_handed_over_date": "2019-03-15",
 "total_price_rupees": null,
 "amount_paid_rupees": null,
 "payments": [],
 "goal": "repair",
 "defects": [
  "big cracks in the walls",
  "seepage in two rooms"
 ],
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
## 🔧 Defect window
```json
{
 "as_of": "2026-11-15",
 "possession_handed_over": "2019-03-15",
 "five_year_window_ends": "2024-03-15",
 "within_five_year_window": false,
 "defects_reported_to_builder_on": null,
 "builder_30_day_fix_deadline": null,
 "builder_past_30_days": null,
 "notes": [
  "Compensation for unfixed defects is decided by the adjudicating officer; I don't estimate it.",
  "You haven't told the builder in writing yet (or didn't give the date). Send a dated written notice first - the 30 days run from it."
 ]
}
```
## 🛡️ Guardrail log
- Escalations: ['defect_window_passed']
- Cautions: none
- Retrieval (id: why): none
- Other log: none
## ✅ Checks
- PASS escalated_correctly
- PASS category
- PASS defect_drafts_blocked
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer