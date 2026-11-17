# 18_telugu_insolvency — Telugu story: builder in insolvency
Commit `not a git checkout` · run 2026-11-18 02:02 · as_of 2026-11-15 · answered by: `default:nvidia/nemotron-3.5-super-vl:free` · 1 model calls · 5508 input tokens (4336 from cache) · 191 output tokens (0 hidden reasoning) · 7s


## 🧑 User
నమస్తే. నేను హైదరాబాద్ నార్సింగిలో Vamsi Projects వారి ఫ్లాట్ బుక్ చేశాను, 45 లక్షలు కట్టాను. ఇప్పుడు ఆ కంపెనీ దివాలా తీసింది, NCLT లో కేసు నడుస్తోందని విన్నాను. నా డబ్బు ఎలా వస్తుంది?

## 🤖 Griha Nyay
**నిజాయితీగా చెప్పాలి: దీనికి నిజమైన న్యాయవాది అవసరం.**

- మీ బిల్డర్ దివాలా ప్రక్రియలో (NCLT/IBC) ఉన్నట్లు కనిపిస్తోంది. దివాలా మొదలైతే సాధారణంగా కంపెనీపై RERA, వినియోగదారుల కేసులు ఆగిపోతాయి; కొనుగోలుదారులు రిజల్యూషన్ ప్రొఫెషనల్ వద్ద క్లెయిమ్ వేయాలి. దీనికి గడువు ఉంటుంది, ఇది సాంకేతిక విషయం - దయచేసి త్వరగా న్యాయవాదిని లేదా DLSAను కలవండి.
- ఇప్పటికే కేసు లేదా విచారణ నడుస్తోంది. నడుస్తున్న కేసుపై నేను సురక్షితంగా సలహా ఇవ్వలేను - ఇప్పుడు మీరు చెప్పేది లేదా ఫైల్ చేసేది దానిపై ప్రభావం చూపవచ్చు. దయచేసి ఆ కేసు చూస్తున్న న్యాయవాదితో, లేకపోతే DLSAతో మాట్లాడండి.

**సహాయం ఎక్కడ దొరుకుతుంది:**
- ఉచిత న్యాయ సలహా: మీ జిల్లా కోర్టులోని జిల్లా న్యాయ సేవా అధికార సంస్థ (DLSA), లేదా NALSA హెల్ప్‌లైన్ 15100. అర్హత ఉంటే ఉచిత న్యాయవాది కూడా (లీగల్ సర్వీసెస్ అథారిటీస్ చట్టం, సెక్షన్ 12).

**ఈ కేసు సారాంశాన్ని మీతో తీసుకెళ్లండి:**
- **Problem:** delay
- **Builder:** Vamsi Projects
- **Project:** —
- **Flat:** —
- **City / State:** Hyderabad, Telangana
- **RERA no.:** —
- **Agreement date:** —
- **Promised possession:** —
- **Possession received:** —
- **Total price:** Rs 45,00,000
- **Paid so far:** Rs 45,00,000
- **Delay:** —
- **Defects:** —
- **Defects reported on:** —
- **Wants:** —
- **Builder's excuses / response:** —
- **Proof they have:** —
- **Assumptions I made:** —
- **Flagged for a lawyer:** builder insolvency, case already in court

## 🗂️ Case file (extracted)
```json
{
 "language": "Telugu",
 "state": "Telangana",
 "city": "Hyderabad",
 "builder_name": "Vamsi Projects",
 "project_name": null,
 "flat_details": null,
 "rera_number": null,
 "rera_registered": null,
 "permission_before_2017": null,
 "categories": [
  "delay"
 ],
 "agreement_date": null,
 "promised_possession_date": null,
 "possession_handed_over_date": null,
 "total_price_rupees": 4500000,
 "amount_paid_rupees": 4500000,
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
 "amount_paid": "Rs 45,00,000",
 "option_stay_monthly_interest": "Rs 41,062",
 "option_stay_interest_accrued_so_far": "unknown",
 "option_refund_interest_so_far": "unknown",
 "option_refund_total_so_far": "unknown",
 "notes": [
  "Simple interest estimate only. The TG-RERA order decides the final rate, period and compensation.",
  "Refund interest runs from the date of each payment; give payment dates for that estimate.",
  "Promised possession date unknown, so delay cannot be calculated."
 ]
}
```
## 🛡️ Guardrail log
- Escalations: ['insolvency', 'already_in_court']
- Cautions: none
- Retrieval (id: why): none
- Other log: none
## ✅ Checks
- PASS escalated_correctly
- PASS replied_in_telugu
- PASS final_reply_ok
- PASS no_llm_errors
- PASS no_cut_off_reply
- PASS no_internal_names
- PASS no_duplicated_answer