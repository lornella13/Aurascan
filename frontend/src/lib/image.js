// Resize in the browser before upload: faster on mobile data and cheaper to analyse.
async function loadBitmap(file) {
  try {
    return await createImageBitmap(file, { imageOrientation: "from-image" });
  } catch {
    return await createImageBitmap(file);
  }
}

function draw(bitmap, maxSide) {
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(bitmap.width * scale);
  canvas.height = Math.round(bitmap.height * scale);
  canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  return canvas;
}

export async function compressImage(file, maxSide = 1280, quality = 0.85) {
  const bitmap = await loadBitmap(file);
  const canvas = draw(bitmap, maxSide);
  return new Promise((resolve, reject) =>
    canvas.toBlob((b) => (b ? resolve(b) : reject(new Error("Couldn't read that photo."))), "image/jpeg", quality)
  );
}

export async function makeThumb(file, size = 160) {
  const bitmap = await loadBitmap(file);
  return draw(bitmap, size).toDataURL("image/jpeg", 0.7);
}
