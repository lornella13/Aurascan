import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import Logo from "./components/Logo.jsx";
import FacePage from "./pages/FacePage.jsx";
import BodyPage from "./pages/BodyPage.jsx";
import HistoryPage from "./pages/HistoryPage.jsx";
import LandingPage from "./pages/LandingPage.jsx";
import AboutPage from "./pages/AboutPage.jsx";
import { purgeRemovedFeatures } from "./lib/storage.js";

const SCAN_ROUTES = ["/face", "/body", "/history"];

function NotFound() {
  return (
    <section className="notfound">
      <h1>That page isn't here</h1>
      <p className="hint">The link may be old, or the address mistyped.</p>
      <Link className="btn btn-primary" to="/">Back to the start</Link>
    </section>
  );
}

// Clear out data left by features that no longer exist.
purgeRemovedFeatures();

export default function App() {
  const { pathname } = useLocation();
  const isScan = SCAN_ROUTES.includes(pathname);

  return (
    <div className="app">
      <header className="topbar">
        {isScan ? (
          <div className="topbar-scan">
            <Link className="wordmark" to="/" aria-label="AuraScan home"><Logo variant="full" height={28} /></Link>
            <Link className="topbar-link" to="/about">About</Link>
          </div>
        ) : (
          <div className="topbar-nav">
            <Link className="wordmark" to="/" aria-label="AuraScan home"><Logo variant="full" height={28} /></Link>
            <nav className="topnav" aria-label="Main">
              <Link to="/about">About</Link>
              <Link className="btn btn-primary topnav-cta" to="/face">Start scanning</Link>
            </nav>
          </div>
        )}
      </header>

      <main className={isScan ? "" : "main-wide"}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/face" element={<FacePage />} />
          <Route path="/body" element={<BodyPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>

      {isScan && (
        <nav className="tabs" aria-label="Main">
          <NavLink to="/face" end>Face</NavLink>
          <NavLink to="/body" end>Body</NavLink>
          <NavLink to="/history" end>History</NavLink>
        </nav>
      )}
    </div>
  );
}