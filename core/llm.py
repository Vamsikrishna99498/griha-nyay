"""Single place that talks to the LLM. Swap models/providers with env vars only.

  MODEL         any model id on the endpoint (default: a free OpenRouter model)
  LLM_API_KEY   API key (falls back to OPENROUTER_API_KEY)
  BASE_URL      any OpenAI-compatible endpoint (default: OpenRouter)
"""
import json
import os
import re
import time

from openai import OpenAI

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "nvidia/nemotron-3.5-super-vl:free"


def model_name() -> str:
    return os.getenv("MODEL", DEFAULT_MODEL)


def _guard_free(model: str) -> None:
    """Cost guard: on OpenRouter, refuse any model that isn't a ':free' variant
    unless ALLOW_PAID=1 is set explicitly. Free models are never billed."""
    on_openrouter = "openrouter.ai" in os.getenv("BASE_URL", DEFAULT_BASE_URL)
    if on_openrouter and not model.endswith(":free") and os.getenv("ALLOW_PAID") != "1":
        raise RuntimeError(
            f"Blocked paid model '{model}'. Use a ':free' model id (or set ALLOW_PAID=1 to allow paid)."
        )


def _client() -> OpenAI:
    key = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError(
            "No API key. Set OPENROUTER_API_KEY (or LLM_API_KEY + BASE_URL) in .env or Streamlit secrets."
        )
    return OpenAI(base_url=os.getenv("BASE_URL", DEFAULT_BASE_URL), api_key=key)


def chat(messages, temperature: float = 0.2, model: str | None = None, retries: int = 3) -> str:
    """Plain chat completion with simple retry/backoff (free tiers rate-limit often)."""
    _guard_free(model or model_name())
    client = _client()
    last_err = None
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model or model_name(),
                messages=messages,
                temperature=temperature,
            )
            content = resp.choices[0].message.content or ""
            if content.strip():
                return _dedupe(content.strip())
            last_err = RuntimeError("empty response")
        except Exception as e:  # network, 429, provider errors
            last_err = e
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"LLM call failed after {retries} tries: {last_err}")


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
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, depth = text.find("{"), 0
    if start == -1:
        raise ValueError("no JSON object in model output")
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("unbalanced JSON in model output")


def chat_json(messages, temperature: float = 0.0, model: str | None = None) -> dict:
    """Ask for JSON; if the reply doesn't parse, ask once more with the error."""
    out = chat(messages, temperature=temperature, model=model)
    try:
        return parse_json(out)
    except (ValueError, json.JSONDecodeError) as e:
        fix = messages + [
            {"role": "assistant", "content": out},
            {"role": "user", "content": f"That was not valid JSON ({e}). Reply with ONLY the JSON object."},
        ]
        return parse_json(chat(fix, temperature=0.0, model=model))


def transcribe(audio_bytes: bytes, fmt: str = "wav") -> str:
    """Optional voice input. Needs VOICE_MODEL set to an audio-capable model on the endpoint
    (e.g. a Gemini model on OpenRouter). Returns the transcript in the spoken language."""
    import base64

    voice_model = os.getenv("VOICE_MODEL")
    if not voice_model:
        raise RuntimeError("Voice is off: set VOICE_MODEL to an audio-capable model id.")
    b64 = base64.b64encode(audio_bytes).decode()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Transcribe this audio exactly, in the language spoken. Output only the transcript."},
                {"type": "input_audio", "input_audio": {"data": b64, "format": fmt}},
            ],
        }
    ]
    return chat(messages, temperature=0.0, model=voice_model)
