# Griha Nyay - AI legal help for Telangana homebuyers (builder delays & defects)

A chat assistant for an ordinary homebuyer in Hyderabad/Telangana whose builder **delayed possession** or left
**defects** in the flat. It turns a messy story (English / Hindi / Telugu / Hinglish / Tenglish) into a case file,
explains the options in plain words using **only exact official law text**, does all money and date maths in code,
drafts a **legal notice**, a **defect notice** and **TG-RERA complaint content** (no AI writes these), and lets the
user **practise negotiating** with an AI playing the builder's rep.

**Solution doc (2 pages, with architecture and inference diagrams):** [`solution.pdf`](solution.pdf) (source: `docs/solution.html`)

**Covers:** (1) delayed possession and (2) defects after possession (RERA s.14(3)), for RERA-registered projects in Telangana.
**Other everyday problems (a landlord keeping a deposit, unpaid salary, a refund that never came, a notice received):**
it states **no law** for these, because none was checked. Instead it gives *first aid*: it turns the story into a case note,
lists the papers to collect, points to the right free help, and offers the note as a download to take there.
**Does not cover - says so honestly and points to specific free help:** other states (central-law explanation + that state's RERA portal), builder insolvency,
cases already in court, criminal matters (police 112), land-title disputes, unregistered / pre-2017 projects, claims above
Rs 2 crore, and defects reported after the 5-year window. It never cites court judgments and never estimates compensation.

## Run
Needs Python 3.9 or newer. With [uv](https://docs.astral.sh/uv/) (installs the exact versions pinned in `uv.lock`):
```bash
cp .env.example .env             # add your free key(s) - see "Models" below
uv run streamlit run app.py      # opens on localhost only
```
Or with plain pip:
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env
.venv/bin/streamlit run app.py
```
With uv, put `uv run` in front of the commands below (e.g. `uv run python -m tests.test_offline`). Lint: `uv run ruff check`
(rules in `pyproject.toml`). Dependencies are listed in `pyproject.toml`; `requirements.txt` is the same list for pip users.

Tests (no key needed unless stated):
- `python -m tests.test_offline` - maths, defect window, parsing, guardrails, privacy, schema, language, retrieval
- `python -m tests.test_law_quotes` - every law quote is verbatim on its official PDF page; PDF hashes; templates
- `python -m tests.eval_retrieval` - retrieval on 32 labelled questions in 5 language styles
- Latest raw outputs: `outputs/gemini-3.5-flash-lite/` - all 25 cases on the current code (Gemini free tier): 229/229 checks passed.
  Cases 22-25 cover a greeting before the story, a general question before the facts, first aid for unpaid salary, and first
  aid followed by a builder case.
  Earlier runs, kept for comparison: `outputs/nvidia_nemotron-3.5-super-vl_free/` (free OpenRouter endpoint; 20 of 21 cases
  passed, case 21 was stopped by the provider's daily free-request limit, and it predates the conversational replies in
  `prompts/chat.txt`) and `outputs/nvidia_nemotron-3.5-super-vl/` (the same model's paid endpoint, earlier prompts).
- Two longer conversations from manual testing (cases 26-27: chat and "I'm testing" then the sample case; a defects
  conversation with a relative date and follow-ups) were run afterwards on the same code: `outputs/conversation_tests/` (39/39).
- `python run_tests.py` - all 27 written cases on the real model -> `outputs/<model>/` (raw, unedited, stamped) **(uses your key)**
- `python run_tests.py --text "a new story" --text "a follow-up"` - run any new input and save the raw output **(uses your key)**

## Use your own model and your own test cases (quick start)
1. Install: `pip install -r requirements.txt`
2. Set the model: copy `.env.example` to `.env` and fill three lines (any OpenAI-compatible API):
   ```
   BASE_URL=https://your-api/v1
   LLM_API_KEY=your-key
   MODEL=your-model-name
   ```
3. Open the app: `streamlit run app.py`. If the key or the model name is wrong, the app and `run_tests.py` say which one
   (missing key, key rejected, model not found) instead of a general error.
4. Try a new input: `python run_tests.py --text "your story"` (add more `--text` for follow-up messages).
5. Add a test case: save a file in `tests/cases/`, e.g. `22_my_case.json`:
   ```json
   {"id": "22_my_case", "title": "My case",
    "turns": ["first message", "follow-up"],
    "expect": {"reaches_advice": true}}
   ```
   (put your own messages in `turns`), then run `python run_tests.py 22`. Other checks you can put in `expect`: `escalate` (e.g. `"insolvency"`),
   `final_reply_contains`, `final_reply_must_not_contain`, `fields` (expected case-file values), `language_hint`,
   `reply_contains` / `reply_must_not_contain` (by turn number, e.g. `{"0": "text"}`), `first_aid`, `general_category`.
6. See results in `outputs/<model>/` - one file per case and `summary.md`.

## Models (swap with env vars only)
Single provider: `MODEL`, `LLM_API_KEY` (or `OPENROUTER_API_KEY`), `BASE_URL` (any OpenAI-compatible endpoint).
Fallback chain across free providers: `LLM_PROVIDERS=openrouter,gemini,groq` plus `<NAME>_BASE_URL`, `<NAME>_API_KEY`,
`<NAME>_MODEL` for each. On a rate limit / outage the next provider answers; the sidebar and every test output show which
one did. Nothing else in the code names a model. On OpenRouter only `:free` models run unless `ALLOW_PAID=1`.

## Prompt caching
Providers can reuse the start of a request when it is identical to a recent one, which makes repeated input cheaper and
faster. The prompts are ordered for that: the text that never changes (the instructions and the law index, roughly 4,900
estimated tokens for intake and 3,500 for advice) comes first, and the case details come last. The intake prefix is the
same for every user; the advice prefix is shared only by users writing in the same language, because the advice
instructions name the reply language.
- OpenAI and Gemini 2.5+ models cache such a prefix automatically (per OpenRouter's prompt-caching guide); nothing to switch on.
- Anthropic models need an explicit breakpoint. `PROMPT_CACHE_MARKERS=1` adds one after the law index for `anthropic/...`
  models on OpenRouter. It is **off by default** because that request shape has only been unit-tested, not run on a live model.
- Every test output and the app sidebar show how many input tokens came from the cache, when the provider reports it.
- Measured: an earlier run on a paid OpenRouter endpoint served 53% of input tokens from its cache, and a free-endpoint
  run 15%; Gemini's free tier reported about 1% in the latest run. Caching is not always a saving - some providers charge extra to write the
  cache, so it pays off only when requests repeat within the cache lifetime.

## How it avoids invented law
| Layer | What it does | Where |
|---|---|---|
| Official corpus | 6 official PDFs (RERA Act, TS RERA Rules, TG-RERA FAQ, Consumer Protection Act 2019 + 2021 Jurisdiction Rules, Legal Services Authorities Act), page text + sha256 committed | `data/laws/`, `knowledge/sources.json` |
| Verified entries | 32 entries whose quotes are **cut from the page text by code** (`tools/build_law.py`), each with PDF page; a test re-checks every quote | `knowledge/law.json`, `tests/test_law_quotes.py` |
| Structured retrieval (no vectors) | exact lookup ("section 14"), the model picks from a compact **law index** during intake, case-state rules, multilingual keywords, linked entries; max 6 (8 when a case has both delay and defects); nothing relevant -> says so | `core/retrieve.py`, `knowledge/retrieval_map.json` |
| Prompt rules | cite only by tag, copy law wording exactly in quotes, no section numbers, no judgments, no own maths | `prompts/advisor.txt` |
| Citation validator (code) | unknown tags removed; a bare "Section 18" becomes a tag only if it matches a retrieved entry of the same Act and sub-section ("Section 19(7)" is not the verified 19(4)); other Acts, Articles, IPC/BNS and case citations removed | `core/guardrails.py` |
| Quote check (code) | text in quotes next to a tag must appear verbatim in that entry; otherwise its quotation marks are removed, so it reads as a paraphrase, not as the law's words (logged) | `core/guardrails.py` |
| Amount check (code) | rupee figures (incl. lakh/crore, Hindi/Telugu) not produced by the calculator are marked "⚠ unverified" | `core/guardrails.py` |
| Grounding check (1 extra model call) | lists each legal claim and judges it against the exact text; unsupported claims are flagged, never deleted (switch off: `GROUNDING_CHECK=0`) | `core/grounding.py` |
| Fixed legal text in drafts | notices/complaints are built by code from the case file; legal paragraphs quote the verified entries. They download as Word files with the same words (only formatting changes) and every [bracket] to fill highlighted | `core/drafts.py`, `templates/`, `core/docx_export.py` |
| Escalation (code + flags) | keyword stems in en/hi/te + structured case rules; intake flags can only escalate, never unlock. A denial ("no case pending") or a question about a possibility ("what if the builder goes bankrupt?") does not escalate. Escalations worked out from case facts (state, amount, registration, defect window) are lifted if the fact is corrected; what the person said in words stays | `knowledge/escalation.json` |
| First aid outside the verified law | for any other everyday problem the bot states no law at all: code writes the reply (scope line, case note, papers to collect, contacts) and drops any sentence in the model's note that names a section, an Act or a court ruling | `core/general.py`, `knowledge/first_aid.json` |

## What is AI vs code
- **Model:** reading the story into structured fields (+ picking relevant law from the index), the case note for a problem
  outside the verified law (`prompts/general_intake.txt`), the plain-language explanation,
  short conversational replies (answering a greeting, a worry or a general question, and asking for missing facts -
  `prompts/chat.txt`, with a code-written fallback), builder role-play, coaching, and the grounding check.
- **Code:** conversation flow, language detection, all maths (delay, interest per payment, the 5-year defect window),
  escalation, retrieval, citation/quote/amount checks, privacy scrubbing, every draft document, all helpline numbers, and
  the whole first-aid reply (scope line, case note layout, papers to collect from `knowledge/first_aid.json`, contacts).

## Privacy, injection, memory
- **Session only:** nothing is written to disk; closing the tab ends the case. The user can download their own case summary.
- **ID numbers removed before any model call:** Aadhaar, PAN, mobile and landline numbers, email, IFSC and account numbers
  (next to an "account" cue) are replaced with `[removed: ...]` and never re-inserted - also in the part of an over-long message
  that is kept. Spaced-out round figures and years ("paid 75000 50000", "in 2022 2023 2024") are left alone, as they are facts. Name/address for documents go in a local form on the Drafts tab
  that is never sent to a model. The app tells users their messages are processed by an AI provider.
- **Local only:** `.streamlit/config.toml` binds to localhost; no usage stats; conversations are never logged.
- **Prompt injection:** user text is wrapped in `<user_message>` tags and treated as data; case data never goes into a
  system prompt; the model's JSON passes a strict whitelist/enum/length check; messages over 4,000 characters are refused.
- **Memory:** the case file *is* the memory. Intake reads only the newest message (+ the case file + the last question) and
  returns changes, which code merges (lists are unioned; a correction replaces the payment it fixes; hypotheticals never change facts; facts can be removed;
  dates that cannot be true, such as a handover in the future, are dropped and listed as an assumption).
  Advice calls get the case file, retrieved law and a token-capped window of recent turns.
- **Sampling:** temperature 0 for intake and grounding, 0.2 advice, 0.4 conversational replies, 0.3 coaching, 0.7 role-play; `max_tokens` on every call,
  scaled up for Hindi/Telugu; reasoning off for JSON tasks; cut-off replies are detected and marked.

## Known limits
- Free models are slow, uneven and rate-limited: about 20-40 s for an advised answer on Gemini's free tier but around 160 s when a call hangs; 35-145 s on the free OpenRouter model, whose 50-requests-a-day cap stopped two test runs. The fallback chain helps but needs more than one key.
- The SBI base rate (8.95%, effective 15 Nov 2026) changes; it is editable in the app and the authority's order decides.
- Rule 35's text routes interest to Form N; current practice differs. The bot states both and says a lawyer should confirm.
- Name/address detection in free text is not attempted (unreliable in Indian languages) - the local form is used instead.
- Hindi/Telugu code-written messages were written once and need review by a fluent speaker; drafts are English only.
- Keyword escalation can miss euphemisms (the model's flags are a second signal) and cannot judge criminal intent. A real
  problem worded as a condition ("if the builder is insolvent, as the news says...") is left to the model's flag.
- The state is not asked for. If no place is mentioned, the flat is taken to be in Telangana and this is listed under
  "What I'm not sure about"; naming a place outside Telangana at any point switches to the out-of-state reply. A person
  elsewhere who never names a place therefore gets Telangana advice with that one line of warning.
- First aid for other problems is deliberately thin: no law, no deadlines, no drafts. The lists of papers to collect are
  practical checklists written by me for seven broad categories, not legal advice; a problem the model files under the wrong
  category gets the wrong checklist (the free-help contacts are still right). Any sentence in the note that names a
  section, an Act or a court ruling is dropped by code.
- **Try a sample case:** a button above the chat (or typing `sample case`) runs a clearly labelled made-up case through the
  whole flow - assessment, figures, drafts - for anyone who wants to see what the tool does first. It is refused in the middle
  of a real case, so made-up facts never mix with real ones.
- Messages that are not about any legal problem (chat, a love letter, "I'm testing this app") get a short, natural reply and
  no helpline list; free-help contacts are shown only for a real legal problem of another kind, and only once.
- A bare greeting gets an instant code-written welcome. Anything more that is not yet a case (a name, "what can you do?", a
  general question) gets a short model-written reply that answers it and invites the story; it uses up no follow-up question,
  and it stops at the same lines as advice (verified law only, no figures, no other legal areas, no drafting in chat).
- Conversational replies add one model call to a follow-up turn (two when the reply carries law and is grounding-checked).
- Some reasoning models refuse `max_tokens` or a custom `temperature`; the call is repeated the way the model asks (unit-tested, not run live).
- The grounding check is a model judging a model: it can miss things or raise false alarms; it only flags.
- The retrieval test set was written by the same person who wrote the keyword tags, so it overstates real-world recall.
- The CPA 2019 copy is the Gazette scan hosted by PRS; the LSA Act copy is from the Jharkhand SLSA (India Code was unreachable).
