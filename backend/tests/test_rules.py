import itertools
import io

from fastapi.testclient import TestClient
from PIL import Image

from app import vision
from app.main import app
from app.rules.makeup import build_routine
from app.rules.style import CLOTHING, PALETTES, pick_season
from app.schemas import BodyProfile, Coloring, FaceProfile

UNDERTONES = ["warm", "cool", "neutral", "olive"]
DEPTHS = ["fair", "light", "medium", "tan", "deep", "rich"]
SKINS = ["oily", "dry", "combination", "normal", "sensitive"]


def face(**kw):
    base = dict(skin_type="normal", undertone="warm", depth="medium", skin_hex="#C68E6B",
                concerns=[], eye_color="brown", hair_color="black", lip_tone="rose",
                contrast="medium", confidence=0.9)
    base.update(kw)
    return FaceProfile(**base)


def test_routine_covers_every_combination():
    for u, d, s in itertools.product(UNDERTONES, DEPTHS, SKINS):
        routine, tips = build_routine(face(undertone=u, depth=d, skin_type=s))
        cats = [r.category for r in routine]
        assert cats[:3] == ["Primer", "Foundation", "Concealer"]
        assert "Eyeshadow" in cats and "Lips" in cats
        assert [r.order for r in routine] == list(range(1, len(routine) + 1))
        assert tips


def test_concerns_change_products():
    routine, _ = build_routine(face(concerns=["dark_circles", "redness"]))
    assert "Green-tinted" in routine[0].product
    assert "corrector" in routine[2].shade_or_finish.lower()


def test_season_and_palettes():
    assert pick_season("warm", "light", "medium") == "spring"
    assert pick_season("warm", "deep", "medium") == "autumn"
    assert pick_season("cool", "light", "low") == "summer"
    assert pick_season("cool", "deep", "high") == "winter"
    for u, d in itertools.product(UNDERTONES, DEPTHS):
        assert pick_season(u, d, "medium") in PALETTES


def test_every_body_shape_has_a_guide():
    for shape in ["hourglass", "pear", "apple", "rectangle", "inverted_triangle"]:
        assert CLOTHING[shape].tops and CLOTHING[shape].avoid


def _jpeg():
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), (200, 160, 140)).save(buf, "JPEG")
    return buf.getvalue()


def test_endpoints_with_mocked_vision(monkeypatch):
    async def fake_face(_):
        return face()

    async def fake_body(_):
        return BodyProfile(body_shape="pear", shoulder_vs_hip="hips_wider", waist_definition="defined",
                           torso_vs_legs="balanced", coloring=Coloring(undertone="cool", depth="light", contrast="low"),
                           confidence=0.8)

    monkeypatch.setattr(vision, "analyze_face", fake_face)
    monkeypatch.setattr(vision, "analyze_body", fake_body)
    client = TestClient(app)

    r = client.post("/api/analyze/face", files={"file": ("f.jpg", _jpeg(), "image/jpeg")})
    assert r.status_code == 200 and r.json()["routine"]

    r = client.post("/api/analyze/body", files={"file": ("b.jpg", _jpeg(), "image/jpeg")})
    assert r.status_code == 200
    assert r.json()["palette"]["season"] == "summer" and r.json()["palette_source"] == "this_photo"

    # The body photo reads cool, so a warm face scan must NOT override it.
    r = client.post("/api/analyze/body", files={"file": ("b.jpg", _jpeg(), "image/jpeg")},
                    data={"face_profile": face(undertone="warm", depth="light").model_dump_json()})
    assert r.json()["palette_source"] == "this_photo"

    # An agreeing face scan refines the undertone only. The body photo reads
    # cool/light/low, so the palette follows that photo, not the face scan's
    # richer depth.
    agreeing = client.post("/api/analyze/body", files={"file": ("b.jpg", _jpeg(), "image/jpeg")},
                           data={"face_profile": face(undertone="cool", depth="rich").model_dump_json()})
    assert agreeing.json()["palette_source"] == "face_scan_undertone"
    assert agreeing.json()["palette"]["season"] == pick_season("cool", "light", "low")

    r = client.post("/api/analyze/face", files={"file": ("f.txt", b"hi", "text/plain")})
    assert r.status_code == 415


# ---- vision layer (network mocked) ----
import asyncio
import pytest


def _gemini_reply(text):
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def test_gemini_parses_profile(monkeypatch):
    good = ('{"photo_ok": true, "skin_type": "dry", "undertone": "cool", "depth": "light", "skin_hex": "#E8C4B0",'
            ' "concerns": ["redness"], "eye_color": "green", "hair_color": "blonde", "lip_tone": "pink",'
            ' "contrast": "low", "confidence": 0.8}')

    async def fake_post(payload):
        assert payload["generationConfig"]["responseMimeType"] == "application/json"
        return _gemini_reply("```json\n" + good + "\n```")

    monkeypatch.setattr(vision, "_post_gemini", fake_post)
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)
    profile = asyncio.run(vision.analyze_face(b"x"))
    assert profile.skin_type == "dry" and profile.concerns == ["redness"]


def test_gemini_photo_rejected_and_blocked(monkeypatch):
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)

    async def rejected(_):
        return _gemini_reply('{"photo_ok": false, "photo_issue": "Too dark."}')

    async def blocked(_):
        return {"promptFeedback": {"blockReason": "OTHER"}}

    monkeypatch.setattr(vision, "_post_gemini", rejected)
    with pytest.raises(vision.PhotoRejected, match="Too dark"):
        asyncio.run(vision.analyze_face(b"x"))
    monkeypatch.setattr(vision, "_post_gemini", blocked)
    with pytest.raises(vision.PhotoRejected):
        asyncio.run(vision.analyze_face(b"x"))


def test_missing_key_gives_clear_error(monkeypatch):
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)
    with pytest.raises(vision.VisionError, match="GEMINI_API_KEY"):
        asyncio.run(vision.analyze_face(b"x"))
