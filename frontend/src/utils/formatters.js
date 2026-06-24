/**
 * Currency formatter helper for Indonesian Rupiah (IDR).
 * 
 * @param {number|string} p - The price value to format
 * @returns {string} Formatted price string (e.g., "Rp162.000")
 */
export function fmt(p) {
  if (!p && p !== 0) return "—";
  return "Rp" + p.toLocaleString("id-ID");
}
