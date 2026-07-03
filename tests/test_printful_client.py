import printful_client as pf


SAMPLE_DETAIL = {
    "sync_product": {"id": 7, "name": "Dragon Tee", "thumbnail_url": "http://img/thumb.png"},
    "sync_variants": [
        {
            "retail_price": "24.00",
            "currency": "USD",
            "files": [
                {"type": "default", "preview_url": "http://img/default.png"},
                {"type": "preview", "preview_url": "http://img/preview.png"},
            ],
        }
    ],
}


def test_extract_image_url_prefers_preview():
    assert pf._extract_image_url(SAMPLE_DETAIL) == "http://img/preview.png"


def test_extract_image_url_falls_back_to_thumbnail():
    detail = {"sync_product": {"thumbnail_url": "http://img/thumb.png"}, "sync_variants": []}
    assert pf._extract_image_url(detail) == "http://img/thumb.png"


def test_normalize_maps_fields_and_override():
    product = pf._normalize(SAMPLE_DETAIL, {"7": "product/dragon"})
    assert product["id"] == 7
    assert product["name"] == "Dragon Tee"
    assert product["price"] == "24.00"
    assert product["currency"] == "USD"
    assert product["image_url"] == "http://img/preview.png"
    assert product["path_override"] == "product/dragon"


def test_normalize_name_fallback_when_missing():
    detail = {"sync_product": {"id": 1}, "sync_variants": []}
    product = pf._normalize(detail, {})
    assert product["name"] == "our latest drop"
    assert product["path_override"] is None


def test_pick_product_returns_none_when_store_empty(monkeypatch):
    monkeypatch.setattr(pf, "list_products", lambda: [])
    assert pf.pick_product("random") is None
