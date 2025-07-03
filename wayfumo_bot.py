#!/usr/bin/env python3

import os
import praw
import requests
import tweepy
from PIL import Image, ImageDraw, ImageFont
import textwrap
from dotenv import load_dotenv

# ========== LOAD ENV VARIABLES ==========
load_dotenv()

# ========== CONFIGURATION ==========

# Reddit API credentials
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# X API credentials (v2 Client for tweeting)
client = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY"),
    consumer_secret=os.getenv("X_API_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_SECRET")
)

# X API credentials (v1.1 API for media upload)
auth = tweepy.OAuth1UserHandler(
    os.getenv("X_API_KEY"),
    os.getenv("X_API_SECRET"),
    os.getenv("X_ACCESS_TOKEN"),
    os.getenv("X_ACCESS_SECRET")
)
api = tweepy.API(auth)

# Ollama endpoint
OLLAMA_URL = "http://ai:11434/api/generate"
OLLAMA_MODEL = "llama3.1:latest"  # adjust to match your installed model

# ========== FUNCTIONS ==========

def get_moronic_post():
    subreddit = reddit.subreddit("AmItheAsshole")
    for post in subreddit.hot(limit=10):
        if not post.stickied and len(post.selftext) > 50:
            return post.title + "\n\n" + post.selftext
    return "No suitable post found."

def summarize_roast(text):
    prompt = f"""
You are WAYFUMO, a savage sarcasm bot. Summarize this Reddit post into a short, savage roast under 280 characters. End with 'WAYFUMO.'

{text}
"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.ok:
        return response.json()["response"].strip()
    else:
        return "Failed to generate roast. WAYFUMO."

def create_image(text, output_path="wayfumo_post.png"):
    img = Image.new('RGB', (1080, 1080), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    lines = textwrap.wrap(text, width=20)
    y_text = 200
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        draw.text(((1080 - width) / 2, y_text), line, font=font, fill=(255, 255, 255))
        y_text += height + 10
    img.save(output_path)
    return output_path

def post_to_x(text, image_path):
    media = api.media_upload(image_path)
    client.create_tweet(text=text, media_ids=[media.media_id])

# ========== MAIN EXECUTION ==========

if __name__ == "__main__":
    print("🔎 Fetching Reddit post...")
    post_text = get_moronic_post()
    print("✅ Post fetched.")

    print("🧠 Generating WAYFUMO roast via Ollama...")
    roast = summarize_roast(post_text)
    print("✅ Roast generated:", roast)

    print("🖼️ Creating image...")
    img_path = create_image(roast)
    print("✅ Image created:", img_path)

    print("🐦 Posting to X...")
    post_to_x(roast, img_path)
    print("✅ Posted to X successfully.")
