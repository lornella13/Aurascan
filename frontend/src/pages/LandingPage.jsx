import { Link } from "react-router-dom";
import Logo from "../components/Logo.jsx";

const STEPS = [
  {
    title: "Take or upload a face photo",
    body: "Use your camera or pick one you already have. Natural light, no filter and hair pulled back give the most accurate read.",
  },
  {
    title: "Get your skin profile and a routine in order",
    body: "Your skin type, undertone, depth and visible concerns come back first, then a full routine in the order you apply it: primer, foundation, concealer, setting powder, bronzer, blush, highlighter, brows, eyeshadow, eyeliner, mascara, lips and setting spray.",
  },
  {
    title: "Add a full-body photo",
    body: "A second scan reads your proportions and colouring, then works out the clothes that fit your shape and the colours that suit you.",
  },
];

export default function LandingPage() {
  return (
    <div className="landing">
      <section className="landing-hero">
        <div className="landing-aura">
          <Logo variant="mark" height={92} />
        </div>
        <h1>Photo in. Makeup and outfit advice built for you out.</h1>
        <p className="landing-sub">
          AuraScan reads your skin tone, undertone and proportions from a photo, then turns them into a
          makeup routine in the order you apply it and a colour palette that suits you.
        </p>
        <div className="landing-actions">
          <Link className="btn btn-primary" to="/face">Start scanning</Link>
          <Link className="btn btn-quiet" to="/about">Our story</Link>
        </div>
      </section>

      <section className="landing-section" aria-labelledby="how-title">
        <h2 id="how-title">How AuraScan works</h2>
        <ol className="landing-steps">
          {STEPS.map((step) => (
            <li key={step.title}>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="landing-section" aria-labelledby="give-title">
        <h2 id="give-title">What you get</h2>
        <div className="landing-give">
          <div className="landing-give-item landing-give-face">
            <h3>Your face result</h3>
            <p>
              Your skin type, undertone and depth, an average skin colour you can match in store, and the
              concerns visible in the photo. Your eye, hair and lip colour too.
            </p>
            <p>
              Then the routine: thirteen steps in the order they go on, each with a product, a shade or
              finish, and a reason it was chosen for your skin rather than a trend.
            </p>
          </div>
          <div className="landing-give-item landing-give-body">
            <h3>Your body result</h3>
            <p>
              Your body shape, whether your shoulders or hips read wider, how defined your waist is and
              whether your torso or legs are longer.
            </p>
            <p>
              With it a clothing guide covering tops, bottoms, dresses, outerwear, necklines and fabrics,
              plus what to skip. And a colour palette: colours that suit you, easy neutrals, and colours to
              leave on the rail.
            </p>
          </div>
        </div>
      </section>

      <section className="landing-section" aria-labelledby="privacy-title">
        <h2 id="privacy-title">Your photos and privacy</h2>
        <p>
          Photos are resized on your device before they are uploaded, so the file that leaves your phone is
          smaller than the one in your camera roll.
        </p>
        <p>
          The photo is then analysed by Google Gemini, Google's AI service. AuraScan does not store your
          photos on its servers, but the photo does travel to Google to be analysed, so treat it as shared
          with a third party. On Gemini's free tier, Google may use submitted content to improve its own
          products.
        </p>
        <p>
          Scan history lives in your browser, on your device only. It holds your results and a small
          thumbnail, never the full photo, and Delete all scans clears it whenever you want.
        </p>
        <p>
          AuraScan shows no garment images. "See on Pinterest" is a plain link that opens a Pinterest
          search in a new tab, and AuraScan requests nothing from Pinterest until you click it.
        </p>
      </section>

      <p className="landing-note">Suggestions are cosmetic guidance, not medical advice.</p>

      <footer className="landing-footer">
        <Link className="landing-footer-mark" to="/">AuraScan</Link>
        <nav className="landing-footer-links" aria-label="Footer">
          <Link to="/about">About</Link>
          <Link to="/face">Start scanning</Link>
        </nav>
      </footer>
    </div>
  );
}
