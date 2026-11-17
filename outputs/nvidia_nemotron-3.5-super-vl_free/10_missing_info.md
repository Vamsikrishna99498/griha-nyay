# 10_missing_info — Vague story, tests follow-up questions
Commit `not a git checkout` · run 2026-11-18 01:58 · as_of 2026-11-15 · answered by: `default:nvidia/nemotron-3.5-super-vl:free` · 6 model calls · 31375 input tokens (17344 from cache) · 7299 output tokens (4937 hidden reasoning) · 72s


## 🧑 User
my builder is cheating me, flat not given. please help

## 🤖 Griha Nyay
Thanks, that helps. To work out your options I still need: the possession date promised in your agreement; how much you have paid the builder so far.

## 🧑 User
It is in Hyderabad, Kondapur. Builder is Meridian Homes.

## 🤖 Griha Nyay
What was the possession date promised in your agreement, and how much have you paid the builder so far?

## 🧑 User
They promised it by July 2024 and I have paid around 50 lakh.

## 🤖 Griha Nyay
**Your case in short**
Meridian Homes promised possession by 31 July 2024. You have paid Rs 50,00,000. As of 15 November 2026, the delay is 837 days (~27.5 months).

**Where you stand**
The law supports your claim because the builder missed the possession date in your agreement.
[RERA-18-1] "in accordance with the terms of the agreement for sale or, as the case may be, duly completed by the date specified therein"
The interest rate is set by [TS-R15] "highest Marginal Cost of Lending Rate of State Bank of India plus two per cent."

**Your two choices**
(a) Withdraw: get your money back with interest plus compensation. Refund interest so far is unknown; I need your payment dates to work it out.
(b) Stay: get interest for every month of delay. Monthly interest: Rs 45,625. Interest accrued so far: Rs 12,55,500.
You have not told me your goal. Ask yourself: do you still need this flat, and do you trust the builder to finish it?

**What to do next**
1. Collect proof: agreement for sale, payment receipts, and any messages to the builder. You still lack the project name, RERA number, agreement date and exact payment dates.
2. Check the project's registration on the TG-RERA portal.
3. Send a legal notice (I can draft it).
4. File a complaint: Form M to TG-RERA [TS-R34-1] or Form N to the adjudicating officer [TS-R35-1]. The practice note to these rules says refund and delay-interest complaints go to the Authority (Form M), while compensation goes to the adjudicating officer (Form N); a lawyer or the TG-RERA page can confirm the route for your case.

**What I'm not sure about**
- The delay count assumes possession was due on 31 July 2024 because only the month was given.
- I was not given the project name, RERA number, agreement date or exact payment dates.
- Whether the project is registered or excluded as an "ongoing project."
- The final interest period, rate and compensation are decided by the authority, not by me.

**When to get a real lawyer**
Speak to a lawyer before you send a notice or file a complaint, to confirm the correct forum and documents.

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
 "city": "Kondapur",
 "builder_name": "Meridian Homes",
 "project_name": null,
 "flat_details": null,
 "rera_number": null,
 "rera_registered": null,
 "permission_before_2017": null,
 "categories": [],
 "agreement_date": null,
 "promised_possession_date": "2024-07-31",
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": 5000000,
 "payments": [],
 "goal": null,
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
- Retrieval (id: why): [{'RERA-18-1': 'index', 'TS-R15': 'index', 'CPJUR-3-5': 'keyword', 'TS-R34-1': 'linked', 'TS-R35-1': 'linked', 'CPA-2-7': 'linked'}]
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 12, 'unsupported': 0, 'error': None}
  - [user_fact] Meridian Homes promised possession by 31 July 2024. (no tag)
  - [user_fact] You have paid Rs 50,00,000. (no tag)
  - [user_fact] As of 15 November 2026, the delay is 837 days (~27.5 months). (no tag)
  - [supported] The law supports your claim because the builder missed the possession date in your agreement. (RERA-18-1)
  - [supported] If the builder does not give possession by the date in the agreement, you can withdraw and get your money back with interest plus compensation, or stay and get interest for every month of delay until  (RERA-18-1)
  - [supported] The interest rate is highest Marginal Cost of Lending Rate of State Bank of India plus two per cent. (TS-R15)
  - [user_fact] Monthly interest: Rs 45,625. (no tag)
  - [user_fact] Interest accrued so far: Rs 12,55,500. (no tag)
  - [supported] A complaint to the Authority is made in Form 'M' with a fee of Rs 1,000. (TS-R34-1)
  - [supported] A claim to the adjudicating officer is made in Form 'N' with a fee of Rs 1,000. (TS-R35-1)
  - [supported] Refund and delay-interest complaints go to the Authority (Form M), while compensation goes to the adjudicating officer (Form N). (TS-R34-1)
  - [supported] The final interest period, rate and compensation are decided by the authority, not by me. (TS-R15)
- Other log: [{'type': 'state_assumed'}, {'type': 'advice_cut_off'}]
## ✅ Checks
- PASS no_false_escalation
- PASS reached_advice
- PASS asked_followup
- PASS no_reasking_known_info
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer