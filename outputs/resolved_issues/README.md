# Resolved issues

Raw outputs saved during development, each showing a problem that testing found **and that has since been fixed**.
They are kept unedited as evidence of how the tool was tested and improved. The current results are in
`outputs/gemini-3.5-flash-lite/`.

| File | What it showed | How it was resolved |
|---|---|---|
| `01_clean_refund_json_cut_off.md` | A long story made the model's structured reply run out of room, so the user got "technical problem". | A reply cut off mid-JSON is now asked for again with twice the room. |
| `01_reply_cut_off.md` | The advice stopped mid-sentence: the model's hidden reasoning used up the output budget. | Cut-off answers are detected and retried with twice the room (0 of 21 cut off after the fix). |
| `15_delay_counted_past_handover.md` | The delay was counted to today (1050 days) instead of to the late handover date (579 days), about Rs 10 lakh too much, also in the notice. | The delay now ends at the handover date; a test pins 579 days. |
