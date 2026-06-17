import { useState, useEffect } from "react"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

function fmt(price) {
  if (!price) return "-"
  return "Rp" + price.toLocaleString("id-ID")
}

function RecommendationBar({ recommendation, reason, changePct }) {
  const config = {
    good_buy: {
      bg: "bg-emerald-950",
      border: "border-emerald-800",
      text: "text-emerald-400",
      icon: "↓",
      label: "Good time to buy",
    },
    wait: {
      bg: "bg-red-950",
      border: "border-red-900",
      text: "text-red-400",
      icon: "↑",
      label: "Wait",
    },
    neutral: {
      bg: "bg-zinc-900",
      border: "border-zinc-700",
      text: "text-zinc-300",
      icon: "→",
      label: "Neutral",
    },
  }

  const c = config[recommendation] || config.neutral

  return (
    <div className={`${c.bg} border ${c.border} rounded-2xl px-5 py-4 flex justify-between items-center`}>
      <div>
        <p className={`text-sm font-medium ${c.text}`}>{c.label}</p>
        <p className={`text-xs mt-1 ${c.text} opacity-70`}>{reason}</p>
      </div>
      <span className={`text-2xl ${c.text}`}>{c.icon}</span>
    </div>
  )
}

function PriceTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-zinc-800 border border-zinc-700 rounded-xl px-3 py-2 text-xs">
      <p className="text-zinc-400 mb-1">{label}</p>
      <p className="text-white font-medium">{fmt(payload[0]?.value)}</p>
    </div>
  )
}

function SidebarItem({ product, selected, onClick, analytics }) {
  const isSelected = selected?.id === product.id
  const rec = analytics?.recommendation
  const dot =
    rec === "good_buy"
      ? "bg-emerald-400"
      : rec === "wait"
      ? "bg-red-400"
      : "bg-zinc-600"

  return (
    <div
      onClick={onClick}
      className={`
        px-4 py-3 cursor-pointer transition border-b border-zinc-900
        hover:bg-zinc-900
        ${isSelected ? "bg-zinc-900 border-l-2 border-l-blue-500" : ""}
      `}
    >
      <div className="flex items-start gap-2">
        <span className={`mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${dot}`} />
        <div className="min-w-0">
          <p className="text-sm text-zinc-300 line-clamp-2 leading-snug">
            {product.name}
          </p>
          {analytics?.current ? (
            <p className="text-xs text-zinc-500 mt-1">
              {fmt(analytics.current)}
              {analytics.change_pct !== 0 && (
                <span className={analytics.change_pct < 0 ? "text-emerald-400" : "text-red-400"}>
                  {" "}{analytics.change_pct > 0 ? "+" : ""}{analytics.change_pct}%
                </span>
              )}
            </p>
          ) : (
            <p className="text-xs text-zinc-600 mt-1">No data yet</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [products, setProducts] = useState([])
  const [selected, setSelected] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [sidebarAnalytics, setSidebarAnalytics] = useState({})
  const [days, setDays] = useState(30)
  const [loading, setLoading] = useState(true)
  const [loadingAnalytics, setLoadingAnalytics] = useState(false)

  useEffect(() => {
    fetch(`${API_URL}/api/products?limit=100`)
      .then(res => res.json())
      .then(data => {
        const productList = data.data || []
        setProducts(productList)
        setLoading(false)
        // Fetch price history for sidebar
        productList.slice(0, 20).forEach(p => {
          fetch(`${API_URL}/api/products/${p.id}/prices?limit=50`)
            .then(r => r.json())
            .then(hist => {
              if (hist.prices?.length > 0) {
                const latest = hist.prices[0]
                setSidebarAnalytics(prev => ({ 
                  ...prev, 
                  [p.id]: {
                    current: latest.price,
                    change_pct: ) => {
    setLoadingAnalytics(true)
    fetch(`${API_URL}/api/products/${product.id}/prices?limit=50`)
      .then(res => res.json())
      .then(data => {
        const prices = data.prices || []
        if (prices.length === 0) {
          setAnalytics(null)
          setLoadingAnalytics(false)
          return
        }

        const current = prices[0].price
        const avg = prices.reduce((sum, p) => sum + (p.price || 0), 0) / prices.length
        const lowest = Math.min(...prices.map(p => p.price || current))
        const oldest = prices[prices.length - 1]?.price || current
        const change_pct = oldest ? Math.round((current - oldest) / oldest * 100) : 0

        setAnalytics({
          current,
          average: Math.round(avg),
          lowest,
          change_pct,
          history: prices,
          recommendation: current <= lowest * 1.05 ? "good_buy" : current >= lowest * 1.2 ? "wait" : "neutral",
          reason: current <= lowest * 1.05 ? "At historical low" : current >= lowest * 1.2 ? "Price is high" : "Stable price"
        })
        setLoadingAnalytics(false)
      })
      .catch(err => {)
  }

  const changeDays = (d) => {
    setDays(d)
    if (selected) loadAnalytics(selecteucts:", err)
        setLoading(false)
      })
  }, [])

  const loadAnalytics = (product, d) => {
    setLoadingAnalytics(true)
    fetch(`${API}/products/${product.id}/analytics?days=${d}`)
      .then(res => res.json())
      .then(data => {
        setAnalytics(data)
        setLoadingAnalytics(false)
      })
      .catch(() => setLoadingAnalytics(false))
  }

  const selectProduct = (product) => {
    setSelected(product)
    setAnalytics(null)
    loadAnalytics(product, days)
  }

  const changeDays = (d) => {
    setDays(d)
    if (selected) loadAnalytics(selected, d)
  }

  // Deduplicate history by date for chart
  const chartData = (() => {
    if (!analytics?.history) return []
    const seen = new Set()
    return analytics.history
      .slice()
      .reverse()
      .filter(h => {
        const date = h.timestamp?.slice(0, 10)
        if (seen.has(date)) return false
        seen.add(date)
        return true
      })
      .map(h => ({
        date: h.timestamp?.slice(5, 10),
        price: h.price,
      }))
  })()

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex">
      {/* Sidebar */}
      <aside className="w-72 border-r border-zinc-800 h-screen overflow-y-auto flex flex-col flex-shrink-0">
        <div className="p-5 border-b border-zinc-800">
          <h1 className="text-base font-semibold">PriceWatchID</h1>
          <p className="text-xs text-zinc-500 mt-0.5">Track prices. Buy smarter.</p>
          <div className="mt-3 flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-2">
            <span className="text-zinc-500 text-sm">⌕</span>
            <input
              type="text"
              placeholder="Search products..."
              className="bg-transparent text-sm text-zinc-300 placeholder-zinc-600 outline-none w-full"
              onChange={e => {
                const q = e.target.value.toLowerCase()
                // visual filter only — full impl can be added
              }}
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <p className="p-4 text-zinc-500 text-sm">Loading...</p>
          ) : (
            products.map(p => (
              <SidebarItem
                key={p.id}
                product={p}
                selected={selected}
                onClick={() => selectProduct(p)}
                analytics={sidebarAnalytics[p.id]}
              />
            ))
          )}
        </div>

        <div className="p-4 border-t border-zinc-800 grid grid-cols-3 text-center">
          <div>
            <p className="text-sm font-medium text-zinc-200">{products.length}</p>
            <p className="text-xs text-zinc-600 mt-0.5">products</p>
          </div>
          <div>
            <p className="text-sm font-medium text-zinc-200">—</p>
            <p className="text-xs text-zinc-600 mt-0.5">records</p>
          </div>
          <div>
            <p className="text-sm font-medium text-zinc-200">—</p>
            <p className="text-xs text-zinc-600 mt-0.5">stores</p>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        {!selected ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-sm">
              <h2 className="text-3xl font-semibold mb-3">PriceWatchID</h2>
              <p className="text-zinc-400 text-sm leading-relaxed">
                Track marketplace prices, monitor trends, and make smarter buying decisions.
              </p>
              <p className="text-zinc-600 text-xs mt-6">
                Select a product from the sidebar to begin.
              </p>
            </div>
          </div>
        ) : (
          <div className="p-8 max-w-4xl">
            {/* Header */}
            <div className="flex items-start justify-between mb-8 gap-4">
              <div className="min-w-0">
                <h2 className="text-xl font-semibold leading-snug line-clamp-1" title={selected.name}>
                  {selected.name}
                </h2>
                <a
                  href={selected.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-400 text-xs hover:underline mt-1 inline-block"
                >
                  View on Tokopedia →
                </a>
              </div>

              <div className="flex gap-1 flex-shrink-0">
                {[30, 60, 90].map(d => (
                  <button
                    key={d}
                    onClick={() => changeDays(d)}
                    className={`
                      px-3 py-1.5 text-xs rounded-lg border transition
                      ${days === d
                        ? "bg-zinc-700 border-zinc-600 text-white"
                        : "border-zinc-800 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300"
                      }
                    `}
                  >
                    {d}d
                  </button>
                ))}
              </div>
            </div>

            {loadingAnalytics ? (
              <p className="text-zinc-500 text-sm">Loading data...</p>
            ) : !analytics ? (
              <p className="text-zinc-500 text-sm">No data available.</p>
            ) : (
              <div className="space-y-5">
                {/* Stat cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { label: "Current price", value: fmt(analytics.current), highlight: true },
                    { label: `${days}d average`, value: fmt(analytics.average) },
                    { label: `${days}d lowest`, value: fmt(analytics.lowest), green: true },
                    {
                      label: `${days}d change`,
                      value: `${analytics.change_pct > 0 ? "+" : ""}${analytics.change_pct}%`,
                      green: analytics.change_pct < 0,
                      red: analytics.change_pct > 0,
                    },
                  ].map(card => (
                    <div key={card.label} className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
                      <p className="text-xs text-zinc-500 mb-2">{card.label}</p>
                      <p className={`text-lg font-semibold ${
                        card.highlight ? "text-white" :
                        card.green ? "text-emerald-400" :
                        card.red ? "text-red-400" :
                        "text-zinc-200"
                      }`}>
                        {card.value}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Chart */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
                  <p className="text-xs text-zinc-500 mb-4">
                    Price trend — {days} days
                  </p>
                  {chartData.length < 2 ? (
                    <div className="h-32 flex items-center justify-center">
                      <p className="text-zinc-600 text-sm text-center">
                        Not enough data points yet.<br/>Scraper needs more runs to show a trend.
                      </p>
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height={160}>
                      <AreaChart data={chartData} margin={{ top: 8, right: 4, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#34d399" stopOpacity={0.2} />
                            <stop offset="100%" stopColor="#34d399" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <XAxis
                          dataKey="date"
                          tick={{ fill: "#52525b", fontSize: 11 }}
                          axisLine={false}
                          tickLine={false}
                        />
                        <YAxis
                          tickFormatter={v => `${(v / 1000000).toFixed(1)}jt`}
                          tick={{ fill: "#52525b", fontSize: 11 }}
                          axisLine={false}
                          tickLine={false}
                          width={38}
                          domain={([min, max]) => {
                            const pad = (max - min) * 0.1 || min * 0.02
                            return [Math.floor(min - pad), Math.ceil(max + pad)]
                          }}
                        />
                        <Tooltip content={<PriceTooltip />} />
                        <Area
                          type="monotone"
                          dataKey="price"
                          stroke="#34d399"
                          strokeWidth={2}
                          fill="url(#priceGrad)"
                          dot={false}
                          activeDot={{ r: 4, fill: "#34d399" }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}
                </div>

                {/* Recommendation */}
                <RecommendationBar
                  recommendation={analytics.recommendation}
                  reason={analytics.reason}
                  changePct={analytics.change_pct}
                />

                {/* Price history table */}
                <div>
                  <p className="text-xs text-zinc-500 mb-3">Price history</p>
                  <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-zinc-800">
                          <th className="text-left px-5 py-3 text-xs text-zinc-500 font-normal">Date</th>
                          <th className="text-left px-5 py-3 text-xs text-zinc-500 font-normal">Store</th>
                          <th className="text-right px-5 py-3 text-xs text-zinc-500 font-normal">Price</th>
                          <th className="text-right px-5 py-3 text-xs text-zinc-500 font-normal">Change</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(() => {
                          const seen = new Set()
                          return analytics.history
                            .filter(h => {
                              const key = h.timestamp?.slice(0, 10) + "_" + h.price
                              if (seen.has(key)) return false
                              seen.add(key)
                              return true
                            })
                            .slice(0, 20)
                            .map((h, i, arr) => {
                              const prev = arr[i + 1]
                              const diff = prev ? ((h.price - prev.price) / prev.price * 100) : null
                              return (
                                <tr key={i} className="border-b border-zinc-800 last:border-0 hover:bg-zinc-800 transition">
                                  <td className="px-5 py-3 text-zinc-400">{h.timestamp?.slice(0, 10)}</td>
                                  <td className="px-5 py-3 text-zinc-400">{h.store}</td>
                                  <td className="px-5 py-3 text-right font-medium text-zinc-200">{fmt(h.price)}</td>
                                  <td className="px-5 py-3 text-right text-xs">
                                    {diff !== null && diff !== 0 ? (
                                      <span className={diff < 0 ? "text-emerald-400" : "text-red-400"}>
                                        {diff > 0 ? "+" : ""}{diff.toFixed(1)}%
                                      </span>
                                    ) : <span className="text-zinc-600">—</span>}
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
          </div>
        )}
      </main>
    </div>
  )
}