# 08_out_of_state — Maharashtra project
Commit `not a git checkout` · run 2026-11-18 02:53 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 1 model calls · 5437 input tokens (cached not reported) · 139 output tokens · 9s


## 🧑 User
My flat in Pune, Maharashtra (Kalpataru Gardens by ABC Developers) was supposed to be handed over in December 2023. I paid 70 lakh. Can you help me file a complaint?

## 🤖 Griha Nyay
I only cover Telangana projects in detail. RERA (the central Act) applies across India, but interest rates, forms and procedure differ by state.

What the central RERA Act says about delay (this applies in every state):
> [RERA-18-1] "18. (1) If the promoter fails to complete or is unable to give possession of an apartment, plot or building,- (a) in accordance with the terms of the agreement for sale or, as the case may be, duly completed by the date specified therein; or (b) due to discontinuance of his business as a developer on account of suspension or revocation of the registration under this Act or for any other reason, he shall be liable on demand to the allottees, in case the allottee wishes to withdraw from the project, without prejudice to any other remedy available, to return the amount received by him in respect of that apartment, plot, building, as the case may be, with interest at such rate as may be prescribed in this behalf including compensation in the manner as provided under this Act: Provided that where an allottee does not intend to withdraw from the project, he shall be paid, by the promoter, interest for every month of delay, till the handing over of the possession, at such rate as may be prescribed."

_If the builder does not give possession by the date in the agreement, you can either withdraw and get your money back with interest (plus compensation), or stay in the project and get interest for every month of delay until handover._

Your state's RERA website: https://maharera.maharashtra.gov.in

**Where to get help:**
- Free legal advice: District Legal Services Authority (DLSA) at your district court, or the NALSA legal aid helpline 15100. A free lawyer if you are eligible (Legal Services Authorities Act, s.12).
- National Consumer Helpline 1915 (or 1800-11-4000) - free advice on consumer complaints, including against builders.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Maharashtra",
 "city": "Pune",
 "builder_name": "ABC Developers",
 "project_name": "Kalpataru Gardens",
 "flat_details": null,
 "rera_number": null,
 "rera_registered": null,
 "permission_before_2017": null,
 "categories": [
  "delay"
 ],
 "agreement_date": null,
 "promised_possession_date": "2023-12-31",
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": 7000000,
 "payments": [],
 "goal": "unsure",
 "defects": [],
 "defect_reported_date": null,
 "builder_response": null,
 "evidence": [],
 "builder_excuses": [],
 "timeline": [],
 "assumptions": [
  "Only the month was given for the promised possession date, so the delay is counted from the last day of that month (31 December 2023)."
 ]
}
```
## 🧮 Calculator
```json
{
 "as_of": "2026-11-15",
 "promised_possession_date": "2023-12-31",
 "delay": "1050 days (~34.5 months)",
 "interest_rate": "10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, Rule 15))",
 "amount_paid": "Rs 70,00,000",
 "option_stay_monthly_interest": "Rs 63,875",
 "option_stay_interest_accrued_so_far": "Rs 22,05,000",
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
- Escalations: ['out_of_state']
- Cautions: none
- Retrieval (id: why): none
- Other log: none
## ✅ Checks
- PASS escalated_correctly
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer