export const label = (s) => {
  const t = String(s).replace(/_/g, " ");
  return t.charAt(0).toUpperCase() + t.slice(1);
};
