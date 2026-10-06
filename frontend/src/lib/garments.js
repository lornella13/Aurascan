// The recommendation sections a body result is built from.
//
// This used to map each recommendation to one of 20 garment silhouettes so the
// card could draw it. AuraScan no longer shows garment images, so only the
// section lists remain.

export const GARMENT_CATEGORIES = [
  ["tops", "Tops"],
  ["bottoms", "Bottoms"],
  ["dresses", "Dresses"],
  ["outerwear", "Outerwear"],
];

// The remaining guides stay plain text.
export const TEXT_CATEGORIES = [
  ["necklines", "Necklines"],
  ["fabrics", "Fabrics"],
];
