import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .routes import analyze

logger = logging.getLogger("aurascan")
logging.basicConfig(level=logging.INFO)

# httpx and httpcore log every request at INFO, including the full URL and its
# query string. Keeping them at WARNING avoids putting request URLs, and
# anything sensitive a caller put in one, into the logs.
for noisy in ("httpx", "httpcore", "httpcore.http11", "httpcore.proxy"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

app = FastAPI(title="AuraScan API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().allowed_origins.split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(analyze.router)


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    """Never let an unexpected error escape as a plain-text 500: the frontend
    can only show a useful message when the body is JSON with a string detail."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on the server. Please try again."},
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}