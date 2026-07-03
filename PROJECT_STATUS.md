# PROJECT STATUS

## Current State
Registered python-runtime bot; deployed on the barn via systemd user timer, running in DRY_RUN (builds posts, does not post to X). Offline unit test suite passing via `make test-fast`.

## Completed
- [ registered in AGENT_OS.md Section 17 ]
- [ bootstrap artifacts created (AGENTS.md, PROJECT_STATUS.md, docs/changes/) ]
- [ venv created and dependencies installed ]
- [ systemd user service + timer installed ]
- [ test suite added (Makefile test-fast, 18 offline unit tests) ]

## Next Steps
- Add products to the Printful store (bot exits "nothing to post" while empty)
- Set STORE_BASE_URL in .env to the real storefront (currently placeholder)
- Flip DRY_RUN=false in .env to go live once cadence is confirmed
- Enable timer persistence across reboot: sudo loginctl enable-linger billyb
