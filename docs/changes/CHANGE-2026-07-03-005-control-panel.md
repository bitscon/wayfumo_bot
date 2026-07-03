# CHANGE: Control panel (configure / control / monitor)

Date: 2026-07-03
Type: feature
ADR: ADR-0002

## What changed

- webapp.py: extended the read-only dashboard into a password-gated control
  panel — editable config form (writes .env), cadence edit (writes
  wayfumo.timer), Save & apply / Run now / Redeploy controls, login+session
  auth. Monitoring and dry-run preview retained.
- tests/test_webapp.py: view-only vs authed control, login flow, 403-without-password, preview
- ~/.config/systemd/user/wayfumo-web.service: gunicorn --timeout 120 (redeploy can exceed the 30s default)
- .env: added DASHBOARD_PASSWORD + DASHBOARD_SECRET (gitignored; not committed)
- docs/adr/: ADR-0002 added; ADR-0001 marked Superseded; ADR_INDEX updated
- PROJECT_STATUS.md updated

## Why

The operator needs to change configuration and redeploy from the site to control
and monitor the bot; the read-only dashboard (ADR-0001) did not allow that.

## Risk

MEDIUM

The panel can rewrite .env, flip DRY_RUN to LIVE, trigger real X posts, and
redeploy. Mitigations: fail-closed password gate (no password ⇒ view-only),
LAN-only via nginx, runs unprivileged (user systemd), git pull is --ff-only.
No CSRF tokens (internal tool) — documented in ADR-0002.

## Verified

- [x] Tests pass — `make test-fast`: 24 passed
- [x] Behavior matches intent — / redirects to /login when password set; correct password unlocks Save/Run/Redeploy; wrong password rejected; /health open; panel active on 127.0.0.1:8095
- [x] No regressions observed — bot + timer untouched; existing tests green
