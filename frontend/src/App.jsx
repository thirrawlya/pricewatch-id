import { useState, useEffect } from "react"
import { 
  TrendingDown, 
  TrendingUp, 
  ChevronRight,
  ArrowDown,
  ArrowUp,
  DollarSign,
  Activity
} from 'lucide-react'
import { fmt } from "./utils/formatters"
import { C } from "./utils/recommendation"
import StatsCard from "./components/StatsCard"
import NextActions from "./components/NextActions"
import PriceChart from "./components/PriceChart"
import RecommendationCard from "./components/RecommendationCard"
import Sidebar from "./components/Sidebar"
import PriceHistoryTable from "./components/PriceHistoryTable"
const API = import.meta.env.VITE_API_URL

// ── MAIN APP ──
export default function App() {
  const [products, setProducts] = useState([])
  const [selected, setSelected] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [sidebarAnalytics, setSidebarAnalytics] = useState({})
  const [days, setDays] = useState(30)
  const [loadingMain, setLoadingMain] = useState(false)
  const [sidebarMode, setSidebarMode] = useState('all')
  useEffect(() => {
    fetch(`${API}/products`)
      .then(r => r.json())
      .then(response => {
        const productsData = response.data || []
        setProducts(productsData)
        if (productsData.length > 0) {
          selectProduct(productsData[0], 30)
        }
        productsData.forEach(p => {
          fetch(`${API}/products/${p.id}/analytics?days=30`)
            .then(r => r.json())
            .then(a => setSidebarAnalytics(prev => ({ ...prev, [p.id]: a })))
            .catch(() => {})
        })     
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
  const chartData = (() => {
    if (!analytics?.history) return []
    const seen = new Set()
    return analytics.history.slice().reverse().filter(h => {
      const d = h.timestamp?.slice(0, 10)
      if (seen.has(d)) return false
      seen.add(d)
      return true
    }).map(h => ({ date: h.timestamp?.slice(5, 10), price: h.price }))
  })()
  return (
    <div style={{ 
      display: "grid", 
      gridTemplateColumns: "260px 1fr", 
      minHeight: "100vh", 
      background: C.bgGradient, 
      fontFamily: C.font, 
      color: C.text 
    }}>
      <Sidebar 
        products={products}
        selected={selected}
        onSelect={selectProduct}
        sidebarAnalytics={sidebarAnalytics}
        sidebarMode={sidebarMode}
        setSidebarMode={setSidebarMode}
      />
      <main style={{ 
        padding: "28px 36px", 
        overflowY: "auto", 
        maxHeight: "100vh",
        background: C.bgGradient
      }}>
        {selected && (
          <div style={{ marginBottom: 24 }}>
            <p style={{ 
              color: C.textMuted, 
              fontSize: 10, 
              margin: "0 0 2px",
              fontWeight: 600,
              letterSpacing: '0.05em',
              textTransform: 'uppercase'
            }}>
              Product
            </p>
            <h1 style={{ 
              fontSize: 22, 
              fontWeight: 700, 
              margin: "0 0 4px",
              letterSpacing: '-0.02em'
            }}>
              {selected.name}
            </h1>
            <a href={selected.url} target="_blank" rel="noreferrer" style={{ 
              color: C.accent, 
              fontSize: 12, 
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4,
              fontWeight: 500
            }}>
              Lihat di Tokopedia <ChevronRight size={14} />
            </a>
          </div>
        )}
        {loadingMain && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: 400,
            color: C.textMuted
          }}>
            <span>Memuat data...</span>
          </div>
        )}
        {!loadingMain && analytics && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <RecommendationCard analytics={analytics} days={days} />
            <PriceChart 
              data={chartData}
              average={analytics.average}
              days={days}
              onChangeDays={changeDays}
              analytics={analytics}
            />
            
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
              <StatsCard 
                label="Harga Sekarang" 
                value={fmt(analytics.current)} 
                color={C.text}
                icon={<DollarSign size={16} />}
                barValue={analytics.current}
                barMax={analytics.highest}
              />
              <StatsCard 
                label={`Rata-rata ${days}d`} 
                value={fmt(analytics.average)} 
                color={C.textSecondary}
                icon={<Activity size={16} />}
                barValue={analytics.average}
                barMax={analytics.highest}
              />
              <StatsCard 
                label="Terendah" 
                value={fmt(analytics.lowest)} 
                color={C.accent}
                icon={<TrendingDown size={16} />}
                subtext={`${Math.round((1 - analytics.lowest / analytics.average) * 100)}% di bawah rata-rata`}
                barValue={analytics.lowest}
                barMax={analytics.highest}
              />
              <StatsCard 
                label="Tertinggi" 
                value={fmt(analytics.highest)} 
                color={C.red}
                icon={<TrendingUp size={16} />}
                subtext={`${Math.round((analytics.highest / analytics.average - 1) * 100)}% di atas rata-rata`}
                barValue={analytics.highest}
                barMax={analytics.highest}
              />
            </div>
            <NextActions />
            <PriceHistoryTable analytics={analytics} />
          </div>
        )}
      </main>
    </div>
  )
}