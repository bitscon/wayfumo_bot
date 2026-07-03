import webapp


def test_health_ok():
    resp = webapp.app.test_client().get("/health")
    assert resp.status_code == 200
    assert resp.data == b"ok"


def test_index_renders(monkeypatch):
    # Stub the read-only shell-outs so the test is fast and offline.
    monkeypatch.setattr(webapp, "_run", lambda cmd: "stub")
    resp = webapp.app.test_client().get("/")
    assert resp.status_code == 200
    assert b"WAYFUMO" in resp.data
    assert b"Ops dashboard" in resp.data


def test_preview_handles_empty_store(monkeypatch):
    monkeypatch.setattr(webapp, "_run", lambda cmd: "stub")
    monkeypatch.setattr(webapp.content_builder, "build_clickbait_post", lambda: (None, None))
    resp = webapp.app.test_client().post("/preview")
    assert resp.status_code == 200
    assert b"Nothing to preview" in resp.data
