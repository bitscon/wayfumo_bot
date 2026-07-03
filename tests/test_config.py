import config


def test_bool_truthy_values(monkeypatch):
    for val in ("1", "true", "TRUE", "Yes", "on", " On "):
        monkeypatch.setenv("WAYFUMO_TEST_FLAG", val)
        assert config._bool("WAYFUMO_TEST_FLAG") is True


def test_bool_falsey_values(monkeypatch):
    for val in ("0", "false", "no", "off", "", "maybe"):
        monkeypatch.setenv("WAYFUMO_TEST_FLAG", val)
        assert config._bool("WAYFUMO_TEST_FLAG") is False


def test_bool_default_when_unset(monkeypatch):
    monkeypatch.delenv("WAYFUMO_TEST_FLAG", raising=False)
    assert config._bool("WAYFUMO_TEST_FLAG", "true") is True
    assert config._bool("WAYFUMO_TEST_FLAG", "false") is False
