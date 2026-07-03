# CHANGE: nginx vhost + placeholder for wayfumo-bot site

Date: 2026-07-03
Type: feature
ADR: none — barn infra/config, no repo architecture change (AGENT_OS §7)

## What changed

Barn-side (outside the repo; documented here for observability, AGENT_OS §13):
- /etc/nginx/sites-available/wayfumo-bot.barn.workshop.home: new plain-HTTP vhost, static root at /var/www/wayfumo-bot, with a commented proxy_pass block for later conversion
- /etc/nginx/sites-enabled/wayfumo-bot.barn.workshop.home: symlink enabling the site
- /var/www/wayfumo-bot/index.html: "coming soon" placeholder page (www-data)
- /etc/hosts: barn-local A entry 192.168.1.188 wayfumo-bot.barn.workshop.home (for local resolution/testing)

Repo:
- docs/changes/: this Change Record
- PROJECT_STATUS.md: noted the placeholder site

## Why

Stand up the web presence at wayfumo-bot.barn.workshop.home before designing the site. Hostname reconciled to barn convention (‹name›.barn.workshop.home, hyphen not underscore) per operator decision; original request was wayfumo_bot.workshop.home.

## Risk

LOW

Additive vhost only; nginx -t passed before reload; sibling vhosts unaffected. Plain HTTP (matches the kanboard precedent). Reversible via the teardown block in the apply script. No secrets, no code changed.

## Verified

- [x] Behavior matches intent — HTTP 200 serving the placeholder; 404 on unknown paths; access log records hits
- [x] No regressions observed — reload succeeded; existing vhosts still resolve and serve
- [ ] Tests pass — N/A (infra config; no application code changed)

## Notes / follow-ups (operator)

- DNS: add A record wayfumo-bot.barn.workshop.home -> 192.168.1.188 on the workshop.home DNS server so non-barn clients resolve it (only /etc/hosts is set today).
- Running nginx master is 1.29.7 while the installed binary is 1.31.2 (reloaded, never restarted). `systemctl restart nginx` picks up 1.31.2 but briefly drops all sites.
- No web backend exists yet — vhost serves static placeholder; convert `location /` to proxy_pass when the app has a port.
