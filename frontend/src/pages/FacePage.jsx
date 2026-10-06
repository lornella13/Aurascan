import { useState } from "react";
import CapturePanel from "../components/CapturePanel.jsx";
import FaceResult from "../components/FaceResult.jsx";
import { analyzeFace } from "../api.js";
import { saveEntry } from "../lib/storage.js";

export default function FacePage() {
  const [result, setResult] = useState(null);

  async function submit(blob, thumb) {
    const data = await analyzeFace(blob);
    saveEntry({ type: "face", thumb, result: data });
    setResult(data);
  }

  if (result) {
    return (
      <>
        <FaceResult result={result} />
        <button className="btn btn-quiet block" onClick={() => setResult(null)}>Scan again</button>
      </>
    );
  }
  return (
    <CapturePanel
      title="Scan your face"
      hint="Use natural light, no filter, and pull your hair back."
      facing="user"
      actionLabel="Analyze face"
      onSubmit={submit}
    />
  );
}
