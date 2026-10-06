// Results (not full photos) are kept on this device only.
const KEY = "aurascan:history";
const MAX = 20;

export function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || [];
  } catch {
    return [];
  }
}

export function saveEntry(entry) {
  const next = [{ id: crypto.randomUUID(), createdAt: new Date().toISOString(), ...entry }, ...loadHistory()].slice(0, MAX);
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {}
  return next[0];
}

export function latestFace() {
  return loadHistory().find((e) => e.type === "face")?.result.profile || null;
}

export function clearHistory() {
  try {
    localStorage.removeItem(KEY);
  } catch {}
}

// Keys written by features that have since been removed. Without this, a
// visitor who used the old wardrobe keeps its data in their browser forever
// with no way to clear it, since the page that could clear it is gone.
const REMOVED_KEYS = ["aurascan:wardrobe"];

let purged = false;

export function purgeRemovedFeatures() {
  if (purged) return;
  purged = true;
  REMOVED_KEYS.forEach((key) => {
    try {
      localStorage.removeItem(key);
    } catch {}
  });
}
