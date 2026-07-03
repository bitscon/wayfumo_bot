"""Pluggable LLM copy generator.

One public entry point, `generate(prompt) -> str`, that dispatches to either a
self-hosted Ollama server or the OpenRouter hosted API based on
`config.LLM_PROVIDER`. Callers only ever see plain text in / plain text out.

On any failure this returns an empty string so the caller can fall back to a
canned template rather than crashing the cron run.
"""

import requests

import config


class LLMError(Exception):
    """Raised internally when a provider call fails; callers see '' instead."""


def _post_json(url, payload, headers=None):
    """POST JSON and return the parsed response, raising LLMError on failure."""
    try:
        resp = requests.post(
            url, json=payload, headers=headers or {}, timeout=config.HTTP_TIMEOUT
        )
    except requests.RequestException as exc:
        raise LLMError(f"request to {url} failed: {exc}") from exc
    if not resp.ok:
        raise LLMError(f"{url} returned HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json()


def _generate_ollama(prompt):
    """Call a local Ollama server (same HTTP shape the old bot used)."""
    payload = {"model": config.OLLAMA_MODEL, "prompt": prompt, "stream": False}
    data = _post_json(config.OLLAMA_URL, payload)
    return (data.get("response") or "").strip()


def _generate_openrouter(prompt):
    """Call OpenRouter's OpenAI-compatible chat completions endpoint."""
    if not config.OPENROUTER_API_KEY:
        raise LLMError("OPENROUTER_API_KEY is not set")
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        # Optional but recommended by OpenRouter for attribution.
        "HTTP-Referer": config.STORE_BASE_URL,
        "X-Title": "WAYFUMO Bot",
    }
    payload = {
        "model": config.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _post_json(config.OPENROUTER_URL, payload, headers=headers)
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"unexpected OpenRouter response: {data}") from exc


def generate(prompt):
    """Generate copy for `prompt`. Returns '' on any provider failure."""
    try:
        if config.LLM_PROVIDER == "openrouter":
            return _generate_openrouter(prompt)
        return _generate_ollama(prompt)
    except LLMError as exc:
        print(f"⚠️  LLM generation failed ({config.LLM_PROVIDER}): {exc}")
        return ""


if __name__ == "__main__":
    import sys

    test_prompt = " ".join(sys.argv[1:]) or "Write a one-line test tweet."
    print(f"Provider: {config.LLM_PROVIDER}")
    print("Prompt  :", test_prompt)
    print("Output  :", generate(test_prompt) or "(empty — provider failed)")
