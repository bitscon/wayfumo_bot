# WAYFUMO Bot 🤖🔥

WAYFUMO (**What Are You A F***ing Moron?**) is an automated savage roast bot that scrapes Reddit posts, summarizes them into savage roasts via your local Ollama AI, generates branded images, and posts them to X (Twitter).

---

## 🚀 Features

✅ Scrapes top posts from **r/AmItheAsshole**  
✅ Generates savage, short roasts using **local Ollama LLM**  
✅ Creates branded square images for social posting  
✅ Posts directly to your verified X account  
✅ Designed for **Linux (Debian)** environments  
✅ Easily extensible to Mastodon, Bluesky, YouTube Shorts, and IG Reels

---

## 🔧 Requirements

- Python 3.10+
- Reddit API credentials
- X (Twitter) API credentials (OAuth 1.0a)
- [Ollama](https://ollama.com/) running locally (tested with llama3:8b)
- pip packages: \`praw tweepy pillow requests python-dotenv\`

---

## ⚙️ Installation

\`\`\`bash
# Clone repository
git clone https://github.com/bitscon/wayfumo_bot.git
cd wayfumo_bot

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
\`\`\`

---

## 🔑 Environment Variables

Create a \`.env\` file in the project root:

\`\`\`
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=WAYFUMO Bot by /u/yourusername

X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
X_ACCESS_TOKEN=your_x_access_token
X_ACCESS_SECRET=your_x_access_secret
\`\`\`

---

## 💻 Usage

Run on demand:

\`\`\`bash
source venv/bin/activate
python wayfumo_bot.py
\`\`\`

This will:

1. Fetch a Reddit post  
2. Generate a savage roast via Ollama  
3. Create a shareable roast image  
4. Post it to X (Twitter)

---

## 📝 Configuration

- **Ollama Model:** Update \`OLLAMA_MODEL\` in \`wayfumo_bot.py\` to match your installed model (\`ollama list\`).  
- **Subreddits:** Modify \`get_moronic_post()\` for different or multiple subreddit scraping.

---

## 🛠️ Roadmap

- [ ] Automate via cron for daily posts  
- [ ] Batch multiple roasts for scheduling  
- [ ] Integrate Mastodon and Bluesky posting  
- [ ] Build a YouTube Shorts pipeline for roast videos  
- [ ] Add meme overlays or video templates for Shorts/Reels

---

## ⚠️ Disclaimer

WAYFUMO is a savage comedic bot project intended for entertainment. Use responsibly. All opinions generated are AI-based roasts and do not reflect the creator's personal views.

---

## 📄 License

MIT License

---

## ✨ Contributing

PRs and savage roast script enhancements are welcome.

---

## 🙏 Credits

Built with ❤️ by [bitscon](https://github.com/bitscon) using:

- [PRAW](https://praw.readthedocs.io/)
- [Tweepy](https://www.tweepy.org/)
- [Pillow](https://pillow.readthedocs.io/)
- [Ollama](https://ollama.com/)

---

### 🔥 **WAYFUMO**

> **What Are You A F***ing Moron?**

Bringing savage AI roasts to your feed daily.
