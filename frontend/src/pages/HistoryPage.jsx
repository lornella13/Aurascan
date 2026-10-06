import { useState } from "react";
import FaceResult from "../components/FaceResult.jsx";
import BodyResult from "../components/BodyResult.jsx";
import { clearHistory, loadHistory } from "../lib/storage.js";
import { label } from "../lib/text.js";

export default function HistoryPage() {
  const [items, setItems] = useState(loadHistory);
  const [openId, setOpenId] = useState(null);
  const open = items.find((i) => i.id === openId);

  if (open) {
    return (
      <>
        <button className="btn btn-quiet" onClick={() => setOpenId(null)}>Back to history</button>
        {open.type === "face" ? <FaceResult result={open.result} /> : <BodyResult result={open.result} />}
      </>
    );
  }

  if (items.length === 0) {
    return (
      <section className="empty">
        <h1>No scans yet</h1>
        <p>Your face and body scans will show up here. They stay on this device.</p>
      </section>
    );
  }

  return (
    <section>
      <h1>History</h1>
      <ul className="history">
        {items.map((i) => (
          <li key={i.id}>
            <button onClick={() => setOpenId(i.id)}>
              <img src={i.thumb} alt="" />
              <span>
                <strong>
                  {i.type === "face" ? `${label(i.result.profile.skin_type)} skin` : `${label(i.result.profile.body_shape)} shape`}
                </strong>
                <small>{new Date(i.createdAt).toLocaleDateString()}</small>
              </span>
            </button>
          </li>
        ))}
      </ul>
      <button className="btn btn-quiet block" onClick={() => { clearHistory(); setItems([]); }}>
        Delete all scans
      </button>
    </section>
  );
}
