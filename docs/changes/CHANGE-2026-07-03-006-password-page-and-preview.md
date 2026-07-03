# CHANGE: Change-password page + real post preview

Date: 2026-07-03
Type: feature
ADR: ADR-0002 (within the accepted control-panel scope)

## What changed

- webapp.py:
  - Added a dedicated /password page (verifies current password, requires new
    ≥ 6 chars and matching confirmation, then writes .env + restarts the panel).
    Added a "Change password" link in the header.
  - Removed DASHBOARD_PASSWORD from the generic API-tokens form so there is one
    clear, verified place to change it.
  - Reworked the preview into a real post card: the composed tweet rendered in a
    tweet-style card with the actual product mockup image, plus char count
    (X-effective), voice, product, and price.
- content_builder.py: added build_preview() returning the post details (tweet,
  image_url, product, price, voice, link) without downloading; build_clickbait_post()
  now reuses it, so the preview matches exactly what would post.
- tests: password flow (wrong current / mismatch / too short / success), preview
  card render, and build_preview unit tests.

## Why

Operator asked for a dedicated change-password page and a real visual preview of
the post for verification (the old preview only showed text + a file path).

## Risk

LOW

Change-password verifies the current password before writing. Preview is
read-only (dry-run, never posts); the mockup image loads from Printful's CDN
over the LAN.

## Verified

- [x] Tests pass — `make test-fast`: 32 passed
- [x] Behavior matches intent — /password gated (302 → login when unauth), renders after login, rejects wrong/short/mismatched input, writes on success; live preview endpoint renders correctly
- [x] No regressions observed — build_clickbait_post() behavior preserved; bot untouched

## Note

The Printful store currently has 0 products, so a live preview shows
"No products in the Printful store". Add a product in Printful and the preview
renders the real post (copy + mockup image).
