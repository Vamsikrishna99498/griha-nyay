# Conversation tests (cases 26-27)

Two longer conversations taken from manual testing, run on the same final code and model (Gemini
`gemini-3.5-flash-lite`) after the 25-case run. They are kept here, separate from `outputs/gemini-3.5-flash-lite/`,
so that folder stays exactly the submitted 25-case run. The output files are unedited.

| Case | Messages | What it shows | Checks |
|---|---|---|---|
| `26_chat_then_sample_case` | 8 | A greeting, an unrelated request (a love letter), "assume a case", "I'm testing this app" - natural replies with no helplines or refusals - then the sample case runs a full assessment. | 23/23 |
| `27_defects_conversation` | 4 | Falling walls, bad plumbing and missing parking: safety advice first, "6 months ago" worked out as a date and stated as an assumption, practical help for a builder who stopped answering, follow-ups without repeated headings. | 16/16 |

Run them again with `python run_tests.py 26 27` (the runner writes its results to `outputs/<model>/`).
