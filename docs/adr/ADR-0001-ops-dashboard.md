# ADR-0001: Internal read-only ops dashboard for WAYFUMO

Status: Superseded by ADR-0002
Date: 2026-07-03

## Context

The WAYFUMO bot is a headless python-runtime job (systemd timer) with no
visibility beyond journald and no way to see what it would post before it goes
live. The nginx vhost `wayfumo-bot.barn.workshop.home` was stood up as a static
placeholder. Everything lives on the private barn network.

## Decision

Add a minimal, read-only web dashboard as a new subsystem, kept deliberately
small — one file, one venv, one service — for easy maintenance:

- `webapp.py` — a single-file Flask app that reuses the bot's own modules
  (`config`, `content_builder`) and shells out to `systemctl`/`journalctl` for
  status.
- Served by gunicorn on `127.0.0.1:8095` via a systemd user unit
  (`wayfumo-web.service`).
- The existing nginx vhost is flipped from static root to
  `proxy_pass -> 127.0.0.1:8095`.
- Scope is **read-only**: it shows config (secrets masked), timer/run status,
  recent logs, and a dry-run "preview next post" that builds copy without
  posting. No config mutation, no posting.

## Consequences

- Visibility and pre-post preview with minimal new surface.
- Easy to manage: `systemctl --user restart wayfumo-web`; edit one file.
- Adds a long-running service and web deps (flask, gunicorn) to the venv.
- The app has **no authentication** — access control is delegated to the private
  network + nginx. Any future control/mutating action (post now, toggle
  DRY_RUN, approvals) MUST be introduced via a superseding ADR that also adds
  authentication.
