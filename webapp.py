#!/usr/bin/env python3
"""WAYFUMO ops dashboard — a tiny, read-only Flask app for the barn.

Shows the bot's config, its systemd timer status, and recent run logs, and lets
you preview the *next* post (dry-run: product + LLM copy) without posting to X.

Read-only by design: it never posts to X and never edits config or .env. It
reuses the bot's own modules and shells out to systemctl/journalctl for status.

Served behind nginx (wayfumo-bot.barn.workshop.home) by gunicorn on
127.0.0.1:8095 via the wayfumo-web.service systemd user unit.

Manage it:
    systemctl --user restart wayfumo-web     # after editing this file
    journalctl --user -u wayfumo-web -f      # tail the dashboard's own logs
"""

import subprocess

from flask import Flask, render_template_string

import config
import content_builder

app = Flask(__name__)


def _run(cmd):
    """Run a read-only command; return its text output. Never raises."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return (r.stdout or r.stderr).strip() or "(no output)"
    except Exception as exc:  # noqa: BLE001 - dashboard degrades gracefully
        return f"(unavailable: {exc})"


def _mask(value):
    return f"set ({len(value)} chars)" if value else "(unset)"


def gather():
    """Collect everything the dashboard shows. All read-only."""
    return {
        "config": {
            "BOT_MODE": config.BOT_MODE,
            "DRY_RUN": config.DRY_RUN,
            "POST_TO_X": config.POST_TO_X,
            "PRODUCT_STRATEGY": config.PRODUCT_STRATEGY,
            "VOICE_MODE": config.VOICE_MODE,
            "LLM_PROVIDER": config.LLM_PROVIDER,
            "OLLAMA_MODEL": config.OLLAMA_MODEL,
            "STORE_BASE_URL": config.STORE_BASE_URL,
            "PRINTFUL_TOKEN": _mask(config.PRINTFUL_TOKEN),
        },
        "timer_active": _run(["systemctl", "--user", "is-active", "wayfumo.timer"]),
        "next_run": _run(["systemctl", "--user", "list-timers", "wayfumo.timer", "--no-pager"]),
        "last_result": _run(["systemctl", "--user", "show", "wayfumo.service", "-p", "Result", "--value"]),
        "logs": _run(["journalctl", "--user", "-u", "wayfumo.service", "-n", "30", "--no-pager", "-o", "short-iso"]),
    }


@app.route("/health")
def health():
    return "ok", 200


@app.route("/")
def index():
    return render_template_string(TEMPLATE, preview=None, **gather())


@app.route("/preview", methods=["POST"])
def preview():
    """Build the next post in dry-run and show it. Never posts."""
    result = {"tweet": None, "image": None, "error": None}
    try:
        tweet, image_path = content_builder.build_clickbait_post()
        result["tweet"], result["image"] = tweet, image_path
        if not tweet:
            result["error"] = "Nothing to preview — Printful store empty or unavailable."
    except Exception as exc:  # noqa: BLE001 - never 500 the dashboard
        result["error"] = f"Preview failed: {exc}"
    return render_template_string(TEMPLATE, preview=result, **gather())


TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WAYFUMO ops</title>
<style>
  :root { color-scheme: dark; }
  body { margin:0; background:#1e1e1e; color:#e8e8e8;
         font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
  header { background:#151515; padding:1rem 1.5rem; border-bottom:2px solid #ff5a36; }
  header .tag { color:#ff5a36; font-weight:700; letter-spacing:.2em; font-size:.75rem; text-transform:uppercase; }
  header h1 { margin:.2rem 0 0; font-size:1.4rem; }
  main { max-width:56rem; margin:0 auto; padding:1.5rem; }
  section { background:#262626; border:1px solid #333; border-radius:8px; padding:1rem 1.25rem; margin-bottom:1.25rem; }
  h2 { margin:0 0 .75rem; font-size:1rem; color:#ffb3a0; }
  table { width:100%; border-collapse:collapse; }
  td { padding:.25rem .5rem; border-bottom:1px solid #303030; vertical-align:top; }
  td.k { color:#9a9a9a; width:14rem; white-space:nowrap; }
  td.v { font-family:ui-monospace,monospace; }
  pre { background:#151515; padding:.75rem; border-radius:6px; overflow-x:auto; font-size:12px; margin:0; white-space:pre-wrap; word-break:break-word; }
  .pill { display:inline-block; padding:.1rem .5rem; border-radius:999px; font-size:.75rem; font-weight:700; }
  .ok { background:#123d1e; color:#5ad07f; }
  .warn { background:#3d2a12; color:#e0a95a; }
  button { background:#ff5a36; color:#fff; border:0; padding:.5rem 1rem; border-radius:6px; font-weight:700; cursor:pointer; }
  .tweet { background:#151515; border-left:3px solid #ff5a36; padding:.75rem 1rem; border-radius:4px; white-space:pre-wrap; }
  .muted { color:#8a8a8a; font-size:.8rem; }
  code { color:#ffb3a0; }
</style>
</head>
<body>
<header>
  <div class="tag">WAYFUMO</div>
  <h1>Ops dashboard <span class="muted">· read-only</span></h1>
</header>
<main>

  <section>
    <h2>Schedule</h2>
    <table>
      <tr><td class="k">Timer active</td><td class="v">
        {% if timer_active == 'active' %}<span class="pill ok">active</span>{% else %}<span class="pill warn">{{ timer_active }}</span>{% endif %}
      </td></tr>
      <tr><td class="k">Last run result</td><td class="v">{{ last_result }}</td></tr>
      <tr><td class="k">Next run</td><td class="v"><pre>{{ next_run }}</pre></td></tr>
    </table>
  </section>

  <section>
    <h2>Config <span class="muted">(secrets masked)</span></h2>
    <table>
      {% for k, v in config.items() %}
      <tr><td class="k">{{ k }}</td><td class="v">
        {% if k == 'DRY_RUN' %}
          {% if v %}<span class="pill ok">DRY_RUN on (won't post)</span>{% else %}<span class="pill warn">LIVE — will post to X</span>{% endif %}
        {% else %}{{ v }}{% endif %}
      </td></tr>
      {% endfor %}
    </table>
  </section>

  <section>
    <h2>Preview next post <span class="muted">· dry-run, never posts</span></h2>
    <form method="post" action="/preview"><button type="submit">Generate preview</button></form>
    {% if preview %}
      {% if preview.error %}
        <p class="muted" style="margin-top:1rem">{{ preview.error }}</p>
      {% else %}
        <div class="tweet" style="margin-top:1rem">{{ preview.tweet }}</div>
        <p class="muted">Image: {{ preview.image or '(none)' }}</p>
      {% endif %}
    {% endif %}
  </section>

  <section>
    <h2>Recent runs <span class="muted">· journalctl</span></h2>
    <pre>{{ logs }}</pre>
  </section>

  <p class="muted">Manage: <code>systemctl --user restart wayfumo-web</code> · <code>journalctl --user -u wayfumo-web -f</code></p>

</main>
</body>
</html>
"""


if __name__ == "__main__":
    # Dev only: `python webapp.py`. In production gunicorn serves `webapp:app`.
    app.run(host="127.0.0.1", port=8095, debug=False)
