# WAYFUMO Bot 🤖🔥

WAYFUMO (**What Are You A F***ing Moron?**) is an automated witty roast bot that scrapes Reddit posts, generates comedic roasts via your local Ollama AI, creates branded images with configurable generators, and posts them to social media platforms like X (Twitter) and TikTok.

---

## 🚀 Features

✅ Scrapes posts from **r/AmItheAsshole**  
✅ Generates witty roasts using **local Ollama LLM**  
✅ Includes **Reddit post URL** in roasts for reference and credibility  
✅ Creates branded images with configurable **image generators** (Pillow, future DALL-E/SD)  
✅ Posts to X (Twitter) with media uploads  
✅ Modular architecture for adding **TikTok and other platforms**  
✅ Platform toggles (`POST_TO_X`, `POST_TO_TIKTOK`) in `wayfumo_bot.py`  
✅ Configurable image generator toggle in `image_config.py`  
✅ Designed for **Linux (Debian)** environments  
✅ Supports **cron job automation** with logging  
✅ Cleaned prompt template instructions for consistent output

---

## 🔧 Requirements

- Python 3.10+
- Reddit API credentials
- X (Twitter) API credentials (OAuth 1.0a)
- [Ollama](https://ollama.com/) running locally (`llama3.2:latest` model)
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

# TikTok API credentials (currently unused)
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=
TIKTOK_ACCESS_TOKEN=
TIKTOK_ACCESS_SECRET=
\`\`\`

---

## 💻 Usage

Run on demand:

\`\`\`bash
source venv/bin/activate
python wayfumo_bot.py
\`\`\`

This will:

1. Fetch a random Reddit post  
2. Generate a witty roast via Ollama  
3. Append the Reddit post URL if missing  
4. Create an image using your configured generator (if enabled)  
5. Post to enabled platforms (e.g. X) with toggles defined in \`wayfumo_bot.py\`

---

## 📝 Configuration

- **Platform toggles:** \`POST_TO_X\`, \`POST_TO_TIKTOK\` in \`wayfumo_bot.py\`  
- **Image creation toggle:** \`CREATE_IMAGE\` in \`wayfumo_bot.py\`  
- **Image generator selection:** Edit \`image_config.py\` to select:

  - \`pillow\` (default text image)  
  - \`dalle\` (future DALL-E integration)  
  - \`stablediffusion\` (future SD integration)

- **Ollama Model:** Uses \`llama3.2:latest\` by default (update in \`wayfumo_bot.py\` if you deploy newer models).

---

## 🔄 Automation

To run daily via cron:

1. Create \`run_wayfumo.sh\`:

\`\`\`bash
#!/bin/bash
cd /home/billybs/projects/wayfumo_bot
source venv/bin/activate
python wayfumo_bot.py >> cron_wayfumo.log 2>&1
\`\`\`

2. Make executable:

\`\`\`bash
chmod +x run_wayfumo.sh
\`\`\`

3. Edit crontab:

\`\`\`bash
crontab -e
\`\`\`

Add:

\`\`\`
0 8 * * * /home/billybs/projects/wayfumo_bot/run_wayfumo.sh
\`\`\`

✅ Adjust time as needed.

---

## 🛠️ Roadmap

- [ ] Implement TikTok posting integration  
- [ ] Add DALL-E and Stable Diffusion image generation  
- [ ] Automate daily cron runs with email notifications  
- [ ] Build YouTube Shorts pipeline for roast videos  
- [ ] Rotate hashtags and CTAs dynamically  
- [ ] Modularize multi-subreddit sourcing for maximum variety

---

## ⚠️ Disclaimer

WAYFUMO is a comedic roast bot project intended for entertainment. Use responsibly. All opinions generated are AI-based roasts and do not reflect the creator's personal views.

---

## 📄 License

MIT License

---

## ✨ Contributing

PRs and witty roast script enhancements are welcome.

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

Bringing witty AI roasts to your feed daily.
