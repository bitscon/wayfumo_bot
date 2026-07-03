import content_builder as cb


def test_fit_tweet_truncates_but_keeps_link_and_brand():
    long_copy = "word " * 120  # ~600 chars
    link = "https://store.example?utm_source=x&utm_medium=social&utm_campaign=clickbait"
    tags = ["#WAYFUMO", "#Tee", "#Merch"]
    result = cb.fit_tweet(long_copy, link, tags)
    assert cb._effective_len(result, link) <= cb.TWEET_LIMIT
    assert link in result
    assert "#WAYFUMO" in result


def test_fit_tweet_strips_model_added_url_and_hashtag():
    link = "https://store.example?utm_source=x"
    tags = ["#WAYFUMO"]
    dirty = "Check it out http://spam.example #Random amazing deal"
    cleaned = cb.fit_tweet(dirty, link, tags)
    assert "spam.example" not in cleaned
    assert "#Random" not in cleaned


def test_strip_model_extras_removes_urls_and_hashtags():
    out = cb._strip_model_extras('Deal https://x.io now #Hype extra')
    assert "https://x.io" not in out
    assert "#Hype" not in out
    assert "Deal" in out and "now" in out


def test_derive_hashtags_skips_stopwords_and_caps_at_three():
    product = {"name": "Premium Unisex Dragon Hoodie"}
    tags = cb._derive_hashtags(product)
    assert tags[0] == "#WAYFUMO"
    assert len(tags) <= 3
    assert "#Dragon" in tags       # meaningful word survives
    assert "#Premium" not in tags  # stopword excluded


def test_format_price_symbol_and_fallback():
    assert cb._format_price({"price": "25.00", "currency": "USD"}) == "$25.00"
    assert cb._format_price({"price": "20", "currency": "EUR"}) == "€20"
    assert cb._format_price({"price": None}) == "a steal"


def test_build_store_link_adds_utm_and_path(monkeypatch):
    monkeypatch.setattr(cb.config, "STORE_BASE_URL", "https://store.example")
    monkeypatch.setattr(cb.config, "UTM_CAMPAIGN", "clickbait")
    link = cb.build_store_link({"path_override": "product/42"})
    assert link.startswith("https://store.example/product/42?")
    assert "utm_source=x" in link
    assert "utm_campaign=clickbait" in link


def test_build_store_link_separator_when_base_has_query(monkeypatch):
    monkeypatch.setattr(cb.config, "STORE_BASE_URL", "https://store.example?ref=1")
    link = cb.build_store_link({})
    assert "?ref=1&utm_source=x" in link


def test_build_preview_none_when_store_empty(monkeypatch):
    monkeypatch.setattr(cb.printful_client, "pick_product", lambda s: None)
    assert cb.build_preview() is None


def test_build_preview_returns_details(monkeypatch):
    prod = {"id": 1, "name": "Dragon Tee", "price": "24.00", "currency": "USD",
            "image_url": "http://img/x.png", "path_override": None}
    monkeypatch.setattr(cb.printful_client, "pick_product", lambda s: prod)
    monkeypatch.setattr(cb.llm_provider, "generate", lambda p: "Buy this now")
    monkeypatch.setattr(cb.config, "VOICE_MODE", "hype")
    d = cb.build_preview()
    assert d["product"] == "Dragon Tee"
    assert d["image_url"] == "http://img/x.png"
    assert d["voice"] == "hype"
    assert "http" in d["link"] and d["tweet"]
