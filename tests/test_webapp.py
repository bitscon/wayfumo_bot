import pytest

import webapp


@pytest.fixture
def client(monkeypatch):
    # Default: no password -> view-only mode. Stub read-only shell-outs.
    monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
    monkeypatch.setattr(webapp, "_run", lambda *a, **k: "stub")
    return webapp.app.test_client()


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.data == b"ok"


def test_index_view_only(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"WAYFUMO" in resp.data
    assert b"controls are disabled" in resp.data.lower()


def test_controls_blocked_without_password(client):
    for path in ("/config", "/run", "/redeploy"):
        assert client.post(path).status_code == 403


def test_preview_handles_empty_store(client, monkeypatch):
    monkeypatch.setattr(webapp.content_builder, "build_clickbait_post", lambda: (None, None))
    resp = client.post("/preview")
    assert resp.status_code == 200
    assert b"Nothing to preview" in resp.data


def test_login_required_when_password_set(monkeypatch):
    monkeypatch.setenv("DASHBOARD_PASSWORD", "secret")
    monkeypatch.setattr(webapp, "_run", lambda *a, **k: "stub")
    resp = webapp.app.test_client().get("/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_login_success_enables_control(monkeypatch):
    monkeypatch.setenv("DASHBOARD_PASSWORD", "secret")
    monkeypatch.setattr(webapp, "_run", lambda *a, **k: "stub")
    c = webapp.app.test_client()
    assert c.post("/login", data={"password": "nope"}).status_code == 200  # re-renders login
    resp = c.post("/login", data={"password": "secret"})
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/")
    assert c.get("/").status_code == 200  # now authed
