"""Practice mode: the AI plays the builder's representative; then a coach gives feedback."""
import json
from pathlib import Path

from . import llm, retrieve

PROMPTS = Path(__file__).parent.parent / "prompts"
PRACTICE_WINDOW = 12   # messages sent to the builder role-play
COACH_WINDOW = 30      # messages the coach reviews


def builder_reply(session, practice_msgs: list) -> str:
    c = session.case
    system = (PROMPTS / "builder_roleplay.txt").read_text().format(
        builder=c.builder_name or "the builder",
        project=c.project_name or "the project",
        language=c.language or "English",
        case_json=json.dumps(c.to_dict(), ensure_ascii=False),
    )
    # only recent turns: keeps long practice sessions fast and inside free-tier limits
    return llm.chat([{"role": "system", "content": system}] + practice_msgs[-PRACTICE_WINDOW:], temperature=0.7)


def coach(session, practice_msgs: list) -> str:
    transcript = "\n".join(
        f"{'BUYER' if m['role'] == 'user' else 'BUILDER REP'}: {m['content']}"
        for m in practice_msgs[-COACH_WINDOW:] if not m["content"].startswith("**🧑‍🏫 Coach:**")
    )
    entries = retrieve.retrieve(transcript)
    prompt = (PROMPTS / "coach.txt").read_text().format(
        language=session.case.language or "English",
        law=retrieve.format_for_prompt(entries),
        transcript=transcript,
    )
    return session._guarded(llm.chat([{"role": "user", "content": prompt}], temperature=0.3), entries)
