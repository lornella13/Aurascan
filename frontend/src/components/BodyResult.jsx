import SwatchStrip from "./SwatchStrip.jsx";
import { label } from "../lib/text.js";
import { GARMENT_CATEGORIES, TEXT_CATEGORIES } from "../lib/garments.js";
import { buildSearchUrl } from "../lib/pinterest.js";

// A plain outbound link: the browser opens Pinterest, we fetch nothing.
function PinterestLink({ garment }) {
  return (
    <a
      className="guide-link"
      href={buildSearchUrl(garment)}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`See ${garment} ideas on Pinterest (opens in a new tab)`}
    >
      See on Pinterest
    </a>
  );
}

export default function BodyResult({ result }) {
  const { profile, clothing, palette, palette_source } = result;
  // Old saved results may be missing a guide section entirely.
  const itemsFor = (key) =>
    Array.isArray(clothing?.[key]) ? clothing[key] : [];

  return (
    <article className="result">
      <header>
        <h2>{label(profile.body_shape)} shape</h2>
        <p className="lead">{clothing.goal}</p>
      </header>

      <h2 className="section-title">Colours for you</h2>
      {/* A saved result from before the palette existed has none, so guard it. */}
      {palette ? (
        <>
          <p className="muted">
            {palette_source === "face_scan_undertone"
              ? `${label(palette.season)} palette, matched to the undertone from your face scan and the skin depth in this photo.`
              : `Estimated from this photo: ${label(palette.season)} palette. Scan your face first for a more accurate match.`}
          </p>
          <SwatchStrip title="Wear these" items={palette.best} />
          <SwatchStrip title="Easy neutrals" items={palette.neutrals} />
          <SwatchStrip title="Skip these" items={palette.avoid} />
        </>
      ) : (
        <p className="muted">
          Scan your face to get a colour palette built from your skin.
        </p>
      )}

      <h2 className="section-title">What fits you</h2>

      {/* Every recommendation reads the same way: a heading and a plain list.
          The clothing sections carry a Pinterest link per item. */}
      <div className="guide">
        {GARMENT_CATEGORIES.map(([key, title]) => {
          const items = itemsFor(key);
          if (!items.length) return null;
          return (
            <section key={key}>
              <h3>{title}</h3>
              <ul>
                {items.map((name) => (
                  <li key={name}>
                    <span>{name}</span>
                    <PinterestLink garment={name} />
                  </li>
                ))}
              </ul>
            </section>
          );
        })}

        {TEXT_CATEGORIES.map(([key, title]) => {
          const items = itemsFor(key);
          if (!items.length) return null;
          return (
            <section key={key}>
              <h3>{title}</h3>
              <ul>
                {items.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </section>
          );
        })}

        {itemsFor("avoid").length > 0 && (
          <section className="skip">
            <h3>Best to skip</h3>
            <ul>
              {itemsFor("avoid").map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </article>
  );
}
