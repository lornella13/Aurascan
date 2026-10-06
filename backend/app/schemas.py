"""Pydantic models. The vision model must return data that validates against
FaceProfile / BodyProfile; everything else is derived by the rules engine."""
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

SkinType = Literal["oily", "dry", "combination", "normal", "sensitive"]
Undertone = Literal["warm", "cool", "neutral", "olive"]
Depth = Literal["fair", "light", "medium", "tan", "deep", "rich"]
Contrast = Literal["low", "medium", "high"]
Concern = Literal[
    "acne", "redness", "dark_spots", "dark_circles", "texture",
    "fine_lines", "enlarged_pores", "dullness", "uneven_tone",
]
EyeColor = Literal["brown", "hazel", "green", "blue", "gray"]
HairColor = Literal["black", "dark_brown", "light_brown", "auburn", "red", "blonde", "gray_white"]
LipTone = Literal["pale", "pink", "rose", "berry", "brown", "deep"]
BodyShape = Literal["hourglass", "pear", "apple", "rectangle", "inverted_triangle"]
Season = Literal["spring", "summer", "autumn", "winter"]


class FaceProfile(BaseModel):
    skin_type: SkinType
    undertone: Undertone
    depth: Depth
    skin_hex: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    concerns: list[Concern] = []
    eye_color: EyeColor
    hair_color: HairColor
    lip_tone: LipTone
    contrast: Contrast
    confidence: float = Field(ge=0, le=1)
    # Normalised [x0, y0, x1, y1] around the face, forehead to chin. Optional so
    # a missing or unusable box degrades to the model's own skin_hex estimate.
    face_box: Optional[list[float]] = None
    skin_hex_source: Literal["measured", "estimated"] = "estimated"

    @field_validator("face_box")
    @classmethod
    def _check_face_box(cls, v):
        if v is None:
            return None
        if not isinstance(v, (list, tuple)) or len(v) != 4:
            return None
        try:
            x0, y0, x1, y1 = (float(n) for n in v)
        except (TypeError, ValueError):
            return None
        if not (0.0 <= x0 < x1 <= 1.0 and 0.0 <= y0 < y1 <= 1.0):
            return None
        # A usable box spans at least a tenth of the image on each side.
        if (x1 - x0) < 0.10 or (y1 - y0) < 0.10:
            return None
        return [x0, y0, x1, y1]


class Coloring(BaseModel):
    undertone: Undertone
    depth: Depth
    contrast: Contrast


class BodyProfile(BaseModel):
    body_shape: BodyShape
    shoulder_vs_hip: Literal["shoulders_wider", "balanced", "hips_wider"]
    waist_definition: Literal["defined", "moderate", "straight"]
    torso_vs_legs: Literal["longer_torso", "balanced", "longer_legs"]
    coloring: Coloring
    confidence: float = Field(ge=0, le=1)


class RoutineStep(BaseModel):
    order: int
    category: str
    product: str
    shade_or_finish: str
    why: str


class FaceResult(BaseModel):
    profile: FaceProfile
    routine: list[RoutineStep]
    tips: list[str]


class Swatch(BaseModel):
    name: str
    hex: str


class Palette(BaseModel):
    season: Season
    best: list[Swatch]
    neutrals: list[Swatch]
    avoid: list[Swatch]


class ClothingGuide(BaseModel):
    goal: str
    tops: list[str]
    bottoms: list[str]
    dresses: list[str]
    outerwear: list[str]
    necklines: list[str]
    fabrics: list[str]
    avoid: list[str]


class BodyResult(BaseModel):
    profile: BodyProfile
    clothing: ClothingGuide
    palette: Palette
    palette_source: Literal["face_scan_undertone", "this_photo"]
    tips: Optional[list[str]] = None
