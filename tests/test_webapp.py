import pytest

import webapp


@pytest.fixture
def client(monkeypatch):
    # No password -> view-only mode. Stub read-only shell-outs.
    monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
    monkeypatch.setattr(webapp, "_run", lambda *a, **k: "stub")
    return webapp.app.test_client()


@pytest.fixture
def authed(monkeypatch):
    monkeypatch.setenv("DASHBOARD_PASSWORD", "secret")
    monkeypatch.setattr(webapp, "_run", lambda *a, **k: "stub")
    c = webapp.app.test_client()
    c.post("/login", data={"password": "secret"})
    return c


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200 and resp.data == b"ok"


def test_index_view_only(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"WAYFUMO" in resp.data
    assert b"controls are disabled" in resp.data.lower()


def test_controls_blocked_without_password(client):
    for path in ("/config", "/run", "/redeploy", "/password"):
        assert client.post(path).status_code == 403


def test_preview_empty_store(client, monkeypatch):
    monkeypatch.setattr(webapp.content_builder, "build_preview", lambda: None)
    resp = client.post("/preview")
    assert resp.status_code == 200
    assert b"No products in the Printful store" in resp.data


def test_preview_renders_card(client, monkeypatch):
    monkeypatch.setattr(webapp.content_builder, "build_preview", lambda: {
        "tweet": "Buy this now https://s.example?x", "image_url": "http://img/x.png",
        "product": "Dragon Tee", "price": "$24", "voice": "hype",
        "link": "https://s.example?x"})
    resp = client.post("/preview")
    assert resp.status_code == 200
    assert b"Buy this now" in resp.data
    assert b"http://img/x.png" in resp.data      # image rendered
    assert b"Dragon Tee" in resp.data            # product meta shown


def test_login_required_when_password_set(monkeypatch):
    monkeypatch.setenv("DASHBOARD_PASSWORD", "secret")
    monkeypatch.setattr(webapp, "_run", lambda *a, **k: "stub")
    resp = webapp.app.test_client().get("/")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]


def test_login_success_enables_control(authed):
    assert b"Save &amp; apply" in authed.get("/").data


def test_password_page_renders_for_authed(authed):
    resp = authed.get("/password")
    assert resp.status_code == 200
    assert b"Change dashboard password" in resp.data


def test_change_password_rejects_wrong_current(authed):
    resp = authed.post("/password", data={"current": "wrong", "new": "abcdef", "confirm": "abcdef"})
    assert resp.status_code == 200 and b"Current password is incorrect" in resp.data


def test_change_password_rejects_mismatch(authed):
    resp = authed.post("/password", data={"current": "secret", "new": "abcdef", "confirm": "abcXYZ"})
    assert resp.status_code == 200 and b"do not match" in resp.data


def test_change_password_rejects_short(authed):
    resp = authed.post("/password", data={"current": "secret", "new": "abc", "confirm": "abc"})
    assert resp.status_code == 200 and b"at least 6" in resp.data


def test_change_password_success(authed, monkeypatch):
    recorded = {}
    monkeypatch.setattr(webapp, "update_env", lambda changes: recorded.update(changes))
    monkeypatch.setattr(webapp, "_restart_panel", lambda: None)
    resp = authed.post("/password", data={"current": "secret", "new": "newpass123", "confirm": "newpass123"})
    assert resp.status_code == 302
    assert recorded.get("DASHBOARD_PASSWORD") == "newpass123"
