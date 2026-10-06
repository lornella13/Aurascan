"""Measure a real skin colour from photo pixels.

The vision model can only *guess* a skin tone from a photo; the actual pixels
are the truth. Once the model tells us where the face is, we sample the cheeks
and forehead and take a robust median that ignores glare and shadow.
"""
import io
import statistics
from typing import Optional, Sequence

from PIL import Image

# Sample patches as fractions of the face box. These sit on cheeks and forehead
# so they avoid eyes, brows, lips, beard and hairline.
PATCHES = (
    (0.22, 0.55, 0.40, 0.72),  # left cheek
    (0.60, 0.55, 0.78, 0.72),  # right cheek
    (0.35, 0.10, 0.65, 0.24),  # forehead
)

# Perceived luminance cut-offs (0-255) mapped to the depth bands in schemas.py.
DEPTH_BANDS = (
    ("fair", 200.0),
    ("light", 170.0),
    ("medium", 140.0),
    ("tan", 110.0),
    ("deep", 75.0),
)
DEPTH_ORDER = ["fair", "light", "medium", "tan", "deep", "rich"]

MIN_PIXELS = 200
TRIM = 0.10  # drop this fraction of the darkest and brightest pixels


def luminance(rgb: Sequence[int]) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def _valid_box(box) -> bool:
    if not box or len(box) != 4:
        return False
    try:
        x0, y0, x1, y1 = (float(v) for v in box)
    except (TypeError, ValueError):
        return False
    return 0.0 <= x0 < x1 <= 1.0 and 0.0 <= y0 < y1 <= 1.0


def measure_skin_hex(image_bytes: bytes, box: Optional[Sequence[float]]) -> Optional[str]:
    """Return the median cheek/forehead colour as "#RRGGBB", or None if the
    photo or the face box can't support a reliable measurement."""
    if not image_bytes or not _valid_box(box):
        return None

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return None

    width, height = img.size
    if width < 2 or height < 2:
        return None

    fx0, fy0, fx1, fy1 = (float(v) for v in box)
    bx0, by0 = fx0 * width, fy0 * height
    bx1, by1 = fx1 * width, fy1 * height
    bw, bh = bx1 - bx0, by1 - by0
    if bw < 1 or bh < 1:
        return None

    pixels: list[tuple[int, int, int]] = []
    for px0, py0, px1, py1 in PATCHES:
        left = int(bx0 + px0 * bw)
        right = int(bx0 + px1 * bw)
        top = int(by0 + py0 * bh)
        bottom = int(by0 + py1 * bh)
        # Clamp to the image, and skip a patch that collapsed or fell outside.
        left, right = max(0, min(left, width)), max(0, min(right, width))
        top, bottom = max(0, min(top, height)), max(0, min(bottom, height))
        if right - left < 1 or bottom - top < 1:
            return None
        patch = img.crop((left, top, right, bottom))
        pixels.extend(patch.getdata())

    if len(pixels) < MIN_PIXELS:
        return None

    ordered = sorted(pixels, key=luminance)
    cut = int(len(ordered) * TRIM)
    kept = ordered[cut : len(ordered) - cut] if cut else ordered
    if len(kept) < MIN_PIXELS:
        return None

    channels = [statistics.median(p[i] for p in kept) for i in range(3)]
    return "#" + "".join(f"{int(round(c)):02X}" for c in channels)


def depth_for_luminance(value: float) -> str:
    for name, floor in DEPTH_BANDS:
        if value >= floor:
            return name
    return "rich"


def reconcile_depth(depth: str, hex_colour: str) -> str:
    """Trust the model unless the measured pixels disagree by 2+ bands, which
    almost always means the lighting fooled it (or the model guessed wrong)."""
    try:
        r = int(hex_colour[1:3], 16)
        g = int(hex_colour[3:5], 16)
        b = int(hex_colour[5:7], 16)
    except (ValueError, IndexError, TypeError):
        return depth
    measured = depth_for_luminance(luminance((r, g, b)))
    if depth not in DEPTH_ORDER:
        return measured
    if abs(DEPTH_ORDER.index(measured) - DEPTH_ORDER.index(depth)) >= 2:
        return measured
    return depth