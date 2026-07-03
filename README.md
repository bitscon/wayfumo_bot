# WAYFUMO Bot 🤖🔥🛍️

WAYFUMO is an automated X (Twitter) bot that turns your **Printful store** into a
clickbait engine. Each run it pulls a real product from your store, has an LLM
write scroll-stopping copy in one of two voices, attaches the product mockup
image, and posts to X with a **tracked link back to your storefront** — so the
feed actually drives traffic and sales.

It also keeps the original **WAYFUMO roast mode** (roast a random
r/AmItheAsshole post) as a legacy option.

---

## 🚀 What it does

**Clickbait mode (default):**

1. Fetches your products from the **Printful API** and picks one (`random` or daily `rotate`)
2. Generates copy via a configurable **LLM** (self-hosted Ollama *or* OpenRouter)
   in a rotating voice — edgy **WAYFUMO roast → merch** tie-in, or straight **product hype**
3. Downloads the product **mockup image** to attach to the tweet
4. Appends your **store link with UTM tracking** and product-relevant hashtags,
   packed to fit X's 280-character limit
5. Posts to X (or just prints it, under `DRY_RUN`)

**Roast mode (legacy):** scrapes r/AmItheAsshole and posts an AI roast, as before.

---

## 🔧 Requirements

- Python 3.10+
- A **Printful-hosted storefront** (`https://yourstore.printful.me`) and a Printful API token
- X (Twitter) API credentials (OAuth 1.0a) with write access
- An LLM backend: either an **Ollama** server, or an **OpenRouter** API key
- (Roast mode only) Reddit API credentials

---

## ⚙️ Installation

```bash
git clone https://github.com/bitscon/wayfumo_bot.git
cd wayfumo_bot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then fill in your keys
```

---

## 🔑 Configuration

All configuration is via environment variables in `.env` (see `.env.example` for
the full, documented list). The most important ones:

| Var | Purpose |
|---|---|
| `BOT_MODE` | `clickbait` (Printful) or `roast` (legacy Reddit) |
| `DRY_RUN` | `true` = build & print the post, never touch X (default) |
| `PRODUCT_STRATEGY` | `random` or `rotate` (day-of-year) product selection |
| `VOICE_MODE` | `blend` (rotate), `roast`, or `hype` |
| `PRINTFUL_TOKEN` | Printful API token (Settings → Developers) |
| `PRINTFUL_STORE_ID` | Only for account-level tokens |
| `STORE_BASE_URL` | Your `https://yourstore.printful.me` |
| `UTM_CAMPAIGN` | Campaign tag appended to store links |
| `LLM_PROVIDER` | `ollama` or `openrouter` |
| `OLLAMA_URL` / `OLLAMA_MODEL` | Ollama endpoint + model |
| `OPENROUTER_API_KEY` / `OPENROUTER_MODEL` | OpenRouter creds + model |
| `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_SECRET` | X OAuth 1.0a |

### Optional deep links

Printful's API does **not** expose per-product page URLs, so links default to
your store homepage. To deep-link specific products, edit `product_links.json`
and map a product's `sync_product` id to its storefront path. Products not listed
there link to the homepage. The mockup image is what showcases the specific item.

### Voice templates

Copy prompts live in `prompts/` — edit `hype.txt` and `roast.txt` to tune the
voice. `roast_reddit.txt` is used by legacy roast mode.

---

## 💻 Usage

```bash
source venv/bin/activate
python wayfumo_bot.py
```

With `DRY_RUN=true` (the default) this builds the post and prints it without
posting — the safe way to tune voice and copy. Flip `DRY_RUN=false` to go live.

### Test the pieces in isolation

```bash
python config.py                       # show resolved config (secrets masked)
python printful_client.py              # list products + dump the picked one
python llm_provider.py "test prompt"   # check the active LLM provider
python content_builder.py              # run the fit_tweet self-checks
```

---

## 🔄 Automation (cron)

`run_wayfumo.sh` cd's to its own directory, activates the venv, and runs the bot,
logging to `cron_wayfumo.log`:

```bash
chmod +x run_wayfumo.sh
crontab -e
```

Add (example — daily at 08:00; keep cadence conservative, see below):

```
0 8 * * * /path/to/wayfumo_bot/run_wayfumo.sh
```

---

## ⚠️ Notes & limits

- **X free tier** has a low monthly write cap. A frequent cron will exhaust it —
  keep the cadence conservative. `DRY_RUN` protects you while tuning.
- **No per-product URLs** from Printful — links go to the store homepage unless
  you fill `product_links.json`.
- LLM output is guarded: any URLs/hashtags the model adds are stripped and the
  link/hashtags are re-appended deterministically to control the 280-char budget.

---

## 📄 License

MIT License

---

### 🔥 **WAYFUMO** — clickbait that sells the merch.
