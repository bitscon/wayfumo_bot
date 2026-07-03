# CHANGE: Register + deploy wayfumo_bot on barn

Date: 2026-07-03
Type: governance
ADR: none — operational deploy of existing code; no architectural change (AGENT_OS §7)

## What changed

- /home/billyb/workspaces/AGENT_OS.md: registered `wayfumo_bot` in §17 registry as `python-runtime`, remote `bitscon/wayfumo_bot`, VPS `—`
- AGENTS.md: created (bootstrap standard §4 minimal template)
- PROJECT_STATUS.md: created (bootstrap standard §4 minimal template)
- docs/changes/: created + CHANGE-TEMPLATE.md added (from billy-runtime)
- venv/: created and requirements.txt installed (gitignored, project-local — not a system package)
- ~/.config/systemd/user/wayfumo.service: created (Type=oneshot, runs venv python, logs to journald)
- ~/.config/systemd/user/wayfumo.timer: created (daily 08:00, Persistent=true) — enabled + started

## Why

Bring the previously-unregistered bot into AGENT_OS compliance and run it on the barn via systemd (python-runtime deploy target, §8) instead of legacy cron.

## Risk

LOW

Deployed in DRY_RUN=true — the bot builds posts but cannot post to X (verified in code: post_to_x returns early on DRY_RUN). No secrets, ADRs, or sibling projects touched. Reversible: `systemctl --user disable --now wayfumo.timer` + remove unit files.

## Verified

- [x] Behavior matches intent — service ran under systemd: Result=success, ExecMainStatus=0, DRY_RUN respected, journald captured output
- [x] No regressions observed — no product/application code changed
- [ ] Tests pass — N/A: no automated test suite exists. python-runtime requires tests (§8) — logged as a gap in PROJECT_STATUS Next Steps. Verification was a DRY_RUN smoke run (CLI + systemd) plus the printful_client self-check.

## Notes

- Printful store returns HTTP 200 with 0 products → token authenticates, store is empty. Bot exits cleanly with "Nothing to post" until products are added (operator content task).
- STORE_BASE_URL is still the placeholder `https://yourstore.printful.me` (operator config).
- Timer persistence across logout/reboot requires one-time `sudo loginctl enable-linger billyb` (operator, needs sudo).
