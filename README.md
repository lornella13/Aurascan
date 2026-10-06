# AuraScan

A PWA that reads a face photo and a full-body photo and returns:

- **Face scan:** skin type, undertone, depth, concerns, plus a full makeup routine in application order (primer, foundation, concealer, setting powder, bronzer, blush, highlighter, brows, eyeshadow, eyeliner, mascara, lips, setting spray).
- **Body scan:** body shape, clothing that flatters (tops, bottoms, dresses, outerwear, necklines, fabrics), things to skip, and a colour palette: colours that suit her, easy neutrals, and colours to avoid.

## How it works

```
Phone / browser (React PWA)
   take or pick photo -> resize in browser -> POST /api/analyze/face | /body
                                                   |
FastAPI backend                                    v
   validate + strip EXIF + downscale  ->  vision.py (Gemini vision by default, returns strict JSON *description*)
                                                   |
                                                   v
   rules/makeup.py + rules/style.py   ->  recommendations (tables you control)
                                                   |
                                                   v
   JSON result -> UI + saved to History (on device only)
```

The AI only **describes** the person (skin type, undertone, body proportions). Every product, shade, cut and colour recommendation comes from the rules tables in `backend/app/rules/`, so results are consistent and you can tune them without changing a prompt.

If the user has already done a face scan, the body scan builds the colour palette from that scan (more accurate than reading skin colour off a full-body photo).

## Get a free API key (no credit card)

1. Go to https://aistudio.google.com/apikey and sign in with a Google account.
2. Click **Create API key** and copy it.
3. Paste it into `backend/.env` as `GEMINI_API_KEY`.

The free tier covers Flash-class Gemini models, which read images. Limits are per project and roughly 10-15 requests per minute and a few hundred to about a thousand per day, depending on the model. Your live limits are shown in AI Studio. When the quota is hit the app tells the user to wait a minute. Model names change over time: if you get a "model isn't available" error, set `GEMINI_MODEL` to another Flash or Flash-Lite model listed in AI Studio.

To use Claude instead later, set `VISION_PROVIDER=anthropic` and add `ANTHROPIC_API_KEY`. Nothing else changes.

## Run it locally

You need Node 18+ and Python 3.11+.

**1. Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then put your GEMINI_API_KEY in .env
uvicorn app.main:app --reload --port 8000
```

Docs and a try-it page: http://localhost:8000/docs

**2. Frontend** (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to the backend.

**3. Tests**

```bash
cd backend && pytest
```

## Try it on your phone

Camera access and PWA install both need HTTPS (localhost is the only exception). Easiest options while developing:

- Deploy the frontend to Vercel/Netlify/Cloudflare Pages and the backend to Render/Fly/Railway. Set `VITE_API_URL` (frontend) to the backend URL and `ALLOWED_ORIGINS` (backend) to the frontend URL.
- Or tunnel your dev server (`cloudflared tunnel --url http://localhost:5173`).

For a static host, add an SPA fallback so `/body` and `/history` load `index.html`.

To check the PWA build: `npm run build && npm run preview`, then look at Application > Manifest in Chrome DevTools.

## Project layout

```
backend/
  app/main.py            FastAPI app + CORS
  app/routes/analyze.py  POST /api/analyze/face, /api/analyze/body
  app/vision.py          image prep + Claude vision call + JSON validation
  app/schemas.py         all request/response models
  app/rules/makeup.py    skin profile -> makeup routine
  app/rules/style.py     body shape -> clothing guide; colouring -> season palette
  tests/                 rules + endpoint tests (vision mocked)
frontend/
  vite.config.js         PWA manifest + service worker (vite-plugin-pwa)
  src/pages/             Face, Body, History
  src/components/        CapturePanel, FaceResult, BodyResult, SwatchStrip
  src/lib/               image resize, on-device history
```

## Privacy

- Photos are processed in memory and never saved on the server. EXIF data (including GPS) is stripped before analysis.
- History keeps results and a tiny thumbnail in the browser's localStorage. "Delete all scans" clears it.
- The photo is sent to Google's Gemini API for analysis. **On Google's free tier, Google may use submitted content to improve its products.** Face and body photos are sensitive, so tell users clearly, ask for consent before the first scan, and mention it in your privacy policy. Paid API usage is not used that way, so switching to a paid tier later removes this concern.
- Your API key stays on the server. Never put it in the frontend.

## Known limits and good next steps

- Skin tone reads depend on lighting. Add a "does this match your skin?" confirmation step and a manual override for undertone and season.
- Test with a wide range of skin tones before launch and tune the prompts and tables from what you see.
- Add rate limiting (for example `slowapi`) and user accounts before going public. The free quota is shared by all your users and will run out quickly with real traffic.
- Add a live camera overlay (face oval, "step back" guide) with `getUserMedia`, and on-device face and pose checks (MediaPipe) to reject bad photos before upload.
- Add product links, budget and style preferences, and a saved profile.
- Colour recommendations use a 4-season heuristic in `pick_season()`. Swap it for a 12-season model if you want finer results.
- Cosmetic guidance only, not medical advice.
