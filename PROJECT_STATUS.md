# PROJECT STATUS

## Current State
Registered python-runtime bot; deployed on the barn via systemd user timer, running in DRY_RUN (builds posts, does not post to X). Offline unit test suite passing via `make test-fast`. Password-gated control panel (Flask/gunicorn, wayfumo-web.service) on 127.0.0.1:8095 — edit config, redeploy, run, and monitor the bot; reachable at http://wayfumo-bot.barn.workshop.home once the nginx proxy flip is applied.

## Completed
- [ registered in AGENT_OS.md Section 17 ]
- [ bootstrap artifacts created (AGENTS.md, PROJECT_STATUS.md, docs/changes/) ]
- [ venv created and dependencies installed ]
- [ systemd user service + timer installed ]
- [ test suite added (Makefile test-fast, 21 offline unit tests) ]
- [ read-only ops dashboard added (webapp.py, ADR-0001) ]
- [ control panel added — config edit + redeploy + auth (webapp.py, ADR-0002) ]

## Next Steps
- Apply the nginx proxy flip (sudo): scratchpad/apply-wayfumo-web-proxy.sh
- Add products to the Printful store (bot exits "nothing to post" while empty)
- Set STORE_BASE_URL in .env to the real storefront (currently placeholder)
- Flip DRY_RUN=false in .env to go live once cadence is confirmed
- Enable timer persistence across reboot: sudo loginctl enable-linger billyb
