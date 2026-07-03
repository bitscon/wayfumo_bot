# CHANGE: Read-only ops dashboard (Flask)

Date: 2026-07-03
Type: feature
ADR: ADR-0001

## What changed

- webapp.py: single-file, read-only Flask dashboard — config (masked), systemd
  timer/run status, recent journald logs, and a dry-run "preview next post"
- tests/test_webapp.py: 3 offline tests (health, index render, empty-store preview)
- requirements.txt: add flask==3.1.3, gunicorn==26.0.0
- ~/.config/systemd/user/wayfumo-web.service: gunicorn on 127.0.0.1:8095 (enabled + started)
- docs/adr/: ADR-0001 (new subsystem) + ADR-TEMPLATE + ADR_INDEX
- nginx vhost wayfumo-bot.barn.workshop.home: flip static -> proxy_pass 127.0.0.1:8095
  (mechanism: scratchpad/apply-wayfumo-web-proxy.sh; applied by operator via sudo)
- PROJECT_STATUS.md: updated

## Why

Give the headless bot visibility (status/logs) and a safe dry-run preview of the
next post, per the operator's choice of an ops dashboard. Read-only by design to
keep it simple and low-risk.

## Risk

LOW

Read-only app, localhost-bound, behind nginx on the private network. No posting,
no config mutation. New long-running service is Restart=on-failure. Reversible
(disable the unit; restore the vhost .bak).

## Verified

- [x] Tests pass — `make test-fast`: 21 passed
- [x] Behavior matches intent — wayfumo-web.service active; /health 200; / renders the dashboard on 127.0.0.1:8095
- [x] No regressions observed — bot + timer untouched; existing tests still green

## Follow-up (operator)

- Run the nginx flip (needs sudo) to make the dashboard reachable at the hostname:
  `sudo bash <scratchpad>/apply-wayfumo-web-proxy.sh`
- Until then the hostname still serves the static placeholder; the dashboard is
  live on 127.0.0.1:8095.
