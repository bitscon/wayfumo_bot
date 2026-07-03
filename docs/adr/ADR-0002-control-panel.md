# ADR-0002: Control panel supersedes the read-only dashboard

Status: Accepted
Date: 2026-07-03
Supersedes: ADR-0001

## Context

ADR-0001 delivered a read-only dashboard. The operator needs to change the
bot's configuration, redeploy, and control/monitor it from the site — not just
view it. That crosses the mutation/security boundary ADR-0001 deliberately
avoided, so it requires a superseding decision.

## Decision

Extend the same single-file Flask app (`webapp.py`) into a control panel, kept
to one file / one venv / one service:

- **Configure** — an editable form writes `.env` (behavior toggles,
  provider/model, store URL, UTM) and the systemd timer cadence. Secrets are
  write-only: shown as set/unset, changed only when a new value is typed.
- **Control** — Save & apply (write config + restart the bot), Run now (trigger
  one run, with a confirm), Redeploy (`git pull --ff-only` + `pip install` +
  restart).
- **Monitor** — status, logs, dry-run preview (unchanged from ADR-0001).
- **Auth** — a single shared password (`DASHBOARD_PASSWORD` in `.env`) gates the
  whole panel via a login + session cookie (`DASHBOARD_SECRET`). If the password
  is unset, the panel is view-only and every control route returns 403 (fail
  closed).

Runs as the billyb user, so all actions work without sudo.

## Consequences

- Full control + monitoring from the browser, no sudo.
- Fail-closed: no password ⇒ no control.
- The panel can flip `DRY_RUN` to LIVE and post to X — protected only by the LAN
  + the shared password. Keep it strong; rotate by editing `DASHBOARD_PASSWORD`.
- No CSRF tokens (internal single-user tool). Residual risk: a logged-in
  operator visiting a hostile page. Acceptable on the private barn network;
  revisit if the panel is ever exposed more widely (superseding ADR).
- Redeploy uses `--ff-only`, so a diverged local tree makes it a safe no-op with
  a message rather than forcing.
