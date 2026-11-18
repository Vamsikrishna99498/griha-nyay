"""Run test cases through the real engine and real model; save raw, unedited outputs.

  python run_tests.py                       # all cases in tests/cases/
  python run_tests.py 01 06                 # only cases whose id starts with these
  python run_tests.py --text "my story" --text "a follow-up"     # a NEW input (e.g. in the interview)
  MODEL=<other model> python run_tests.py   # same tests, different model (or set LLM_PROVIDERS)

Writes outputs/<model-slug>/<case>.md, results.json (accumulates across runs) and summary.md.
Each file is stamped with the git commit, the model(s) that actually answered, and the date.
"""
import json
import re
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

from core import drafts, guardrails, llm, roleplay
from core.engine import Session

load_dotenv()

ROOT = Path(__file__).parent
TELUGU = re.compile(r"[ఀ-౿]")
DEVANAGARI = re.compile(r"[ऀ-ॿ]")
MIN_GAP_S = 4.5            # pacing: at most ~13 calls/minute
PRACTICE_CASES = {"01_clean_refund", "13_defects_hindi"}

_real_complete = llm.complete
_last = [0.0]
outbound: list = []        # every message sent to a model in the current case (kept in memory only)


def _paced_complete(messages, **kw):
    gap = time.time() - _last[0]
    if gap < MIN_GAP_S:
        time.sleep(MIN_GAP_S - gap)
    outbound.append(" ".join(str(m.get("content")) for m in messages))
    try:
        return _real_complete(messages, **kw)
    finally:
        _last[0] = time.time()


llm.complete = _paced_complete


def stamp() -> str:
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", "core", "prompts", "knowledge", "templates"],
                               capture_output=True, text=True, cwd=ROOT).stdout.strip()
        return (h + ("+uncommitted" if dirty else "")) or "not a git checkout"
    except OSError:
        return "unknown"


def used_models(start: int) -> str:
    seen = []
    for c in llm.call_log[start:]:
        x = f"{c['provider']}:{c['model']}"
        if x not in seen:
            seen.append(x)
    return ", ".join(seen) or "none (no model call)"


def _total(start: int, field: str):
    seen = [c[field] for c in llm.call_log[start:] if c.get(field) is not None]
    return sum(seen) if seen else None


def token_counts(start: int) -> tuple:
    """(input tokens, cached input tokens) over this case's calls; None where no call reported the number."""
    return _total(start, "prompt_tokens"), _total(start, "cached_tokens")


def output_note(start: int) -> str:
    out, thinking = _total(start, "completion_tokens"), _total(start, "reasoning_tokens")
    if out is None:
        return "output tokens not reported"
    return f"{out} output tokens" + ("" if thinking is None else f" ({thinking} hidden reasoning)")


def cached_note(sent, cached) -> str:
    if sent is None:
        return "tokens not reported"
    return f"{sent} input tokens ({'cached not reported' if cached is None else f'{cached} from cache'})"


def transcript(s: Session, turns: list, replies: list) -> list:
    lines = []
    for t, r in zip(turns, replies):
        lines += ["## 🧑 User", t, "", "## 🤖 Griha Nyay", r, ""]
    return lines


def appendix(s: Session) -> list:
    guards = [x for x in s.log if x["type"] == "guard"]
    note = (["## 📝 Case note (first aid - a problem outside the verified law)", "```json",
             json.dumps(s.general.to_dict(), ensure_ascii=False, indent=1), "```"] if s.mode == "general" else [])
    lines = note + ["## 🗂️ Case file (extracted)", "```json", json.dumps(s.case.to_dict(), ensure_ascii=False, indent=1), "```",
             "## 🧮 Calculator", "```json", json.dumps(s.calc().figures(), ensure_ascii=False, indent=1), "```"]
    if "defects" in s.case.categories:
        lines += ["## 🔧 Defect window", "```json", json.dumps(s.defect_calc().figures(), ensure_ascii=False, indent=1), "```"]
    lines += ["## 🛡️ Guardrail log", f"- Escalations: {s.escalations or 'none'}", f"- Cautions: {s.cautions or 'none'}",
              f"- Retrieval (id: why): {[x['ids'] for x in s.log if x['type'] == 'retrieval'] or 'none'}"]
    for g in guards:
        lines.append(f"- Answer check: citations removed {g['citations_removed'] or 'none'}; quotes not exact: {g['quotes_not_exact']}; "
                     f"amounts unverified: {g['amounts_unverified']}; grounding: {g['grounding']}")
        for c in g.get("grounding_claims", []):
            lines.append(f"  - [{c['verdict']}] {c['claim']} ({c['tag'] or 'no tag'})")
    other = [x for x in s.log if x["type"] not in ("guard", "retrieval")]
    lines.append(f"- Other log: {other or 'none'}")
    return lines


def run_case(tc: dict, outdir: Path) -> dict:
    outbound.clear()
    start = len(llm.call_log)
    s = Session(as_of=date.fromisoformat(tc.get("as_of", date.today().isoformat())))
    t0 = time.time()
    replies = [s.handle(turn) for turn in tc["turns"]]
    lines = [f"# {tc['id']} — {tc['title']}", ""]
    lines += transcript(s, tc["turns"], replies)

    exp, checks = tc.get("expect", {}), {}
    if exp:
        if exp.get("escalate"):
            checks["escalated_correctly"] = exp["escalate"] in s.escalations
        elif "escalate" in exp:
            checks["no_false_escalation"] = not s.escalations
        if exp.get("reaches_advice"):
            checks["reached_advice"] = s.stage == "advised" and not s.escalations
        if exp.get("needs_followup"):
            checks["asked_followup"] = s.followups >= 1
        if exp.get("caution"):
            checks["caution_flagged"] = exp["caution"] in s.cautions
        lh = exp.get("language_hint")
        if lh == "Telugu":
            checks["replied_in_telugu"] = bool(TELUGU.search(replies[-1]))
        elif lh == "Hindi":
            checks["replied_in_hindi"] = bool(DEVANAGARI.search(replies[-1]))
        elif lh == "Hinglish":
            checks["hinglish_detected"] = s.case.language in ("Hinglish", "Hindi")
        if exp.get("no_case_law"):
            checks["no_case_law_in_final"] = not re.search(r"SCC| v\. | vs\.? |versus", replies[-1])
        if exp.get("second_reply_must_not_ask") and len(replies) > 1:
            checks["no_reasking_known_info"] = exp["second_reply_must_not_ask"] not in replies[1].lower()
        if exp.get("final_reply_contains"):
            checks["final_reply_ok"] = exp["final_reply_contains"].lower() in replies[-1].lower()
        for bad in exp.get("final_reply_must_not_contain", []):
            checks[f"not_in_reply:{bad}"] = bad.lower() not in replies[-1].lower()
        for i, wanted in exp.get("reply_contains", {}).items():           # {"0": "text" or ["a", "b"]}: by turn number
            for w in [wanted] if isinstance(wanted, str) else wanted:
                checks[f"reply{i}_has:{w}"] = int(i) < len(replies) and w.lower() in replies[int(i)].lower()
        for i, banned in exp.get("reply_must_not_contain", {}).items():
            for b in [banned] if isinstance(banned, str) else banned:
                checks[f"reply{i}_lacks:{b}"] = int(i) < len(replies) and b.lower() not in replies[int(i)].lower()
        if exp.get("first_aid"):
            checks["first_aid_mode"] = s.mode == "general" and not s.drafts_allowed()
        if exp.get("general_category"):
            checks["general_category"] = s.general.category == exp["general_category"]
        got = s.case.to_dict()
        for k, v in exp.get("fields", {}).items():
            checks[f"field_{k}"] = got.get(k) == v
        if exp.get("category"):
            checks["category"] = sorted(s.case.categories) == sorted(exp["category"])
        if exp.get("category_includes"):
            checks["categories_include"] = set(exp["category_includes"]) <= set(s.case.categories)
        if exp.get("defect_drafts_blocked"):
            checks["defect_drafts_blocked"] = not s.defect_drafts_allowed()
        if exp.get("delay_notice_blocked"):
            checks["delay_notice_blocked"] = not s.draft_plan()["notice"]
        for k, v in exp.get("calc", {}).items():
            checks[f"calc_{k}"] = getattr(s.calc(), k) == v
        if exp.get("pii_not_sent"):
            sent = " ".join(outbound)
            checks["pii_not_sent_to_model"] = all(x not in sent for x in exp["pii_not_sent"])
    checks["no_llm_errors"] = not any(x["type"] == "error" for x in s.log)
    checks["no_cut_off_reply"] = not any(x["type"] == "advice_still_cut_off" for x in s.log)
    checks["no_internal_names"] = not any(guardrails.leaked_names(r) for r in replies)
    checks["no_duplicated_answer"] = all(r[: len(r) // 2].strip() != r[len(r) // 2:].strip() for r in replies)

    # drafts are made by code (no model call); a short practice round only on two cases to save quota
    if s.drafts_allowed():
        s.party = {"name": "[Test Buyer]", "address": "[Test address]"}
        plan = s.draft_plan()
        if plan["notice"]:
            lines += ["## 📄 Generated legal notice (code-built)", drafts.legal_notice(s), ""]
        elif plan["needs_choice"]:
            lines += ["## 📄 Legal notice not generated", "The buyer has not said whether they want a refund or the flat; the Drafts tab asks them to choose first.", ""]
        elif plan["no_delay_yet"]:
            lines += ["## 📄 Legal notice not generated", "There is no delay to claim: the promised date has not passed, or possession was given by then.", ""]
        if plan["defect_notice"]:
            lines += ["## 📄 Generated defect notice (code-built)", drafts.defect_notice(s), ""]
        if tc["id"] in PRACTICE_CASES:
            try:
                pm = [{"role": "user", "content": "I want my rights under RERA. When will you fix this?"}]
                pm.append({"role": "assistant", "content": roleplay.builder_reply(s, pm)})
                lines += ["## 🥊 Practice round", f"**Buyer:** {pm[0]['content']}", f"**Builder rep:** {pm[1]['content']}", ""]
            except (llm.LLMError, roleplay.NoCaseYet) as e:
                s.log.append({"type": "error", "detail": f"practice: {type(e).__name__}"})
                checks["no_llm_errors"] = False

    lines += appendix(s)
    lines += ["## ✅ Checks", *[f"- {'PASS' if v else 'FAIL'} {k}" for k, v in checks.items()]]
    models = used_models(start)
    sent, cached = token_counts(start)
    lines[1:1] = [f"Commit `{stamp()}` · run {datetime.now().strftime('%Y-%m-%d %H:%M')} · as_of {s.as_of} · "
                  f"answered by: `{models}` · {len(llm.call_log) - start} model calls · {cached_note(sent, cached)} · {output_note(start)} · {time.time() - t0:.0f}s", ""]
    (outdir / f"{tc['id']}.md").write_text("\n".join(lines))
    g = [x["grounding"] for x in s.log if x["type"] == "guard"]
    return {"id": tc["id"], "title": tc["title"], "checks": checks, "models": models, "commit": stamp(),
            "calls": len(llm.call_log) - start, "prompt_tokens": sent, "cached_tokens": cached,
            "removed": sum(len(x["citations_removed"]) for x in s.log if x["type"] == "guard"),
            "unsupported": sum(x["unsupported"] for x in g)}


def write_summary(outdir: Path, results: dict) -> str:
    total = sum(len(r["checks"]) for r in results.values())
    passed = sum(v for r in results.values() for v in r["checks"].values())
    lines = [f"# Test summary — `{outdir.name}`", f"**{passed}/{total} checks passed** across {len(results)} cases", "",
             "| Case | Checks | Refs removed | Grounding flags | Calls | Input tokens | Answered by | Commit |", "|---|---|---|---|---|---|---|---|"]
    for cid in sorted(results):
        r = results[cid]
        cs = ", ".join(f"{'✅' if v else '❌'} {k}" for k, v in r["checks"].items())
        lines.append(f"| {cid} {r['title']} | {cs} | {r['removed']} | {r['unsupported']} | {r['calls']} | {cached_note(r.get('prompt_tokens'), r.get('cached_tokens'))} | {r['models']} | {r['commit']} |")
    (outdir / "summary.md").write_text("\n".join(lines) + "\n")
    return "\n".join(lines)


def main():
    problems = llm.config_problems()
    if problems:
        sys.exit("The AI model is not set up: " + "; ".join(problems) + ". See .env.example.")
    args = sys.argv[1:]
    texts = [args[i + 1] for i, a in enumerate(args) if a == "--text" and i + 1 < len(args)]
    filters = [a for i, a in enumerate(args) if a != "--text" and (i == 0 or args[i - 1] != "--text")]
    first = next((p for p in llm.providers() if p["model"]), {"model": "model"})
    slug = re.sub(r"[^\w.-]+", "_", first["model"])
    outdir = ROOT / "outputs" / slug
    outdir.mkdir(parents=True, exist_ok=True)
    if texts:
        tc = {"id": f"live_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "title": "New input", "turns": texts}
        r = run_case(tc, outdir)
        print((outdir / f"{tc['id']}.md").read_text())
        print(f"\nsaved: outputs/{slug}/{tc['id']}.md ({r['calls']} model calls)")
        return
    res_path = outdir / "results.json"
    results = json.loads(res_path.read_text()) if res_path.exists() else {}
    for p in sorted((ROOT / "tests" / "cases").glob("*.json")):
        if filters and not any(p.stem.startswith(f) for f in filters):
            continue
        print("running", p.stem, flush=True)
        results[p.stem] = run_case(json.loads(p.read_text()), outdir)
        res_path.write_text(json.dumps(results, ensure_ascii=False, indent=1))
    print(write_summary(outdir, results))


if __name__ == "__main__":
    main()
