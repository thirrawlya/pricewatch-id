import { useState, useEffect } from "react"

const API = "http://localhost:8000"

const fmtIDR = (n) =>
  n == null ? "-" : "Rp " + Number(n).toLocaleString("id-ID")

const fmtDate = (ts) => {
  const d = new Date(ts)
  return isNaN(d) ? ts : d.toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" })
}

const RECOMMENDATIONS = {
  good_buy: { label: "Good time to buy", cls: "bg-green-500/15 text-green-400 border-green-500/30" },
  wait: { label: "Better to wait", cls: "bg-amber-500/15 text-amber-400 border-amber-500/30" },
  neutral: { label: "Neutral", cls: "bg-gray-500/15 text-gray-300 border-gray-500/30" },
}

function RecommendationBadge({ recommendation, reason }) {
  const r = RECOMMENDATIONS[recommendation] || RECOMMENDATIONS.neutral
  return (
    <div className={`inline-flex flex-col gap-1 rounded-xl border px-4 py-3 ${r.cls}`}>
      <span className="text-sm font-semibold">{r.label}</span>
      {reason && <span className="text-xs opacity-80">{reason}</span>}
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="bg-gray-900 rounded-xl p-4">
      <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
      <p className="text-lg font-semibold mt-1">{value}</p>
    </div>
  )
}

function PriceChart({ history }) {
  const points = [...history]
    .filter((p) => p.price != null)
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))

  if (points.length < 2) {
    return (
      <p className="text-sm text-gray-500">
        Not enough price history yet to draw a chart.
      </p>
    )
  }

  const W = 600
  const H = 180
  const pad = 12
  const prices = points.map((p) => p.price)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1

  const coords = points.map((p, i) => {
    const x = pad + (i / (points.length - 1)) * (W - 2 * pad)
    const y = pad + (1 - (p.price - min) / range) * (H - 2 * pad)
    return [x, y]
  })

  const line = coords.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x} ${y}`).join(" ")
  const area = `${line} L${coords[coords.length - 1][0]} ${H - pad} L${coords[0][0]} ${H - pad} Z`

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" preserveAspectRatio="none">
      <path d={area} fill="rgb(59 130 246 / 0.15)" />
      <path d={line} fill="none" stroke="rgb(96 165 250)" strokeWidth="2" />
      {coords.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="2.5" fill="rgb(96 165 250)" />
      ))}
    </svg>
  )
}

function ProductDetail({ id, onBack }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let active = true
    fetch(`${API}/products/${id}/analytics`)
      .then(async (res) => {
        if (!res.ok) {
          const body = await res.json().catch(() => ({}))
          throw new Error(body.detail || `Request failed (${res.status})`)
        }
        return res.json()
      })
      .then((d) => active && setData(d))
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [id])

  return (
    <div>
      <button
        onClick={onBack}
        className="text-sm text-gray-400 hover:text-white transition mb-6"
      >
        ← Back to products
      </button>

      {loading && <p className="text-gray-500">Loading analytics...</p>}
      {error && <p className="text-red-400">{error}</p>}

      {data && (
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-bold">{data.product.name}</h2>
            <a
              href={data.product.url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-blue-400 hover:underline break-all"
            >
              {data.product.url}
            </a>
          </div>

          <RecommendationBadge recommendation={data.recommendation} reason={data.reason} />

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Stat label="Current" value={fmtIDR(data.current)} />
            <Stat label={`Avg (${data.period_days}d)`} value={fmtIDR(data.average)} />
            <Stat label="Lowest" value={fmtIDR(data.lowest)} />
            <Stat label="Highest" value={fmtIDR(data.highest)} />
          </div>

          <div className="bg-gray-900 rounded-xl p-4">
            <p className="text-sm font-medium mb-3">
              Price history{" "}
              <span className="text-gray-500">({data.history.length} points)</span>
            </p>
            <PriceChart history={data.history} />
          </div>

          <div className="bg-gray-900 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="text-left text-gray-500 border-b border-gray-800">
                <tr>
                  <th className="p-3 font-medium">Date</th>
                  <th className="p-3 font-medium">Store</th>
                  <th className="p-3 font-medium text-right">Price</th>
                </tr>
              </thead>
              <tbody>
                {data.history.map((h, i) => (
                  <tr key={i} className="border-b border-gray-800 last:border-0">
                    <td className="p-3 text-gray-400">{fmtDate(h.timestamp)}</td>
                    <td className="p-3 text-gray-400">{h.store || "-"}</td>
                    <td className="p-3 text-right font-medium">{fmtIDR(h.price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedId, setSelectedId] = useState(null)

  useEffect(() => {
    fetch(`${API}/products`)
      .then((res) => {
        if (!res.ok) throw new Error(`Request failed (${res.status})`)
        return res.json()
      })
      .then(setProducts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">PriceWatchID</h1>
        <p className="text-gray-400 mb-8">Buying intelligence for Indonesian shoppers</p>

        {selectedId != null ? (
          <ProductDetail key={selectedId} id={selectedId} onBack={() => setSelectedId(null)} />
        ) : loading ? (
          <p className="text-gray-500">Loading products...</p>
        ) : error ? (
          <p className="text-red-400">{error}</p>
        ) : (
          <div className="grid gap-3">
            {products.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedId(p.id)}
                className="text-left bg-gray-900 rounded-xl p-4 flex justify-between items-center hover:bg-gray-800 cursor-pointer transition"
              >
                <div>
                  <p className="font-medium text-sm line-clamp-1">{p.name}</p>
                  <p className="text-xs text-gray-500 mt-1">ID #{p.id}</p>
                </div>
                <span className="text-xs text-gray-600">→</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
