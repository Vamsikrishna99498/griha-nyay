# Griha Nyay — AI legal help for homebuyers facing builder delays (Telangana)

A chat assistant for an ordinary homebuyer whose builder hasn't handed over the flat on time.
It turns a messy story (English / Hindi / Telugu / mixed) into a case file, explains the buyer's
options under RERA in plain words with **real calculated interest**, drafts a **legal notice** and a
**TG-RERA complaint**, and lets them **practise negotiating** with an AI playing the builder's rep.

**Covers:** delayed possession of RERA-registered projects in Telangana.
**Does not cover (says so and points to a lawyer / DLSA):** other states, builder insolvency (NCLT/IBC),
unregistered projects, criminal matters (forgery, double sale, threats), title disputes, cases already in court,
claims above Rs 2 crore, and anything that isn't a builder-delay problem (e.g. landlord deposits). It never cites court judgments.

## Run
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env          # add your free OpenRouter key
.venv/bin/streamlit run app.py
```
Tests:
- `python -m tests.test_offline` — maths, parsing, guardrails (no key needed)
- `python -m tests.test_engine_mocked` — conversation flows with a fake model (no key, no cost)
- `python run_tests.py` — all 12 written cases on the real model → `outputs/<model>/` (raw, unedited)

## Swap the model
Only env vars: `MODEL=<any OpenRouter id>`; or `BASE_URL` + `LLM_API_KEY` for any OpenAI-compatible endpoint.
Nothing else in the code names a model. `MODEL=x python run_tests.py` writes results to a separate folder for side-by-side comparison.

## How it avoids invented law
| Layer | What it does | Where |
|---|---|---|
| Closed knowledge base | ~20 provisions written as plain summaries, each with source + verification status | `knowledge/*.json` |
| Retrieval | Only the matching entries are given to the model, tagged like `[RERA-18-1]` | `core/retrieve.py` |
| Prompt rules | Cite only given tags; no judgments; no own maths; say "I don't know" | `prompts/advisor.txt` |
| **Validator (code)** | Removes any tag, section/rule number or case citation not in that turn's entries; flags rupee amounts the calculator didn't produce | `core/guardrails.py` |
| Fixed legal text | Legal paragraphs in notices/complaints are templates, not AI text; the LLM only writes the facts | `templates/` |
| Escalation rules (code) | Keyword + case-field rules send risky cases to a lawyer / DLSA | `knowledge/escalation.json` |

## What is AI vs code
- **LLM:** extracting facts from the story, follow-up questions, plain-language explanation, facts section of drafts, builder role-play, coaching.
- **Code:** conversation flow, delay/interest maths, escalation decisions, citation validation, legal text of drafts, Indian number formatting.

## Memory
Per browser tab, in memory only (no database; refresh = new case). Facts live in a structured case file that is
merged by code (nulls never erase known facts; later corrections win and are shown to the user as
"Updated your case file: X → Y"). Each model call is rebuilt from the case file + the last 8 messages.

## Known limits
- Knowledge entries are written from memory + secondary sources (marked `memory+secondary`); **not yet checked line-by-line against the bare act.** The Telangana interest rule wording/number is unconfirmed (orders apply SBI MCLR + 2%).
- Interest is a simple-interest estimate; the authority's order decides.
- Refreshing the page loses the case (no saved sessions).
- Off-topic detection relies on the model's `in_scope` judgement during intake.
- Escalation is keyword-based, so it can miss euphemisms or trigger on unrelated words.
- The section validator checks numbers, not which Act they belong to (e.g. "Section 18 of another Act" would pass).
- Cost guard: on OpenRouter only `:free` models run (`core/llm.py` blocks others unless `ALLOW_PAID=1`). Voice needs a free audio-capable `VOICE_MODEL`, so it is off by default; text in Indian languages works.
