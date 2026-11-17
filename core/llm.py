"""The only place that talks to a model. Swap models/providers with env vars only.

Single provider (simplest):
  MODEL       model id (default: a free OpenRouter model)
  LLM_API_KEY key (falls back to OPENROUTER_API_KEY)
  BASE_URL    any OpenAI-compatible endpoint (default: OpenRouter)

Fallback chain (several free providers, tried in order on rate-limit / outage):
  LLM_PROVIDERS=openrouter,gemini,groq
  OPENROUTER_BASE_URL / OPENROUTER_API_KEY / OPENROUTER_MODEL
  GEMINI_BASE_URL     / GEMINI_API_KEY     / GEMINI_MODEL      ... one triple per name

Keys are read with os.getenv only; they are never printed, logged or put in error messages.
"""
from __future__ import annotations

import json
import os
import re
import time

from openai import OpenAI, OpenAIError

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "nvidia/nemotron-3.5-super-vl:free"

# output budgets per task (tokens), scaled up for scripts that cost more tokens per word
BUDGET = {"intake": 2500, "advice": 3000, "chat": 1000, "coach": 1500, "roleplay": 400, "grounding": 1500, "transcribe": 600}
# reasoning ("thinking") is only useful for free-form advice; structured JSON tasks run with it off,
# otherwise reasoning models can spend the whole budget thinking and return nothing
REASONING = {"intake": "off", "grounding": "off", "roleplay": "off", "chat": "off"}   # short conversational turns must be quick
LANG_FACTOR = {"English": 1.0, "Hinglish": 1.3, "Tenglish": 1.3, "Hindi": 2.5, "Telugu": 3.5}
TIMEOUT_S = 150          # per model call; free tiers can take a minute or more

# Request settings a model turned down, remembered per (endpoint, model) so later calls skip the failed try.
# Some reasoning models accept only "max_completion_tokens" and only their default temperature.
_quirks: dict = {}

last_call: dict = {}     # provider/model/finish/token counts of the latest call (names only, never keys)
call_log: list = []      # same, for every call in this process (used by run_tests stamps)


class LLMError(RuntimeError):
    pass


class LLMConfigError(LLMError):
    """No provider can be called at all (missing key/model, or a blocked paid model)."""


def user_message(fixed: str, changing: str) -> dict:
    """A user message whose text that is identical on every call comes first, so providers can cache it.
    'cache_chars' marks where that text ends; complete() removes the key before anything is sent."""
    return {"role": "user", "content": fixed + changing, "cache_chars": len(fixed)}


def max_tokens_for(task: str, language: str | None = "English") -> int:
    return int(BUDGET.get(task, 1000) * LANG_FACTOR.get(language or "English", 1.0))


def estimate_tokens(text: str) -> int:
    """Rough: ~4 ASCII chars per token; Indic scripts ~1 token per character."""
    ascii_n = sum(1 for ch in text if ord(ch) < 128)
    return ascii_n // 4 + (len(text) - ascii_n)


def providers() -> list[dict]:
    names = [n.strip() for n in os.getenv("LLM_PROVIDERS", "").split(",") if n.strip()]
    out = []
    for n in names:
        u = n.upper()
        is_or = n.lower().startswith("openrouter")  # openrouter, openrouter2, ... (several keys)
        out.append({"name": n, "base_url": os.getenv(f"{u}_BASE_URL", DEFAULT_BASE_URL if is_or else ""),
                    "key_env": f"{u}_API_KEY",
                    # OpenRouter without an explicit model falls back to MODEL / the default free model
                    "model": os.getenv(f"{u}_MODEL", os.getenv("MODEL", DEFAULT_MODEL) if is_or else "")})
    if not out:
        out.append({"name": "default", "base_url": os.getenv("BASE_URL", DEFAULT_BASE_URL),
                    "key_env": "LLM_API_KEY" if os.getenv("LLM_API_KEY") else "OPENROUTER_API_KEY",
                    "model": os.getenv("MODEL", DEFAULT_MODEL)})
    return out


def describe_providers() -> list[dict]:
    """Safe diagnostics: names, endpoints, models, and only WHETHER a key is set - never the key."""
    return [{"name": p["name"], "base_url": p["base_url"], "model": p["model"] or "(missing)",
             "key_set": bool(os.getenv(p["key_env"])), "key_var": p["key_env"],
             "free_guard": ("ok" if p["model"].endswith(":free") else "BLOCKED unless ALLOW_PAID=1")
             if "openrouter.ai" in p["base_url"] else "n/a (not OpenRouter)"} for p in providers()]


def list_models(name: str, contains: str = "") -> list[str]:
    """Safe diagnostics: model ids a configured provider offers (ids only, never the key)."""
    p = next(x for x in providers() if x["name"] == name)
    client = OpenAI(base_url=p["base_url"], api_key=os.getenv(p["key_env"]) or "", timeout=30, max_retries=0)
    try:
        return sorted(m.id for m in client.models.list() if contains in m.id)
    except OpenAIError as e:
        raise LLMError(f"{name}: cannot list models: {type(e).__name__} {_safe(str(e))}") from None


def ping(name: str, model: str | None = None, max_tokens: int = 20, reasoning: str | None = None) -> str:
    """Safe diagnostics: one tiny request to a configured provider. Returns 'ok: ...' or the error type."""
    p = next(x for x in providers() if x["name"] == name)
    client = OpenAI(base_url=p["base_url"], api_key=os.getenv(p["key_env"]) or "", timeout=60, max_retries=0)
    extra = _reasoning_args(p, reasoning) if reasoning else None
    try:
        r = client.chat.completions.create(model=model or p["model"], max_tokens=max_tokens, temperature=0,
                                           messages=[{"role": "user", "content": "Reply with the word OK."}], extra_body=extra)
    except (OpenAIError, json.JSONDecodeError) as e:
        return f"{type(e).__name__} {_status(e)}: {_safe(str(e))[:200]}"
    text, finish = _reply_text(r)
    return f"ok: {text[:20]!r} finish={finish} tokens={getattr(getattr(r, 'usage', None), 'completion_tokens', None)}"


def model_name() -> str:
    p = providers()
    return ", ".join(f"{x['name']}:{x['model']}" for x in p) if len(p) > 1 else p[0]["model"]


def _paid_blocked(p: dict) -> bool:
    """Cost guard: on OpenRouter only ':free' models run unless ALLOW_PAID=1."""
    return "openrouter.ai" in p["base_url"] and not p["model"].endswith(":free") and os.getenv("ALLOW_PAID") != "1"


def config_problems() -> list[str]:
    """Why no provider can be called, in words safe to show (variable names and model ids only,
    never key values). Empty if at least one provider is usable."""
    problems = []
    for p in providers():
        if not os.getenv(p["key_env"]):
            names = "LLM_API_KEY (or OPENROUTER_API_KEY)" if p["name"] == "default" else p["key_env"]
            problems.append(f"no API key - set {names}")
        elif not p["model"] or not p["base_url"]:
            u = p["name"].upper()
            problems.append(f"{p['name']}: set {u}_MODEL and {u}_BASE_URL")
        elif _paid_blocked(p):
            problems.append(f"'{p['model']}' is a paid OpenRouter model - set ALLOW_PAID=1 to allow it, or use a model id ending in ':free'")
        else:
            return []
    return problems


def _safe(msg: str) -> str:
    """Strip anything key-like from an error message before it is logged or shown."""
    for p in providers():
        k = os.getenv(p["key_env"]) or ""
        if k:
            msg = msg.replace(k, "***")
    return re.sub(r"(sk|gsk|AIza|csk)[-_A-Za-z0-9]{12,}", "***", msg)[:300]


def _reasoning_args(p: dict, reasoning: str) -> dict | None:
    """Turn 'thinking' down per provider, so reasoning models don't spend the whole budget thinking.
    OpenRouter: reasoning.enabled/effort. Gemini's OpenAI-compatible API: reasoning_effort."""
    if "openrouter.ai" in p["base_url"]:
        return {"reasoning": {"enabled": False} if reasoning == "off" else {"effort": reasoning}}
    if "generativelanguage.googleapis.com" in p["base_url"]:
        return {"reasoning_effort": "low" if reasoning == "off" else reasoning}
    return None


def _reply_text(resp) -> tuple[str, str]:
    """(text, finish_reason) of a chat reply; ("", "malformed") when a provider sends an unexpected shape."""
    try:
        ch = resp.choices[0] if resp.choices else None
        text = ((ch.message.content if ch and ch.message else None) or "").strip()
        return text, (ch.finish_reason if ch else None) or "stop"
    except (AttributeError, IndexError, TypeError):
        return "", "malformed"


def _cache_markers(p: dict) -> bool:
    """Explicit cache breakpoints, only for the one documented case that needs them (Anthropic models on
    OpenRouter) and only when switched on: this request shape has not been run against a live model."""
    return (os.getenv("PROMPT_CACHE_MARKERS") == "1" and "openrouter.ai" in p["base_url"]
            and p["model"].lstrip("~").startswith("anthropic/"))


def _api_messages(messages: list, p: dict) -> list:
    out = []
    for m in messages:
        body = {k: v for k, v in m.items() if k != "cache_chars"}
        n, text = m.get("cache_chars"), m.get("content")
        if _cache_markers(p) and isinstance(n, int) and isinstance(text, str) and 0 < n < len(text):
            body["content"] = [{"type": "text", "text": text[:n], "cache_control": {"type": "ephemeral"}},
                               {"type": "text", "text": text[n:]}]
        out.append(body)
    return out


def _count(v) -> int | None:
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else None


def _usage(resp) -> dict:
    """Token counts as the provider reports them (None where it doesn't): input, input served from its
    prompt cache, output, and the part of the output spent on hidden reasoning."""
    usage = getattr(resp, "usage", None)
    details = getattr(usage, "prompt_tokens_details", None)
    cached = details.get("cached_tokens") if isinstance(details, dict) else getattr(details, "cached_tokens", None)
    out_details = getattr(usage, "completion_tokens_details", None)
    thinking = (out_details.get("reasoning_tokens") if isinstance(out_details, dict)
                else getattr(out_details, "reasoning_tokens", None))
    return {"prompt_tokens": _count(getattr(usage, "prompt_tokens", None)), "cached_tokens": _count(cached),
            "completion_tokens": _count(getattr(usage, "completion_tokens", None)), "reasoning_tokens": _count(thinking)}


def _request_args(p: dict, temperature: float, budget: int) -> dict:
    q = _quirks.get((p["base_url"], p["model"]), set())
    args = {"max_completion_tokens" if "completion_tokens" in q else "max_tokens": budget}
    if "no_temperature" not in q:
        args["temperature"] = temperature
    return args


def _learn_quirk(p: dict, error_text: str) -> bool:
    """True if a 400 was about a request setting this model does not take and we can send it differently."""
    q = _quirks.setdefault((p["base_url"], p["model"]), set())
    msg = error_text.lower()
    if "max_tokens" in msg and "completion_tokens" not in q:
        q.add("completion_tokens")
        return True
    if "temperature" in msg and "no_temperature" not in q:
        q.add("no_temperature")
        return True
    return False


def _status(e: Exception) -> int | None:
    return getattr(e, "status_code", None) or getattr(getattr(e, "response", None), "status_code", None)


def complete(messages, *, temperature: float, max_tokens: int, rounds: int = 2, reasoning: str = "low",
             timeout: float = TIMEOUT_S) -> tuple[str, str]:
    """Try each provider in order. Returns (text, finish_reason). Falls through to the next provider
    on rate limits, outages, timeouts, auth/model errors. A 400 about max_tokens or temperature is retried
    with the setting that model takes (see _quirks); any other 400 (our bad request) is raised at once."""
    problems = config_problems()
    if problems:
        raise LLMConfigError("; ".join(problems))
    errors = []
    for rnd in range(rounds):
        for p in providers():
            key = os.getenv(p["key_env"])
            if not key or not p["model"] or not p["base_url"]:
                errors.append(f"{p['name']}: not configured")
                continue
            if _paid_blocked(p):
                errors.append(f"{p['name']}: blocked paid model '{p['model']}' (use a ':free' id or ALLOW_PAID=1)")
                continue
            client = OpenAI(base_url=p["base_url"], api_key=key, timeout=timeout, max_retries=0)  # free tiers can be slow
            budget = max_tokens
            sent = _api_messages(messages, p)
            doubled = False
            while True:  # repeated only for a setting the model refused, or once for 'cut off with no text'
                extra = _reasoning_args(p, reasoning)
                try:
                    resp = client.chat.completions.create(model=p["model"], messages=sent, extra_body=extra,
                                                          **_request_args(p, temperature, budget))
                except (OpenAIError, json.JSONDecodeError) as e:
                    st = _status(e)
                    errors.append(f"{p['name']}: {type(e).__name__} {st or ''} {_safe(str(e))}")
                    if st == 400 and _learn_quirk(p, str(e)):
                        continue  # same request, with the setting this model wants (at most twice per model)
                    if st == 400:
                        raise LLMError(f"bad request to {p['name']}: {_safe(str(e))}") from None
                    break  # 429/5xx/timeout/auth -> next provider
                text, finish = _reply_text(resp)
                if not text and finish == "length" and not doubled:
                    doubled = True
                    budget *= 2  # a reasoning model spent the whole budget thinking
                    continue
                if not text:
                    used = getattr(getattr(resp, "usage", None), "completion_tokens", None)
                    errors.append(f"{p['name']}: empty response (finish={finish}, completion_tokens={used}, budget={budget})")
                    break
                meta = {"provider": p["name"], "model": p["model"], "finish": finish, **_usage(resp)}
                last_call.clear()
                last_call.update(meta)
                call_log.append(meta)
                return _dedupe(text), finish
        if rnd < rounds - 1:
            time.sleep(8 * (rnd + 1))  # every provider busy: short wait, then one more round
    raise LLMError("all providers failed: " + " | ".join(errors[-6:]))


def chat_finish(messages, temperature: float = 0.2, max_tokens: int | None = None, task: str = "advice",
                language: str | None = "English", rounds: int = 2, timeout: float = TIMEOUT_S) -> tuple[str, str]:
    """(text, finish_reason); finish_reason is "length" when the model ran out of room mid-answer."""
    return complete(messages, temperature=temperature, max_tokens=max_tokens or max_tokens_for(task, language),
                    reasoning=REASONING.get(task, "low"), rounds=rounds, timeout=timeout)


def chat(messages, temperature: float = 0.2, max_tokens: int | None = None, task: str = "advice",
         language: str | None = "English") -> str:
    return chat_finish(messages, temperature, max_tokens, task, language)[0]


def _dedupe(text: str) -> str:
    """Some free models emit their whole answer twice back-to-back; keep one copy."""
    n = len(text)
    for cut in range(n // 2 - 5, n // 2 + 6):
        if 0 < cut < n:
            a, b = text[:cut].strip(), text[cut:].strip()
            if a and a == b:
                return a
    return text


def parse_json(text: str) -> dict:
    """Models often wrap JSON in prose or ```json fences; pull out the first object."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, depth, in_str, esc = text.find("{"), 0, False, False
    if start == -1:
        raise ValueError("no JSON object in model output")
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            esc = (c == "\\") and not esc
            if c == '"' and not esc:
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start: i + 1])
    raise ValueError("unbalanced JSON in model output")


def chat_json(messages, temperature: float = 0.0, max_tokens: int | None = None, task: str = "intake",
              language: str | None = "English", rounds: int = 2) -> dict:
    """Ask for JSON; if the reply is cut off or doesn't parse, ask once more."""
    budget = max_tokens or max_tokens_for(task, language)
    mode = REASONING.get(task, "low")
    out, finish = complete(messages, temperature=temperature, max_tokens=budget, rounds=rounds, reasoning=mode)
    try:
        return parse_json(out)
    except (ValueError, json.JSONDecodeError) as e:
        if finish == "length":
            # cut off mid-JSON: repeating the same request with room to finish beats asking for a repair
            out2, _ = complete(messages, temperature=temperature, max_tokens=budget * 2, rounds=rounds, reasoning=mode)
            return parse_json(out2)
        fix = messages + [
            {"role": "assistant", "content": out[:4000]},
            {"role": "user", "content": f"That was not valid JSON ({str(e)[:80]}). Reply with ONLY the complete JSON object, shorter if needed."},
        ]
        out2, _ = complete(fix, temperature=0.0, max_tokens=budget * (2 if finish == "length" else 1), rounds=rounds, reasoning=mode)
        return parse_json(out2)


def transcribe(audio_bytes: bytes, fmt: str = "wav") -> str:
    """Optional voice input (off unless VOICE_MODEL is set). Not used in the current build."""
    import base64
    voice_model = os.getenv("VOICE_MODEL")
    if not voice_model:
        raise LLMError("Voice is off: set VOICE_MODEL to an audio-capable model id.")
    p = providers()[0]
    client = OpenAI(base_url=p["base_url"], api_key=os.getenv(p["key_env"]) or "", timeout=90)
    b64 = base64.b64encode(audio_bytes).decode()
    resp = client.chat.completions.create(model=voice_model, temperature=0.0, max_tokens=BUDGET["transcribe"], messages=[{
        "role": "user", "content": [
            {"type": "text", "text": "Transcribe this audio exactly, in the language spoken. Output only the transcript."},
            {"type": "input_audio", "input_audio": {"data": b64, "format": fmt}}]}])
    return (resp.choices[0].message.content or "").strip()
