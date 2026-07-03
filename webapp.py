#!/usr/bin/env python3
"""WAYFUMO control panel — configure, control, and monitor the bot from a browser.

Supersedes the read-only dashboard (ADR-0002 supersedes ADR-0001). Runs as the
billyb user, so it edits .env, edits the timer cadence, and drives the bot's
systemd units with no sudo.

Auth: if DASHBOARD_PASSWORD is set (in .env) the panel requires login and all
controls are enabled. If it is unset the panel is view-only (monitoring +
dry-run preview) and every control action returns 403.

Served by gunicorn on 127.0.0.1:8095 (wayfumo-web.service), behind nginx.
Manage: systemctl --user restart wayfumo-web ; journalctl --user -u wayfumo-web -f
"""

import os
import re
import subprocess
from functools import wraps

from dotenv import dotenv_values
from flask import (Flask, flash, get_flashed_messages, redirect,
                   render_template_string, request, session, url_for)

import config
import content_builder

REPO = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(REPO, ".env")
TIMER_UNIT = os.path.expanduser("~/.config/systemd/user/wayfumo.timer")

# Editable non-secret settings (prefilled from .env).
BOOL_FIELDS = ["DRY_RUN", "POST_TO_X", "POST_TO_TIKTOK"]
SELECT_FIELDS = {
    "BOT_MODE": ["clickbait", "roast"],
    "PRODUCT_STRATEGY": ["random", "rotate"],
    "VOICE_MODE": ["blend", "roast", "hype"],
    "LLM_PROVIDER": ["ollama", "openrouter"],
}
TEXT_FIELDS = ["OLLAMA_MODEL", "OPENROUTER_MODEL", "STORE_BASE_URL", "UTM_CAMPAIGN"]
# Write-only: set a new value to change; current value is never shown.
SECRET_FIELDS = ["PRINTFUL_TOKEN", "OPENROUTER_API_KEY", "X_API_KEY", "X_API_SECRET",
                 "X_ACCESS_TOKEN", "X_ACCESS_SECRET", "DASHBOARD_PASSWORD"]

_TRUTHY = {"1", "true", "yes", "on"}

app = Flask(__name__)
app.secret_key = os.environ.get("DASHBOARD_SECRET") or os.urandom(32)


# ---------- helpers (read-only) ----------

def _run(cmd, timeout=15):
    """Run a command; return its text output. Never raises."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or r.stderr).strip() or "(no output)"
    except Exception as exc:  # noqa: BLE001 - panel degrades gracefully
        return f"(unavailable: {exc})"


def _as_bool(v):
    return str(v or "").strip().lower() in _TRUTHY


def _password():
    return os.environ.get("DASHBOARD_PASSWORD", "").strip()


def _authed():
    return bool(session.get("auth"))


def can_control():
    """Controls are usable only when a password is configured and the user is in."""
    return bool(_password()) and _authed()


def current_cadence():
    try:
        m = re.search(r"(?m)^OnCalendar=(.*)$", open(TIMER_UNIT).read())
        return m.group(1).strip() if m else ""
    except OSError:
        return ""


def env_form():
    """Current .env values for form prefill (read fresh so edits show immediately)."""
    e = dotenv_values(ENV_PATH)
    vals = {k: _as_bool(e.get(k)) for k in BOOL_FIELDS}
    for k in list(SELECT_FIELDS) + TEXT_FIELDS:
        vals[k] = (e.get(k) or "").strip()
    vals["_secrets"] = {k: ("set" if (e.get(k) or "").strip() else "unset")
                        for k in SECRET_FIELDS}
    vals["cadence"] = current_cadence()
    return vals


def status():
    return {
        "timer_active": _run(["systemctl", "--user", "is-active", "wayfumo.timer"]),
        "next_run": _run(["systemctl", "--user", "list-timers", "wayfumo.timer", "--no-pager"]),
        "last_result": _run(["systemctl", "--user", "show", "wayfumo.service", "-p", "Result", "--value"]),
        "logs": _run(["journalctl", "--user", "-u", "wayfumo.service", "-n", "30", "--no-pager", "-o", "short-iso"]),
    }


# ---------- writers (mutating; control routes only) ----------

def update_env(changes):
    """Update KEY=value lines in .env, preserving order and inline comments."""
    lines = open(ENV_PATH).read().splitlines()
    seen = set()
    for i, line in enumerate(lines):
        m = re.match(r"^(\s*)([A-Z][A-Z0-9_]*)=(.*)$", line)
        if not m or m.group(2) not in changes:
            continue
        key = m.group(2)
        comment = ""
        cm = re.search(r"\s+#.*$", m.group(3))
        if cm:
            comment = cm.group(0)
        lines[i] = f"{m.group(1)}{key}={changes[key]}{comment}"
        seen.add(key)
    for key, val in changes.items():
        if key not in seen:
            lines.append(f"{key}={val}")
    tmp = ENV_PATH + ".tmp"
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.replace(tmp, ENV_PATH)


def update_cadence(oncalendar):
    """Rewrite OnCalendar in the timer unit. Returns True if it changed."""
    try:
        text = open(TIMER_UNIT).read()
    except OSError:
        return False
    new = re.sub(r"(?m)^OnCalendar=.*$", f"OnCalendar={oncalendar}", text)
    if new == text:
        return False
    tmp = TIMER_UNIT + ".tmp"
    with open(tmp, "w") as f:
        f.write(new)
    os.replace(tmp, TIMER_UNIT)
    return True


# ---------- auth gate ----------

@app.before_request
def _gate():
    # When a password is configured, everything except login/health needs a session.
    if _password() and not _authed() and request.endpoint not in ("login", "health"):
        return redirect(url_for("login"))


def require_control(fn):
    @wraps(fn)
    def wrapper(*a, **k):
        if not _password():
            return ("Controls are disabled. Set DASHBOARD_PASSWORD in .env and "
                    "restart wayfumo-web to enable them.", 403)
        if not _authed():
            return redirect(url_for("login"))
        return fn(*a, **k)
    return wrapper


# ---------- routes ----------

@app.route("/health")
def health():
    return "ok", 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if not _password():
        return redirect(url_for("index"))
    if request.method == "POST":
        if request.form.get("password", "") == _password():
            session["auth"] = True
            return redirect(url_for("index"))
        flash("Wrong password.")
    return render_template_string(LOGIN_TEMPLATE, messages=get_flashed_messages())


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    return render_template_string(
        TEMPLATE, preview=None, can_control=can_control(), has_password=bool(_password()),
        form=env_form(), selects=SELECT_FIELDS, texts=TEXT_FIELDS, secrets=SECRET_FIELDS,
        messages=get_flashed_messages(), **status())


@app.route("/preview", methods=["POST"])
def preview():
    """Build the next post in dry-run and show it. Never posts."""
    result = {"tweet": None, "image": None, "error": None}
    try:
        tweet, image_path = content_builder.build_clickbait_post()
        result["tweet"], result["image"] = tweet, image_path
        if not tweet:
            result["error"] = "Nothing to preview — Printful store empty or unavailable."
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"Preview failed: {exc}"
    return render_template_string(
        TEMPLATE, preview=result, can_control=can_control(), has_password=bool(_password()),
        form=env_form(), selects=SELECT_FIELDS, texts=TEXT_FIELDS, secrets=SECRET_FIELDS,
        messages=get_flashed_messages(), **status())


@app.route("/config", methods=["POST"])
@require_control
def save_config():
    changes = {k: ("true" if request.form.get(k) == "on" else "false") for k in BOOL_FIELDS}
    for k in list(SELECT_FIELDS) + TEXT_FIELDS:
        val = request.form.get(k, "").strip()
        if val:
            changes[k] = val
    for k in SECRET_FIELDS:
        val = request.form.get(k, "").strip()
        if val:  # only write a secret when a new value is typed
            changes[k] = val
    update_env(changes)

    cadence = request.form.get("cadence", "").strip()
    if cadence and update_cadence(cadence):
        _run(["systemctl", "--user", "daemon-reload"])
        _run(["systemctl", "--user", "restart", "wayfumo.timer"])

    # Restart the panel (detached) so it reloads config for previews.
    _run(["systemd-run", "--user", "--on-active=2", "systemctl", "--user", "restart", "wayfumo-web"])
    flash("Config saved. The bot uses it on its next run; panel is reloading…")
    return redirect(url_for("index"))


@app.route("/run", methods=["POST"])
@require_control
def run_now():
    _run(["systemctl", "--user", "start", "--no-block", "wayfumo.service"])
    flash("Triggered a bot run — watch Recent runs below for the result.")
    return redirect(url_for("index"))


@app.route("/redeploy", methods=["POST"])
@require_control
def redeploy():
    pull = _run(["git", "-C", REPO, "pull", "--ff-only", "origin", "main"], timeout=60)
    _run([os.path.join(REPO, "venv/bin/pip"), "install", "-q", "-r",
          os.path.join(REPO, "requirements.txt")], timeout=180)
    _run(["systemctl", "--user", "restart", "wayfumo.timer"])
    # Restart the panel itself detached so this response returns first.
    _run(["systemd-run", "--user", "--on-active=2", "systemctl", "--user", "restart", "wayfumo-web"])
    flash(f"Redeploy: {pull[:200]} — deps checked, bot restarted, panel reloading…")
    return redirect(url_for("index"))


# ---------- templates ----------

STYLE = """
<style>
  :root { color-scheme: dark; }
  body { margin:0; background:#1e1e1e; color:#e8e8e8;
         font:14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
  header { background:#151515; padding:1rem 1.5rem; border-bottom:2px solid #ff5a36;
           display:flex; align-items:center; justify-content:space-between; }
  header .tag { color:#ff5a36; font-weight:700; letter-spacing:.2em; font-size:.75rem; text-transform:uppercase; }
  header h1 { margin:.2rem 0 0; font-size:1.4rem; }
  main { max-width:60rem; margin:0 auto; padding:1.5rem; }
  section { background:#262626; border:1px solid #333; border-radius:8px; padding:1rem 1.25rem; margin-bottom:1.25rem; }
  h2 { margin:0 0 .75rem; font-size:1rem; color:#ffb3a0; }
  table { width:100%; border-collapse:collapse; }
  td { padding:.3rem .5rem; border-bottom:1px solid #303030; vertical-align:top; }
  td.k { color:#9a9a9a; width:13rem; white-space:nowrap; }
  pre { background:#151515; padding:.75rem; border-radius:6px; overflow-x:auto; font-size:12px; margin:0; white-space:pre-wrap; word-break:break-word; }
  .pill { display:inline-block; padding:.1rem .5rem; border-radius:999px; font-size:.75rem; font-weight:700; }
  .ok { background:#123d1e; color:#5ad07f; } .warn { background:#3d2a12; color:#e0a95a; }
  input,select { background:#151515; color:#eee; border:1px solid #444; border-radius:5px; padding:.35rem .5rem; font:inherit; width:100%; box-sizing:border-box; }
  input[type=checkbox]{ width:auto; }
  button { background:#ff5a36; color:#fff; border:0; padding:.5rem 1rem; border-radius:6px; font-weight:700; cursor:pointer; }
  button.ghost { background:#333; }
  .row { display:flex; gap:.75rem; flex-wrap:wrap; align-items:center; margin-top:.75rem; }
  .tweet { background:#151515; border-left:3px solid #ff5a36; padding:.75rem 1rem; border-radius:4px; white-space:pre-wrap; }
  .muted { color:#8a8a8a; font-size:.8rem; } code { color:#ffb3a0; }
  .flash { background:#123d1e; color:#bfe; border:1px solid #2a5; padding:.6rem .9rem; border-radius:6px; margin-bottom:1rem; }
  .banner { background:#3d2a12; color:#e0a95a; border:1px solid #7a5; padding:.6rem .9rem; border-radius:6px; margin-bottom:1rem; }
  label.f { display:block; margin:.5rem 0; }
  label.f span { display:block; color:#9a9a9a; font-size:.8rem; margin-bottom:.15rem; }
</style>
"""

LOGIN_TEMPLATE = """
<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1"><title>WAYFUMO login</title>
""" + STYLE + """</head><body>
<header><div><div class=tag>WAYFUMO</div><h1>Control panel</h1></div></header>
<main><section style="max-width:22rem;margin:3rem auto">
  <h2>Log in</h2>
  {% for m in messages %}<div class=banner>{{ m }}</div>{% endfor %}
  <form method=post>
    <label class=f><span>Password</span><input type=password name=password autofocus></label>
    <div class=row><button type=submit>Log in</button></div>
  </form>
</section></main></body></html>
"""

TEMPLATE = """
<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1"><title>WAYFUMO control</title>
""" + STYLE + """</head><body>
<header>
  <div><div class=tag>WAYFUMO</div><h1>Control panel</h1></div>
  {% if can_control %}<form method=post action="/logout"><button class=ghost type=submit>Log out</button></form>{% endif %}
</header>
<main>

  {% for m in messages %}<div class=flash>{{ m }}</div>{% endfor %}
  {% if not has_password %}<div class=banner>View-only — controls are disabled. Set <code>DASHBOARD_PASSWORD</code> in .env and restart <code>wayfumo-web</code> to enable editing.</div>{% endif %}

  <section>
    <h2>Status</h2>
    <table>
      <tr><td class=k>Timer</td><td>{% if timer_active=='active' %}<span class="pill ok">active</span>{% else %}<span class="pill warn">{{ timer_active }}</span>{% endif %}</td></tr>
      <tr><td class=k>Posting mode</td><td>{% if form.DRY_RUN %}<span class="pill ok">DRY_RUN — won't post</span>{% else %}<span class="pill warn">LIVE — posts to X</span>{% endif %}</td></tr>
      <tr><td class=k>Last run result</td><td>{{ last_result }}</td></tr>
      <tr><td class=k>Next run</td><td><pre>{{ next_run }}</pre></td></tr>
    </table>
    {% if can_control %}
    <div class=row>
      <form method=post action="/run" onsubmit="return confirm('Run the bot once now?{% if not form.DRY_RUN %} DRY_RUN is OFF — this will POST to X.{% endif %}')"><button type=submit>Run now</button></form>
      <form method=post action="/redeploy" onsubmit="return confirm('Pull latest from GitHub and restart the bot?')"><button class=ghost type=submit>Redeploy (pull latest)</button></form>
    </div>
    {% endif %}
  </section>

  <section>
    <h2>Configuration{% if not can_control %} <span class=muted>(read-only)</span>{% endif %}</h2>
    <form method=post action="/config">
      <fieldset style="border:0;padding:0;margin:0" {% if not can_control %}disabled{% endif %}>
        {% for k in ['DRY_RUN','POST_TO_X','POST_TO_TIKTOK'] %}
        <label class=f><input type=checkbox name="{{k}}" {% if form[k] %}checked{% endif %}> {{k}}</label>
        {% endfor %}
        {% for k, opts in selects.items() %}
        <label class=f><span>{{k}}</span><select name="{{k}}">{% for o in opts %}<option value="{{o}}" {% if form[k]==o %}selected{% endif %}>{{o}}</option>{% endfor %}</select></label>
        {% endfor %}
        {% for k in texts %}
        <label class=f><span>{{k}}</span><input name="{{k}}" value="{{ form[k] }}"></label>
        {% endfor %}
        <label class=f><span>Cadence (systemd OnCalendar)</span><input name="cadence" value="{{ form.cadence }}"></label>

        <h2 style="margin-top:1.25rem">Secrets <span class=muted>(leave blank to keep current)</span></h2>
        {% for k in secrets %}
        <label class=f><span>{{k}} <span class=muted>· {{ form._secrets[k] }}</span></span><input type=password name="{{k}}" placeholder="•••• (unchanged)"></label>
        {% endfor %}
      </fieldset>
      {% if can_control %}<div class=row><button type=submit>Save &amp; apply</button></div>{% endif %}
    </form>
  </section>

  <section>
    <h2>Preview next post <span class=muted>· dry-run, never posts</span></h2>
    <form method=post action="/preview"><button {% if not has_password or can_control %}{% else %}{% endif %}type=submit>Generate preview</button></form>
    {% if preview %}{% if preview.error %}<p class=muted style="margin-top:1rem">{{ preview.error }}</p>
      {% else %}<div class=tweet style="margin-top:1rem">{{ preview.tweet }}</div><p class=muted>Image: {{ preview.image or '(none)' }}</p>{% endif %}{% endif %}
  </section>

  <section>
    <h2>Recent runs <span class=muted>· journalctl</span></h2>
    <pre>{{ logs }}</pre>
  </section>

  <p class=muted>Manage: <code>systemctl --user restart wayfumo-web</code> · <code>journalctl --user -u wayfumo-web -f</code></p>
</main></body></html>
"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8095, debug=False)
