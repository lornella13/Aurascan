import { useState } from "react";
import { Link } from "react-router-dom";

const STORY = [
  "I remember standing in a shop aisle with a foundation in my hand, holding it up to my jaw under the harsh white light. Too pale. Too orange. Too grey. I tried five more. Nothing looked like me.",
  "I left with nothing, and with a quiet feeling I couldn't name: that beauty had been built for someone else.",
  "For years I thought the problem was my skin. I copied looks from videos that never worked on my face. I bought colours that made me look tired. I stood in front of my wardrobe and felt like a stranger in my own clothes.",
  "It took me a long time to understand that nobody had ever shown me how to read my own face. My undertone. My skin type. The colours that make me glow, and the ones that dim me.",
  "I built AuraScan for the girl in that aisle. For every woman who has ever wondered whether the problem was her. It isn't. You just deserve someone to look at you carefully, and tell you what works for you.",
];

// Served from public/, so the build never depends on the file being processed.
const BUILDER_PHOTO = "/leilla-keza.jpg";
// Intrinsic size of the original file, so the browser reserves the right space.
const BUILDER_PHOTO_W = 2877;
const BUILDER_PHOTO_H = 3552;

function BuilderPhoto() {
  const [failed, setFailed] = useState(false);

  if (failed) {
    // A monogram rather than a broken-image icon, so the page still looks
    // finished if the photo has not been added yet.
    return (
      <div className="builder-photo builder-photo-fallback" aria-hidden="true">
        <span>LK</span>
      </div>
    );
  }

  return (
    <img
      className="builder-photo"
      src={BUILDER_PHOTO}
      // The original file is used as-is: no crop, no resampling, no filter.
      alt="Leilla Keza, the builder of AuraScan"
      width={BUILDER_PHOTO_W}
      height={BUILDER_PHOTO_H}
      loading="lazy"
      decoding="async"
      onError={() => setFailed(true)}
    />
  );
}

export default function AboutPage() {
  return (
    <article className="about">
      <header className="about-head">
        <h1>Why I built AuraScan</h1>
      </header>

      <div className="about-body">
        {STORY.map((paragraph) => (
          <p key={paragraph.slice(0, 32)}>{paragraph}</p>
        ))}
      </div>

      <section className="builder" aria-labelledby="builder-title">
        <p className="builder-eyebrow" id="builder-title">
          <span className="builder-rule" aria-hidden="true" />
          Meet the builder
        </p>

        <div className="builder-grid">
          <div className="builder-figure">
            <div className="builder-frame">
              <BuilderPhoto />
            </div>
            <h2 className="builder-name">Leilla Keza</h2>
            <p className="builder-role">Builder &amp; Creator of AuraScan</p>
          </div>

          <div className="builder-intro">
            <p>
              I built AuraScan to make beauty and skincare guidance more personal, practical and
              accessible. What started as a frustration with never finding the right foundation became
              a tool designed to help women understand what works for them.
            </p>
            <p>
              The story above is the reason it exists. I wrote the guidance, designed the experience
              and built the thing myself, because I wanted the advice I was never given.
            </p>
            <p className="builder-note">
              Every recommendation AuraScan gives is meant to be tried, adjusted and thrown away if
              it isn't right. Your face is the only data that matters.
            </p>
          </div>
        </div>
      </section>

      <div className="about-end">
        <p className="about-closing">So I built the thing I needed, and kept using it.</p>
        <Link className="btn btn-primary" to="/face">Try AuraScan</Link>
      </div>
    </article>
  );
}
