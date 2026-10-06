// One row of the colour palette: a chip and its name for each colour.
export default function SwatchStrip({ title, items }) {
  if (!Array.isArray(items) || !items.length) return null;

  return (
    <div className="swatches">
      <p className="swatches-title">{title}</p>
      <ul>
        {items.map((s) => (
          <li key={s.hex + s.name}>
            <span
              className="chip"
              style={{ background: s.hex }}
              aria-hidden="true"
            />
            {s.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
