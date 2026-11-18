# 23_question_before_facts — A general question first, facts afterwards
Commit `not a git checkout` · run 2026-11-18 15:16 · as_of 2026-11-15 · answered by: `gemini:gemini-3.5-flash-lite` · 6 model calls · 24372 input tokens (cached not reported) · 1328 output tokens · 72s


## 🧑 User
can I get my money back if the builder is late?

## 🤖 Griha Nyay
Yes, you can. Under the law, if the builder fails to hand over possession by the date promised in your agreement, you have the right to withdraw from the project and get your money back with interest and compensation [RERA-18-1]. 

Could you tell me a little about your situation—the builder and project name, the city, the promised date, and what you would like to do? Or, if you want to see how this works first, just type "sample case".

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)

## 🧑 User
They promised 31 March 2024 and I paid 40 lakh. The flat is in Kondapur.

## 🤖 Griha Nyay
**Your case in short**
Your possession is delayed by 959 days (~31.5 months) past the promised date of 31 March 2024.

**Where you stand**
The law supports your right to relief for this delay. Under [RERA-18-1] "interest for every month of delay, till the handing over of the possession", you can claim monthly interest if you stay in the project. Alternatively, [RERA-19-4] claim of refund of amount paid along with interest allows you to seek a refund if the builder fails to give possession as agreed. In Telangana, this interest is calculated as [TS-R15] "highest Marginal Cost of Lending Rate of State Bank of India plus two per cent".

**Your two choices**
(a) Withdraw from the project and get your money back with interest and compensation. Based on your payment of Rs 40,00,000, the total refund and interest so far are unknown because exact payment dates were not provided.
(b) Stay in the project and receive monthly interest until handover. Based on your amount paid, the monthly interest is Rs 36,500, and the interest accrued so far is Rs 11,50,800. Since you are unsure, ask yourself: do you still need this flat, and do you trust the builder to finish it?

**What to do next**
1. Collect proof: gather your payment receipts, bank statements, and the builder's allotment letter or agreement.
2. Check the project's registration on the TG-RERA portal [FAQ-3].
3. Send a dated written notice to the builder demanding your dues, and keep proof of delivery.
4. File a complaint using Form 'M' with the Authority or Form 'N' with the adjudicating officer [TS-R34-1] [TS-R35-1].

**What I'm not sure about**
I am calculating based on the assumption that your Rs 40,00,000 was paid before the promised date. I do not know your exact payment dates, the builder's name, or project registration details. The final interest rate, exact period, and compensation amount will be decided by the authority.

**When to get a real lawyer**
Consult a lawyer or free legal aid to review your agreement, draft your legal notice, and confirm the correct complaint forum.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[RERA-19-4]** Real Estate (Regulation and Development) Act, 2016, Section 19(4) - _Buyer's right to refund with interest and compensation_ (PDF p. 17; https://rera.telangana.gov.in)
- **[TS-R15]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 15 - _Interest rate in Telangana: highest SBI MCLR + 2%_ (PDF p. 13; https://rera.telangana.gov.in)
- **[FAQ-3]** TG-RERA Frequently Asked Questions (07.07.2023), FAQ 3 (guidance, not law) - _How to check if a project is registered_ (PDF p. 2; https://rera.telangana.gov.in)
- **[TS-R34-1]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 34(1) - _Complaint to TG-RERA (Form M)_ (PDF p. 22; https://rera.telangana.gov.in)
- **[TS-R35-1]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 35(1) - _Claim to the adjudicating officer (Form N)_ (PDF p. 23; https://rera.telangana.gov.in)

## 📄 Legal notice not generated
The buyer has not said whether they want a refund or the flat; the Drafts tab asks them to choose first.

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Kondapur",
 "builder_name": null,
 "project_name": null,
 "flat_details": null,
 "rera_number": null,
 "rera_registered": null,
 "permission_before_2017": null,
 "categories": [
  "delay"
 ],
 "agreement_date": null,
 "promised_possession_date": "2024-03-31",
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": 4000000,
 "payments": [],
 "goal": "unsure",
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
 "promised_possession_date": "2024-03-31",
 "delay": "959 days (~31.5 months)",
 "interest_rate": "10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, Rule 15))",
 "amount_paid": "Rs 40,00,000",
 "option_stay_monthly_interest": "Rs 36,500",
 "option_stay_interest_accrued_so_far": "Rs 11,50,800",
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
- Retrieval (id: why): [{'RERA-18-1': 'index', 'TS-R15': 'index', 'TS-R34-1': 'case', 'RERA-19-4': 'case', 'TS-R35-1': 'linked'}]
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 1, 'unsupported': 0, 'error': None}
  - [supported] You have the right to withdraw from the project and get your money back with interest and compensation if the builder fails to hand over possession on time. (RERA-18-1)
- Answer check: citations removed none; quotes not exact: 1; amounts unverified: 0; grounding: {'claims': 5, 'unsupported': 0, 'error': None}
  - [supported] You can claim monthly interest if you stay in the project if possession is delayed. (RERA-18-1)
  - [supported] You can seek a refund if the builder fails to give possession as agreed. (RERA-19-4)
  - [supported] In Telangana, interest is calculated as SBI's highest MCLR plus 2 percent. (TS-R15)
  - [supported] Check the project's registration on the TG-RERA portal. (FAQ-3)
  - [supported] File a complaint using Form 'M' with the Authority or Form 'N' with the adjudicating officer. (TS-R34-1)
- Other log: [{'type': 'no_problem_yet', 'count': 1}, {'type': 'chat_reply', 'ids': {'RERA-18-1': 'index', 'RERA-19-4': 'index', 'TS-R15': 'linked', 'TS-R34-1': 'linked', 'TS-R35-1': 'linked'}}, {'type': 'index_tags_added', 'ids': ['FAQ-3']}]
## ✅ Checks
- PASS no_false_escalation
- PASS reached_advice
- PASS reply0_has:Sources used
- PASS reply0_lacks:which state
- PASS reply0_lacks:outside what I cover
- PASS field_promised_possession_date
- PASS field_amount_paid_rupees
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer