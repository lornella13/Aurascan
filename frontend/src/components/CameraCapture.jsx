import { useCallback, useEffect, useRef, useState } from "react";

const GUIDES = {
  user: {
    line: "Centre your face in the oval",
    mirror: true,
    shape: (
      <ellipse className="camera-guide-shape" cx="100" cy="78" rx="46" ry="58" />
    ),
  },
  environment: {
    line: "Step back until your whole body fits",
    mirror: false,
    shape: (
      <>
        <circle className="camera-guide-shape" cx="100" cy="30" r="14" />
        <path
          className="camera-guide-shape"
          d="M100 46c-13 0-23 9-25 22l-4 30 8 3 3-18v41h9v26h7V83h4v26h7V83l3 18 8-3-4-30c-2-13-12-22-25-22z"
        />
        <path className="camera-guide-line" d="M22 24V8h16M178 24V8h-16M22 152v16h16M178 152v16h-16" />
      </>
    ),
  },
};

function friendlyError(err) {
  switch (err?.name) {
    case "NotAllowedError":
    case "SecurityError":
      return "Camera access was blocked. Allow the camera in your browser's site settings, or choose a photo instead.";
    case "NotFoundError":
    case "OverconstrainedError":
      return "No camera found on this device. Choose a photo instead.";
    case "NotReadableError":
    case "AbortError":
      return "Your camera is being used by another app. Close it and try again.";
    default:
      return "The camera could not start. Choose a photo instead.";
  }
}

/**
 * Live camera capture. Renders the stream, an alignment guide and a shutter
 * button, then hands a JPEG File back through onCapture. Nothing is uploaded
 * from here; the caller decides what happens next.
 */
export default function CameraCapture({ facing = "user", onCapture, onCancel, onFallback }) {
  const guide = GUIDES[facing] || GUIDES.user;
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const shutterRef = useRef(null);
  const requestIdRef = useRef(0);
  const [status, setStatus] = useState("starting");
  const [error, setError] = useState("");
  const [useFront, setUseFront] = useState(facing !== "environment");
  const [multiCamera, setMultiCamera] = useState(false);

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  const start = useCallback(async (front) => {
    const id = ++requestIdRef.current;
    stopStream();
    setError("");

    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus("error");
      setError("The camera needs a secure connection (https). Choose a photo instead.");
      return;
    }

    setStatus("starting");
    const open = (video) => navigator.mediaDevices.getUserMedia({ video, audio: false });

    let stream;
    try {
      try {
        stream = await open({
          facingMode: { ideal: front ? "user" : "environment" },
          width: { ideal: 1280 },
          height: { ideal: 1280 },
        });
      } catch (err) {
        // A narrow constraint set (e.g. a back camera that only does 1080p)
        // can fail outright; fall back to whatever the device offers.
        if (err?.name !== "OverconstrainedError") throw err;
        stream = await open(true);
      }
    } catch (err) {
      if (id !== requestIdRef.current) return;
      setStatus("error");
      setError(friendlyError(err));
      return;
    }

    if (id !== requestIdRef.current) {
      stream.getTracks().forEach((t) => t.stop());
      return;
    }

    streamRef.current = stream;
    const video = videoRef.current;
    if (video) {
      video.srcObject = stream;
      try {
        await video.play();
      } catch {
        /* autoplay of a muted stream is allowed; ignore a late abort */
      }
    }
    if (id !== requestIdRef.current) {
      stopStream();
      return;
    }

    const devices = await navigator.mediaDevices.enumerateDevices().catch(() => []);
    const cameras = devices.filter((d) => d.kind === "videoinput").length;
    setMultiCamera(cameras > 1);
    setStatus("live");
    setUseFront(front);
  }, [stopStream]);

  useEffect(() => {
    start(facing !== "environment");
    return () => {
      requestIdRef.current++;
      stopStream();
    };
  }, [start, stopStream, facing]);

  // The shutter is disabled while the stream warms up, so focus it once it is live.
  useEffect(() => {
    if (status === "live") shutterRef.current?.focus();
  }, [status]);

  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") onCancel();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  function shutter() {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      stopStream();
      if (!blob) {
        setStatus("error");
        setError("The photo could not be saved. Choose a photo instead.");
        return;
      }
      const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
      onCapture(file);
    }, "image/jpeg", 0.92);
  }

  function switchCamera() {
    start(!useFront);
  }

  return (
    <div className="camera">
      <p className="sr-only" role="status">
        {status === "live" ? "Camera ready" : ""}
      </p>

      <div className={`frame camera-frame${facing === "environment" ? " frame-tall" : ""}`}>
        {status === "error" ? (
          <span className="camera-placeholder">Camera unavailable</span>
        ) : (
          <>
            <video
              ref={videoRef}
              className={`camera-video${guide.mirror && useFront ? " camera-mirror" : ""}`}
              autoPlay
              playsInline
              muted
              aria-label={facing === "user" ? "Front camera preview" : "Back camera preview"}
            />
            <svg className="camera-guide" viewBox="0 0 200 176" aria-hidden="true" focusable="false">
              {guide.shape}
            </svg>
            {status !== "live" && <span className="camera-status">Starting camera…</span>}
          </>
        )}
      </div>

      <p className="camera-line">{guide.line}</p>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {status !== "error" && (
        <div className="camera-controls">
          {multiCamera && (
            <button className="btn btn-quiet" type="button" onClick={switchCamera}>
              Switch camera
            </button>
          )}
          <button
            ref={shutterRef}
            className="camera-shutter"
            type="button"
            onClick={shutter}
            disabled={status !== "live"}
            aria-label="Take picture"
          >
            <span className="camera-shutter-ring" aria-hidden="true" />
          </button>
          <button className="btn btn-quiet" type="button" onClick={onCancel}>
            Cancel
          </button>
        </div>
      )}

      {error && onFallback && (
        <button className="btn btn-quiet block" type="button" onClick={onFallback}>
          Choose photo instead
        </button>
      )}
    </div>
  );
}