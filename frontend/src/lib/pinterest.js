// The "See on Pinterest" link builder.
//
// This builds a plain outbound link that the user clicks. Nothing here fetches
// anything from Pinterest: AuraScan never requests Pinterest content, and the
// only Pinterest script the app can load is gone, so the app makes no outbound
// request to Pinterest at all.

export const PINTEREST_SEARCH_BASE = "https://www.pinterest.com/search/pins/";

/** "wrap top" + "terracotta" -> a Pinterest search link. Never fetched. */
export function buildSearchUrl(garment, colorName) {
  const query = [garment, colorName, "women outfit"]
    .map((part) => String(part || "").trim())
    .filter(Boolean)
    .join(" ");
  return `${PINTEREST_SEARCH_BASE}?q=${encodeURIComponent(query)}`;
}
