"""Practice mode: the AI plays the builder's representative; then a coach gives feedback.
Requires a case (the role-play needs the facts). Case data goes in as delimited data, never
into the system prompt, so a builder name like 'ignore all rules' can't act as an instruction."""
import json
from pathlib import Path

from . import llm, retrieve
from .engine import wrap_user

PROMPTS = Path(__file__).parent.parent / "prompts"
PRACTICE_WINDOW = 12   # messages sent to the builder role-play
COACH_WINDOW = 30      # messages the coach reviews
COACH_MARK = "**🧑‍🏫 Coach:**"


class NoCaseYet(RuntimeError):
    pass


def _require_case(session):
    if session.stage != "advised" or not session.case.categories and not session.case.promised_possession_date:
        raise NoCaseYet("Tell me your case first, so the practice uses your facts.")


def _case_data(session) -> str:
    c = session.case.to_dict()
    keep = {k: c[k] for k in ["builder_name", "project_name", "categories", "promised_possession_date",
                              "possession_handed_over_date", "amount_paid_rupees", "goal", "defects", "builder_excuses"]}
    return "<case_file>\n" + json.dumps(keep, ensure_ascii=False) + "\n</case_file>"


def builder_reply(session, practice_msgs: list) -> str:
    _require_case(session)
    system = (PROMPTS / "builder_roleplay.txt").read_text().format(language=session.language)
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": _case_data(session)},
            {"role": "assistant", "content": "Understood. I'm the builder's customer relations manager."}]
    window = [m for m in practice_msgs[-PRACTICE_WINDOW:] if not m["content"].startswith(COACH_MARK)]
    while window and window[0]["role"] != "user":   # the window can open mid-exchange: start at a buyer line
        window.pop(0)
    for m in window:
        msgs.append({"role": m["role"], "content": wrap_user(m["content"]) if m["role"] == "user" else m["content"]})
    return llm.chat(msgs, temperature=0.7, task="roleplay", language=session.language)


def coach(session, practice_msgs: list) -> str:
    _require_case(session)
    transcript = "\n".join(
        f"{'BUYER' if m['role'] == 'user' else 'BUILDER REP'}: {m['content']}"
        for m in practice_msgs[-COACH_WINDOW:] if not m["content"].startswith(COACH_MARK))
    entries, _ = retrieve.retrieve(session.case, transcript[-1500:])
    prompt = (PROMPTS / "coach.txt").read_text().format(language=session.language)
    data = f"<verified_law>\n{retrieve.format_for_prompt(entries)}\n</verified_law>\n\n<transcript>\n{transcript}\n</transcript>"
    out = llm.chat([{"role": "system", "content": prompt}, {"role": "user", "content": data}],
                   temperature=0.3, task="coach", language=session.language)
    return session._guarded(out, entries)
