import llm_provider as llm


def test_generate_returns_empty_on_provider_error(monkeypatch):
    monkeypatch.setattr(llm.config, "LLM_PROVIDER", "ollama")

    def boom(prompt):
        raise llm.LLMError("provider down")

    monkeypatch.setattr(llm, "_generate_ollama", boom)
    assert llm.generate("hi") == ""


def test_generate_dispatches_to_openrouter(monkeypatch):
    monkeypatch.setattr(llm.config, "LLM_PROVIDER", "openrouter")
    monkeypatch.setattr(llm, "_generate_openrouter", lambda p: "OR:" + p)
    assert llm.generate("ping") == "OR:ping"


def test_generate_dispatches_to_ollama_by_default(monkeypatch):
    monkeypatch.setattr(llm.config, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(llm, "_generate_ollama", lambda p: "OL:" + p)
    assert llm.generate("ping") == "OL:ping"
