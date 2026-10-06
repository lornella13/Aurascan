"""Makeup rules engine: FaceProfile -> ordered routine.

The vision model only *describes* the face. Every product recommendation comes
from the tables below, so results are consistent and you can tune them without
touching a prompt."""
from ..schemas import FaceProfile, RoutineStep


def _band(depth: str) -> str:
    if depth in ("fair", "light"):
        return "light"
    if depth in ("deep", "rich"):
        return "deep"
    return "mid"


def _tone(undertone: str) -> str:
    # olive is shade-matched separately in foundation; for colour cosmetics it
    # behaves like a neutral undertone.
    return "neutral" if undertone == "olive" else undertone


BLUSH = {
    "warm": {"light": "soft peach", "mid": "apricot or coral", "deep": "deep coral or terracotta"},
    "cool": {"light": "baby pink", "mid": "rose", "deep": "berry or plum"},
    "neutral": {"light": "rosy peach", "mid": "dusty rose or warm mauve", "deep": "deep rose or raisin"},
}
BRONZER = {
    "warm": {"light": "golden sand", "mid": "golden caramel", "deep": "rich copper-bronze"},
    "cool": {"light": "taupe-beige", "mid": "neutral tan", "deep": "cocoa brown"},
    "neutral": {"light": "soft beige-brown", "mid": "warm tan", "deep": "espresso brown"},
}
HIGHLIGHT = {
    "warm": {"light": "champagne", "mid": "golden champagne", "deep": "bronze-gold"},
    "cool": {"light": "pearl or icy pink", "mid": "rose pearl", "deep": "cool copper-pink"},
    "neutral": {"light": "soft peach pearl", "mid": "peachy champagne", "deep": "warm gold"},
}
LIPS = {  # (everyday, bold)
    "warm": {
        "light": ("peachy nude", "coral or warm red"),
        "mid": ("caramel rose", "brick or tomato red"),
        "deep": ("chocolate nude", "burnt orange or brick"),
    },
    "cool": {
        "light": ("pink beige", "raspberry or blue-red"),
        "mid": ("rosy mauve", "berry or cherry"),
        "deep": ("plum brown", "wine or deep berry"),
    },
    "neutral": {
        "light": ("soft rose", "classic red"),
        "mid": ("dusty rose", "rose red or berry-red"),
        "deep": ("warm brown-rose", "deep red or plum"),
    },
}
SHADOW = {
    "brown": "teal, emerald, navy, plum and warm gold",
    "hazel": "olive green, bronze, gold, warm purple",
    "green": "plum, burgundy, mauve, copper",
    "blue": "copper, bronze, peach, warm brown",
    "gray": "soft plum, taupe, silver, navy",
}
TRANSITION = {"warm": "warm caramel-brown", "cool": "soft taupe", "neutral": "muted rose-brown"}
LINER = {
    "brown": "black or espresso; navy or emerald for a colour pop",
    "hazel": "brown, bronze or olive",
    "green": "plum or deep brown",
    "blue": "brown or bronze",
    "gray": "charcoal or navy",
}
BROW = {
    "black": "soft black or dark brown",
    "dark_brown": "medium-to-dark brown",
    "light_brown": "ash or medium brown",
    "auburn": "warm auburn-brown",
    "red": "warm ginger-brown",
    "blonde": "taupe or soft ash blonde",
    "gray_white": "soft grey-brown",
}
FOUNDATION_UNDERTONE = {
    "warm": "golden or yellow-based",
    "cool": "pink or rosy-based",
    "neutral": "balanced neutral",
    "olive": "olive or green-yellow neutral (avoid pink-based shades)",
}


def _primer(p: FaceProfile) -> tuple[str, str, str]:
    c = p.concerns
    if "redness" in c:
        return ("Green-tinted colour-correcting primer", "light layer on red areas", "Cancels redness before foundation.")
    if p.skin_type == "sensitive":
        return ("Fragrance-free gel primer", "silicone-free", "Adds a barrier without common irritants.")
    if "enlarged_pores" in c or "texture" in c:
        return ("Pore-filling primer", "smoothing, blurring", "Softens the look of pores and uneven texture.")
    if p.skin_type == "oily":
        return ("Mattifying primer", "oil-control", "Keeps shine down and helps makeup last.")
    if p.skin_type == "dry":
        return ("Hydrating primer", "hyaluronic acid or glycerin based", "Stops foundation clinging to dry patches.")
    if p.skin_type == "combination":
        return ("Dual-zone primer", "mattifying on the T-zone, hydrating on cheeks", "Treats oily and dry areas differently.")
    if "dullness" in c:
        return ("Illuminating primer", "soft glow", "Brings life back to dull skin.")
    return ("Lightweight grip primer", "natural finish", "Helps makeup stay put without changing your skin.")


def _foundation(p: FaceProfile) -> tuple[str, str, str]:
    finish = {
        "oily": "matte to soft-matte, oil-free, long-wear",
        "dry": "dewy to satin, hydrating",
        "combination": "satin or skin-tint",
        "normal": "natural satin",
        "sensitive": "mineral or fragrance-free skin tint",
    }[p.skin_type]
    heavy = any(x in p.concerns for x in ("acne", "dark_spots", "uneven_tone"))
    coverage = "medium to full coverage" if heavy else "light to medium coverage"
    shade = f"{p.depth} depth, {FOUNDATION_UNDERTONE[p.undertone]}; match near {p.skin_hex}"
    return (f"Foundation, {coverage}", f"{finish}. Shade: {shade}", "Chosen for your skin type, coverage needs and undertone.")


def _concealer(p: FaceProfile) -> tuple[str, str, str]:
    if "dark_circles" in p.concerns:
        corrector = {"light": "peach", "mid": "orange-peach", "deep": "orange or red-orange"}[_band(p.depth)]
        return (
            "Colour corrector plus concealer",
            f"{corrector} corrector under the eyes, then a concealer one shade lighter than foundation",
            "Correctors neutralise blue-purple tones before concealer.",
        )
    kind = "full-coverage matte on blemishes" if "acne" in p.concerns else "hydrating, one shade lighter than foundation"
    return ("Concealer", kind, "Brightens the eye area and covers spots.")


def _setting(p: FaceProfile) -> tuple[str, str, str]:
    return {
        "oily": ("Translucent setting powder", "all over the face, extra on the T-zone", "Locks in makeup and controls shine."),
        "dry": ("Setting powder, light touch", "only under the eyes and centre of the face", "Sets concealer without drying the skin."),
        "combination": ("Translucent setting powder", "T-zone only", "Controls the oily areas and keeps cheeks fresh."),
        "normal": ("Finely milled setting powder", "light dusting where you crease", "Keeps things in place without going flat."),
        "sensitive": ("Talc-free, fragrance-free powder", "light dusting", "Sets makeup with fewer irritants."),
    }[p.skin_type]


def build_routine(p: FaceProfile) -> tuple[list[RoutineStep], list[str]]:
    tone, band = _tone(p.undertone), _band(p.depth)
    everyday, bold = LIPS[tone][band]
    blush_form = "powder blush" if p.skin_type == "oily" else "cream blush"
    hl_form = "powder highlighter, subtle" if p.skin_type == "oily" else "liquid or cream highlighter"

    rows: list[tuple[str, str, str, str]] = []
    rows.append(("Primer", *_primer(p)))
    rows.append(("Foundation", *_foundation(p)))
    rows.append(("Concealer", *_concealer(p)))
    rows.append(("Setting powder", *_setting(p)))
    rows.append(("Bronzer or contour", "Bronzer", BRONZER[tone][band], "Adds warmth and shape, chosen to sit close to your undertone."))
    rows.append(("Blush", blush_form.capitalize(), BLUSH[tone][band], "Flatters your undertone and depth."))
    rows.append(("Highlighter", hl_form.capitalize(), HIGHLIGHT[tone][band], "Adds glow on cheekbones without looking chalky."))
    rows.append(("Brows", "Brow pencil or gel", BROW[p.hair_color], "Close to your hair colour so brows look natural."))
    rows.append((
        "Eyeshadow", "Palette with a matte transition, a shimmer and a deeper shade",
        f"Transition: {TRANSITION[tone]}. Best colours for {p.eye_color} eyes: {SHADOW[p.eye_color]}",
        "These shades make your eye colour stand out.",
    ))
    rows.append(("Eyeliner", "Pencil or gel liner", LINER[p.eye_color], "Defines the eyes and complements the iris."))
    waterproof = " Waterproof formula if your lids get oily." if p.skin_type in ("oily", "combination") else ""
    rows.append(("Mascara", "Volumising or lengthening mascara", "Black, or brown-black for a softer look." + waterproof, "Opens up the eyes."))
    rows.append(("Lips", "Lipstick or tinted balm", f"Everyday: {everyday}. Bold: {bold}", "Undertone-matched so lips look fresh, not washed out."))
    spray = "Mattifying setting spray" if p.skin_type == "oily" else "Hydrating setting mist"
    rows.append(("Setting spray", spray, "Light mist to finish", "Melts powders together and extends wear."))

    routine = [
        RoutineStep(order=i, category=cat, product=prod, shade_or_finish=shade, why=why)
        for i, (cat, prod, shade, why) in enumerate(rows, start=1)
    ]

    tips = [
        "Check shades in natural daylight. Store lighting changes how a shade looks.",
        "Swatch foundation along the jaw and let it dry for a minute before deciding.",
    ]
    if p.confidence < 0.7:
        tips.insert(0, "This scan had lower confidence. Retake in soft daylight facing a window for a better read.")
    if any(x in p.concerns for x in ("acne", "redness")):
        tips.append("For ongoing acne or redness, a dermatologist can help. These are cosmetic suggestions, not medical advice.")
    return routine, tips
