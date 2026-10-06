import { useState } from "react";
import CapturePanel from "../components/CapturePanel.jsx";
import BodyResult from "../components/BodyResult.jsx";
import { analyzeBody } from "../api.js";
import { latestFace, saveEntry } from "../lib/storage.js";

export default function BodyPage() {
  const [result, setResult] = useState(null);

  async function submit(blob, thumb) {
    const data = await analyzeBody(blob, latestFace());
    saveEntry({ type: "body", thumb, result: data });
    setResult(data);
  }

  if (result) {
    return (
      <>
        <BodyResult result={result} />
        <button className="btn btn-quiet block" onClick={() => setResult(null)}>Scan again</button>
      </>
    );
  }
  return (
    <CapturePanel
      title="Scan your outfit"
      hint="Stand a few steps back so your whole body is in frame. Fitted clothes give the best read."
      facing="environment"
      actionLabel="Analyze body"
      onSubmit={submit}
    />
  );
}
