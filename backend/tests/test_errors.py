"""Failure-path tests: every error leaves the API as JSON with a usable detail."""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import vision
from app.main import app
from app.schemas import BodyProfile, Coloring

client = TestClient(app, raise_server_exceptions=False)


def _jpeg():
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), (200, 160, 140)).save(buf, "JPEG")
    return buf.getvalue()


def _post_face():
    return client.post("/api/analyze/face", files={"file": ("f.jpg", _jpeg(), "image/jpeg")})


def test_vision_error_returns_502_with_detail(monkeypatch):
    async def boom(_):
        raise vision.VisionError("The AI service is busy or unavailable right now. Try again shortly.")

    monkeypatch.setattr(vision, "analyze_face", boom)
    r = _post_face()
    assert r.status_code == 502
    assert r.headers["content-type"].startswith("application/json")
    assert "busy or unavailable" in r.json()["detail"]


def test_unexpected_exception_returns_json_500(monkeypatch):
    async def boom(_):
        raise KeyError("something internal")

    monkeypatch.setattr(vision, "analyze_face", boom)
    r = _post_face()
    assert r.status_code == 500
    assert r.headers["content-type"].startswith("application/json")
    assert isinstance(r.json()["detail"], str)
    assert r.json()["detail"] != ""


def test_photo_rejected_stays_422_with_string_detail(monkeypatch):
    async def rejected(_):
        raise vision.PhotoRejected("No clear face in that photo.")

    monkeypatch.setattr(vision, "analyze_face", rejected)
    r = _post_face()
    assert r.status_code == 422
    assert r.json()["detail"] == "No clear face in that photo."


def test_body_unexpected_exception_returns_json_500(monkeypatch):
    async def boom(_):
        raise TypeError("bad shape")

    monkeypatch.setattr(vision, "analyze_body", boom)
    r = client.post("/api/analyze/body", files={"file": ("b.jpg", _jpeg(), "image/jpeg")})
    assert r.status_code == 500
    assert isinstance(r.json()["detail"], str)


def test_body_vision_error_returns_502(monkeypatch):
    async def boom(_):
        raise vision.VisionError("The AI couldn't read this photo. Try better lighting.")

    monkeypatch.setattr(vision, "analyze_body", boom)
    r = client.post("/api/analyze/body", files={"file": ("b.jpg", _jpeg(), "image/jpeg")})
    assert r.status_code == 502
    assert "better lighting" in r.json()["detail"]


def test_missing_file_is_a_validation_array(monkeypatch):
    # FastAPI answers a missing upload field with a list of error objects.
    r = client.post("/api/analyze/face")
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], list)
    assert all("msg" in d for d in r.json()["detail"])


# ---- vision layer: truncated / empty / invalid model output ----

def test_truncated_json_is_reported(monkeypatch):
    """A response cut off at maxOutputTokens must never reach the user as a 500."""
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)

    async def truncated(payload):
        return {"candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": [
            {"text": '{"photo_ok": true, "skin_type": "dro'}]}}]}

    monkeypatch.setattr(vision, "_post_gemini", truncated)
    with pytest.raises(vision.VisionError, match="unreadable"):
        __import__("asyncio").run(vision.analyze_face(b"x"))


def test_malformed_json_is_reported(monkeypatch):
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)

    async def broken(payload):
        return {"candidates": [{"content": {"parts": [
            {"text": '{"photo_ok": true, "skin_type": }'}]}}]}

    monkeypatch.setattr(vision, "_post_gemini", broken)
    with pytest.raises(vision.VisionError, match="malformed"):
        __import__("asyncio").run(vision.analyze_face(b"x"))


def test_empty_model_text_reports_unreadable_photo(monkeypatch):
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)

    async def empty(payload):
        return {"candidates": [{"content": {"parts": []}}]}

    monkeypatch.setattr(vision, "_post_gemini", empty)
    with pytest.raises(vision.VisionError, match="better lighting"):
        __import__("asyncio").run(vision.analyze_face(b"x"))


def test_no_candidates_reports_unreadable_photo(monkeypatch):
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)

    async def nothing(payload):
        return {"candidates": []}

    monkeypatch.setattr(vision, "_post_gemini", nothing)
    with pytest.raises(vision.VisionError, match="better lighting"):
        __import__("asyncio").run(vision.analyze_face(b"x"))


def test_invalid_enum_values_report_validation_problem(monkeypatch):
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)

    async def bad(payload):
        return {"candidates": [{"content": {"parts": [{"text": (
            '{"photo_ok": true, "skin_type": "sparkly", "undertone": "warm", "depth": "light",'
            ' "skin_hex": "E8B8A5", "concerns": [], "eye_color": "brown", "hair_color": "black",'
            ' "lip_tone": "pink", "contrast": "medium", "confidence": 0.5}')}]}}]}

    monkeypatch.setattr(vision, "_post_gemini", bad)
    with pytest.raises(vision.VisionError, match="couldn't read"):
        __import__("asyncio").run(vision.analyze_face(b"x"))


@pytest.mark.parametrize("status,expected", [
    (429, "quota"),
    (400, "rejected the request"),
    (404, "isn't available"),
    (503, "busy or unavailable"),
])
def test_gemini_http_errors_map_to_clear_messages(monkeypatch, status, expected):
    monkeypatch.setattr(vision.get_settings(), "gemini_api_key", "test", raising=False)
    monkeypatch.setattr(vision.get_settings(), "vision_provider", "gemini", raising=False)

    class FakeRes:
        def __init__(self, code):
            self.status_code = code
            self.text = "{}"

        def json(self):
            return {}

    class FakeClient:
        def __init__(self, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **kw):
            return FakeRes(status)

    monkeypatch.setattr(vision.httpx, "AsyncClient", lambda **kw: FakeClient())
    with pytest.raises(vision.VisionError, match=expected):
        __import__("asyncio").run(vision.analyze_face(b"x"))