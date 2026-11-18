# 02_unsure_refund_or_flat — Unsure whether to take refund or wait
Commit `not a git checkout` · run 2026-11-18 01:41 · as_of 2026-11-15 · answered by: `default:nvidia/nemotron-3.5-super-vl:free` · 6 model calls · 27773 input tokens (13008 from cache) · 7026 output tokens (3444 hidden reasoning) · 76s


## 🧑 User
Builder Greenvale Homes, project Greenvale Meadows in Tellapur. Possession was due June 2024. I paid 35 lakh so far. I don't know whether to ask for refund or wait, I really need a house for my family and rent is killing me. What should I do?

## 🤖 Griha Nyay
**Your case in short**
Greenvale Homes promised possession of your flat in Greenvale Meadows, Tellapur, by 30 June 2024. By my calculation, the delay is 868 days (~28.5 months).

**Where you stand**
The law supports you. [RERA-18-1] "fails to complete or is unable to give possession of an apartment" [RERA-19-4] "claim the refund of amount paid along with interest"

**Your two choices**
(a) Withdraw: get your Rs 35,00,000 back with interest plus compensation. Refund interest so far is unknown; I need your payment dates to work it out.
(b) Stay: get interest for every month of delay. Monthly interest: Rs 31,937. Interest accrued so far: Rs 9,11,400.

You are unsure. One question may help: do you still want this flat, and do you trust the builder to finish?

**What to do next**
1. Collect proof: payment receipts, the agreement for sale, and any messages from Greenvale Homes. You still lack the agreement date, total price, RERA number, and payment dates.
2. Check the project's registration on the TG-RERA portal.
3. Send a legal notice (I can draft it).
4. File a complaint: Form M to TG-RERA for refund and delay interest (fee Rs 1,000); Form N to the adjudicating officer for compensation (fee Rs 1,000).

**What I'm not sure about**
- The delay count assumes possession was due on the last day of June 2024, because only the month was given.
- I was not given the agreement date, total price, RERA number, or payment dates.
- The final interest rate, period, and compensation are decided by TG-RERA or the adjudicating officer.

**When to get a real lawyer**
Speak to a lawyer or the DLSA before you send a notice or file, to confirm the correct form and route.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[RERA-19-4]** Real Estate (Regulation and Development) Act, 2016, Section 19(4) - _Buyer's right to refund with interest and compensation_ (PDF p. 17; https://rera.telangana.gov.in)

## 🧑 User
It's registered under TG RERA I think. Agreement signed August 2021.

## 🤖 Griha Nyay
📝 **Updated your case file:** RERA registered: — → True; Agreement date: — → 2021-08-01

Thank you. Agreement signed August 2021, possession due 30 June 2024. Delay: 868 days (~28.5 months). Amount paid: Rs 35,00,000.

**Your two choices under RERA**
[RERA-18-1] "he shall be liable on demand to the allottees, in case the allottee wishes to withdraw from the project... to return the amount received by him... with interest... including compensation"
[RERA-18-1] "where an allottee does not intend to withdraw from the project, he shall be paid... interest for every month of delay"

(a) **Withdraw:** Get Rs 35,00,000 back with interest plus compensation. Refund interest so far is unknown; I need your payment dates to work it out.
(b) **Stay:** Get interest for every month of delay. Monthly interest: Rs 31,937. Interest accrued so far: Rs 9,11,400.

Interest rate: [TS-R15] highest SBI MCLR + 2% (10.95% per year as calculated).

**Next steps**
1. Verify TG-RERA registration on the portal. [RERA-3-1] bars builders from selling without registering. TG-RERA's FAQ says you can complain even if the agreement was signed before registration. (⚠ I couldn't confirm this against the law text)
2. Collect payment receipts, the agreement copy, and any builder messages.
3. Send a legal notice to Greenvale Homes.
4. File Form M with TG-RERA (fee Rs 1,000) for refund and delay interest. [TS-R34-1]
5. File Form N with the adjudicating officer (fee Rs 1,000) for compensation.

I do not know the final interest period or compensation amount; TG-RERA or the adjudicating officer decides that. Please speak to a lawyer or the DLSA before you file.

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[TS-R15]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 15 - _Interest rate in Telangana: highest SBI MCLR + 2%_ (PDF p. 13; https://rera.telangana.gov.in)
- **[RERA-3-1]** Real Estate (Regulation and Development) Act, 2016, Section 3(1) - _Projects must be registered with RERA_ (PDF p. 7; https://rera.telangana.gov.in)
- **[TS-R34-1]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 34(1) - _Complaint to TG-RERA (Form M)_ (PDF p. 22; https://rera.telangana.gov.in)

## 📄 Legal notice not generated
The buyer has not said whether they want a refund or the flat; the Drafts tab asks them to choose first.

## 🗂️ Case file (extracted)
```json
{
 "language": "English",
 "state": "Telangana",
 "city": "Tellapur",
 "builder_name": "Greenvale Homes",
 "project_name": "Greenvale Meadows",
 "flat_details": null,
 "rera_number": null,
 "rera_registered": true,
 "permission_before_2017": null,
 "categories": [
  "delay"
 ],
 "agreement_date": "2021-08-01",
 "promised_possession_date": "2024-06-30",
 "possession_handed_over_date": null,
 "total_price_rupees": null,
 "amount_paid_rupees": 3500000,
 "payments": [],
 "goal": "unsure",
 "defects": [],
 "defect_reported_date": null,
 "builder_response": null,
 "evidence": [],
 "builder_excuses": [],
 "timeline": [],
 "assumptions": [
  "Only the month was given for the promised possession date, so the delay is counted from the last day of that month (30 June 2024).",
  "Only the month and year were given for the agreement date, so the 1st of that month is assumed."
 ]
}
```
## 🧮 Calculator
```json
{
 "as_of": "2026-11-15",
 "promised_possession_date": "2024-06-30",
 "delay": "868 days (~28.5 months)",
 "interest_rate": "10.95% per year (highest SBI Marginal Cost of Lending Rate (MCLR) + 2% per year (TS RERA Rules 2017, Rule 15))",
 "amount_paid": "Rs 35,00,000",
 "option_stay_monthly_interest": "Rs 31,937",
 "option_stay_interest_accrued_so_far": "Rs 9,11,400",
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
- Retrieval (id: why): [{'RERA-18-1': 'index', 'RERA-19-4': 'index', 'TS-R15': 'index', 'TS-R34-1': 'case', 'TS-R35-1': 'linked'}, {'RERA-3-1': 'index', 'TS-R2-ONGOING': 'index', 'RERA-18-1': 'case', 'TS-R15': 'case', 'TS-R34-1': 'case', 'RERA-19-4': 'case'}]
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 10, 'unsupported': 0, 'error': None}
  - [user_fact] Greenvale Homes promised possession by 30 June 2024 (no tag)
  - [user_fact] The delay is 868 days (~28.5 months) (no tag)
  - [supported] Section 18(1) covers failure to complete or give possession of an apartment (RERA-18-1)
  - [supported] Section 19(4) entitles a buyer to claim refund of amount paid along with interest (RERA-19-4)
  - [user_fact] Withdraw: get Rs 35,00,000 back with interest plus compensation (no tag)
  - [supported] Stay: get interest for every month of delay (RERA-18-1)
  - [calculator] Monthly interest: Rs 31,937 (no tag)
  - [calculator] Interest accrued so far: Rs 9,11,400 (no tag)
  - [supported] File Form M to TG-RERA for refund and delay interest (fee Rs 1,000) (TS-R34-1)
  - [supported] File Form N to the adjudicating officer for compensation (fee Rs 1,000) (TS-R35-1)
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 14, 'unsupported': 1, 'error': None}
  - [supported] RERA bars builders from selling without registering (RERA-3-1)
  - [unsupported] TG-RERA's FAQ says you can complain even if the agreement was signed before registration (no tag)
  - [supported] File Form M with TG-RERA (fee Rs 1,000) for refund and delay interest (TS-R34-1)
  - [supported] File Form N with the adjudicating officer (fee Rs 1,000) for compensation (TS-R34-1)
  - [supported] Interest rate: highest SBI MCLR + 2% (10.95% per year as calculated) (TS-R15)
  - [user_fact] Monthly interest: Rs 31,937 (no tag)
  - [user_fact] Interest accrued so far: Rs 9,11,400 (no tag)
  - [user_fact] Delay: 868 days (~28.5 months) (no tag)
  - [user_fact] Amount paid: Rs 35,00,000 (no tag)
  - [user_fact] Possession due 30 June 2024 (no tag)
  - [user_fact] Agreement signed August 2021 (no tag)
  - [supported] Get Rs 35,00,000 back with interest plus compensation (RERA-18-1)
  - [supported] Get interest for every month of delay (RERA-18-1)
  - [not_law] TG-RERA or the adjudicating officer decides the final interest period or compensation amount (no tag)
- Other log: [{'type': 'case_updated', 'fields': ['rera_registered', 'agreement_date']}]
## ✅ Checks
- PASS no_false_escalation
- PASS reached_advice
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer