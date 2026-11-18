"""The conversation engine. Code owns the flow; the model only fills in language.

intake (newest message only) -> escalate? / out of scope? / ask for missing facts -> advise -> Q&A
Memory = the structured case file + a token-capped window of recent messages.
Used by both the Streamlit app and run_tests.py, so tests exercise the real path.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from . import grounding, guardrails, llm, retrieve
from .calculator import compute, defect_check, inr
from .case import CaseFile, clean_extraction
from .i18n import ESC_LABELS, T, code_lang, detect_language, field_label
from .privacy import scrub

ROOT = Path(__file__).parent.parent
PROMPTS = ROOT / "prompts"
HELP = json.loads((ROOT / "knowledge" / "helplines.json").read_text())

MAX_USER_CHARS = 4000
MAX_FOLLOWUPS = 2          # questions about missing facts before advising anyway
HISTORY_TOKENS = 2500      # recent turns sent with each advice call
# After the first advice, re-run extraction only when a message may carry a fact.
FACT_HINT = re.compile(
    r"\d|lakh|lac|crore|actually|correction|mistake|wrong|typo|i meant|changed my mind|instead|"
    r"paid|refund|possession|handed|registered|rera|agreement|promised|crack|leak|seep|defect|damp|"
    r"లక్ష|కోటి|తేదీ|కట్టా|పగుళ్లు|లీకేజీ|లోపం|తప్పు|लाख|करोड़|तारीख|दरार|लीकेज|गलत|ग़लत", re.IGNORECASE)
WHAT_IF_FIGURES = re.compile(r"(?i)\d|lakh|lac\b|crore|rupee|amount|paid|लाख|करोड़|रुपय|లక్ష|కోటి|రూపాయ")
TRACKED = {
    "state": "State", "builder_name": "Builder", "project_name": "Project", "rera_number": "RERA no.",
    "rera_registered": "RERA registered", "agreement_date": "Agreement date",
    "promised_possession_date": "Promised possession", "possession_handed_over_date": "Possession received",
    "total_price_rupees": "Total price", "amount_paid_rupees": "Amount paid", "goal": "What you want",
    "payments": "Payments", "defects": "Defects", "defect_reported_date": "Defects reported on",
    "categories": "Problem type",
}
# Escalations after which the bot must not draft filings for the user.
DRAFT_BLOCKERS = {"insolvency", "already_in_court", "criminal", "title_dispute", "out_of_state", "unregistered"}
# Escalations worked out from the case file. They are re-checked every turn, so a corrected fact
# (wrong state, wrong amount) lifts them. Keyword and flag escalations stay once raised.
CASE_ESCALATIONS = {"out_of_state", "unregistered", "high_value", "defect_window_passed"}
# Facts that show the person has started describing a builder problem (the state alone does not).
PROBLEM_FIELDS = ["categories", "builder_name", "project_name", "promised_possession_date", "possession_handed_over_date",
                  "amount_paid_rupees", "total_price_rupees", "defects", "goal", "rera_number", "agreement_date"]
SHORT_MESSAGE_WORDS = 3    # "hi", "hello there": a greeting, not a different legal problem
OFF_TOPIC_MIN_WORDS = 6    # "outside what I cover" needs a described problem; shorter lines get the welcome instead
# "Try a sample case": a clearly labelled made-up case, run through the whole flow, for anyone who wants to see what
# the tool does before telling their own story (or who is testing it). Typing one of these words does the same.
SAMPLE_TRIGGERS = {"sample case", "sample", "try a sample case", "demo", "/sample", "example case"}
SAMPLE_CASE = ("Sample case (made-up facts): I booked Flat 504, Tower B in Skyline Heights, Kokapet, Hyderabad from Sunrise "
               "Constructions. The agreement for sale was signed on 10 March 2021 and possession was promised by 31 December 2023. "
               "The total price is 62 lakh and I have paid 48 lakh: 6 lakh on 10 March 2021, 20 lakh on 1 September 2021 and "
               "22 lakh on 15 June 2022. The RERA number is P02400003456. I still don't have the flat and the builder keeps "
               "saying next quarter. I have the agreement and bank statements. I want my money back.")
CORE_FACTS = ["promised_possession_date", "possession_handed_over_date", "amount_paid_rupees", "payments", "defects"]
SMALL_TALK_TOPIC = re.compile(r"(?i)greet|introduc|\bname\b|small talk|thank|chit|hello|pleasantr")   # intake's own label for it
CHAT_PATIENCE = {"timeout": 30, "rounds": 2}   # a conversational turn gets two quick tries; then the code-written reply
STORY_ITEMS = "the builder and project, the area or city, the promised date (or the date they got the flat), how much they paid, what they want"


def _p(name: str) -> str:
    return (PROMPTS / name).read_text()


def wrap_user(text: str) -> str:
    """Delimit user text so the model treats it as data; neutralise any fake closing tag."""
    safe = re.sub(r"(?i)</?\s*user_message\s*>", "[tag removed]", text)
    return f"<user_message>\n{safe}\n</user_message>"


def help_block(ids, language: str) -> str:
    keys = []
    for i in ids:
        for k in HELP["when"].get(i, []):
            if k not in keys:
                keys.append(k)
    lc = code_lang(language)
    return "\n".join(f"- {HELP['pointers'][k]['label'].get(lc, HELP['pointers'][k]['label']['en'])}" for k in keys)


class Session:
    def __init__(self, as_of: date | None = None, rate_pct: float | None = None):
        self.case = CaseFile()
        self.messages = []          # visible chat [{"role","content"}]; user text is stored AFTER scrubbing
        self.stage = "intake"       # intake | advised
        self.followups = 0
        self.idle = 0               # messages in a row that described no builder problem (greetings, small talk)
        self._story_asked = 0       # times the full list of details to give has been shown
        self._sample_offered = False  # the sample case has been pointed out once already
        self._pointers_shown = False  # free-help contacts for another kind of problem are listed once, not every turn
        self.assessed = False       # the structured first assessment has been given
        self.escalations = []       # rule ids
        self.cautions = []
        self.flags = {}
        self.as_of = as_of
        self.rate_pct = rate_pct
        self.notice_choice = None
        self.party = {}             # name/address etc. from the local Drafts form - NEVER sent to a model
        self.log = []               # audit trail: counts, ids and types only - never message text
        self.progress = None        # optional callable(step: str): the app shows which step is running
        self._in_scope = None
        self._topic = ""
        self.last_retrieval = {}

    # ---------- helpers ----------
    @property
    def language(self) -> str:
        return self.case.language or "English"

    def stored_text(self, text: str) -> tuple[str, list]:
        """(text as it is kept and shown, kinds of ID numbers removed). ID numbers are removed from the WHOLE
        message before an over-long one is shortened, so nothing unscrubbed is ever stored or sent on."""
        clean, kinds = scrub(text)
        if len(text) > MAX_USER_CHARS:
            clean = clean[:300] + " …"
        return clean, kinds

    def has_problem(self) -> bool:
        return any(getattr(self.case, f) for f in PROBLEM_FIELDS)

    def _step(self, name: str) -> None:
        if self.progress:
            self.progress(name)

    def user_text(self) -> str:
        """All user text - used ONLY by code-side keyword scans, never sent to the model."""
        return "\n".join(m["content"] for m in self.messages if m["role"] == "user")

    def calc(self):
        c = self.case
        return compute(c.promised_possession_date, c.amount_paid_rupees, c.payments, as_of=self.as_of,
                       rate_pct=self.rate_pct, handed_over=c.possession_handed_over_date)

    def defect_calc(self):
        c = self.case
        return defect_check(c.possession_handed_over_date, c.defect_reported_date, as_of=self.as_of)

    def drafts_allowed(self) -> bool:
        return self.stage == "advised" and not (set(self.escalations) & DRAFT_BLOCKERS)

    def defect_drafts_allowed(self) -> bool:
        return (self.drafts_allowed() and "defects" in self.case.categories and "defect_window_passed" not in self.escalations
                and self.defect_calc().within_window is not False)

    def draft_plan(self) -> dict:
        """Which documents may be drafted now, and what the delay notice should demand.
        The single decision point for the app and run_tests."""
        c = self.case
        allowed = self.drafts_allowed()
        delay_case = "delay" in c.categories or not c.categories
        no_delay = bool(c.promised_possession_date) and self.calc().delay_days == 0
        delay_ok = allowed and delay_case and not no_delay
        handed_over = bool(c.possession_handed_over_date)
        stated = c.goal if c.goal in ("refund", "possession") else None
        demand = "interest_only" if handed_over else stated or self.notice_choice
        choice_applies = delay_ok and not handed_over and not stated
        needs_choice = choice_applies and demand is None
        defects_ok = self.defect_drafts_allowed()
        return {
            "delay": delay_ok, "no_delay_yet": allowed and delay_case and no_delay,
            "demand": demand if delay_ok else None, "choice_applies": choice_applies, "needs_choice": needs_choice,
            "defects": defects_ok, "notice": delay_ok and not needs_choice, "defect_notice": defects_ok,
            "complaint": (delay_ok or defects_ok) and not needs_choice,
        }

    def allowed_amounts(self) -> set:
        c = self.case
        return self.calc().amounts() | {x for x in [c.amount_paid_rupees, c.total_price_rupees] if x} | {
            p["amount_rupees"] for p in c.payments}

    def _history(self) -> list:
        """Recent chat for the model, newest last, capped by an estimated token budget.
        'Sources' blocks are dropped (code re-adds them) and user turns are delimited as data."""
        out, used = [], 0
        for m in reversed(self.messages):
            content = m["content"].split("\n\n---\n")[0]
            n = llm.estimate_tokens(content)
            if out and used + n > HISTORY_TOKENS:
                break
            used += n
            out.append({"role": m["role"], "content": wrap_user(content) if m["role"] == "user" else content})
        return out[::-1]

    @staticmethod
    def _fmt(k, v):
        if v is None or v == []:
            return "—"
        if k.endswith("_rupees"):
            return inr(v)
        if k == "payments":
            return f"{len(v)} dated payment(s)"
        if isinstance(v, list):
            return ", ".join(map(str, v))
        return str(v)

    def _diff_note(self, before: dict, after: dict) -> str:
        changes = [f"{label}: {self._fmt(k, before.get(k))} → {self._fmt(k, after.get(k))}"
                   for k, label in TRACKED.items() if before.get(k) != after.get(k)]
        if changes:
            self.log.append({"type": "case_updated", "fields": [k for k in TRACKED if before.get(k) != after.get(k)]})
            return T("updated_case", self.language, changes="; ".join(changes)) + "\n\n"
        return ""

    # ---------- intake ----------
    def _intake(self, text: str) -> dict:
        last_q = next((m["content"].split("\n\n---\n")[0][:600] for m in reversed(self.messages[:-1])
                       if m["role"] == "assistant"), "")
        missing = ", ".join(self.case.missing_required()) or "nothing"
        self._step("reading")
        fixed = f"<law_index>\n{retrieve.law_index()}\n</law_index>\n"
        data_msg = (f"<case_file>\n{json.dumps(self.case.to_dict(), ensure_ascii=False)}\n</case_file>\n"
                    f"<missing>{missing}</missing>\n<last_question>\n{last_q}\n</last_question>\n\n" + wrap_user(text))
        raw = llm.chat_json([{"role": "system", "content": _p("intake.txt")}, llm.user_message(fixed, data_msg)],
                            temperature=0.0, task="intake", language=self.language)
        clean, dropped = clean_extraction(raw)
        if dropped:
            self.log.append({"type": "schema_dropped", "keys": dropped[:10]})
        if clean.get("language") in ("Hinglish", "Tenglish") and self.case.language == "English":
            self.case.language = clean["language"]
        kind = clean.get("message_kind", "facts")
        if kind == "remove" and clean.get("remove_fields"):
            self.case.remove(clean["remove_fields"])
            self.log.append({"type": "fields_removed", "fields": clean["remove_fields"]})
        if kind == "hypothetical":
            self.log.append({"type": "hypothetical_not_merged"})
        else:  # a question often carries facts too ("paid 37 lakh, can I get a refund?"), so they are kept
            self.case.update_from(clean)
            self._drop_impossible_dates()
        self.flags.update(clean.get("flags") or {})
        if self._in_scope is not True and isinstance(clean.get("in_scope"), bool):
            self._in_scope = clean["in_scope"]  # once a case is in scope it stays in scope
        self._topic = clean.get("topic") or self._topic
        return clean

    def _drop_impossible_dates(self) -> None:
        """Things that have 'happened' cannot be dated in the future. Such a date is dropped and the case
        file says so, instead of going into the sums and the notice as a fact."""
        c, today = self.case, self.as_of or date.today()
        notes = []
        for f, what in (("possession_handed_over_date", "possession"), ("defect_reported_date", "reporting the defects"),
                        ("agreement_date", "the agreement")):
            d = getattr(c, f)
            if d and d > today:
                setattr(c, f, None)
                notes.append(f"The date given for {what} ({d.isoformat()}) is in the future, so it was not used.")
        future = [p for p in c.payments if p["date"] > today]
        if future:
            c.payments = [p for p in c.payments if p["date"] <= today]
            notes.append(f"{len(future)} payment(s) dated in the future were not counted.")
        for n in notes:
            if n not in c.assumptions:
                c.assumptions.append(n)
        if notes:
            self.log.append({"type": "impossible_dates_dropped", "count": len(notes)})

    # ---------- replies written by code ----------
    def _escalation_reply(self, newly: list) -> str:
        lang = self.language
        lines = [T("need_lawyer", lang), ""]
        lines += [f"- {guardrails.escalation_message(i, lang)}" for i in newly]
        lines += ["", T("where_help", lang), help_block(newly, lang), "", T("take_summary", lang), self.case_summary_md()]
        return "\n".join(lines)

    def _central_law_reply(self) -> str:
        """Out-of-state (or state never given): explain the central Act only, from exact text."""
        lang = self.language
        cats = self.case.categories
        topics = [("central_law", "RERA-18-1")] if "delay" in cats or "defects" not in cats else []
        topics += [("central_law_defects", "RERA-14-3")] if "defects" in cats else []
        portal = HELP["state_rera_portals"].get(self.case.state or "")
        lines = [guardrails.escalation_message("out_of_state", lang), ""]
        for head, i in topics:
            e = retrieve.KB[i]
            lines += [T(head, lang), f"> [{e['id']}] \"{e['quote_text']}\"", "", f"_{e['gist']}_", ""]
        lines += [T("out_of_state_portal", lang, url=portal["url"]) if portal else T("out_of_state_generic", lang),
                  "", T("where_help", lang), help_block(["out_of_state"], lang),
                  "\n---\n" + T("sources_head", lang) + "\n" + retrieve.sources_block([i for _, i in topics])]
        return "\n".join(lines)

    def _off_topic_reply(self) -> str:
        lang = self.language
        return "\n".join([T("off_topic", lang, topic=self._topic or "a different kind of legal problem"), "",
                          T("where_help", lang), help_block(["off_topic"], lang), "", T("off_topic_tail", lang)])

    def _followup(self, x: dict, missing_before: list | None, progressed: bool = True) -> str:
        """The model wrote its question before code merged facts (e.g. Hyderabad -> Telangana).
        Use it only if the missing set didn't change; otherwise build the question in code.
        'Thanks, that helps' is said only when the message really added something."""
        missing = self.case.missing_required()
        q = (x.get("followup_question") or "").strip()
        if q and missing_before is not None and set(missing_before) == set(missing):
            return q
        return T("need" if progressed else "need_plain", self.language,
                 items="; ".join(field_label(f, self.language) for f in missing))

    @staticmethod
    def _small_talk(text: str, x: dict) -> bool:
        """Models label "hi" as out of scope (topic: greeting). A greeting, a name or a few words is not a
        different legal problem: it gets the welcome, and the free-help pointers if it keeps happening."""
        return x.get("message_kind") in ("other", "chat") or len(text.split()) < OFF_TOPIC_MIN_WORDS

    @staticmethod
    def _asks_something(text: str, x: dict) -> bool:
        return x.get("message_kind") in ("question", "hypothetical") or "?" in text

    def _tell_me_reply(self, text: str, x: dict) -> str:
        """Nothing about a builder problem yet. No question is counted.
        - a bare greeting ("hi"): the welcome, written by code, at once;
        - anything more (a name, "what can you do?", a general question, a worry): a short reply from the
          model that answers what was said and then invites the story (falls back to the welcome).
        Free-help pointers are added by code when it looks like a different kind of problem."""
        lang = self.language
        self.idle += 1
        self.log.append({"type": "no_problem_yet", "count": self.idle})
        first = not any(m["role"] == "assistant" for m in self.messages)
        short = len(text.split()) <= SHORT_MESSAGE_WORDS
        chat = x.get("message_kind") in ("chat", "other") or bool(SMALL_TALK_TOPIC.search(x.get("topic") or ""))
        # contacts only for a real legal problem of another kind, and only once - never for chat, a joke or a test
        elsewhere = x.get("in_scope") is False and not short and not chat
        pointers = ["off_topic"] if elsewhere and not self._pointers_shown else None
        if not (short and first):   # only the very first bare greeting gets the instant code-written welcome
            if self._story_asked == 0:
                ending = f"invite them in one sentence to tell you what happened with their flat: {STORY_ITEMS}"
            else:
                ending = ("invite them briefly to share their situation whenever they are ready. Do not list again the details to "
                          "give - they have already seen that list")
            if not self._sample_offered:
                demo = "If they want to see what you can do, point them to the sample case."
            else:
                demo = ("You have already told them about the sample case. Mention it again only if they ask again for an example, "
                        "and then in a few words only (for example: just type sample case). Do not repeat sentences from your "
                        "earlier replies.")
            situation = [f"No builder problem has been described yet. After responding to what they said, {ending}. {demo}"]
            if elsewhere:
                situation.append(f"The intake step read this message as a different kind of legal problem ({x.get('topic') or 'not a builder matter'}). "
                                 "If it is, say kindly, in one sentence, that it is outside what you cover, and stop there.")
            reply = self._chat_reply(text, x, situation, pointers=pointers, pointers_head="where_help")
            if reply:
                self._story_asked += 1
                self._pointers_shown = self._pointers_shown or bool(pointers)
                self._sample_offered = self._sample_offered or "sample case" in reply.lower()
                return reply
        self._story_asked += 1
        lines = [(T("hello", lang) if first else "") + T("tell_me", lang)]   # greet once, not every time
        if pointers:
            self._pointers_shown = True
            lines += ["", T("where_help", lang), help_block(pointers, lang)]
        return "\n".join(lines)

    def _ask_for_missing(self, text: str, x: dict, missing_before: list | None, progressed: bool) -> str:
        """A builder problem is on the table but facts are missing: acknowledge what was said, answer any
        question, then ask for what is needed. Written by the model; the code-built question is the fallback."""
        missing = self.case.missing_required()
        situation = ["Still needed before the full assessment: " + "; ".join(field_label(f, "English") for f in missing) + ". "
                     "After responding to what they said, end with one short, friendly question asking for these (nothing else)."]
        if self.case.state_assumed:
            situation.append("No place was mentioned, so the flat is being treated as in Telangana. Do not ask about the state.")
        return (self._chat_reply(text, x, situation, ground=self._asks_something(text, x))
                or self._followup(x, missing_before, progressed))

    def _chat_reply(self, text: str, x: dict, situation: list, law=None, pointers: list | None = None,
                    ground: bool = True, pointers_head: str = "where_help") -> str | None:
        """One short conversational turn from the model (prompts/chat.txt): respond to what the person said,
        then do what <situation> says. It passes the same citation, quote and amount checks as advice; the
        extra grounding call runs when the reply could carry law. Returns None if the model can't be reached,
        so the caller can use its code-written reply instead."""
        entries, why = retrieve.retrieve(self.case if self.has_problem() else None, text, law_ids=x.get("law_ids"),
                                         cautions=self.cautions, escalations=self.escalations)
        if law:
            entries = [e for e in entries if law(e)]
        if not entries:
            situation = situation + ["No verified law matches this message, so do not state any law in this reply."]
        data = (f"<verified_law>\n{retrieve.format_for_prompt(entries) or 'none'}\n</verified_law>\n\n"
                f"<case_file>\n{json.dumps(self.case.to_dict(), ensure_ascii=False)}\n</case_file>\n\n"
                f"<situation>\n{chr(10).join(situation)}\n</situation>")
        msgs = [{"role": "system", "content": _p("chat.txt").format(language=self.language)},
                {"role": "user", "content": data}, {"role": "assistant", "content": "Understood."}] + self._history()
        self._step("writing")
        try:
            raw, finish = llm.chat_finish(msgs, temperature=0.4, task="chat", language=self.language, **CHAT_PATIENCE)
            if finish == "length":   # hidden reasoning used up the room: once more with twice as much
                raw, finish = llm.chat_finish(msgs, temperature=0.4, task="chat", language=self.language, **CHAT_PATIENCE,
                                              max_tokens=2 * llm.max_tokens_for("chat", self.language))
            if finish == "length":
                raise llm.LLMError("reply cut off twice")
        except llm.LLMConfigError:
            raise
        except llm.LLMError as e:
            self.log.append({"type": "chat_fallback", "detail": f"{type(e).__name__}: {str(e)[:160]}"})
            return None
        self.last_retrieval = why
        self.log.append({"type": "chat_reply", "ids": why})
        reply = self._guarded(raw, entries, ground=ground or bool(guardrails.cited_ids(guardrails.split_tag_lists(raw))))
        if pointers:   # contacts are written by code, never by the model, and sit above the sources list
            body, sep, sources = reply.partition("\n\n---\n")
            reply = body + "\n\n" + T(pointers_head, self.language) + "\n" + help_block(pointers, self.language) + sep + sources
        return reply

    # ---------- advice ----------
    def _advise(self, text: str, x: dict, first: bool = False) -> str:
        calc, dcalc = self.calc(), self.defect_calc()
        entries, why = retrieve.retrieve(self.case, text, law_ids=x.get("law_ids"), cautions=self.cautions,
                                         escalations=self.escalations)
        self.last_retrieval = why
        self.log.append({"type": "retrieval", "ids": why})
        if not entries:
            return T("no_law", self.language) + "\n\n" + T("where_help", self.language) + "\n" + help_block(["off_topic"], self.language)
        _, unknown_refs = retrieve.lookup(text)
        notes = []
        if x.get("message_kind") == "hypothetical" and WHAT_IF_FIGURES.search(text):
            # only a what-if about amounts or dates ("what if I had paid 10 lakh?"); "what if the builder
            # blames covid?" is an ordinary question and is simply answered
            notes.append("The user asked a hypothetical. Do not recalculate; say you calculate only on their actual facts and ask whether this is a correction.")
        if unknown_refs:
            notes.append(f"The user named {', '.join(unknown_refs)}, which is NOT in the verified list. Say you haven't verified it.")
        if "force_majeure" in self.cautions:
            notes.append("The builder claims force majeure/pandemic/extension. Use [RERA-6-FM] honestly: whether the excuse counts is for TG-RERA to decide; suggest checking the TG-RERA portal for any extension granted.")
        overrides = self._draft_overrides()
        notes += overrides
        if self.escalations:
            notes.append(f"This case was flagged for a real lawyer ({', '.join(self.escalations)}). Do NOT tell them to file anything themselves; only help them understand and prepare for a lawyer/DLSA.")
        fixed = f"<law_index>\n{retrieve.law_index()}\n</law_index>\n\n"
        data = (f"<verified_law>\n{retrieve.format_for_prompt(entries)}\n</verified_law>\n\n"
                f"<case_file>\n{json.dumps(self.case.to_dict(), ensure_ascii=False)}\n</case_file>\n\n"
                f"<calculator>\n{json.dumps(calc.figures(), ensure_ascii=False, indent=1)}\n</calculator>\n\n"
                + (f"<defect_check>\n{json.dumps(dcalc.figures(), ensure_ascii=False, indent=1)}\n</defect_check>\n\n"
                   if "defects" in self.case.categories else "")
                + f"<notes>\n{chr(10).join(notes) or 'none'}\n</notes>")
        msgs = [{"role": "system", "content": _p("advisor.txt").format(language=self.language)},
                llm.user_message(fixed, data),
                {"role": "assistant", "content": "Understood. I will rely only on this data."}]
        if first:
            tmpl = "first_advice_defects.txt" if "defects" in self.case.categories else "first_advice.txt"
            tail = "\n\nFor THIS case, these points override the headings above:\n- " + "\n- ".join(overrides) if overrides else ""
            msgs.append({"role": "user", "content": wrap_user(text) + "\n\n" + _p(tmpl) + tail})
        else:
            msgs += self._history()
        self._step("writing")
        raw, finish = llm.chat_finish(msgs, temperature=0.2, task="advice", language=self.language)
        if finish == "length":
            self._step("rewriting")
            raw = self._retry_cut_off(msgs, raw)
        if first:
            self.assessed = True
        return self._guarded(raw, entries)

    def _draft_overrides(self) -> list:
        """What this tool will and won't prepare for this case, so the advice never offers a document the
        Drafts tab refuses. Worded as what the tool does, not as statements of law."""
        c, plan = self.case, self.draft_plan()
        window = []
        if "defects" in c.categories and self.defect_calc().within_window is False:
            window = ["By the dates given, the five-year period for defects ended before they were reported, so this tool does NOT "
                      "prepare a defect notice for this case. Do not offer to draft one; say the defects need a lawyer or free legal "
                      "aid (DLSA) to look at other routes."]
        return window + self._delay_overrides(c, plan)

    @staticmethod
    def _delay_overrides(c, plan) -> list:
        if plan["no_delay_yet"]:
            later = "" if c.possession_handed_over_date else " They can come back if the promised date passes without possession."
            return ["There is no delay to claim today, so this tool does NOT prepare a delay notice or a delay complaint for this case. "
                    "Do not offer to draft one, and do not tell them to send a legal notice or file a complaint about delay now. "
                    "Tell them what to keep ready (agreement, payment receipts, written updates from the builder)." + later]
        if plan["delay"] and c.possession_handed_over_date and c.promised_possession_date:
            return ["Possession has already been handed over, so do not describe it as pending. For the delay, this tool only works out "
                    "interest for the period from the promised date to the handover date (see <calculator>) and has no refund figures. "
                    "Do not list withdrawing or a refund as one of their choices; give the delay-interest figures, and add one line "
                    "that a lawyer can confirm whether anything else applies."]
        return []

    def _retry_cut_off(self, msgs: list, partial: str) -> str:
        """The model ran out of room mid-answer (its hidden reasoning shares the output budget): ask once
        more with twice the room. If that fails or is cut off too, keep the longer text and say so."""
        self.log.append({"type": "advice_cut_off"})
        try:
            again, finish = llm.chat_finish(msgs, temperature=0.2, task="advice", language=self.language,
                                            max_tokens=2 * llm.max_tokens_for("advice", self.language))
        except llm.LLMError:
            again, finish = "", "length"
        if finish != "length":
            return again
        self.log.append({"type": "advice_still_cut_off"})
        return max(partial, again, key=len) + "\n\n" + T("cut_short", self.language)

    def _guarded(self, text: str, entries: list, ground: bool = True) -> str:
        lang = self.language
        text = guardrails.split_tag_lists(text)
        # The model also sees the law INDEX; if it cites a verified entry from there, pull in that entry
        # so the tag is kept and its quotes/claims are checked against the real text (not just removed).
        have = {e["id"] for e in entries}
        extra = [retrieve.KB[i] for i in guardrails.cited_ids(text) if i in retrieve.KB and i not in have]
        if extra:
            entries = entries + extra
            self.log.append({"type": "index_tags_added", "ids": [e["id"] for e in extra]})
        clean, removed = guardrails.validate_citations(text, entries)
        clean, bad_quotes = guardrails.check_quotes(clean, entries, lang)
        clean, flagged = guardrails.mark_amounts(clean, self.allowed_amounts(), lang)
        facts = {k: v for k, v in self.case.to_dict().items() if v not in (None, [], "")}
        facts["delay"] = self.calc().figures()["delay"]
        if grounding.enabled() and ground and entries:
            self._step("checking")
        clean, report = grounding.check(clean, entries if ground else [], lang, self.allowed_amounts(), case_facts=facts)
        self.log.append({"type": "guard", "citations_removed": [r[0] for r in removed], "quotes_not_exact": len(bad_quotes),
                         "amounts_unverified": len(flagged), "grounding": {
                             "claims": len(report["claims"]), "unsupported": report["unsupported"], "error": report["error"]},
                         "grounding_claims": report["claims"]})
        ids = guardrails.cited_ids(clean)
        if ids:
            clean += "\n\n---\n" + T("sources_head", lang) + "\n" + retrieve.sources_block(ids)
        return clean

    # ---------- public ----------
    def handle(self, text: str) -> str:
        if text.strip().lower().strip(".!") in SAMPLE_TRIGGERS:
            if self.has_problem():
                self.messages += [{"role": "user", "content": text.strip()}, {"role": "assistant", "content": T("sample_busy", self.language)}]
                return self.messages[-1]["content"]
            self.log.append({"type": "sample_case"})
            text = SAMPLE_CASE
        clean, kinds = self.stored_text(text)
        if len(text) > MAX_USER_CHARS:
            reply = T("too_long", self.language, n=len(text), max=MAX_USER_CHARS)
            self.messages += [{"role": "user", "content": clean}, {"role": "assistant", "content": reply}]
            self.log.append({"type": "too_long", "chars": len(text)})
            if kinds:
                self.log.append({"type": "ids_removed", "kinds": kinds})
            return reply
        self.case.language = detect_language(clean, self.case.language if self.messages else None)
        self.messages.append({"role": "user", "content": clean})
        prefix = T("removed_ids", self.language, kinds=", ".join(kinds)) + "\n\n" if kinds else ""
        if kinds:
            self.log.append({"type": "ids_removed", "kinds": kinds})
        try:
            reply = prefix + self._handle(clean)
        except llm.LLMConfigError as e:
            self.log.append({"type": "error", "detail": f"LLMConfigError: {str(e)[:200]}"})
            reply = prefix + T("setup", self.language, detail=str(e))
        except (llm.LLMError, ValueError) as e:  # provider failure or unparseable model output; other errors are bugs and should surface
            self.log.append({"type": "error", "detail": f"{type(e).__name__}: {str(e)[:200]}"})
            reply = prefix + T("error", self.language)
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def _new_escalations(self, text: str) -> list:
        ids = guardrails.check_escalation(self.user_text(), self.case, self.flags,
                                          self.defect_calc() if "defects" in self.case.categories else None)
        lifted = [i for i in self.escalations if i in CASE_ESCALATIONS and i not in ids]
        if lifted:
            self.escalations = [i for i in self.escalations if i not in lifted]
            self.log.append({"type": "escalation_lifted", "ids": lifted})
        newly = [i for i in ids if i not in self.escalations]
        self.escalations += newly
        return newly

    def _first_advice(self, text: str, x: dict) -> str:
        """The structured first assessment. The stage moves on only if the model call succeeds, so a
        provider failure here is simply retried on the person's next message."""
        self.stage = "advised"
        try:
            return self._advise(text, x, first=True)
        except (llm.LLMError, ValueError):
            self.stage = "intake"
            raise

    def _next_step(self, text: str, x: dict, missing_before: list | None, progressed: bool) -> str:
        """Intake, after escalation checks: ask for what is missing, or give the first assessment."""
        if not self.has_problem():
            return self._tell_me_reply(text, x)
        self.idle = 0
        missing = self.case.missing_required()
        # a general question asked before any case fact is known is simply answered: it uses up no follow-up
        just_asking = self._asks_something(text, x) and not progressed and not any(getattr(self.case, f) for f in CORE_FACTS)
        if missing and (just_asking or self.followups < MAX_FOLLOWUPS):
            self.followups += 0 if just_asking else 1
            return self._ask_for_missing(text, x, missing_before, progressed)
        return self._first_advice(text, x)

    def _assume_state(self) -> None:
        """The welcome and the sidebar say this covers Telangana, so the state is not asked for. Once a
        builder problem is described with no place named, Telangana is assumed and listed as an assumption;
        a place outside Telangana, whenever it is named, still switches to the out-of-state reply."""
        if not self.case.state and self.has_problem():
            self.case.assume_telangana()
            self.log.append({"type": "state_assumed"})

    def _handle(self, text: str) -> str:
        for c in guardrails.check_cautions(text):
            if c not in self.cautions:
                self.cautions.append(c)

        if self.stage == "intake":
            missing_before = self.case.missing_required()
            before = self.case.to_dict()
            x = self._intake(text)
            if x.get("in_scope") is False and self._in_scope is not True and not self._small_talk(text, x) and not self._pointers_shown:
                # judged on THIS message, so a later greeting or unclear line is not called off-topic again;
                # the contacts are given once - after that the conversation simply continues
                self.log.append({"type": "off_topic"})
                self._pointers_shown = True
                return self._off_topic_reply()
            after = self.case.to_dict()   # what the person's message itself added (before any assumption by code)
            progressed = any(before[k] != after[k] for k in after if k != "language")
            self._assume_state()
            newly = self._new_escalations(text)
            if newly == ["out_of_state"]:
                self.stage = "advised"
                return self._central_law_reply()
            if newly:
                self.stage = "advised"
                return self._escalation_reply(newly)
            return self._next_step(text, x, missing_before, progressed)

        # advised stage: free Q&A. Re-extract only if the message may change a fact.
        prefix, x = "", {}
        if FACT_HINT.search(text) or not text.strip().endswith("?"):
            before = self.case.to_dict()
            x = self._intake(text)
            prefix = self._diff_note(before, self.case.to_dict())
        self._assume_state()
        newly = self._new_escalations(text)
        if newly:
            if newly == ["out_of_state"]:
                return prefix + self._central_law_reply()
            return prefix + self._escalation_reply(newly)
        if "out_of_state" in self.escalations:
            situation = [f"The flat is in {self.case.state}, outside Telangana, and they have already been told this tool covers Telangana "
                         "in detail only. Answer from the central Act entries in <verified_law> alone. Do not give Telangana's interest "
                         "rate, forms or portal as theirs, and do not offer to draft anything: their own state's RERA authority has its "
                         "own rules and forms. End by pointing them to that authority or a lawyer."]
            reply = self._chat_reply(text, x, situation, law=lambda e: e["act_key"] == "rera", pointers=["out_of_state"])
            return prefix + (reply or self._central_law_reply())
        if not self.assessed and not self.escalations:
            # whatever stopped the first assessment (e.g. a wrong state, since corrected) is gone:
            # pick the normal flow up again instead of answering without one
            self.stage = "intake"
            return prefix + self._next_step(text, x, None, bool(prefix))
        if not self.case.state:
            return prefix + self._central_law_reply()
        return prefix + self._advise(text, x)

    def case_summary_md(self) -> str:
        c = self.case
        calc = self.calc()
        rows = [
            ("Problem", ", ".join(c.categories) or None), ("Builder", c.builder_name), ("Project", c.project_name),
            ("Flat", c.flat_details), ("City / State", ", ".join(filter(None, [c.city, c.state]))),
            ("RERA no.", c.rera_number), ("Agreement date", c.agreement_date),
            ("Promised possession", c.promised_possession_date),
            ("Possession received", c.possession_handed_over_date),
            ("Total price", inr(c.total_price_rupees) if c.total_price_rupees else None),
            ("Paid so far", inr(c.amount_paid_rupees) if c.amount_paid_rupees else None),
            ("Delay", f"{calc.delay_days} days" if c.promised_possession_date else None),
            ("Defects", "; ".join(c.defects) or None), ("Defects reported on", c.defect_reported_date),
            ("Wants", c.goal), ("Builder's excuses / response", "; ".join(c.builder_excuses + ([c.builder_response] if c.builder_response else [])) or None),
            ("Proof they have", "; ".join(c.evidence) or None),
            ("Assumptions I made", "; ".join(c.assumptions) or None),
            ("Flagged for a lawyer", ", ".join(ESC_LABELS[i]["en"] for i in self.escalations) or None),
        ]
        out = "\n".join(f"- **{k}:** {v if v else '—'}" for k, v in rows)
        if c.timeline:
            out += "\n- **Timeline:**\n" + "\n".join(f"  - {t.get('date') or 'date not given'}: {t.get('event', '')}" for t in c.timeline)
        return out

    def download_md(self) -> str:
        """The user's own copy of their case (session memory is lost when the tab closes)."""
        parts = ["# My case summary (Griha Nyay)", f"_Prepared {date.today().isoformat()} by an AI assistant - not legal advice. Check every fact._", "",
                 self.case_summary_md(), "", "## Figures (calculated by code)", "```json",
                 json.dumps(self.calc().figures(), ensure_ascii=False, indent=1), "```"]
        if "defects" in self.case.categories:
            parts += ["## Defect window", "```json", json.dumps(self.defect_calc().figures(), ensure_ascii=False, indent=1), "```"]
        parts += ["## Free help", help_block(["advice", "off_topic"], "English")]
        return "\n".join(parts)
