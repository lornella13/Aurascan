"""Skin colour measured from real pixels, and the depth sanity check."""
import asyncio
import io

from PIL import Image

from app import vision
from app.skin import DEPTH_ORDER, measure_skin_hex, reconcile_depth

SKIN = (198, 150, 124)
HAIR = (40, 28, 22)
GLARE = (255, 255, 255)


def _photo(skin=SKIN, hair=HAIR, glare=GLARE, size=(400, 500)):
    """A synthetic portrait: skin face on a dark hair background, one white glare spot."""
    img = Image.new("RGB", size, hair)
    # Face fills most of the frame so box [0.2, 0.15, 0.8, 0.85] lands on skin.
    img.paste(Image.new("RGB", (int(size[0] * 0.6), int(size[1] * 0.7)), skin),
              (int(size[0] * 0.2), int(size[1] * 0.15)))
    # Glare blob inside the left cheek patch, bright enough to be trimmed.
    img.paste(Image.new("RGB", (24, 18), glare), (int(size[0] * 0.30), int(size[1] * 0.57)))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=95)
    return buf.getvalue()


BOX = [0.2, 0.15, 0.8, 0.85]


def _rgb(hex_colour):
    return tuple(int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))


def test_measures_skin_from_pixels():
    got = measure_skin_hex(_photo(), BOX)
    assert got is not None and got.startswith("#") and got == got.upper()
    for measured, expected in zip(_rgb(got), SKIN):
        assert abs(measured - expected) <= 6, f"{got} vs {SKIN}"


def test_glare_is_trimmed_not_averaged_in():
    """A naive mean would be pulled far too light by the white blob."""
    got = _rgb(measure_skin_hex(_photo(), BOX))
    assert got[0] < 215, f"glare leaked into the result: {got}"


def test_dark_skin_is_measured_not_lightened():
    dark = (74, 48, 36)
    got = _rgb(measure_skin_hex(_photo(skin=dark), BOX))
    for measured, expected in zip(got, dark):
        assert abs(measured - expected) <= 6, f"{got} vs {dark}"


def test_missing_box_returns_none():
    assert measure_skin_hex(_photo(), None) is None


def test_invalid_box_returns_none():
    assert measure_skin_hex(_photo(), [0.8, 0.15, 0.2, 0.85]) is None  # x reversed
    assert measure_skin_hex(_photo(), [0.5, 0.5, 0.5, 0.9]) is None    # zero width
    assert measure_skin_hex(_photo(), [1.4, 0.1, 1.9, 0.9]) is None   # out of range
    assert measure_skin_hex(_photo(), [0.1, 0.1]) is None             # wrong length


def test_tiny_image_returns_none():
    assert measure_skin_hex(_photo(size=(24, 30)), [0.2, 0.15, 0.8, 0.85]) is None


def test_reconcile_depth_only_on_big_disagreement():
    # measured luminance 205 -> "fair", model says "fair": agree.
    assert reconcile_depth("fair", "#E8C4B0") == "fair"
    # measured luminance 178 -> "light", one band from the model's "medium": trust the model.
    assert reconcile_depth("medium", "#D8A882") == "medium"
    # measured "fair" but model said "medium": two bands apart, so correct it.
    assert reconcile_depth("medium", "#E8C4B0") == "fair"
    # measured very dark but model said fair -> correct to the measured band.
    assert reconcile_depth("fair", "#4A3228") == "rich"  # luminance 56
    assert reconcile_depth("fair", "#6E4A38") == "deep"   # luminance 83
    # measured very light but model said rich -> correct.
    assert reconcile_depth("rich", "#F6E2D4") == "fair"
    assert reconcile_depth("fair", "not-a-colour") == "fair"


def test_depth_bands_ordered_consistently():
    for depth in DEPTH_ORDER:
        assert depth in DEPTH_ORDER


# ---- analyze_face fallback path ----

GOOD = ('{"photo_ok": true, "skin_type": "normal", "undertone": "warm", "depth": "medium",'
        ' "skin_hex": "#E8B8A5", "concerns": [], "eye_color": "brown", "hair_color": "black",'
        ' "lip_tone": "pink", "contrast": "medium", "confidence": 0.7}')


def _use_gemini(monkeypatch, text):
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)

    async def fake(payload):
        return {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    monkeypatch.setattr(vision, "_post_gemini", fake)


def test_measured_hex_overrides_model_estimate(monkeypatch):
    import json
    payload = json.loads(GOOD)
    payload["face_box"] = BOX
    _use_gemini(monkeypatch, json.dumps(payload))
    profile = asyncio.run(vision.analyze_face(_photo()))
    assert profile.skin_hex_source == "measured"
    assert profile.skin_hex == measure_skin_hex(_photo(), BOX)


def test_fallback_keeps_model_hex_when_no_box(monkeypatch):
    _use_gemini(monkeypatch, GOOD)
    profile = asyncio.run(vision.analyze_face(_photo()))
    assert profile.skin_hex_source == "estimated"
    assert profile.skin_hex == "#E8B8A5"


def test_invalid_box_degrades_to_estimate(monkeypatch):
    import json
    payload = json.loads(GOOD)
    payload["face_box"] = [0.9, 0.9, 0.5, 0.5]  # reversed: rejected by the schema
    _use_gemini(monkeypatch, json.dumps(payload))
    profile = asyncio.run(vision.analyze_face(_photo()))
    assert profile.skin_hex_source == "estimated"
    assert profile.skin_hex == "#E8B8A5"