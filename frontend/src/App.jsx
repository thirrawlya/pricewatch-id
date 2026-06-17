import { useState, useEffect } from "react"
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"

const API = "http://localhost:8000/api"
const C = {
  bg:     "#0B0F14",
  card:   "#111827",
  border: "#1F2937",
  text:   "#F8FAFC",
  muted:  "#374151",
  dim:    "#6B7280",
  accent: "#10B981",
  red:    "#EF4444",
  yellow: "#F59E0B",
}

function fmt(p) {
  if (!p && p !== 0) return "—"
  return "Rp" + p.toLocaleString("id-ID")
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: C.card, border: `0.5px solid ${C.border}`, borderRadius: 8, padding: "8px 14px" }}>
      <p style={{ color: C.dim, fontSize: 11, margin: "0 0 3px" }}>{label}</p>
      <p style={{ color: C.text, fontSize: 14, fontWeight: 700, margin: 0 }}>{fmt(payload[0]?.value)}</p>
    </div>
  )
}

function calcScore(a) {
  if (!a) return 50
  let s = 50
  if (a.change_pct <= -10) s += 30
  else if (a.change_pct <= -5) s += 20
  else if (a.change_pct <= 0)  s += 10
  else if (a.change_pct <= 5)  s -= 10
  else s -= 20
  const range = a.highest - a.lowest
  if (range > 0) {
    const pos = (a.current - a.lowest) / range
    if (pos < 0.2) s += 20
    else if (pos < 0.4) s += 10
    else if (pos > 0.8) s -= 15
  }
  return Math.min(100, Math.max(0, s))
}

function scoreColor(s) {
  return s >= 70 ? C.accent : s >= 45 ? C.yellow : C.red
}
function scoreLabel(s) {
  return s >= 70 ? "Beli sekarang" : s >= 45 ? "Pertimbangkan" : "Tunggu dulu"
}

// ── Sidebar item ──────────────────────────────────────────────
function SidebarItem({ product, active, onClick, analytics }) {
  const score = calcScore(analytics)
  const dot   = analytics?.current ? scoreColor(score) : C.muted
  const [hover, setHover] = useState(false)

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        padding: "10px 14px",
        cursor: "pointer",
        borderBottom: `0.5px solid ${C.bg}`,
        borderLeft: `2px solid ${active ? C.accent : "transparent"}`,
        background: active ? "#0d1520" : hover ? "#0d1117" : "transparent",
        transition: "background .1s",
      }}
    >
      <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
        <div style={{ width: 6, height: 6, borderRadius: "50%", background: dot, marginTop: 4, flexShrink: 0 }} />
        <div style={{ minWidth: 0 }}>
          <p style={{ color: active ? C.text : C.dim, fontSize: 11, margin: "0 0 2px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {product.name}
          </p>
          {analytics?.current
            ? <p style={{ fontSize: 11, color: C.muted, margin: 0 }}>
                {fmt(analytics.current)}
                {analytics.change_pct !== 0 &&
                  <span style={{ color: analytics.change_pct < 0 ? C.accent : C.red, marginLeft: 5 }}>
                    {analytics.change_pct > 0 ? "+" : ""}{analytics.change_pct}%
                  </span>}
              </p>
            : <p style={{ fontSize: 10, color: C.muted, margin: 0 }}>—</p>
          }
        </div>
      </div>
    </div>
  )
}

// ── Main App ──────────────────────────────────────────────────
export default function App() {
  const [products, setProducts]                 = useState([])
  const [selected, setSelected]                 = useState(null)
  const [analytics, setAnalytics]               = useState(null)
  const [sidebarAnalytics, setSidebarAnalytics] = useState({})
  const [days, setDays]                         = useState(30)
  const [loadingMain, setLoadingMain]           = useState(false)
  const [query, setQuery]                       = useState("")
  const [ready, setReady]                       = useState(false)

  // Load products, then auto-select first one
  useEffect(() => {
    fetch(`${API}/products`)
      .then(r => r.json())
      .then(response => {
        // FIX: Ambil data dari response.data
        const productsData = response.data || []
        setProducts(productsData)
        if (productsData.length > 0) {
          selectProduct(productsData[0], 30)
        }
        // Sidebar analytics — load in background, don't block
        productsData.forEach(p => {
          fetch(`${API}/products/${p.id}/analytics?days=30`)
            .then(r => r.json())
            .then(a => setSidebarAnalytics(prev => ({ ...prev, [p.id]: a })))
            .catch(() => {})
        })
        setReady(true)
      })
      .catch(err => console.error("Failed to load products:", err))
  }, [])

  function selectProduct(product, d = days) {
    setSelected(product)
    setAnalytics(null)
    setLoadingMain(true)
    fetch(`${API}/products/${product.id}/analytics?days=${d}`)
      .then(r => r.json())
      .then(a => { 
        setAnalytics(a)
        setLoadingMain(false)
      })
      .catch(() => setLoadingMain(false))
  }

  function changeDays(d) {
    setDays(d)
    if (selected) selectProduct(selected, d)
  }

  const filtered = query.trim()
    ? products.filter(p => p.name.toLowerCase().includes(query.toLowerCase()))
    : products

  const score    = calcScore(analytics)
  const sc       = scoreColor(score)

  const chartData = (() => {
    if (!analytics?.history) return []
    const seen = new Set()
    return analytics.history.slice().reverse().filter(h => {
      const d = h.timestamp?.slice(0, 10)
      if (seen.has(d)) return false
      seen.add(d); return true
    }).map(h => ({ date: h.timestamp?.slice(5, 10), price: h.price }))
  })()

  const signals = analytics ? [
    analytics.change_pct <= -5  && `Turun ${Math.abs(analytics.change_pct)}% dari rata-rata ${days}h`,
    analytics.current <= analytics.lowest * 1.02 && "Mendekati harga terendah historis",
    analytics.change_pct >= 5   && `Naik ${analytics.change_pct}% di atas rata-rata ${days}h`,
    analytics.current >= analytics.highest * 0.95 && "Mendekati harga tertinggi historis",
  ].filter(Boolean) : []

  return (
    <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", minHeight: "100vh", background: C.bg, fontFamily: "'Inter',system-ui,sans-serif", color: C.text }}>

      {/* ── Sidebar ─────────────────────────────────────── */}
      <aside style={{ borderRight: `0.5px solid ${C.border}`, display: "flex", flexDirection: "column", height: "100vh", position: "sticky", top: 0 }}>

        {/* Logo */}
        <div style={{ padding: "16px 14px 12px", borderBottom: `0.5px solid ${C.border}` }}>
          <p style={{ color: C.text, fontSize: 13, fontWeight: 700, margin: "0 0 1px", letterSpacing: "-.01em" }}>PriceWatchID</p>
          <p style={{ color: C.muted, fontSize: 10, margin: 0, letterSpacing: ".02em" }}>Buying Intelligence</p>
        </div>

        {/* Search */}
        <div style={{ padding: "10px 12px", borderBottom: `0.5px solid ${C.border}` }}>
          <input
            type="text"
            placeholder="Cari produk..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            style={{ width: "100%", background: C.bg, border: `0.5px solid ${C.border}`, borderRadius: 6, padding: "7px 10px", color: C.text, fontSize: 11, outline: "none", fontFamily: "inherit", boxSizing: "border-box" }}
          />
        </div>

        {/* Product list */}
        <div style={{ flex: 1, overflowY: "auto" }}>
          {filtered.map(p => (
            <SidebarItem
              key={p.id}
              product={p}
              active={selected?.id === p.id}
              onClick={() => selectProduct(p)}
              analytics={sidebarAnalytics[p.id]}
            />
          ))}
        </div>

        {/* Footer stats */}
        <div style={{ padding: "12px 14px", borderTop: `0.5px solid ${C.border}`, display: "flex", justifyContent: "space-between" }}>
          {[{ val: products.length, label: "produk" }, { val: "daily", label: "update" }, { val: "free", label: "always" }].map(s => (
            <div key={s.label} style={{ textAlign: "center" }}>
              <p style={{ color: C.text, fontSize: 12, fontWeight: 600, margin: 0 }}>{s.val}</p>
              <p style={{ color: C.muted, fontSize: 9, margin: "2px 0 0", textTransform: "uppercase", letterSpacing: ".06em" }}>{s.label}</p>
            </div>
          ))}
        </div>
      </aside>

      {/* ── Main ────────────────────────────────────────── */}
      <main style={{ padding: "28px 36px", overflowY: "auto" }}>

        {/* Header */}
        {selected && (
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
            <div style={{ minWidth: 0, flex: 1 }}>
              <p title={selected.name} style={{ fontSize: 18, fontWeight: 700, margin: "0 0 3px", letterSpacing: "-.02em", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 560 }}>
                {selected.name}
              </p>
              <a href={selected.url} target="_blank" rel="noreferrer" style={{ color: C.accent, fontSize: 11, textDecoration: "none" }}>
                Lihat di Tokopedia →
              </a>
            </div>
            <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
              {[30, 60, 90].map(d => (
                <button key={d} onClick={() => changeDays(d)} style={{ padding: "5px 12px", fontSize: 11, borderRadius: 6, border: `0.5px solid ${days === d ? C.dim : C.border}`, cursor: "pointer", fontFamily: "inherit", background: days === d ? C.card : "transparent", color: days === d ? C.text : C.dim }}>
                  {d}d
                </button>
              ))}
            </div>
          </div>
        )}

        {loadingMain && (
          <p style={{ color: C.muted, fontSize: 13 }}>Memuat data...</p>
        )}

        {!loadingMain && analytics && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>

            {/* ① RECOMMENDATION ─────────────────────────── */}
            <div style={{ background: C.card, border: `0.5px solid ${C.border}`, borderRadius: 12, padding: "20px 24px", display: "grid", gridTemplateColumns: "1fr auto", gap: 24, alignItems: "center" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                  <span style={{ color: sc, fontSize: 20, fontWeight: 700, letterSpacing: "-.02em" }}>{scoreLabel(score)}</span>
                  <span style={{ background: sc + "22", color: sc, fontSize: 11, fontWeight: 600, padding: "2px 10px", borderRadius: 100 }}>
                    {score}/100
                  </span>
                </div>
                <p style={{ color: C.dim, fontSize: 12, margin: "0 0 10px" }}>{analytics.reason}</p>
                <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                  {signals.map((s, i) => (
                    <div key={i} style={{ display: "flex", gap: 6, alignItems: "center" }}>
                      <span style={{ color: sc, fontSize: 11 }}>✓</span>
                      <span style={{ color: C.dim, fontSize: 11 }}>{s}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <p style={{ color: C.muted, fontSize: 10, margin: "0 0 4px", textTransform: "uppercase", letterSpacing: ".06em" }}>Harga sekarang</p>
                <p style={{ color: C.text, fontSize: 30, fontWeight: 700, margin: 0, letterSpacing: "-.03em" }}>{fmt(analytics.current)}</p>
                <p style={{ color: analytics.change_pct < 0 ? C.accent : analytics.change_pct > 0 ? C.red : C.dim, fontSize: 12, margin: "4px 0 0", fontWeight: 600 }}>
                  {analytics.change_pct > 0 ? "+" : ""}{analytics.change_pct}% dari rata-rata {days}d
                </p>
              </div>
            </div>

            {/* ② CHART ─────────────────────────────────── */}
            <div style={{ background: C.card, border: `0.5px solid ${C.border}`, borderRadius: 12, padding: "20px 24px" }}>
              <p style={{ color: C.muted, fontSize: 10, margin: "0 0 16px", textTransform: "uppercase", letterSpacing: ".08em" }}>
                Tren harga — {days} hari
              </p>
              {chartData.length < 2 ? (
                <div style={{ height: 180, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <p style={{ color: C.muted, fontSize: 12, textAlign: "center", lineHeight: 1.8 }}>
                    Belum cukup variasi data.<br />
                    <span style={{ color: C.muted, fontSize: 11 }}>Scraper perlu jalan di hari yang berbeda untuk menampilkan tren.</span>
                  </p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={chartData} margin={{ top: 8, right: 4, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={C.accent} stopOpacity={0.2} />
                        <stop offset="100%" stopColor={C.accent} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="date" tick={{ fill: C.muted, fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis
                      tickFormatter={v => `${(v / 1000000).toFixed(1)}jt`}
                      tick={{ fill: C.muted, fontSize: 10 }} axisLine={false} tickLine={false} width={36}
                      domain={([min, max]) => { const p = (max - min) * .2 || min * .02; return [min - p, max + p] }}
                    />
                    <Tooltip content={<ChartTooltip />} />
                    <ReferenceLine y={analytics.average} stroke={C.muted} strokeDasharray="3 3" strokeWidth={1} label={{ value: "avg", fill: C.muted, fontSize: 9, position: "right" }} />
                    <Area type="monotone" dataKey="price" stroke={C.accent} strokeWidth={2} fill="url(#ag)" dot={false} activeDot={{ r: 4, fill: C.accent, strokeWidth: 0 }} />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* ③ STAT CARDS ───────────────────────────── */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }}>
              {[
                { label: "Harga sekarang", value: fmt(analytics.current), color: C.text },
                { label: `Rata-rata ${days}d`, value: fmt(analytics.average), color: C.dim },
                { label: `Terendah ${days}d`, value: fmt(analytics.lowest), color: C.accent },
                { label: `Tertinggi ${days}d`, value: fmt(analytics.highest), color: C.red },
              ].map(c => (
                <div key={c.label} style={{ background: C.card, border: `0.5px solid ${C.border}`, borderRadius: 10, padding: "14px 16px" }}>
                  <p style={{ color: C.muted, fontSize: 10, margin: "0 0 8px", textTransform: "uppercase", letterSpacing: ".06em" }}>{c.label}</p>
                  <p style={{ color: c.color, fontSize: 16, fontWeight: 700, margin: 0, letterSpacing: "-.02em" }}>{c.value}</p>
                </div>
              ))}
            </div>

            {/* ④ HISTORY TABLE ────────────────────────── */}
            <div>
              <p style={{ color: C.muted, fontSize: 10, margin: "0 0 10px", textTransform: "uppercase", letterSpacing: ".08em" }}>Riwayat harga</p>
              <div style={{ background: C.card, border: `0.5px solid ${C.border}`, borderRadius: 10, overflow: "hidden" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                  <thead>
                    <tr style={{ borderBottom: `0.5px solid ${C.border}` }}>
                      {["Tanggal", "Toko", "Harga", "Perubahan"].map((h, i) => (
                        <th key={h} style={{ padding: "10px 16px", color: C.muted, fontWeight: 400, textAlign: i >= 2 ? "right" : "left", fontSize: 10, textTransform: "uppercase", letterSpacing: ".06em" }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(() => {
                      const seen = new Set()
                      return analytics.history
                        .filter(h => { const k = h.timestamp?.slice(0,10)+"_"+h.price; if (seen.has(k)) return false; seen.add(k); return true })
                        .slice(0, 20)
                        .map((h, i, arr) => {
                          const prev = arr[i + 1]
                          const diff = prev ? ((h.price - prev.price) / prev.price * 100) : null
                          return (
                            <tr key={i} style={{ borderBottom: `0.5px solid #0d1117` }}
                              onMouseEnter={e => e.currentTarget.style.background = "#0d1117"}
                              onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                            >
                              <td style={{ padding: "10px 16px", color: C.dim }}>{h.timestamp?.slice(0, 10)}</td>
                              <td style={{ padding: "10px 16px", color: C.dim }}>{h.store}</td>
                              <td style={{ padding: "10px 16px", color: C.text, textAlign: "right", fontWeight: 600 }}>{fmt(h.price)}</td>
                              <td style={{ padding: "10px 16px", textAlign: "right" }}>
                                {diff !== null && Math.abs(diff) > 0.01
                                  ? <span style={{ color: diff < 0 ? C.accent : C.red, fontSize: 11 }}>{diff > 0 ? "+" : ""}{diff.toFixed(1)}%</span>
                                  : <span style={{ color: C.muted }}>—</span>
                                }
                              </td>
                            </tr>
                          )
                        })
                    })()}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}
      </main>
    </div>
  )
}