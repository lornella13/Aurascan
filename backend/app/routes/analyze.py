import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from .. import vision
from ..config import get_settings
from ..rules.makeup import build_routine
from ..rules.style import clothing_for, palette_for
from ..schemas import BodyResult, FaceProfile, FaceResult

logger = logging.getLogger("aurascan")

router = APIRouter(prefix="/api/analyze", tags=["analyze"])
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def _read_upload(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Use a JPG, PNG or WebP photo.")
    limit = get_settings().max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"Photo is too large. Max {get_settings().max_upload_mb} MB.")
    return data


def _fail(exc: Exception) -> JSONResponse:
    """Map any analysis failure to JSON. Vision/provider problems are a 502 so
    the frontend can say "the AI service is the problem"; anything else is 500."""
    if isinstance(exc, vision.VisionError):
        logger.error("Vision error: %s", exc)
        return JSONResponse(status_code=502, content={"detail": str(exc)})
    logger.exception("Unexpected analysis failure: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on the server. Please try again."},
    )


@router.post("/face", response_model=FaceResult)
async def analyze_face(file: UploadFile = File(...)):
    raw = await _read_upload(file)
    try:
        profile = await vision.analyze_face(vision.prepare_image(raw))
        routine, tips = build_routine(profile)
        return FaceResult(profile=profile, routine=routine, tips=tips)
    except vision.PhotoRejected as exc:
        raise HTTPException(422, str(exc))
    except Exception as exc:
        return _fail(exc)


# A face close-up is the better place to read undertone, because a full-body
# photo is mostly clothing and shadow. But undertone is also the one attribute
# that does not change between photos of the same person, which makes it the
# only safe thing to carry over.
#
# Depth and contrast must come from the body photo. Earlier this route let the
# face scan supply all three, so one saved face scan pinned depth and contrast
# for good and every later body scan returned the identical palette. Guarding on
# undertone alone did not help: the guard almost always passed, because two
# photos of the same person agree on undertone by definition. The palette has
# to follow the photo in front of the user, so the face scan refines undertone
# and nothing else.


def _merge_face_undertone(coloring, face_profile: Optional[str]):
    """Return (coloring, source) for a body scan, refined by a saved face scan."""
    if not face_profile:
        return coloring, "this_photo"
    try:
        fp = FaceProfile.model_validate_json(face_profile)
    except Exception:
        return coloring, "this_photo"  # ignore a bad client value

    if fp.undertone == coloring.undertone:
        return coloring, "face_scan_undertone"

    logger.info(
        "Face scan undertone %s disagrees with body photo %s; keeping the body photo",
        fp.undertone,
        coloring.undertone,
    )
    return coloring, "this_photo"


@router.post("/body", response_model=BodyResult)
async def analyze_body(file: UploadFile = File(...), face_profile: Optional[str] = Form(None)):
    """face_profile (optional): JSON of a previous FaceProfile, used to refine
    the undertone only. See _merge_face_undertone for why the face scan does
    not supply depth or contrast."""
    raw = await _read_upload(file)
    try:
        profile = await vision.analyze_body(vision.prepare_image(raw))
    except vision.PhotoRejected as exc:
        raise HTTPException(422, str(exc))
    except Exception as exc:
        return _fail(exc)

    try:
        coloring, source = _merge_face_undertone(profile.coloring, face_profile)

        return BodyResult(
            profile=profile,
            clothing=clothing_for(profile.body_shape),
            palette=palette_for(coloring.undertone, coloring.depth, coloring.contrast),
            palette_source=source,
        )
    except Exception as exc:
        return _fail(exc)