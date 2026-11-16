"""Griha Nyay — free legal help for Telangana homebuyers facing builder delays.
Run: streamlit run app.py
"""
import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
try:  # Streamlit Cloud secrets -> env, so core/llm.py stays UI-agnostic
    for k, v in st.secrets.items():
        os.environ.setdefault(k, str(v))
except Exception:
    pass

from core import drafts, llm, roleplay  # noqa: E402
from core.calculator import TG, default_rate_pct, inr  # noqa: E402
from core.engine import Session  # noqa: E402

st.set_page_config(page_title="Griha Nyay — homebuyer legal help", page_icon="🏠", layout="wide")

if "s" not in st.session_state:
    st.session_state.s = Session()
    st.session_state.practice = []
    st.session_state.drafts = {}
s: Session = st.session_state.s

# ---------------- sidebar ----------------
with st.sidebar:
    st.markdown("### 🏠 Griha Nyay")
    st.caption("For homebuyers in **Telangana** whose builder has **delayed possession**. "
               "Not a lawyer. Not for other states, criminal matters, insolvent builders, or cases already in court.")
    mode = st.radio("What do you want to do?", ["💬 Get help", "📄 Drafts", "🥊 Practise with builder"])
    st.divider()
    st.markdown("**Your case file**")
    c = s.case
    calc = s.calc()
    st.markdown(
        f"- State: {c.state or '—'}\n- Builder: {c.builder_name or '—'}\n- Project: {c.project_name or '—'}\n"
        f"- Promised: {c.promised_possession_date or '—'}\n- Paid: {inr(c.amount_paid_rupees) if c.amount_paid_rupees else '—'}\n"
        f"- Delay: {str(calc.delay_days) + ' days' if c.promised_possession_date else '—'}\n- Wants: {c.goal or '—'}"
    )
    if s.messages:
        tips = c.missing_proof()
        if tips:
            st.markdown("**Proof to collect**\n" + "\n".join(f"- [ ] {t}" for t in tips))
    with st.expander("Interest rate"):
        st.caption(TG["interest"]["rule"] + ". " + TG["interest"]["_note"])
        s.rate_pct = st.number_input("Rate used (% per year)", value=s.rate_pct or default_rate_pct(), step=0.05)
    if s.escalations:
        st.error("Flagged for a real lawyer: " + ", ".join(i for i, _ in s.escalations))
    st.divider()
    st.caption(f"Model: `{llm.model_name()}`")
    if st.button("Start a new case"):
        for k in ["s", "practice", "drafts"]:
            st.session_state.pop(k, None)
        st.rerun()

# ---------------- main ----------------
if mode == "💬 Get help":
    st.title("Tell me what happened with your flat")
    st.caption("Write in English, Hindi, Telugu — or mix. Include: builder, project, promised date, how much you paid, and what you want.")
    if not s.messages:
        with st.chat_message("assistant"):
            st.markdown("Namaste / నమస్కారం 🙏 I help homebuyers in Telangana whose builder hasn't handed over the flat on time. "
                        "Tell me your story in your own words — I'll turn it into a case, explain your options, and draft a legal notice.")
    for m in s.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    text = st.chat_input("Type your problem…")
    if os.getenv("VOICE_MODEL"):
        audio = st.audio_input("…or speak")
        if audio is not None and st.session_state.get("last_audio") != audio.file_id:
            st.session_state.last_audio = audio.file_id
            with st.spinner("Listening…"):
                try:
                    text = llm.transcribe(audio.getvalue(), "wav")
                except Exception as e:
                    st.error(f"Voice failed: {e}")
    if text:
        with st.spinner("Thinking…"):
            s.handle(text)
        st.rerun()

elif mode == "📄 Drafts":
    st.title("Documents")
    if s.stage != "advised":
        st.info("First tell me your case in **Get help**, then come back here.")
    elif not s.drafts_allowed():
        st.warning("Your case was flagged for a real lawyer, so I won't draft filings. Take the case summary below to a lawyer or DLSA.")
        st.markdown(s.case_summary_md())
    else:
        st.caption("Drafts only. Check every fact and fill the [brackets]. The legal paragraphs are fixed text, not AI-written.")
        col1, col2 = st.columns(2)
        if col1.button("Draft legal notice to builder"):
            with st.spinner("Drafting…"):
                st.session_state.drafts["notice"] = drafts.legal_notice(s)
        if col2.button("Draft TG-RERA complaint"):
            with st.spinner("Drafting…"):
                st.session_state.drafts["complaint"] = drafts.rera_complaint(s)
        for key, label in [("notice", "Legal notice"), ("complaint", "TG-RERA complaint")]:
            if key in st.session_state.drafts:
                st.subheader(label)
                st.markdown(st.session_state.drafts[key])
                st.download_button(f"Download {label}", st.session_state.drafts[key], file_name=f"{key}.md")

else:
    st.title("Practise talking to your builder")
    st.caption("I'll play the builder's customer-relations manager. Push for your rights; type **/feedback** any time for coaching.")
    if s.stage != "advised":
        st.info("Tell me your case in **Get help** first, so I know the facts.")
    for m in st.session_state.practice:
        with st.chat_message("user" if m["role"] == "user" else "assistant", avatar=None if m["role"] == "user" else "🏗️"):
            st.markdown(m["content"])
    t = st.chat_input("Say something to the builder…")
    if t:
        with st.spinner("…"):
            if t.strip().lower() == "/feedback":
                fb = roleplay.coach(s, st.session_state.practice)
                st.session_state.practice.append({"role": "assistant", "content": "**🧑‍🏫 Coach:**\n\n" + fb})
            else:
                st.session_state.practice.append({"role": "user", "content": t})
                st.session_state.practice.append({"role": "assistant", "content": roleplay.builder_reply(s, st.session_state.practice)})
        st.rerun()
