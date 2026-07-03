#!/usr/bin/env python3
"""WAYFUMO bot — Printful clickbait machine (with legacy Reddit roast mode).

Primary mode (BOT_MODE=clickbait): pull a product from your Printful store,
have the LLM write scroll-stopping copy, attach the product mockup, and post to
X with a tracked link back to your storefront.

Legacy mode (BOT_MODE=roast): the original behavior — roast a random
r/AmItheAsshole post. Kept for continuity; its copy now also flows through the
configurable LLM provider.

Set DRY_RUN=true (the default) to build and print the post without touching X.
"""

import tweepy

import config
import content_builder
import llm_provider

# ========== X (Twitter) clients ==========
# Built lazily so DRY_RUN / config checks work without X credentials set.
# v2 Client for create_tweet; v1.1 API only for media upload (v2 has no
# media-upload endpoint).

def _x_clients():
    client = tweepy.Client(
        consumer_key=config.X_API_KEY,
        consumer_secret=config.X_API_SECRET,
        access_token=config.X_ACCESS_TOKEN,
        access_token_secret=config.X_ACCESS_SECRET,
    )
    auth = tweepy.OAuth1UserHandler(
        config.X_API_KEY,
        config.X_API_SECRET,
        config.X_ACCESS_TOKEN,
        config.X_ACCESS_SECRET,
    )
    return client, tweepy.API(auth)


# ========== Posting ==========

def post_to_x(text, image_path=None):
    """Post to X. Honors DRY_RUN (prints instead of posting)."""
    if config.DRY_RUN:
        print("🧪 DRY_RUN — not posting. Tweet would be:")
        print("-" * 60)
        print(text)
        print("-" * 60)
        print("🖼️  Image:", image_path or "(none)")
        return

    try:
        client, api = _x_clients()
        if image_path:
            media = api.media_upload(image_path)
            client.create_tweet(text=text, media_ids=[media.media_id])
        else:
            client.create_tweet(text=text)
        print("✅ Posted to X successfully.")
    except Exception as e:  # noqa: BLE001 - cron job: log and move on
        print("⚠️  Posting to X failed. Error:", e)


def post_to_tiktok(text, image_path=None):
    """Placeholder — TikTok integration not implemented yet."""
    print("⚠️  TikTok posting is disabled or not implemented yet.")


# ========== Content modes ==========

def build_clickbait():
    """Printful product clickbait. Returns (text, image_path) or (None, None)."""
    print("🛍️  Fetching a product from Printful...")
    text, image_path = content_builder.build_clickbait_post()
    if not text:
        print("⚠️  No product available — is the store empty or the token unset?")
        return None, None
    print("✅ Copy generated.")
    return text, image_path


def build_roast():
    """Legacy Reddit roast. Returns (text, None) or (None, None)."""
    # praw is only needed here, so import lazily — clickbait users don't need
    # Reddit credentials installed/configured.
    import praw

    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )

    print("🔎 Fetching Reddit post...")
    import random

    subreddit = reddit.subreddit("AmItheAsshole")
    posts = [
        p for p in subreddit.hot(limit=25)
        if not p.stickied and len(p.selftext) > 50
    ]
    if not posts:
        print("⚠️  No suitable Reddit post found.")
        return None, None
    selected = random.choice(posts)
    post = {"text": f"{selected.title}\n\n{selected.selftext}", "url": selected.url}

    print("🧠 Generating WAYFUMO roast...")
    with open("prompts/roast_reddit.txt") as f:
        prompt = f.read().replace("{{POST_CONTENT}}", post["text"]).replace(
            "{{POST_URL}}", post["url"]
        )
    roast = llm_provider.generate(prompt)
    if not roast:
        roast = f"What are ya, a F'n Moron?. {post['url']} #wayfumo #roast #reddit"
    if post["url"] not in roast:
        roast += f" {post['url']}"
    print("✅ Roast generated.")
    return roast, None


# ========== Main ==========

if __name__ == "__main__":
    print(f"🚀 WAYFUMO bot — mode: {config.BOT_MODE}, dry_run: {config.DRY_RUN}")

    if config.BOT_MODE == "roast":
        text, image_path = build_roast()
    else:
        text, image_path = build_clickbait()

    if not text:
        print("🛑 Nothing to post this run.")
        raise SystemExit(0)

    if config.POST_TO_X:
        print("🐦 Posting to X...")
        post_to_x(text, image_path)
    else:
        print("⚠️  X posting disabled by config.")

    if config.POST_TO_TIKTOK:
        print("🎵 Posting to TikTok...")
        post_to_tiktok(text, image_path)
