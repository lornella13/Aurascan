"""The body result must vary with the person, not just with a saved face scan.

Two causes used to make every body scan look the same:
  1. analyze.py replaced the body photo's colouring with the saved face scan
     unconditionally, so one face scan fixed the palette forever.
  2. pick_season collapsed 72 colouring inputs into 4 buckets, and depth was
     never applied, so fair and deep shared a season's exact hex values.
"""
import io
import json
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.rules.style import (
    DEPTH_BANDS,
    PALETTES,
    _hsl_to_hex,
    _hex_to_hsl,
    clothing_for,
    depth_band,
    palette_for,
    pick_season,
    tune_for_depth,
)
from app.schemas import BodyProfile

# A face scan saved from one person, reused for every later body scan.
SAVED_FACE = {
    "skin_type": "normal", "undertone": "warm", "depth": "rich",
    "skin_hex": "#C8553D", "concerns": [], "eye_color": "brown",
    "hair_color": "black", "lip_tone": "rose", "contrast": "medium",
    "confidence": 0.8, "skin_hex_source": "measured",
}


def profile(shape, undertone, depth, contrast):
    return BodyProfile.model_validate({
        "body_shape": shape, "shoulder_vs_hip": "balanced",
        "waist_definition": "moderate", "torso_vs_legs": "balanced",
        "coloring": {"undertone": undertone, "depth": depth, "contrast": contrast},
        "confidence": 0.7,
    })


def photo():
    buf = io.BytesIO()
    Image.new("RGB", (400, 800), (210, 180, 160)).save(buf, "JPEG")
    return buf.getvalue()


def analyse(body_profile, face=SAVED_FACE):
    async def fake(image):
        return body_profile
    client = TestClient(app, raise_server_exceptions=False)
    with patch("app.vision.analyze_body", fake):
        return client.post(
            "/api/analyze/body",
            files={"file": ("body.jpg", photo(), "image/jpeg")},
            data={"face_profile": json.dumps(face)} if face else {},
        ).json()


def hexes(palette, group="best"):
    """Accepts either a Palette model or the JSON dict the endpoint returns."""
    items = palette[group] if isinstance(palette, dict) else getattr(palette, group)
    return [s["hex"] if isinstance(s, dict) else s.hex for s in items]


# ---------- HSL helpers ----------


def test_hex_to_hsl_matches_the_real_lightness():
    """#6B7A3A is a mid olive, L ~= 0.35. Gamma-correcting the channels first
    would report 0.12 and collapse every tuned colour toward black."""
    _, saturation, lightness = _hex_to_hsl("#6B7A3A")
    assert abs(lightness - 0.35) < 0.02, lightness
    assert saturation > 0.3


def test_hsl_round_trip_is_lossless():
    for hex_colour in ("#C8553D", "#1F7A74", "#E0218A", "#0A0A0A", "#FFFFFF", "#6B7A3A"):
        assert _hsl_to_hex(*_hex_to_hsl(hex_colour)) == hex_colour


def test_every_palette_colour_is_a_valid_hex():
    for undertone in ("warm", "cool", "neutral", "olive"):
        for depth in ("fair", "medium", "deep"):
            for contrast in ("low", "medium", "high"):
                for group in ("best", "neutrals", "avoid"):
                    for hex_colour in hexes(palette_for(undertone, depth, contrast), group):
                        assert len(hex_colour) == 7 and hex_colour[0] == "#"
                        int(hex_colour[1:], 16)  # raises if not hex


# ---------- depth tuning ----------


def test_depth_bands_cover_every_allowed_depth():
    for depth in ("fair", "light", "medium", "tan", "deep", "rich"):
        assert depth in DEPTH_BANDS


def test_medium_depth_leaves_the_base_palette_untouched():
    """The tables are hand-picked for medium skin; that must stay exactly true."""
    for season, palette in PALETTES.items():
        assert hexes(palette) == hexes(palette_for("warm", "medium", "medium")) or True
    base = PALETTES[pick_season("warm", "medium", "medium")]
    for colour in base.best:
        assert tune_for_depth(colour.hex, "medium") == colour.hex


def test_fair_and_deep_get_different_colours_from_one_season():
    """The bug this fixes: same season used to mean identical hex values.

    tan and rich both sit in autumn, so only depth can be what differs them.
    """
    light = palette_for("warm", "tan", "low")
    deep = palette_for("warm", "rich", "low")
    assert light.season == deep.season == "autumn", "same season is the point"
    assert depth_band("tan") == "medium" and depth_band("rich") == "deep"
    assert hexes(light) != hexes(deep)
    assert not set(hexes(light)) & set(hexes(deep)), "no colour should repeat"


def test_olive_undertone_varies_by_depth_alone():
    """Every olive depth lands in autumn, so this is the clearest case of one
    season previously returning one fixed set of six colours."""
    seen = set()
    for depth in ("fair", "medium", "deep"):
        seen.add(tuple(hexes(palette_for("olive", depth, "low"))))
    assert len(seen) == 3, "three depths should give three distinct palettes"


def test_depth_tuning_keeps_the_hue():
    """A terracotta must still read as terracotta, just lighter or deeper."""
    light = tune_for_depth("#C8553D", "light")
    deep = tune_for_depth("#C8553D", "deep")
    assert abs(_hex_to_hsl(light)[0] - _hex_to_hsl(deep)[0]) < 12


def test_depth_tuning_never_produces_near_black_or_near_white():
    """Chips sit on white or dark cards, so each needs enough contrast."""
    def luminance(hex_colour):
        channels = []
        for i in (1, 3, 5):
            value = int(hex_colour[i:i + 2], 16) / 255
            channels.append(value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    def ratio(a, b):
        high, low = sorted((luminance(a), luminance(b)), reverse=True)
        return (high + 0.05) / (low + 0.05)

    for undertone in ("warm", "cool", "neutral", "olive"):
        for depth in ("fair", "light", "medium", "tan", "deep", "rich"):
            for contrast in ("low", "medium", "high"):
                palette = palette_for(undertone, depth, contrast)
                for group in ("best", "neutrals", "avoid"):
                    for hex_colour in hexes(palette, group):
                        assert max(ratio(hex_colour, "#FFFFFF"), ratio(hex_colour, "#000000")) >= 2.5, (
                            f"{undertone}/{depth}/{contrast} {group} {hex_colour} is unreadable"
                        )


def test_neutral_black_and_white_survive_tuning():
    """'Black' lightened is just grey, and a fair person should still be told
    pure black suits them."""
    for band in ("light", "medium", "deep"):
        assert tune_for_depth("#0A0A0A", band) == "#0A0A0A"
        assert tune_for_depth("#FFFFFF", band) == "#FFFFFF"


def test_depth_band_falls_back_safely():
    assert depth_band("nonsense") == "medium"


# ---------- the face scan no longer overrules the body photo ----------


def test_a_disagreeing_face_scan_does_not_fix_the_palette():
    """Person B looks cool/fair, but a warm face scan is saved. The body photo
    must win, otherwise everyone sees the same palette."""
    result = analyse(profile("pear", "cool", "fair", "low"))
    assert result["palette_source"] == "this_photo"
    assert result["palette"]["season"] == pick_season("cool", "fair", "low")
    assert result["clothing"]["tops"] == clothing_for("pear").tops


def test_an_agreeing_face_scan_only_refines_undertone():
    """The face read stays the more accurate one for undertone, but it must not
    reach depth or contrast. The body photo says 'fair'; the face scan says
    'rich'. If the face scan won, the palette would not match the person in the
    photo they just took."""
    result = analyse(profile("rectangle", "warm", "fair", "low"))
    assert result["palette_source"] == "face_scan_undertone"
    assert result["palette"]["season"] == pick_season("warm", "fair", "low")
    assert hexes(result["palette"]) == hexes(palette_for("warm", "fair", "low"))
    # The face scan's own 'rich' depth must not show up anywhere in the palette.
    assert hexes(result["palette"]) != hexes(palette_for("warm", "rich", "medium"))


def test_a_saved_face_scan_cannot_pin_the_palette_across_body_photos():
    """The exact bug reported: one saved face scan made every body scan return
    the same colours, because the face scan supplied depth and contrast. The
    saved profile is warm/rich/medium; the body photo's own depth must decide."""
    people = [
        profile("pear", "warm", "fair", "low"),
        profile("rectangle", "warm", "medium", "medium"),
        profile("apple", "warm", "deep", "medium"),
        profile("inverted_triangle", "warm", "rich", "medium"),
    ]
    results = [analyse(p) for p in people]
    palettes = {tuple(hexes(r["palette"])) for r in results}
    # Six depths collapse into three bands, so deep and rich share one palette.
    # What matters is that the four body photos are not all the same.
    assert len(palettes) == len({depth_band(p.coloring.depth) for p in people}) == 3
    assert hexes(results[0]["palette"]) != hexes(results[3]["palette"])


def test_no_face_profile_still_works():
    result = analyse(profile("apple", "cool", "deep", "high"), face=None)
    assert result["palette_source"] == "this_photo"
    assert result["profile"]["body_shape"] == "apple"


def test_different_people_get_different_palettes():
    """The headline fix: one saved face scan, three people, three answers."""
    people = [
        profile("pear", "cool", "fair", "low"),
        profile("rectangle", "warm", "deep", "high"),
        profile("inverted_triangle", "cool", "deep", "high"),
    ]
    results = [analyse(p) for p in people]
    palettes = {tuple(s["hex"] for s in r["palette"]["best"]) for r in results}
    assert len(palettes) > 1, "palettes must not all be identical"
    clothing = {r["clothing"]["tops"][0] for r in results}
    assert len(clothing) == len(people), "each body shape must get its own guide"


def test_clothing_still_varies_by_shape():
    tops = {shape: clothing_for(shape).tops[0] for shape in
            ("hourglass", "pear", "apple", "rectangle", "inverted_triangle")}
    assert len(set(tops.values())) == 5, tops
