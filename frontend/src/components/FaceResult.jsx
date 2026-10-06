import { label } from "../lib/text.js";

export default function FaceResult({ result }) {
  const { profile: p, routine, tips } = result;
  // Older history entries predate measurement, so anything but "measured" is an estimate.
  const measured = p.skin_hex_source === "measured";
  return (
    <article className="result">
      <header className="aura-head">
        <div className="aura" style={{ "--skin": p.skin_hex }} role="img" aria-label={`Detected skin tone ${p.skin_hex}`} />
        <div>
          <h2>{label(p.skin_type)} skin</h2>
          <dl className="facts">
            <div><dt>Undertone</dt><dd>{label(p.undertone)}</dd></div>
            <div><dt>Depth</dt><dd>{label(p.depth)}</dd></div>
            <div><dt>Eyes</dt><dd>{label(p.eye_color)}</dd></div>
            <div><dt>Hair</dt><dd>{label(p.hair_color)}</dd></div>
          </dl>
          <p className="swatch-note">
            <span className="swatch-value">{p.skin_hex}</span>
            <span className="muted">{measured ? "Measured from your photo" : "Estimated from your photo"}</span>
          </p>
          <p className="muted">
            Your camera and lighting change how skin looks. If this doesn't match you, retake the photo near a
            window.
          </p>
        </div>
      </header>

      {p.concerns.length > 0 && (
        <ul className="tags" aria-label="Skin concerns">
          {p.concerns.map((c) => <li key={c}>{label(c)}</li>)}
        </ul>
      )}

      <h2 className="section-title">Your makeup routine, in order</h2>
      <ol className="routine">
        {routine.map((s) => (
          <li key={s.order}>
            <h3>{s.category}</h3>
            <p className="product">{s.product}</p>
            <p className="shade">{s.shade_or_finish}</p>
            <p className="why">{s.why}</p>
          </li>
        ))}
      </ol>

      <aside className="tips">
        <h3>Before you buy</h3>
        <ul>{tips.map((t) => <li key={t}>{t}</li>)}</ul>
      </aside>
    </article>
  );
}
