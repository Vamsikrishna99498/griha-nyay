# 10_missing_info — Vague story, tests follow-up questions
Commit `not a git checkout` · run 2026-11-17 23:41 · as_of 2026-11-15 · answered by: `default:nvidia/nemotron-3.5-super-vl` · 7 model calls · 34906 input tokens (19200 from cache) · 8015 output tokens (5304 hidden reasoning) · 54s


## 🧑 User
my builder is cheating me, flat not given. please help

## 🤖 Griha Nyay
Which city is your flat in, and by when did the builder promise to give you possession? Also, how much have you paid the builder so far?

## 🧑 User
It is in Hyderabad, Kondapur. Builder is Meridian Homes.

## 🤖 Griha Nyay
Thanks, that helps. To work out your options I still need: the possession date promised in your agreement; how much you have paid the builder so far.

## 🧑 User
They promised it by July 2024 and I have paid around 50 lakh.

## 🤖 Griha Nyay
**Your case in short**
Meridian Homes promised possession of your flat by 31 July 2024. You have paid Rs 50,00,000. By my calculation, the delay is 837 days (~27.5 months).

**Where you stand**
The law supports your claim. [RERA-18-1] "with interest at such rate as may be prescribed in this behalf including compensation". [RERA-18-1] "he shall be paid, by the promoter, interest for every month of delay, till the handing over of the possession, at such rate as may be prescribed." [TS-R15] "highest Marginal Cost of Lending Rate of State Bank of India plus two per cent."

**Your two choices**
(a) Withdraw: get back Rs 50,00,000 with interest plus compensation. Refund interest so far is unknown; I need the date of each payment to work it out.
(b) Stay: get interest for every month of delay. Monthly interest is Rs 45,625. Interest accrued so far is Rs 12,55,500.

If you still need this flat and trust the builder to finish it, staying may fit. If not, withdrawing may fit. Ask yourself: do you still need this flat, and do you trust the builder?

**What to do next**
1. Collect proof: payment receipts, the agreement for sale, and messages about possession. You still lack the agreement date, total price, RERA number, and payment dates.
2. Check the project's registration on the TG-RERA portal.
3. Send a legal notice (I can draft it).
4. File a complaint. Refund and delay-interest complaints go to the Authority in Form 'M'; compensation claims go to the adjudicating officer in Form 'N'. Each costs Rs 1,000. A lawyer or the TG-RERA complaint page can confirm the route.

**What I'm not sure about**
- The delay count assumes possession was due on 31 July 2024, because only the month was given.
- I was not given the agreement date, total price, RERA number, project name, or payment dates.
- The final interest rate, period, and compensation are decided by the authority.

**When to get a real lawyer**
Before you send or file anything, show the draft notice and complaint to a lawyer or free legal aid (DLSA).

---
**Sources used** (official text, checked):
- **[RERA-18-1]** Real Estate (Regulation and Development) Act, 2016, Section 18(1) - _Delay in possession: refund with interest, or interest for every month of delay_ (PDF p. 16; https://rera.telangana.gov.in)
- **[TS-R15]** Telangana State Real Estate (Regulation and Development) Rules, 2017, Rule 15 - _Interest rate in Telangana: highest SBI MCLR + 2%_ (PDF p. 13; https://rera.telangana.gov.in)

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
- Answer check: citations removed none; quotes not exact: 0; amounts unverified: 0; grounding: {'claims': 8, 'unsupported': 0, 'error': None}
  - [supported] If the builder does not give possession by the date in the agreement, you can withdraw and get your money back with interest plus compensation, or stay and get interest for every month of delay until  (RERA-18-1)
  - [supported] In Telangana, interest owed by the builder is SBI's highest Marginal Cost of Lending Rate plus 2% a year. (TS-R15)
  - [supported] Refund and delay-interest complaints go to the Authority in Form 'M'; compensation claims go to the adjudicating officer in Form 'N'. Each costs Rs 1,000. (TS-R34-1)
  - [user_fact] Meridian Homes promised possession of your flat by 31 July 2024. You have paid Rs 50,00,000. By my calculation, the delay is 837 days (~27.5 months). (no tag)
  - [user_fact] Monthly interest is Rs 45,625. Interest accrued so far is Rs 12,55,500. (no tag)
  - [supported] The final interest rate, period, and compensation are decided by the authority. (TS-R15)
  - [supported] A buyer who pays for a service is a consumer, but not if it is for a commercial purpose. (CPA-2-7)
  - [supported] The commission depends on the value paid as consideration: up to Rs 50 lakh, District; above Rs 50 lakh up to Rs 2 crore, State; above Rs 2 crore, National. (CPJUR-3-5)
- Other log: [{'type': 'advice_cut_off'}]
## ✅ Checks
- PASS no_false_escalation
- PASS reached_advice
- PASS asked_followup
- PASS no_reasking_known_info
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer