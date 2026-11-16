"""Run every test case through the real engine and save raw, unedited outputs.

  python run_tests.py                 # all cases
  python run_tests.py 01 06           # only cases whose id starts with these
  MODEL=<other model> python run_tests.py   # same tests, different model

Writes outputs/<model-slug>/<case>.md and outputs/<model-slug>/summary.md
"""
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from core import drafts, llm, roleplay  # noqa: E402
from core.engine import Session  # noqa: E402

ROOT = Path(__file__).parent
TELUGU = re.compile(r"[ఀ-౿]")
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def run_case(path: Path, outdir: Path) -> dict:
    tc = json.loads(path.read_text())
    s = Session(as_of=date.fromisoformat(tc["as_of"]))
    t0 = time.time()
    lines = [f"# {tc['id']} — {tc['title']}", f"Model: `{llm.model_name()}` · as_of: {tc['as_of']}", ""]
    replies = []
    for turn in tc["turns"]:
        r = s.handle(turn)
        replies.append(r)
        lines += ["## 🧑 User", turn, "", "## 🤖 Griha Nyay", r, ""]

    exp, checks = tc["expect"], {}
    esc_ids = [i for i, _ in s.escalations]
    if exp.get("escalate"):
        checks["escalated_correctly"] = exp["escalate"] in esc_ids
    else:
        checks["no_false_escalation"] = not esc_ids
    if exp.get("reaches_advice"):
        checks["reached_advice"] = s.stage == "advised" and not esc_ids
    if exp.get("needs_followup"):
        checks["asked_followup"] = s.followups >= 1
    if exp.get("caution"):
        checks["caution_flagged"] = exp["caution"] in s.cautions
    if exp.get("language_hint") == "Telugu":
        checks["replied_in_telugu"] = bool(TELUGU.search(replies[-1]))
    if exp.get("language_hint") == "Hinglish":
        checks["replied_hindi_or_hinglish"] = "hinglish" in s.case.language.lower() or bool(DEVANAGARI.search(replies[-1])) or "aap" in replies[-1].lower()
    if exp.get("no_case_law"):
        checks["no_case_law_in_final"] = "SCC" not in replies[-1] and " v. " not in replies[-1]
    checks["no_llm_errors"] = not any(l["type"] == "error" for l in s.log)
    if exp.get("second_reply_must_not_ask") and len(replies) > 1:
        checks["no_reasking_known_info"] = exp["second_reply_must_not_ask"] not in replies[1].lower()
    if exp.get("final_reply_contains"):
        checks["final_reply_ok"] = exp["final_reply_contains"].lower() in replies[-1].lower()
    got = s.case.to_dict()
    for k, v in exp.get("fields", {}).items():
        checks[f"field_{k}"] = got.get(k) == v
    checks["no_duplicated_answer"] = all(r[: len(r) // 2].strip() != r[len(r) // 2 :].strip() for r in replies)

    # drafts + a short practice round for cases that reach advice
    if s.stage == "advised" and not esc_ids and "error" not in str(s.log):
        try:
            lines += ["## 📄 Generated legal notice", drafts.legal_notice(s), ""]
            pm = [{"role": "user", "content": "I want possession or my refund with interest. When will you hand over?"}]
            pm.append({"role": "assistant", "content": roleplay.builder_reply(s, pm)})
            lines += ["## 🥊 Practice round", f"**Buyer:** {pm[0]['content']}", f"**Builder rep:** {pm[1]['content']}", ""]
        except Exception as e:
            s.log.append({"type": "error", "detail": f"drafts/practice: {e}"})
            checks["no_llm_errors"] = False

    removed = [x for l in s.log if l["type"].startswith("citations_removed") for x in l["items"]]
    lines += [
        "## 🗂️ Case file (extracted)", "```json", json.dumps(s.case.to_dict(), ensure_ascii=False, indent=1), "```",
        "## 🧮 Calculator", "```json", json.dumps(s.calc().figures(), ensure_ascii=False, indent=1), "```",
        "## 🛡️ Guardrail log", f"- Escalations: {esc_ids or 'none'}", f"- Cautions: {s.cautions or 'none'}",
        f"- Citations/references removed by validator: {removed or 'none'}",
        f"- Other log: {[l for l in s.log if not l['type'].startswith('citations_removed')] or 'none'}",
        "## ✅ Checks", *[f"- {'PASS' if v else 'FAIL'} {k}" for k, v in checks.items()],
        f"\n_Time: {time.time() - t0:.1f}s_",
    ]
    (outdir / f"{tc['id']}.md").write_text("\n".join(lines))
    return {"id": tc["id"], "title": tc["title"], "checks": checks, "removed": len(removed)}


def main():
    filters = sys.argv[1:]
    slug = re.sub(r"[^\w.-]+", "_", llm.model_name())
    outdir = ROOT / "outputs" / slug
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    for p in sorted((ROOT / "tests" / "cases").glob("*.json")):
        if filters and not any(p.stem.startswith(f) for f in filters):
            continue
        print("running", p.stem, flush=True)
        results.append(run_case(p, outdir))
    total = sum(len(r["checks"]) for r in results)
    passed = sum(v for r in results for v in r["checks"].values())
    summ = [f"# Test summary — `{llm.model_name()}`", f"**{passed}/{total} checks passed**", "",
            "| Case | Checks | Refs removed by validator |", "|---|---|---|"]
    for r in results:
        cs = ", ".join(f"{'✅' if v else '❌'} {k}" for k, v in r["checks"].items())
        summ.append(f"| {r['id']} {r['title']} | {cs} | {r['removed']} |")
    (outdir / "summary.md").write_text("\n".join(summ))
    print("\n".join(summ))


if __name__ == "__main__":
    main()
