"""Minimal Printful Store API client.

Fetches products from your Printful store and normalizes them into a simple
dict the rest of the bot can consume without knowing Printful's response
shapes. Only two endpoints are used:

    GET /store/products        -> list of sync products
    GET /store/products/{id}   -> one sync product + its variants

Auth is a Bearer token (Printful dashboard -> Settings -> Developers). Account
level tokens also need the store id, sent as the X-PF-Store-Id header.
"""

import json
import os
import random
from datetime import datetime, timezone

import requests

import config

_LINKS_FILE = os.path.join(os.path.dirname(__file__), "product_links.json")


class PrintfulError(Exception):
    """Raised when the Printful API call fails or the store is misconfigured."""


def _headers():
    if not config.PRINTFUL_TOKEN:
        raise PrintfulError("PRINTFUL_TOKEN is not set")
    headers = {"Authorization": f"Bearer {config.PRINTFUL_TOKEN}"}
    if config.PRINTFUL_STORE_ID:
        headers["X-PF-Store-Id"] = config.PRINTFUL_STORE_ID
    return headers


def _get(path, params=None):
    url = f"{config.PRINTFUL_API_BASE}{path}"
    try:
        resp = requests.get(
            url, headers=_headers(), params=params, timeout=config.HTTP_TIMEOUT
        )
    except requests.RequestException as exc:
        raise PrintfulError(f"request to {url} failed: {exc}") from exc
    if not resp.ok:
        raise PrintfulError(f"{url} returned HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json().get("result", [])


def list_products():
    """Return all sync products in the store (handles simple pagination)."""
    products = []
    offset = 0
    limit = 100
    while True:
        batch = _get("/store/products", params={"offset": offset, "limit": limit})
        products.extend(batch)
        # Printful returns fewer than `limit` items on the last page.
        if len(batch) < limit:
            break
        offset += limit
    return products


def get_product(sync_product_id):
    """Return the detail payload {sync_product, sync_variants} for one product."""
    return _get(f"/store/products/{sync_product_id}")


def _load_link_overrides():
    """Return the optional {sync_product_id: path} deep-link map, or {}."""
    try:
        with open(_LINKS_FILE) as fh:
            # JSON keys are strings; normalize to str for lookup.
            return {str(k): v for k, v in json.load(fh).items()}
    except (FileNotFoundError, ValueError):
        return {}


def _extract_image_url(detail):
    """Pick the best mockup image from a product detail payload."""
    variants = detail.get("sync_variants") or []
    for variant in variants:
        for f in variant.get("files") or []:
            if f.get("type") == "preview":
                return f.get("preview_url") or f.get("thumbnail_url")
    # Fall back to the product-level thumbnail.
    return (detail.get("sync_product") or {}).get("thumbnail_url")


def _normalize(detail, overrides):
    """Turn a product detail payload into the bot's simple product dict."""
    product = detail.get("sync_product") or {}
    variants = detail.get("sync_variants") or []
    first = variants[0] if variants else {}
    pid = product.get("id")
    return {
        "id": pid,
        "name": product.get("name") or "our latest drop",
        "price": first.get("retail_price"),
        "currency": first.get("currency") or "USD",
        "image_url": _extract_image_url(detail),
        "path_override": overrides.get(str(pid)),
    }


def pick_product(strategy="random"):
    """Pick one product and return the normalized dict, or None if none exist.

    strategy:
        "random" - random.choice over the catalog.
        "rotate" - deterministic day-of-year rotation (no state file needed).
    """
    products = list_products()
    if not products:
        return None

    if strategy == "rotate":
        day = datetime.now(timezone.utc).timetuple().tm_yday
        chosen = products[day % len(products)]
    else:
        chosen = random.choice(products)

    detail = get_product(chosen["id"])
    return _normalize(detail, _load_link_overrides())


if __name__ == "__main__":
    try:
        catalog = list_products()
        print(f"Store has {len(catalog)} product(s).")
        picked = pick_product(config.PRODUCT_STRATEGY)
        if picked:
            print("Picked product:")
            print(json.dumps(picked, indent=2))
            if picked["image_url"]:
                head = requests.head(picked["image_url"], timeout=config.HTTP_TIMEOUT)
                print("Image URL status:", head.status_code)
        else:
            print("No products found — store empty or misconfigured.")
    except PrintfulError as exc:
        print("Printful error:", exc)
