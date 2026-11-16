"""Conversation-flow tests with a FAKE model (no API key, no cost).
They test our code paths (re-extraction, escalation, off-topic, drafts gating, history),
not the model's quality. Run: python -m tests.test_engine_mocked"""
from datetime import date

from core import engine, llm, roleplay


def fake_extract(user_text: str) -> dict:
    """Pretend intake model: reads the conversation, latest correction wins."""
    t = user_text.lower()
    d = {"language": "English", "in_scope": True, "topic": "builder delayed flat possession",
         "followup_question": "", "assumptions": []}
    if "landlord" in t:
        return {**d, "in_scope": False, "topic": "landlord not returning deposit"}
    if "hyderabad" in t:
        d["city"] = "Hyderabad"
    if "december 2023" in t:
        d["promised_possession_date"] = "2023-12-01"
        d["assumptions"] = ["December 2023 taken as 1 December 2023"]
    if "48 lakh" in t:
        d["amount_paid_rupees"] = 4800000
    if "55 lakh" in t:  # correction later in the chat
        d["amount_paid_rupees"] = 5500000
    if "refund" in t:
        d["goal"] = "refund"
    if "pune" in t:  # later correction: latest wins
        d["city"], d["state"] = "Pune", "Maharashtra"
    return d


def install_fake(monkey_calls: list):
    def fake_chat_json(messages, **kw):
        monkey_calls.append(("json", messages))
        return fake_extract(messages[-1]["content"])

    def fake_chat(messages, **kw):
        monkey_calls.append(("chat", messages))
        return "You can withdraw and get a refund with interest [RERA-18-1]. Also see Section 420 IPC."

    llm.chat_json = fake_chat_json
    llm.chat = fake_chat


def new_session():
    return engine.Session(as_of=date(2026, 11, 15), rate_pct=10.0)


def test_late_correction_updates_case_and_tells_user():
    calls = []
    install_fake(calls)
    s = new_session()
    s.handle("My flat in Hyderabad was promised December 2023, I paid 48 lakh, I want a refund.")
    assert s.stage == "advised" and s.case.amount_paid_rupees == 4800000
    r = s.handle("Sorry, actually I paid 55 lakh, not 48.")
    assert s.case.amount_paid_rupees == 5500000, "correction must reach the case file"
    assert "Updated your case file" in r and "Rs 48,00,000 → Rs 55,00,000" in r
    assert s.calc().amount_paid == 5500000, "calculator must use corrected amount"


def test_plain_question_does_not_reextract():
    calls = []
    install_fake(calls)
    s = new_session()
    s.handle("My flat in Hyderabad was promised December 2023, I paid 48 lakh, I want a refund.")
    n_json = sum(1 for k, _ in calls if k == "json")
    r = s.handle("Can I also go to consumer court?")
    assert sum(1 for k, _ in calls if k == "json") == n_json, "no extra extraction call for a plain question"
    assert "Updated your case file" not in r


def test_validator_still_runs_on_answers():
    install_fake([])
    s = new_session()
    r = s.handle("My flat in Hyderabad was promised December 2023, I paid 48 lakh, I want a refund.")
    assert "420" not in r and "[RERA-18-1]" in r and "unverified legal reference removed" in r


def test_off_topic_is_refused_honestly():
    install_fake([])
    s = new_session()
    r = s.handle("My landlord won't return my 50,000 deposit.")
    assert "outside what I cover" in r and "landlord not returning deposit" in r
    assert s.stage == "intake" and not s.drafts_allowed()


def test_assumptions_kept_and_shown():
    install_fake([])
    s = new_session()
    s.handle("My flat in Hyderabad was promised December 2023, I paid 48 lakh, I want a refund.")
    assert s.case.assumptions == ["December 2023 taken as 1 December 2023"]
    assert "December 2023 taken as 1 December 2023" in s.case_summary_md()


def test_state_change_after_advice_escalates_and_blocks_drafts():
    install_fake([])
    s = new_session()
    s.handle("My flat in Hyderabad was promised December 2023, I paid 48 lakh, I want a refund.")
    assert s.drafts_allowed()
    r = s.handle("Wait, I mixed up two flats - this one is in Pune.")
    assert "out_of_state" in [i for i, _ in s.escalations] and "real lawyer" in r
    assert not s.drafts_allowed()


def test_given_state_not_overridden_by_old_city():
    from core.case import CaseFile
    c = CaseFile()
    c.update_from({"city": "Hyderabad"})
    assert c.state == "Telangana"
    c.update_from({"state": "Maharashtra"})  # city still says Hyderabad from before
    assert c.state == "Maharashtra"


def test_history_strips_sources_blocks():
    install_fake([])
    s = new_session()
    s.handle("My flat in Hyderabad was promised December 2023, I paid 48 lakh, I want a refund.")
    assert "Sources used" in s.messages[-1]["content"]
    assert all("Sources used" not in m["content"] for m in s._history())


def test_practice_window_caps_history():
    calls = []
    install_fake(calls)
    s = new_session()
    msgs = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"} for i in range(40)]
    roleplay.builder_reply(s, msgs)
    sent = calls[-1][1]
    assert len(sent) == 1 + roleplay.PRACTICE_WINDOW and sent[-1]["content"] == "m39"


if __name__ == "__main__":
    real_chat, real_json = llm.chat, llm.chat_json
    try:
        for name, fn in list(globals().items()):
            if name.startswith("test_"):
                fn()
                print("PASS", name)
    finally:
        llm.chat, llm.chat_json = real_chat, real_json
