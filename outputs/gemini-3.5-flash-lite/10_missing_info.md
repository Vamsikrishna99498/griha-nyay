# 10_missing_info — Vague story, tests follow-up questions
Commit `not a git checkout` · run 2026-11-18 02:58 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 8 model calls · 32097 input tokens (cached not reported) · 1495 output tokens · 64s


## 🧑 User
my builder is cheating me, flat not given. please help

## 🤖 Griha Nyay
It is very stressful when a builder delays possession like this, but you do have legal options under the law [RERA-18-1]. 

To help me understand your situation better, could you tell me the possession date promised in your agreement and how much you have paid the builder so far?

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)

## 🧑 User
It is in Hyderabad, Kondapur. Builder is Meridian Homes.

## 🤖 Griha Nyay
Thank you for sharing that detail about your flat in Kondapur, Hyderabad. 

Could you tell me what possession date was promised in your agreement, and how much you have paid the builder so far?

## 🧑 User
They promised it by July 2024 and I have paid around 50 lakh.

## 🤖 Griha Nyay
**Your case in short**
You paid Meridian Homes Rs 50,00,000 for a flat. They promised possession by 31 July 2024, but it is now delayed by 837 days (~27.5 months).

**Where you stand**
The law supports buyers when a builder misses the delivery deadline. Under [RERA-18-1] "If the promoter fails to complete or is unable to give possession of an apartment", you have clear rights. In Telangana, the interest rate is fixed at the [TS-R15] "highest Marginal Cost of Lending Rate of State Bank of India plus two per cent".

**Your two choices**
(a) Withdraw from the project and get a refund of your amount with interest and compensation [RERA-18-1]. The exact refund interest and total so far are unknown because specific payment dates are missing.
(b) Stay in the project and get interest for every month of delay until handover [RERA-18-1]. By my calculation, your monthly interest is Rs 45,625, and the interest accrued so far is Rs 12,55,500 based on Rs 50,00,000 paid. 
Since you are unsure which path to take, ask yourself: do you still need this flat, or do you trust the builder to finish it?

**What to do next**
1. Collect your payment receipts and agreement.
2. Check if the project is registered on the TG-RERA portal.
3. Send a legal notice to the builder (I can help draft it).
4. File a complaint. Refund and delay-interest complaints are filed with the Authority using Form 'M' with a fee of Rs 1,000, and compensation claims go to the adjudicating officer using Form 'N' with a fee of Rs 1,000 [TS-R34-1] [TS-R35-1]. A lawyer or the TG-RERA portal can confirm the exact filing route for your case.

**What I'm not sure about**
I assumed that because only the month was given for the promised possession date, the delay is counted from the last day of that month (31 July 2024). I do not have your exact payment dates to calculate refund interest. The final interest rate, period, and compensation amounts are decided by the authority.

**When to get a real lawyer**
Consult a lawyer before filing notices or cases, or if you need help verifying your exact payment dates and documents.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[TS-R15]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 15 - _Interest rate in Telangana: highest SBI MCLR + 2%_ (PDF p. 13; https://rera.telangana.gov.in)
- **[TS-R34-1]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 34(1) - _Complaint to TG-RERA (Form M)_ (PDF p. 22; https://rera.telangana.gov.in)
- **[TS-R35-1]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 35(1) - _Claim to the adjudicating officer (Form N)_ (PDF p. 23; https://rera.telangana.gov.in)

## 📄 Legal notice not generated
The buyer has not said whether they want a refund or the flat; the Drafts tab asks them to choose first.

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Hyderabad",
 "builder_name": "Meridian Homes",
 "project_name": null,
 "flat_details": null,
 "rera_number": null,
 "rera_registered": null,
 "permission_before_2017": null,
 "categories": [
  "delay"
 ],
 "agreement_date": null,
 "promised_possession_date": "2024-07-31",
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": 5000000,
 "payments": [],
 "goal": "unsure",
 "defects": [],
 "defect_reported_date": null,
 "builder_response": null,
 "evidence": [],
 "builder_excuses": [],
 "timeline": [],
 "assumptions": [
  "Only the month was given for the promised possession date, so the delay is counted from the last day of that month (31 July 2024)."
 ]
}
```
## 🧮 Calculator
```json
{
 "as_of": "2026-11-15",
 "promised_possession_date": "2024-07-31",
 "delay": "837 days (~27.5 months)",
 "interest_rate": "10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, Rule 15))",
 "amount_paid": "Rs 50,00,000",
 "option_stay_monthly_interest": "Rs 45,625",
 "option_stay_interest_accrued_so_far": "Rs 12,55,500",
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
- Escalations: none
- Cautions: none
- Retrieval (id: why): [{'RERA-18-1': 'index', 'TS-R15': 'index', 'TS-R34-1': 'case', 'RERA-19-4': 'case', 'CPJUR-3-5': 'keyword', 'TS-R35-1': 'linked'}]
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 1, 'unsupported': 0, 'error': None}
  - [supported] You have legal options under the law when a builder delays possession. (RERA-18-1)
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 0, 'unsupported': 0, 'error': 'skipped'}
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 6, 'unsupported': 0, 'error': None}
  - [supported] If the promoter fails to give possession, you have rights under Section 18(1). (RERA-18-1)
  - [supported] In Telangana, the interest rate is SBI's highest MCLR plus 2 percent. (TS-R15)
  - [supported] Withdraw from the project and get a refund with interest and compensation. (RERA-18-1)
  - [supported] Stay in the project and get interest for every month of delay until handover. (RERA-18-1)
  - [supported] Refund and delay-interest complaints are filed with the Authority using Form 'M' with a fee of Rs 1,000. (TS-R34-1)
  - [supported] Compensation claims go to the adjudicating officer using Form 'N' with a fee of Rs 1,000. (TS-R35-1)
- Other log: [{'type': 'state_assumed'}, {'type': 'chat_reply', 'ids': {'RERA-18-1': 'index', 'RERA-19-4': 'index', 'TS-R15': 'case', 'TS-R34-1': 'case', 'TS-R35-1': 'linked'}}, {'type': 'chat_reply', 'ids': {'RERA-18-1': 'case', 'TS-R15': 'case', 'TS-R34-1': 'case', 'RERA-19-4': 'case', 'TS-R35-1': 'linked'}}]
## ✅ Checks
- PASS no_false_escalation
- PASS reached_advice
- PASS asked_followup
- PASS no_reasking_known_info
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer