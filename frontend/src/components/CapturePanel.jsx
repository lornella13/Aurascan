import { useEffect, useRef, useState } from "react";
import CameraCapture from "./CameraCapture.jsx";
import { compressImage, makeThumb } from "../lib/image.js";

export default function CapturePanel({ title, hint, facing, actionLabel, onSubmit }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const galleryRef = useRef(null);

  useEffect(() => {
    if (!file) return setPreview(null);
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function accept(next) {
    setError("");
    setCameraOpen(false);
    setFile(next);
    setStatus("Photo captured. Ready to analyze.");
  }

  function pick(e) {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    setError("");
    setFile(f);
  }

  async function run() {
    setBusy(true);
    setError("");
    try {
      const [blob, thumb] = await Promise.all([compressImage(file), makeThumb(file)]);
      await onSubmit(blob, thumb);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="capture">
      <h1>{title}</h1>
      <p className="hint">{hint}</p>

      {cameraOpen ? (
        <CameraCapture
          facing={facing}
          onCapture={accept}
          onCancel={() => setCameraOpen(false)}
          onFallback={() => {
            setCameraOpen(false);
            galleryRef.current.click();
          }}
        />
      ) : (
        <>
          <div className={`frame ${facing === "environment" ? " frame-tall" : ""}`}>
            {preview ? <img src={preview} alt="Your selected photo" /> : <span>No photo yet</span>}
          </div>

          <div className="row">
            <button className="btn" type="button" onClick={() => setCameraOpen(true)} disabled={busy}>
              {file ? "Retake" : "Take photo"}
            </button>
            <button
              className="btn btn-quiet"
              type="button"
              onClick={() => galleryRef.current.click()}
              disabled={busy}
            >
              Choose photo
            </button>
          </div>

          {file && (
            <button className="btn btn-primary" type="button" onClick={run} disabled={busy}>
              {busy ? "Analyzing…" : actionLabel}
            </button>
          )}
        </>
      )}

      <input ref={galleryRef} type="file" accept="image/*" onChange={pick} hidden />

      <p className="sr-only" role="status">
        {status}
      </p>
      {busy && <p className="status" role="status">Reading your photo. This takes a few seconds.</p>}
      {error && <p className="error" role="alert">{error}</p>}
    </section>
  );
}