import { C } from '../utils/recommendation'
import { fmt } from '../utils/formatters'

export default function PriceHistoryTable({ analytics }) {
  return (
    <div>
              <p style={{ 
                color: C.textMuted, 
                fontSize: 10, 
                margin: "0 0 12px", 
                textTransform: "uppercase", 
                letterSpacing: ".08em",
                fontWeight: 600
              }}>
                📋 Price History
              </p>
              <div style={{ 
                background: C.card,
                backdropFilter: 'blur(20px)',
                border: `1px solid ${C.cardBorder}`,
                borderRadius: 14,
                overflow: "hidden"
              }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                  <thead>
                    <tr style={{ borderBottom: `1px solid ${C.cardBorder}` }}>
                      {["Tanggal", "Toko", "Harga", "Perubahan"].map((h, i) => (
                        <th key={h} style={{ 
                          padding: "10px 16px", 
                          color: C.textMuted, 
                          fontWeight: 500, 
                          textAlign: i >= 2 ? "right" : "left", 
                          fontSize: 9, 
                          textTransform: "uppercase", 
                          letterSpacing: ".06em" 
                        }}>
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(() => {
                      const seen = new Set()
                      return analytics.history
                        .filter(h => {
                          const k = h.timestamp?.slice(0,10) + "_" + h.price
                          if (seen.has(k)) return false
                          seen.add(k)
                          return true
                        })
                        .slice(0, 20)
                        .map((h, i, arr) => {
                          const prev = arr[i + 1]
                          const diff = prev ? ((h.price - prev.price) / prev.price * 100) : null
                          return (
                            <tr key={i} style={{ 
                              borderBottom: `1px solid ${C.cardBorder}`,
                              transition: 'background 0.15s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = C.cardHover}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                            >
                              <td style={{ padding: "8px 16px", color: C.textSecondary, fontSize: 11 }}>{h.timestamp?.slice(0, 10)}</td>
                              <td style={{ padding: "8px 16px", color: C.textSecondary, fontSize: 11 }}>{h.store || "—"}</td>
                              <td style={{ padding: "8px 16px", color: C.text, textAlign: "right", fontWeight: 600, fontSize: 11 }}>{fmt(h.price)}</td>
                              <td style={{ padding: "8px 16px", textAlign: "right" }}>
                                {diff !== null && Math.abs(diff) > 0.01 ? (
                                  <span style={{ 
                                    color: diff < 0 ? C.accent : C.red, 
                                    fontSize: 10,
                                    fontWeight: 600,
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: 2
                                  }}>
                                    {diff < 0 ? <ArrowDown size={10} /> : <ArrowUp size={10} />}
                                    {Math.abs(diff).toFixed(1)}%
                                  </span>
                                ) : (
                                  <span style={{ color: C.textMuted, fontSize: 10 }}>—</span>
                                )}
                              </td>
                            </tr>
                          )
                        })
                    })()}
                  </tbody>
                </table>
              </div>
            </div>
  )
}