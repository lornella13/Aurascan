"""The app no longer serves garment images.

AuraScan used to proxy Unsplash photos for every garment card. Those endpoints
are gone: the app now links out to Pinterest and shows no images of its own, so
there is no third-party image API, no API key, and no outbound request at all for
a body result.

These tests guard that. If an image endpoint, an Unsplash reference or a stock
photo domain ever comes back, they fail.
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)

APP_DIR = Path(__file__).resolve().parent.parent / "app"
FRONTEND = Path(__file__).resolve().parent.parent.parent / "frontend" / "src"

# Hosts and terms that must not reappear now that images are gone.
BANNED_BACKEND = ("unsplash", "pexels", "client_id", "api/images", "api/dev")
BANNED_FRONTEND = (
    "unsplash",
    "pexels",
    "images.unsplash",
    "api/images",
    "api/dev",
    "/dev/curate",
)

# The wardrobe feature and its optional Pinterest pin embeds are gone too.
BANNED_WARDROBE_FRONTEND = (
    "lib/wardrobe",
    "PinEmbeds",
    "pinUrl",
    "validatePinUrl",
    "buildSearchQuery",
    "data-pin-do",
    "pinit.js",
    "Save to wardrobe",
)


def _sources(root: Path, pattern: str) -> list[Path]:
    return [p for p in root.rglob(pattern) if "node_modules" not in p.parts and ".git" not in p.parts]


# ---------- no image endpoints ----------


@pytest.mark.parametrize(
    "path",
    [
        "/api/images/status",
        "/api/images/types",
        "/api/images/clothing",
        "/api/images/curated",
        "/api/dev/curated",
        "/api/dev/search",
    ],
)
def test_image_endpoints_are_gone(path):
    assert client.get(path).status_code == 404


def test_health_still_works():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_no_image_routes_registered():
    paths = [getattr(r, "path", "") for r in app.routes]
    assert not [p for p in paths if p.startswith("/api/images")]
    assert not [p for p in paths if p.startswith("/api/dev")]


# ---------- no image credentials or dependencies ----------


def test_settings_expose_no_image_keys():
    fields = Settings_fields()
    assert "unsplash_access_key" not in fields
    assert "pexels_api_key" not in fields


def test_settings_expose_no_cache_or_dev_flags():
    fields = Settings_fields()
    assert "cache_dir" not in fields
    assert "unsplash_cache_dir" not in fields
    assert "enable_dev_tools" not in fields


def Settings_fields() -> set:
    from app.config import Settings

    return set(Settings.model_fields)


# ---------- no image code left behind ----------


def test_backend_source_has_no_image_references():
    offenders = []
    for path in _sources(APP_DIR, "*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for banned in BANNED_BACKEND:
            if banned in text:
                offenders.append(f"{path}: {banned}")
    assert not offenders, "backend still references images: " + "; ".join(offenders)


def test_frontend_source_has_no_image_references():
    root = FRONTEND
    offenders = []
    for path in _sources(root, "*.js") + _sources(root, "*.jsx"):
        text = path.read_text(encoding="utf-8").lower()
        for banned in BANNED_FRONTEND:
            if banned in text:
                offenders.append(f"{path}: {banned}")
    assert not offenders, "frontend still references images: " + "; ".join(offenders)


def test_env_files_have_no_image_keys():
    for name in (".env", ".env.example"):
        path = APP_DIR.parent / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for banned in ("unsplash", "pexels"):
            assert banned not in text, f"{name} still configures {banned}"


def test_image_data_files_are_gone():
    data = APP_DIR / "data"
    assert not data.exists(), f"stale image data directory: {sorted(data.glob('*'))}"


# ---------- the wardrobe is gone ----------


@pytest.mark.parametrize(
    "path",
    [
        "src/pages/WardrobePage.jsx",
        "src/lib/wardrobe.js",
        "src/components/PinEmbeds.jsx",
    ],
)
def test_wardrobe_files_are_deleted(path):
    assert not (FRONTEND / path).exists(), f"{path} should be deleted"


def test_frontend_has_no_wardrobe_code():
    offenders = []
    for path in _sources(FRONTEND, "*.js") + _sources(FRONTEND, "*.jsx"):
        text = path.read_text(encoding="utf-8").lower()
        for banned in BANNED_WARDROBE_FRONTEND:
            if banned.lower() in text:
                offenders.append(f"{path}: {banned}")
    assert not offenders, "wardrobe code came back: " + "; ".join(offenders)


def test_no_wardrobe_route_or_tab():
    app_src = (FRONTEND / "App.jsx").read_text(encoding="utf-8")
    assert "/wardrobe" not in app_src
    assert "WardrobePage" not in app_src
    assert "Wardrobe" not in app_src


def test_body_result_has_no_save_button():
    body = (FRONTEND / "components" / "BodyResult.jsx").read_text(encoding="utf-8").lower()
    # Match the actual save UI, not the word "save" in a comment.
    for banned in ("save to wardrobe", "aria-pressed", "additem", "issaved", "toggle()"):
        assert banned not in body, f"save UI came back: {banned}"
    assert "buildsearchurl" in body, "clothing items must still link to Pinterest"


def test_clothing_uses_the_plain_guide_cards():
    """Clothing reads like the Necklines/Fabrics cards: a heading and a list."""
    body = (FRONTEND / "components" / "BodyResult.jsx").read_text(encoding="utf-8")
    assert 'className="guide"' in body, "clothing must sit in the .guide grid"
    for dead in ("GarmentCard", "garment-card", "garment-grid", "garment-group"):
        assert dead not in body, f"{dead} came back"


def test_the_per_garment_colour_picker_stays_gone():
    """The palette section came back, but a colour picker per garment must not."""
    body = (FRONTEND / "components" / "BodyResult.jsx").read_text(encoding="utf-8")
    for dead in ('type="radio"', "garment-swatch", "garment-colour", "setColor"):
        assert dead not in body, f"per-garment colour UI came back: {dead}"
    assert not (FRONTEND / "components" / "GarmentCard.jsx").exists(), "GarmentCard should be deleted"


def test_the_palette_section_is_restored_above_the_guide():
    body = (FRONTEND / "components" / "BodyResult.jsx").read_text(encoding="utf-8")
    assert "SwatchStrip" in body, "the palette section must render"
    for strip in ("Wear these", "Easy neutrals", "Skip these"):
        assert strip in body, f"lost the {strip} strip"
    assert "Colours for you" in body
    # It has to come before the clothing guide, not after it.
    assert body.index("Colours for you") < body.index("What fits you")
    assert (FRONTEND / "components" / "SwatchStrip.jsx").exists()


def test_the_palette_section_tolerates_a_missing_palette():
    """A body result saved before the palette existed must still render."""
    body = (FRONTEND / "components" / "BodyResult.jsx").read_text(encoding="utf-8")
    assert "{palette ?" in body or "{palette &&" in body, "palette access must be guarded"


def test_dead_garment_card_css_is_gone():
    css = (FRONTEND / "index.css").read_text(encoding="utf-8").lower()
    assert "garment-" not in css, "the per-garment card CSS should stay deleted"
    # .swatches and .chip belong to the palette section, which is back.
    assert ".swatches" in css and ".chip" in css


def test_wardrobe_css_is_gone():
    css = (FRONTEND / "index.css").read_text(encoding="utf-8").lower()
    for banned in ("wardrobe-", "pin-embeds", "pin-section", "wardrobe {"):
        assert banned not in css, f"stale CSS: {banned}"


def test_landing_page_no_longer_mentions_the_wardrobe():
    landing = (FRONTEND / "pages" / "LandingPage.jsx").read_text(encoding="utf-8").lower()
    assert "wardrobe" not in landing
    assert "inspiration pin" not in landing
    # The Pinterest link disclosure stays.
    assert "pinterest" in landing


def test_orphaned_wardrobe_data_is_purged():
    storage = (FRONTEND / "lib" / "storage.js").read_text(encoding="utf-8")
    assert "aurascan:wardrobe" in storage
    app_src = (FRONTEND / "App.jsx").read_text(encoding="utf-8")
    assert "purgeRemovedFeatures" in app_src


# ---------- Pinterest links stay ----------




def test_pinterest_helper_survives():
    """The Pinterest link is the only image affordance left, so it must remain."""
    helper = FRONTEND / "lib" / "pinterest.js"
    assert helper.exists()
    text = helper.read_text(encoding="utf-8")
    assert "https://www.pinterest.com/search/pins/" in text
    assert "buildSearchUrl" in text


def test_clothing_items_link_out_to_pinterest():
    text = (FRONTEND / "components" / "BodyResult.jsx").read_text(encoding="utf-8")
    assert "buildSearchUrl" in text, "clothing items lost their Pinterest link"
    assert 'rel="noopener noreferrer"' in text, "links must open safely"
    assert "See on Pinterest" in text, "clothing items lost the link label"


def test_pinterest_helper_builds_a_plain_search_link():
    """Plain outbound link only: no Pinterest request is ever made for it."""
    text = (FRONTEND / "lib" / "pinterest.js").read_text(encoding="utf-8")
    assert "fetch(" not in text
    assert "XMLHttpRequest" not in text
    assert "encodeURIComponent" in text


def test_backend_still_never_contacts_pinterest():
    """Unchanged from before: the server never talks to Pinterest either."""
    offenders = []
    for path in _sources(APP_DIR, "*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for host in ("pinterest.com", "pin.it", "pinimg.com"):
            if host in text:
                offenders.append(f"{path}: {host}")
    assert not offenders, "backend references Pinterest: " + "; ".join(offenders)


def test_httpx_loggers_stay_quiet():
    import logging

    for name in ("httpx", "httpcore", "httpcore.http11", "httpcore.proxy"):
        assert logging.getLogger(name).level == logging.WARNING
