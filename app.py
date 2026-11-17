"""Griha Nyay - free legal help for Telangana homebuyers facing builder delays or defects.
Run: streamlit run app.py   (binds to localhost only - see .streamlit/config.toml)
"""
import os

import streamlit as st
from dotenv import load_dotenv

from core import drafts, llm, roleplay
from core.calculator import TG, default_rate_pct, inr
from core.engine import MAX_USER_CHARS, Session
from core.i18n import ESC_LABELS, T
from core.privacy import scrub

load_dotenv()
# Streamlit secrets -> env, so core/llm.py stays UI-agnostic; no secrets file is normal when running locally
if st.secrets.load_if_toml_exists():
    for k, v in st.secrets.items():
        os.environ.setdefault(k, str(v))

STEPS = {"reading": "Reading your message…", "writing": "Writing the answer from the verified law…",
         "rewriting": "The answer was cut short - writing it again…", "checking": "Checking the answer against the law text…"}

# Each document in one line: what it is, and when to use it.
DOCS = {
    "notice": ("Legal notice to builder (delay)", "A formal letter telling the builder what you demand for the delay.",
               "Send it first, before any complaint.", drafts.legal_notice),
    "defect": ("Defect notice to builder", "A dated list of the defects in your flat.",
               "Send it first - it starts the builder's 30 days to repair.", drafts.defect_notice),
    "complaint": ("TG-RERA complaint (content)", "Text to copy into the online complaint form.",
                  "Only if the builder ignores your notice.", drafts.rera_complaint),
}


def intro(what: str, when: str, get: str) -> None:
    """Three one-line answers at the top of a section, so nobody reads a paragraph to learn what it is for."""
    with st.container(border=True):
        for col, (head, line) in zip(st.columns(3), [("What this is", what), ("Use it when", when), ("You get", get)]):
            col.markdown(f"**{head}**  \n{line}")


st.set_page_config(page_title="Griha Nyay - homebuyer legal help", page_icon="🏠", layout="wide")

if "s" not in st.session_state:
    st.session_state.s = Session()
    st.session_state.practice = []
    st.session_state.drafts = set()   # which drafts are open; the text is rebuilt on every run so it is never stale
s: Session = st.session_state.s

# ---------------- sidebar ----------------
with st.sidebar:
    st.markdown("### 🏠 Griha Nyay")
    st.markdown("**Covers** - Telangana only\n- Builder delayed possession\n- Defects after possession")
    st.caption("**Not for:** criminal matters · insolvent builders · cases already in court.  \nNot a lawyer.")
    mode = st.radio("What do you want to do?", ["💬 Get help", "📄 Drafts", "🥊 Practise with builder"],
                    captions=["Start here: tell me what happened", "Letters you can send the builder", "Rehearse the conversation"])
    st.divider()
    st.markdown("**Your case file**")
    c = s.case
    calc = s.calc()
    lines = [f"- Problem: {', '.join(c.categories) or '—'}", f"- State: {c.state or '—'}{' (assumed)' if c.state_assumed else ''}",
             f"- Builder: {c.builder_name or '—'}", f"- Project: {c.project_name or '—'}"]
    if "defects" in c.categories:
        dc = s.defect_calc()
        lines += [f"- Possession: {c.possession_handed_over_date or '—'}",
                  f"- 5-year window ends: {dc.window_end or '—'}", f"- Defects: {len(c.defects)} listed"]
    if "delay" in c.categories or not c.categories:
        lines += [f"- Promised: {c.promised_possession_date or '—'}",
                  f"- Paid: {inr(c.amount_paid_rupees) if c.amount_paid_rupees else '—'}",
                  f"- Delay: {str(calc.delay_days) + ' days' if c.promised_possession_date else '—'}"]
    lines.append(f"- Wants: {c.goal or '—'}")
    st.markdown("\n".join(lines))
    if s.messages:
        tips = c.missing_proof()
        if tips:
            st.markdown("**Proof to collect**\n" + "\n".join(f"- [ ] {t}" for t in tips))
        st.download_button("⬇️ Download my case summary", s.download_md(), file_name="my_case_summary.md")
    with st.expander("Interest rate"):
        i = TG["interest"]
        st.caption(f"{i['rule']}. Base rate {i['base_rate_pct']}% effective {i['base_rate_effective']} ({i['base_rate_source']}). {i['_note']}")
        s.rate_pct = st.number_input("Rate used (% per year)", min_value=0.0, max_value=30.0, step=0.05,
                                     value=float(default_rate_pct() if s.rate_pct is None else s.rate_pct))
    setup_problems = llm.config_problems()
    if setup_problems:
        st.warning(T("setup", detail="; ".join(setup_problems)))
    if s.escalations:
        st.error("Flagged for a real lawyer: " + ", ".join(ESC_LABELS[x]["en"] for x in s.escalations))
    st.divider()
    used = llm.last_call.get("provider")
    cached, sent = llm.last_call.get("cached_tokens"), llm.last_call.get("prompt_tokens")
    st.caption(f"Model: `{llm.model_name()}`" + (f" · last answer from `{used}`" if used else "")
               + (f" · {cached} of {sent} input tokens from cache" if cached is not None and sent else ""))
    if st.button("Start a new case"):
        for k in ["s", "practice", "drafts"]:
            st.session_state.pop(k, None)
        st.rerun()

# ---------------- main ----------------
if mode == "💬 Get help":
    st.title("Tell me what happened with your flat")
    if not s.messages:
        intro("A chat that turns your story into a case file and explains your options.",
              "Start here - your builder is late with possession, or the flat has defects.",
              "Where you stand, your choices with figures, and the next steps.")
    st.caption("**Tell me:** builder and project · area or city · promised date (or the date you got the flat) · "
               "amount paid · what you want.  \nEnglish, Hindi, Telugu or a mix.")
    if not s.messages:
        with st.chat_message("assistant"):
            st.markdown(T("welcome") + "\n\n" + T("privacy"))
    for m in s.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    text = st.chat_input("Type your problem…")
    if text:
        with st.chat_message("user"):   # show the message at once, exactly as it will be kept (ID numbers removed)
            st.markdown(s.stored_text(text)[0])
        with st.chat_message("assistant"):
            st.caption("Free AI models can take a minute or two.")
            with st.status(STEPS["reading"]) as status:   # says which step is running, instead of a bare spinner
                s.progress = lambda step: status.update(label=STEPS.get(step, step))
                try:
                    s.handle(text)
                finally:
                    s.progress = None
        st.rerun()

elif mode == "📄 Drafts":
    st.title("Documents")
    intro("Letters built from your case file, ready to edit. No AI writes them.",
          "After the chat has given your assessment and you are ready to write to the builder.",
          "Up to three documents to check, complete and download.")
    if s.stage != "advised":
        st.info("First tell me your case in **Get help**, then come back here.")
    elif not s.drafts_allowed():
        st.warning("Your case was flagged for a real lawyer, so I won't draft filings. Take the case summary below to a lawyer or DLSA.")
        st.markdown(s.case_summary_md())
    else:
        st.caption("Before you send: check every fact · fill the [brackets] · drafts are in English.")
        with st.expander("🔒 Your name and address for the letters (optional)", expanded=not s.party):
            st.caption("Stays on this device · never sent to the AI · leave blank to fill in by hand later.")
            with st.form("party"):
                name = st.text_input("Your full name", s.party.get("name", ""))
                address = st.text_area("Your address", s.party.get("address", ""))
                contact = st.text_input("Your phone / email (for the letter only)", s.party.get("contact", ""))
                baddr = st.text_area("Builder's registered office address", s.party.get("builder_address", ""))
                if st.form_submit_button("Save details"):
                    s.party = {k: v.strip() for k, v in dict(name=name, address=address, contact=contact, builder_address=baddr).items() if v.strip()}
        plan = s.draft_plan()
        if plan["choice_applies"]:
            options = {"refund": "My money back, with interest", "possession": "The flat, with interest for the delay"}
            picked = st.radio("You haven't told me which you want. What should the notice demand?", list(options),
                              format_func=options.get, index=list(options).index(s.notice_choice) if s.notice_choice else None)
            if picked != s.notice_choice:
                s.notice_choice = picked
                plan = s.draft_plan()
            if plan["needs_choice"]:
                st.info("Choose one above and I'll prepare the notice. If you're not sure yet, ask me about the difference in **Get help**.")
        if plan["no_delay_yet"]:
            st.info("There is no delay to claim today (the promised date has not passed, or possession was given by then), so no delay notice is offered.")
        if "defects" in s.case.categories and not plan["defect_notice"]:
            st.info("The defect notice is not offered because the 5-year window seems to have passed - see the chat for where to get help.")
        offered = [k for k, ok in (("notice", plan["notice"]), ("defect", plan["defect_notice"]), ("complaint", plan["complaint"])) if ok]
        opened = st.session_state.drafts
        for col, key in zip(st.columns(len(offered)) if offered else [], offered):
            label, what, when, _ = DOCS[key]
            with col.container(border=True):   # one card per document: what it is, when to use it, one button
                st.markdown(f"**{label}**  \n{what}  \n**When:** {when}")
                if st.button("Hide draft" if key in opened else "Show draft", key=f"show_{key}"):
                    opened.symmetric_difference_update({key})
                    st.rerun()
        for key in offered:
            if key in opened:
                label, _, _, build = DOCS[key]
                text = build(s)   # rebuilt now, so a corrected fact, saved name or changed rate shows at once
                st.subheader(label)
                st.download_button(f"⬇️ Download: {label}", text, file_name=f"{key}.md", key=f"dl_{key}")
                with st.container(border=True):
                    st.markdown(text)

else:
    st.title("Practise talking to your builder")
    if not st.session_state.practice:
        intro("A rehearsal: I play the builder's customer-relations manager.",
              "Before you call or meet the builder.",
              "The excuses a builder's office gives, to practise against - and coaching when you ask.")
    st.caption("Say what you would say to the builder.  \nType **/feedback** any time for coaching.")
    if s.stage != "advised":
        st.info("Tell me your case in **Get help** first, so the practice uses your facts.")
        st.stop()
    for m in st.session_state.practice:
        with st.chat_message("user" if m["role"] == "user" else "assistant", avatar=None if m["role"] == "user" else "🏗️"):
            st.markdown(m["content"])
    t = st.chat_input("Say something to the builder…")
    if t and len(t) > MAX_USER_CHARS:
        st.warning(T("too_long", s.language, n=len(t), max=MAX_USER_CHARS))
    elif t:
        t, _ = scrub(t)
        practice = st.session_state.practice
        with st.spinner("…"):
            try:
                if t.strip().lower() == "/feedback":
                    fb = roleplay.coach(s, practice)
                    practice.append({"role": "assistant", "content": roleplay.COACH_MARK + "\n\n" + fb})
                else:
                    # the buyer's line is kept only together with the builder's reply: a failed call leaves no orphan
                    reply = roleplay.builder_reply(s, practice + [{"role": "user", "content": t}])
                    practice += [{"role": "user", "content": t}, {"role": "assistant", "content": reply}]
            except llm.LLMConfigError as e:
                st.error(T("setup", s.language, detail=str(e)))
            except roleplay.NoCaseYet as e:
                st.info(str(e))
            except llm.LLMError:
                st.error(T("error", s.language))
            else:
                st.rerun()
