"""Builds the final clickbait post: product -> prompt -> copy -> packed tweet.

Keeps tight, deterministic control of the 280-character budget by telling the
LLM to omit URLs/hashtags and appending them here instead.
"""

import os
import random
import re
import tempfile
from urllib.parse import urlencode

import requests

import config
import llm_provider
import printful_client

_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")

# X wraps every link in a t.co URL of a fixed length, regardless of the real
# URL. Media (images) do not count toward the 280-char limit.
TWEET_LIMIT = 280
TCO_LEN = 23

# Evergreen brand tags; 1-2 product tags get derived per post.
BASE_HASHTAGS = ["#WAYFUMO"]

_STOPWORDS = {"the", "a", "an", "and", "of", "for", "with", "your", "our", "shirt",
              "tee", "t-shirt", "mug", "hoodie", "unisex", "premium", "classic"}


def _load_prompt(name):
    with open(os.path.join(_PROMPT_DIR, name)) as fh:
        return fh.read()


def _choose_voice():
    if config.VOICE_MODE == "roast":
        return "roast"
    if config.VOICE_MODE == "hype":
        return "hype"
    return random.choice(["roast", "hype"])  # blend


def _format_price(product):
    price = product.get("price")
    if not price:
        return "a steal"
    currency = product.get("currency") or "USD"
    symbol = {"USD": "$", "EUR": "€", "GBP": "£"}.get(currency, "")
    return f"{symbol}{price}" if symbol else f"{price} {currency}"


def build_store_link(product):
    """Store base URL (+ optional per-product path) with UTM tracking."""
    base = config.STORE_BASE_URL
    path = product.get("path_override")
    if path:
        base = f"{base}/{path.lstrip('/')}"
    query = urlencode(
        {
            "utm_source": "x",
            "utm_medium": "social",
            "utm_campaign": config.UTM_CAMPAIGN,
        }
    )
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}{query}"


def _derive_hashtags(product):
    """Pick 1-2 product-relevant hashtags plus the evergreen brand tag."""
    tags = list(BASE_HASHTAGS)
    words = re.findall(r"[A-Za-z]+", product.get("name", ""))
    for word in words:
        lw = word.lower()
        if len(lw) >= 4 and lw not in _STOPWORDS:
            tag = "#" + word.capitalize()
            if tag not in tags:
                tags.append(tag)
        if len(tags) >= 3:
            break
    return tags


def _strip_model_extras(text):
    """Remove any URLs or hashtags the model added despite instructions."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"#\w+", "", text)
    # Collapse whitespace left behind.
    return re.sub(r"\s+", " ", text).strip().strip('"')


def fit_tweet(copy, link, hashtags):
    """Pack copy + link + hashtags into <= 280 chars, truncating copy if needed.

    The link always counts as TCO_LEN characters. Copy is truncated on a word
    boundary (with an ellipsis) to make room; hashtags are trimmed last.
    """
    copy = _strip_model_extras(copy)
    tag_str = " ".join(hashtags)

    # Budget: link (t.co length) + a space before it + space before tags.
    fixed = TCO_LEN + 1  # link + one leading space
    tag_cost = (len(tag_str) + 1) if tag_str else 0
    budget_for_copy = TWEET_LIMIT - fixed - tag_cost

    if budget_for_copy < 20:
        # Hashtags are eating the budget; drop the derived ones, keep brand tag.
        hashtags = BASE_HASHTAGS
        tag_str = " ".join(hashtags)
        tag_cost = len(tag_str) + 1
        budget_for_copy = TWEET_LIMIT - fixed - tag_cost

    if len(copy) > budget_for_copy:
        truncated = copy[: budget_for_copy - 1].rsplit(" ", 1)[0].rstrip()
        copy = truncated + "…"

    parts = [copy, link]
    if tag_str:
        parts.append(tag_str)
    return " ".join(parts)


def download_image(url, output_path=None):
    """Download a mockup image to a temp file. Returns path or None."""
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=config.HTTP_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"⚠️  Image download failed: {exc}")
        return None
    if output_path is None:
        suffix = os.path.splitext(url.split("?")[0])[1] or ".png"
        fd, output_path = tempfile.mkstemp(prefix="wayfumo_product_", suffix=suffix)
        os.close(fd)
    with open(output_path, "wb") as fh:
        fh.write(resp.content)
    return output_path


def _fallback_copy(product, voice):
    """Canned copy used when the LLM is unavailable."""
    price = _format_price(product)
    name = product["name"]
    if voice == "roast":
        return f"You could keep settling for boring. Or you could grab {name} for {price}. What are ya, a moron?"
    return f"New drop alert: {name} — {price}. Blink and it's gone. 👀"


def build_clickbait_post():
    """Return (tweet_text, image_path) for a Printful product, or (None, None)."""
    try:
        product = printful_client.pick_product(config.PRODUCT_STRATEGY)
    except printful_client.PrintfulError as exc:
        print(f"⚠️  Printful error: {exc}")
        return None, None
    if not product:
        return None, None

    voice = _choose_voice()
    template = _load_prompt("roast.txt" if voice == "roast" else "hype.txt")
    prompt = template.replace("{{PRODUCT_NAME}}", product["name"]).replace(
        "{{PRODUCT_PRICE}}", _format_price(product)
    )

    copy = llm_provider.generate(prompt) or _fallback_copy(product, voice)
    link = build_store_link(product)
    hashtags = _derive_hashtags(product)
    tweet = fit_tweet(copy, link, hashtags)

    image_path = download_image(product["image_url"])
    return tweet, image_path


def _effective_len(text, link):
    """Length as X counts it: the link weighs TCO_LEN regardless of real size."""
    return len(text) - len(link) + TCO_LEN if link in text else len(text)


if __name__ == "__main__":
    # Self-check for fit_tweet: overlong copy must still fit and keep link+tags.
    long_copy = "word " * 120  # ~600 chars
    link = "https://yourstore.printful.me?utm_source=x&utm_medium=social&utm_campaign=clickbait"
    tags = ["#WAYFUMO", "#Tee", "#Merch"]
    result = fit_tweet(long_copy, link, tags)
    eff = _effective_len(result, link)
    assert eff <= TWEET_LIMIT, f"tweet too long: {eff}"
    assert link in result, "link missing from tweet"
    assert "#WAYFUMO" in result, "brand hashtag missing"
    print("fit_tweet OK — effective length:", eff)
    print(result)

    # Verify model-added URLs/hashtags get stripped and re-controlled.
    dirty = "Check it out http://spam.example #Random amazing deal"
    cleaned = fit_tweet(dirty, link, tags)
    assert "spam.example" not in cleaned, "model URL not stripped"
    assert "#Random" not in cleaned, "model hashtag not stripped"
    print("strip guard OK")
