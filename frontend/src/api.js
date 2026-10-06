const BASE = import.meta.env.VITE_API_URL || "";

/** Turn any error response into something worth showing the user. */
export async function messageFromResponse(res) {
  const text = await res.text();
  let body = null;
  try {
    body = JSON.parse(text);
  } catch {
    console.error(`AuraScan: ${res.status} ${res.statusText} — non-JSON body:`, text.slice(0, 500));
    return `Server error (HTTP ${res.status}). Please try again.`;
  }

  const detail = body?.detail;
  if (typeof detail === "string") return detail;

  // FastAPI request-validation errors arrive as a list of objects.
  if (Array.isArray(detail)) {
    const parts = detail
      .map((d) => (d && typeof d.msg === "string" ? d.msg : JSON.stringify(d)))
      .filter(Boolean);
    if (parts.length) return `The server rejected that photo (${res.status}): ${parts.join("; ")}`;
  }

  console.error(`AuraScan: ${res.status} ${res.statusText} — unhandled body:`, text.slice(0, 500));
  return `Server error (HTTP ${res.status}). Please try again.`;
}

async function post(path, form) {
  let res;
  try {
    res = await fetch(`${BASE}/api/analyze/${path}`, { method: "POST", body: form });
  } catch (err) {
    console.error("AuraScan: network failure", err);
    throw new Error("Can't reach the server. Is the backend running on port 8000?");
  }
  if (!res.ok) throw new Error(await messageFromResponse(res));
  return res.json();
}

export function analyzeFace(blob) {
  const form = new FormData();
  form.append("file", blob, "face.jpg");
  return post("face", form);
}

export function analyzeBody(blob, faceProfile) {
  const form = new FormData();
  form.append("file", blob, "body.jpg");
  if (faceProfile) form.append("face_profile", JSON.stringify(faceProfile));
  return post("body", form);
}
