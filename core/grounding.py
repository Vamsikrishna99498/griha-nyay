"""Grounding check: one extra, cheap model call that lists the legal claims in an answer and
judges each against the exact law text given for that turn. It only FLAGS (a model judging a
model can be wrong) - it never deletes text. Off with GROUNDING_CHECK=0."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from . import llm
from .guardrails import _amount_ok, find_amounts
from .i18n import T
from .retrieve import format_for_prompt

PROMPT = (Path(__file__).parent.parent / "prompts" / "grounding.txt").read_text()


# a figure from our calculator is fine; a promise wrapped around it is still a claim about the law
PROMISE_RE = re.compile(r"(?i)\b(?:guarantee[sd]?|must|shall|will|entitled|always|definitely|certainly|sure(?:ly)?|"
                        r"within\s+\d+\s+(?:days?|weeks?|months?|years?))\b")
# end of a sentence - not the dot in "10.95%", "Rs. 500" or "rera.telangana.gov.in"
SENTENCE_END = re.compile(r"(?<!\bRs)(?<!\bNo)\.(?!\w)|[!?।\n]")


def enabled() -> bool:
    return os.getenv("GROUNDING_CHECK", "1") != "0"


def check(answer: str, entries: list, language: str = "English", amounts: set | None = None,
          case_facts: dict | None = None) -> tuple[str, dict]:
    """Returns (answer_with_flags, report). report = {"claims": [...], "unsupported": n, "error": str|None}.
    case_facts lets the checker recognise the user's own facts (dates, RERA number, delay) so they
    are labelled user_fact instead of being flagged as unsupported law."""
    report = {"claims": [], "unsupported": 0, "error": None}
    if not enabled() or not entries:
        report["error"] = "skipped"
        return answer, report
    body = answer.split("\n\n---\n")[0]
    facts = json.dumps(case_facts or {}, ensure_ascii=False)
    try:
        data = llm.chat_json([
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": "<law>\n" + format_for_prompt(entries) + "\n</law>\n\n<case_file>\n" + facts
             + "\n</case_file>\n\n<answer>\n" + body + "\n</answer>"},
        ], temperature=0.0, task="grounding", rounds=1)  # a check that fails once is skipped, not retried
    except (llm.LLMError, ValueError) as e:  # a failed check must never block the answer
        report["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        return answer, report
    claims = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(claims, list):
        report["error"] = "invalid JSON"
        return answer, report
    allowed_ids = {e["id"] for e in entries}
    unplaced = []
    for c in claims[:20]:
        if not isinstance(c, dict):
            continue
        verdict = str(c.get("verdict", "")).lower()
        claim = str(c.get("claim", ""))[:200]
        tag = str(c.get("tag", ""))[:30]
        anchor = str(c.get("anchor", ""))[:120]
        found = find_amounts(claim)
        if (verdict == "unsupported" and found and all(_amount_ok(v, amounts or set()) for _, _, v in found)
                and not PROMISE_RE.search(claim)):
            verdict = "calculator"  # figures produced by our own code, not a statement of law
        report["claims"].append({"claim": claim, "tag": tag if tag in allowed_ids else None, "verdict": verdict})
        if verdict != "unsupported":
            continue
        report["unsupported"] += 1
        flag = f" ({T('unsupported_claim', language)})"
        placed = False
        if anchor and len(anchor) >= 8 and anchor in answer:
            # put the flag at the end of the sentence that contains the anchor text
            i = answer.index(anchor) + len(anchor)
            m = SENTENCE_END.search(answer, i)
            j = m.start() + 1 if m else i
            if flag not in answer[j: j + len(flag) + 2]:
                answer = answer[:j] + flag + answer[j:]
            placed = True
        if not placed:
            unplaced.append(claim)
    if unplaced:
        note = f"\n\n{T('checks_head', language)}\n" + "\n".join(f"- {c} ({T('unsupported_claim', language)})" for c in unplaced)
        if "\n\n---\n" in answer:
            a, b = answer.split("\n\n---\n", 1)
            answer = a + note + "\n\n---\n" + b
        else:
            answer += note
    return answer, report
