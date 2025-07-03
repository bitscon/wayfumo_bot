#!/usr/bin/env python3

import os
import praw
import requests
import tweepy
from dotenv import load_dotenv

# Import image creator module
import image_creator

# ========== LOAD ENV VARIABLES ==========
load_dotenv()

# ========== CONFIGURATION ==========

# Toggle image creation
CREATE_IMAGE = True

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
OLLAMA_MODEL = "llama3.2:latest"  # adjust to match your installed model

# ========== FUNCTIONS ==========

def get_moronic_post():
    subreddit = reddit.subreddit("AmItheAsshole")
    for post in subreddit.hot(limit=10):
        if not post.stickied and len(post.selftext) > 50:
            return post.title + "\n\n" + post.selftext
    return "No suitable post found."

def summarize_roast(text):
    with open("prompt_template.txt", "r") as f:
        prompt = f.read().replace("{{POST_CONTENT}}", text)
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.ok:
        return response.json()["response"].strip()
    else:
        return "Failed to generate roast. What are ya, a F'n Moron?. #wayfumo #roast #reddit"

def post_to_x(text, image_path=None):
    try:
        if image_path:
            media = api.media_upload(image_path)
            client.create_tweet(text=text, media_ids=[media.media_id])
        else:
            client.create_tweet(text=text)
    except Exception as e:
        print("⚠️ Posting failed. Error:", e)

# ========== MAIN EXECUTION ==========

if __name__ == "__main__":
    print("🔎 Fetching Reddit post...")
    post_text = get_moronic_post()
    print("✅ Post fetched.")

    print("🧠 Generating WAYFUMO roast via Ollama...")
    roast = summarize_roast(post_text)
    print("✅ Roast generated:", roast)

    img_path = None
    if CREATE_IMAGE:
        print("🖼️ Creating image...")
        img_path = image_creator.create_image(roast)
        print("✅ Image created:", img_path)
    else:
        print("⚠️ Image creation disabled by config.")

    print("🐦 Posting to X...")
    post_to_x(roast, img_path)
    print("✅ Posted to X successfully.")
