"""Style rules engine: body shape + colouring -> clothing guide and palette."""
from ..schemas import ClothingGuide, Palette, Swatch

CLOTHING: dict[str, ClothingGuide] = {
    "hourglass": ClothingGuide(
        goal="Follow your natural waist and keep balance between shoulders and hips.",
        tops=["Wrap tops", "Fitted knits", "Tucked-in blouses"],
        bottoms=["High-waisted trousers", "Pencil skirts", "Straight or bootcut jeans"],
        dresses=["Wrap dresses", "Belted shirt dresses", "Fit-and-flare"],
        outerwear=["Belted coats", "Nipped-waist blazers", "Cropped jackets"],
        necklines=["V-neck", "Scoop", "Sweetheart", "Wrap"],
        fabrics=["Stretch fabrics with drape", "Jersey", "Soft crepe"],
        avoid=["Boxy shapeless cuts that hide the waist", "Very stiff, thick fabrics at the waist"],
    ),
    "pear": ClothingGuide(
        goal="Add visual weight on top and let the lower half flow.",
        tops=["Structured shoulders", "Statement sleeves", "Boat-neck and off-shoulder tops", "Bright or patterned tops"],
        bottoms=["A-line skirts", "Wide-leg trousers", "Bootcut or flared jeans in dark washes"],
        dresses=["A-line", "Fit-and-flare", "Empire waist"],
        outerwear=["Blazers with shoulder structure", "Jackets that end at the hip or below"],
        necklines=["Boat", "Square", "Off-shoulder", "Wide scoop"],
        fabrics=["Fluid fabrics on the bottom half", "Structured fabrics on top"],
        avoid=["Tight tapered trousers with plain tops", "Clingy fabrics across the hips", "Cropped jackets that stop at the widest point"],
    ),
    "apple": ClothingGuide(
        goal="Create length through the torso and show off your legs and shoulders.",
        tops=["Empire-line tops", "Long open cardigans", "Loose wrap-front tops"],
        bottoms=["Straight-leg trousers", "Mid-rise pieces with a smooth waistband", "A-line skirts to the knee"],
        dresses=["Empire waist", "A-line", "Wrap with a lower tie point"],
        outerwear=["Long open blazers", "Waterfall cardigans", "Unbelted coats"],
        necklines=["V-neck", "Scoop", "Open collar"],
        fabrics=["Fabrics with soft drape", "Ponte", "Matte jersey"],
        avoid=["Very clingy fabrics around the middle", "Thick belts at the waist", "High necklines with heavy detail"],
    ),
    "rectangle": ClothingGuide(
        goal="Add curves and definition at the waist, shoulders and hips.",
        tops=["Peplum tops", "Ruffles and layers", "Cropped tops with high-waisted bottoms"],
        bottoms=["Full skirts", "Paperbag-waist trousers", "Flared or wide-leg pants"],
        dresses=["Fit-and-flare", "Belted styles", "Ruched or wrap dresses"],
        outerwear=["Belted trench coats", "Peplum jackets", "Cropped jackets"],
        necklines=["Sweetheart", "Halter", "Cowl", "Square"],
        fabrics=["Textured fabrics", "Structured fabrics with body", "Layered pieces"],
        avoid=["Straight shift shapes with no waist definition", "Head-to-toe tubular silhouettes"],
    ),
    "inverted_triangle": ClothingGuide(
        goal="Soften the shoulders and add volume to the lower half.",
        tops=["Simple, soft tops", "V-necks", "Raglan or dolman sleeves"],
        bottoms=["Full or pleated skirts", "Wide-leg trousers", "Patterned or bright bottoms", "Cargo pockets"],
        dresses=["A-line", "Wrap", "Tiered or gathered skirts"],
        outerwear=["Soft unstructured jackets", "Long coats with a relaxed shoulder"],
        necklines=["V-neck", "Scoop", "Plunge"],
        fabrics=["Soft flowing fabrics on top", "Volume and texture below"],
        avoid=["Shoulder pads and puff sleeves", "Boat necks and halters", "Skinny bottoms with heavy tops"],
    ),
}


def _s(*pairs: tuple[str, str]) -> list[Swatch]:
    return [Swatch(name=n, hex=h) for n, h in pairs]


PALETTES: dict[str, Palette] = {
    "spring": Palette(
        season="spring",
        best=_s(("Coral", "#FF7F6B"), ("Peach", "#FFB48A"), ("Warm turquoise", "#2EC4B6"),
                ("Golden yellow", "#F5C242"), ("Leaf green", "#7BC96F"), ("Warm pink", "#FF8FA3")),
        neutrals=_s(("Ivory", "#FFF6E5"), ("Camel", "#C8A26B"), ("Warm navy", "#3E5C76"), ("Soft tan", "#D9BE94")),
        avoid=_s(("Pure black", "#0A0A0A"), ("Burgundy", "#5B2333"), ("Cool grey", "#8E9AAF"), ("Icy lilac", "#E8C2E8")),
    ),
    "summer": Palette(
        season="summer",
        best=_s(("Soft rose", "#E39BB0"), ("Lavender", "#B5A1D6"), ("Powder blue", "#8FB8DE"),
                ("Sage", "#8FAF9B"), ("Dusty mauve", "#B48A9D"), ("Raspberry", "#C2456E")),
        neutrals=_s(("Soft white", "#F4F4F8"), ("Rose taupe", "#A38B8F"), ("Slate grey", "#6E7A8A"), ("Soft navy", "#3D4A6B")),
        avoid=_s(("Bright orange", "#F26A21"), ("Mustard", "#D9A520"), ("Olive brown", "#7A6A2F"), ("Rusty camel", "#A9713B")),
    ),
    "autumn": Palette(
        season="autumn",
        best=_s(("Terracotta", "#C8553D"), ("Mustard", "#D4A017"), ("Olive", "#6B7A3A"),
                ("Rust", "#A8451F"), ("Deep teal", "#1F7A74"), ("Brick red", "#B33A2E")),
        neutrals=_s(("Cream", "#F3E7CF"), ("Camel", "#B98B57"), ("Chocolate", "#4A2F22"), ("Khaki", "#A39A6A")),
        avoid=_s(("Fuchsia", "#E0218A"), ("Icy blue", "#BFE3F7"), ("Stark white", "#FFFFFF"), ("Cool grey", "#9AA3AD")),
    ),
    "winter": Palette(
        season="winter",
        best=_s(("True red", "#D0021B"), ("Royal blue", "#2A4BD7"), ("Emerald", "#0B8F5A"),
                ("Fuchsia", "#D81B7D"), ("Deep purple", "#6A2BA8"), ("Ice blue", "#BEE3FF")),
        neutrals=_s(("Black", "#0A0A0A"), ("Charcoal", "#33363D"), ("Navy", "#14213D"), ("Pure white", "#FFFFFF")),
        avoid=_s(("Orange", "#F28C28"), ("Mustard", "#C99A1E"), ("Beige camel", "#C9A66B"), ("Muted olive", "#7A7A3A")),
    ),
}


def pick_season(undertone: str, depth: str, contrast: str) -> str:
    """Heuristic 4-season colour analysis. The season picks the colour *family*;
    skin depth is then applied to each colour separately (see depth_for).
    Treat it as a good starting point, and let users override it in the UI."""
    light = depth in ("fair", "light")
    deep = depth in ("deep", "rich")
    if undertone == "warm":
        return "spring" if (light or (contrast == "high" and not deep)) else "autumn"
    if undertone == "cool":
        return "winter" if (deep or contrast == "high") else "summer"
    if undertone == "olive":
        return "winter" if (deep and contrast == "high") else "autumn"
    # neutral
    if contrast == "high":
        return "winter"
    return "summer" if light else "autumn"


# ---------------------------------------------------------------- depth
# A season alone is too coarse: 4 buckets for 72 possible colouring inputs, and
# 'autumn' alone took 34 of them. Within one season a fair and a deep
# complexion are not flattered by the same hex value, so the season chooses the
# family and depth tunes every colour in it. That way two people can share a
# season and still get visibly different palettes.

DEPTH_BANDS: dict[str, str] = {
    "fair": "light", "light": "light",
    "medium": "medium", "tan": "medium",
    "deep": "deep", "rich": "deep",
}

# (lightness delta, saturation delta, lightness floor, saturation ceiling).
# The deltas are deliberately gentle: a large shift turns an already-rich
# family into neon, which is not what "richer" should look like.
_DEPTH_TUNING: dict[str, tuple[float, float, float, float]] = {
    # Fair skin is flattered by softer, lighter versions of the family.
    "light": (-0.06, -0.10, 0.60, 0.72),
    # Deep skin is flattered by deeper, slightly richer versions. The ceiling
    # stops already-saturated hues turning neon, and the floor stops a dark
    # family member collapsing into near-black where the chip stops reading.
    "deep": (+0.05, +0.08, 0.16, 0.82),
    "medium": (0.0, 0.0, 0.0, 1.0),
}


def _hex_to_hsl(hex_colour: str) -> tuple[float, float, float]:
    """sRGB hex -> HSL, all channels 0-1.

    The channels are used directly: CSS HSL lightness is defined on the
    gamma-encoded values, so gamma-correcting here first (as you would for
    relative luminance) would make #6B7A3A read as L=0.12 instead of L=0.35
    and collapse every colour toward black.
    """
    r, g, b = (int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5))
    high, low = max(r, g, b), min(r, g, b)
    lightness = (high + low) / 2
    if high == low:
        return 0.0, 0.0, lightness
    delta = high - low
    saturation = delta / (2 - high - low) if lightness > 0.5 else delta / (high + low)
    if high == r:
        hue = ((g - b) / delta) % 6
    elif high == g:
        hue = (b - r) / delta + 2
    else:
        hue = (r - g) / delta + 4
    return hue * 60, saturation, lightness


def _hsl_to_hex(hue: float, saturation: float, lightness: float) -> str:
    saturation = min(max(saturation, 0.0), 1.0)
    lightness = min(max(lightness, 0.0), 1.0)
    c = (1 - abs(2 * lightness - 1)) * saturation
    x = c * (1 - abs((hue / 60) % 2 - 1))
    m = lightness - c / 2
    sector = int(hue // 60) % 6
    rgb = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][sector]
    return "#" + "".join(f"{round((v + m) * 255):02X}" for v in rgb)


def tune_for_depth(hex_colour: str, band: str) -> str:
    """Shift one colour within its season family to suit a skin depth.

    Near-black and near-white neutrals are left alone: 'black' lightened is
    just grey, and a fair person should still be told that pure black suits
    them.
    """
    delta_l, delta_s, floor, ceiling = _DEPTH_TUNING[band]
    if delta_l == 0 and delta_s == 0:
        return hex_colour.upper()
    hue, saturation, lightness = _hex_to_hsl(hex_colour)
    # Skip achromatic colours so near-black/near-white survive intact.
    if saturation < 0.08:
        return hex_colour.upper()
    tuned = _hsl_to_hex(hue, saturation + delta_s, max(lightness + delta_l, floor))
    hue2, sat2, light2 = _hex_to_hsl(tuned)
    return _hsl_to_hex(hue2, min(sat2, ceiling), light2)


def depth_band(depth: str) -> str:
    return DEPTH_BANDS.get(depth, "medium")


def palette_for(undertone: str, depth: str, contrast: str) -> Palette:
    """Season picks the family, depth tunes every colour inside it."""
    base = PALETTES[pick_season(undertone, depth, contrast)]
    band = depth_band(depth)

    def tune(items: list[Swatch]) -> list[Swatch]:
        return [
            Swatch(name=s.name, hex=tune_for_depth(s.hex, band))
            for s in items
        ]

    return Palette(
        season=base.season,
        best=tune(base.best),
        neutrals=tune(base.neutrals),
        avoid=tune(base.avoid),
    )


def clothing_for(shape: str) -> ClothingGuide:
    return CLOTHING[shape]
