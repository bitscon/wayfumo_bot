"""Centralized configuration for the WAYFUMO bot.

Every environment variable the bot reads lives here, with sensible defaults,
so the rest of the code just imports `config` instead of scattering
`os.getenv` calls around. Loading `.env` here means importing this module is
enough to pick up local secrets.
"""

import os

from dotenv import load_dotenv

# Load .env once, on first import.
load_dotenv()


def _bool(name, default="false"):
    """Read a boolean-ish env var. Accepts 1/true/yes/on (case-insensitive)."""
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


# ========== Mode / behavior ==========
# clickbait = Printful product promotion (primary). roast = legacy Reddit roast.
BOT_MODE = os.getenv("BOT_MODE", "clickbait").strip().lower()

# When true, the bot builds the post but prints it instead of calling X.
DRY_RUN = _bool("DRY_RUN", "true")

POST_TO_X = _bool("POST_TO_X", "true")
POST_TO_TIKTOK = _bool("POST_TO_TIKTOK", "false")

# How to pick a product each run: "random" or "rotate" (day-of-year based).
PRODUCT_STRATEGY = os.getenv("PRODUCT_STRATEGY", "random").strip().lower()

# Voice for the copy: "blend" (rotate), "roast" (WAYFUMO tie-in), or "hype".
VOICE_MODE = os.getenv("VOICE_MODE", "blend").strip().lower()

# ========== Printful ==========
PRINTFUL_TOKEN = os.getenv("PRINTFUL_TOKEN", "")
# Only needed for account-level tokens (store-level tokens don't require it).
PRINTFUL_STORE_ID = os.getenv("PRINTFUL_STORE_ID", "")
PRINTFUL_API_BASE = os.getenv("PRINTFUL_API_BASE", "https://api.printful.com")

# Your Printful-hosted storefront, e.g. https://yourstore.printful.me
STORE_BASE_URL = os.getenv("STORE_BASE_URL", "https://yourstore.printful.me").rstrip("/")
UTM_CAMPAIGN = os.getenv("UTM_CAMPAIGN", "clickbait")

# ========== LLM provider ==========
# "ollama" (self-hosted) or "openrouter" (hosted, needs API key).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

# Full Ollama generate URL, including the /api/generate path.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://llm.workshop.home/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = os.getenv(
    "OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions"
)

# Shared HTTP timeout (seconds) for outbound API calls.
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "60"))

# ========== X / Twitter (OAuth 1.0a) ==========
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# ========== Reddit (legacy roast mode) ==========
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")


if __name__ == "__main__":
    # Quick sanity dump (never prints full secrets).
    def _mask(value):
        if not value:
            return "(unset)"
        return f"set ({len(value)} chars)"

    print("BOT_MODE        :", BOT_MODE)
    print("DRY_RUN         :", DRY_RUN)
    print("POST_TO_X       :", POST_TO_X)
    print("PRODUCT_STRATEGY:", PRODUCT_STRATEGY)
    print("VOICE_MODE      :", VOICE_MODE)
    print("LLM_PROVIDER    :", LLM_PROVIDER)
    print("OLLAMA_URL      :", OLLAMA_URL)
    print("OLLAMA_MODEL    :", OLLAMA_MODEL)
    print("OPENROUTER_MODEL:", OPENROUTER_MODEL)
    print("STORE_BASE_URL  :", STORE_BASE_URL)
    print("PRINTFUL_TOKEN  :", _mask(PRINTFUL_TOKEN))
    print("OPENROUTER_KEY  :", _mask(OPENROUTER_API_KEY))
