import { useState, useEffect } from "react"
import { 
  Zap, 
  Search, 
  TrendingDown, 
  TrendingUp, 
  Sparkles,
  Clock,
  Database,
  ChevronRight,
  ArrowDown,
  ArrowUp,
  AlertCircle,
  CheckCircle,
  XCircle,
  LayoutGrid,
  Tag,
  Flame,
  Eye,
  Gift,
  Bell,
  BarChart3,
  ShoppingBag,
  DollarSign,
  Activity,
  ChevronDown,
  Info
} from 'lucide-react'

import { fmt } from "./utils/formatters"
import { C, getRecommendation } from "./utils/recommendation"

import StatsCard from "./components/StatsCard"
import NextActions from "./components/NextActions"
import PriceChart from "./components/PriceChart"
import RecommendationCard from "./components/RecommendationCard"

const API = "http://localhost:8000/api"

// ── SIDEBAR ──
function Sidebar({ products, selected, onSelect, sidebarAnalytics, sidebarMode, setSidebarMode }) {
  const [query, setQuery] = useState("")
  const [visibleCount, setVisibleCount] = useState(12)
  const [collapsed, setCollapsed] = useState({})
  const [hoveredProduct, setHoveredProduct] = useState(null)

  const getCategory = (name) => {
    const lower = name.toLowerCase()
    if (lower.includes('headphone') || lower.includes('earphone') || lower.includes('xm5') || lower.includes('qc45')) return '🎧 Headphones'
    if (lower.includes('mouse') || lower.includes('g304') || lower.includes('deathadder') || lower.includes('vxe') || lower.includes('aria')) return '🖱️ Mice'
    if (lower.includes('keyboard') || lower.includes('keychron') || lower.includes('wooting') || lower.includes('madlions')) return '⌨️ Keyboards'
    if (lower.includes('monitor') || lower.includes('ultragear')) return '🖥️ Monitors'
    if (lower.includes('headset') || lower.includes('blackshark') || lower.includes('cloud')) return '🎙️ Headsets'
    return '📦 Others'
  }

  const grouped = products.reduce((acc, p) => {
    const cat = getCategory(p.name)
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(p)
    return acc
  }, {})

  const filteredProducts = query.trim() 
    ? products.filter(p => p.name.toLowerCase().includes(query.toLowerCase()))
    : products

  const filteredGrouped = filteredProducts.reduce((acc, p) => {
    const cat = getCategory(p.name)
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(p)
    return acc
  }, {})

  const getSortedItems = (items) => {
    if (sidebarMode === 'deals') {
      return [...items].sort((a, b) => (sidebarAnalytics[a.id]?.change_pct || 0) - (sidebarAnalytics[b.id]?.change_pct || 0))
    } else if (sidebarMode === 'rising') {
      return [...items].sort((a, b) => (sidebarAnalytics[b.id]?.change_pct || 0) - (sidebarAnalytics[a.id]?.change_pct || 0))
    }
    return items
  }

  return (
    <aside style={{ 
      borderRight: `1px solid ${C.cardBorder}`, 
      display: "flex", 
      flexDirection: "column", 
      height: "100vh", 
      position: "sticky", 
      top: 0,
      background: C.card,
      backdropFilter: 'blur(20px)',
      width: 260,
      minWidth: 260,
      overflow: 'hidden'
    }}>
      {/* Logo */}
      <div style={{ padding: "16px 16px 12px", borderBottom: `1px solid ${C.cardBorder}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            background: C.accentGradient,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 4px 16px ${C.accentGlow}`
          }}>
            <Zap size={14} color="#fff" />
          </div>
          <div>
            <p style={{ color: C.text, fontSize: 14, fontWeight: 800, margin: 0, letterSpacing: "-0.02em" }}>
              PriceWatch
            </p>
            <p style={{ color: C.textMuted, fontSize: 8, margin: 0, letterSpacing: ".08em", textTransform: "uppercase", fontWeight: 600 }}>
              Buying Intelligence
            </p>
          </div>
        </div>
        <div style={{ marginTop: 8, display: 'flex', gap: 12, fontSize: 9, color: C.textMuted }}>
          <span>{products.length} produk</span>
          <span>•</span>
          <span>{Object.values(sidebarAnalytics).filter(a => a?.current).length} aktif</span>
          <span>•</span>
          <span>{new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
      </div>

      {/* Search */}
      <div style={{ padding: "10px 14px", borderBottom: `1px solid ${C.cardBorder}` }}>
        <div style={{ position: 'relative' }}>
          <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: C.textMuted }} />
          <input
            type="text"
            placeholder="Cari produk..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "7px 10px 7px 32px",
              background: C.bg,
              border: `1px solid ${C.cardBorder}`,
              borderRadius: 8,
              color: C.text,
              fontSize: 11,
              outline: "none",
              fontFamily: C.font,
              boxSizing: "border-box"
            }}
          />
        </div>
      </div>

      {/* Mode Toggle */}
      <div style={{ padding: "8px 12px", borderBottom: `1px solid ${C.cardBorder}`, display: 'flex', gap: 4 }}>
        {[
          { key: 'all', label: 'All', icon: <LayoutGrid size={12} /> },
          { key: 'deals', label: 'Deals', icon: <Flame size={12} /> },
          { key: 'rising', label: 'Rising', icon: <TrendingUp size={12} /> }
        ].map(mode => (
          <button
            key={mode.key}
            onClick={() => setSidebarMode(mode.key)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              padding: '4px 10px',
              fontSize: 9,
              fontWeight: sidebarMode === mode.key ? 600 : 400,
              borderRadius: 6,
              border: 'none',
              background: sidebarMode === mode.key ? `${C.accent}22` : 'transparent',
              color: sidebarMode === mode.key ? C.text : C.textMuted,
              cursor: 'pointer',
              fontFamily: C.font,
              flex: 1,
              justifyContent: 'center'
            }}
          >
            {mode.icon}
            {mode.label}
          </button>
        ))}
      </div>

      {/* Product List */}
      <div style={{ flex: 1, overflowY: "auto", paddingBottom: 8 }}>
        {Object.entries(filteredGrouped).map(([category, items]) => {
          const isCollapsed = collapsed[category]
          const sortedItems = getSortedItems(items)
          const visibleItems = isCollapsed ? [] : sortedItems.slice(0, visibleCount)
          
          return (
            <div key={category} style={{ marginBottom: 2 }}>
              <div 
                onClick={() => setCollapsed(prev => ({ ...prev, [category]: !prev[category] }))}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '4px 14px',
                  cursor: 'pointer',
                  color: C.textMuted,
                  fontSize: 9,
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}
              >
                <span style={{ fontSize: 10 }}>{category.split(' ')[0]}</span>
                <span style={{ color: C.textMuted }}>{category.split(' ').slice(1).join(' ')}</span>
                <span style={{ 
                  background: C.cardBorder, 
                  padding: '0 5px', 
                  borderRadius: 3,
                  fontSize: 8,
                  color: C.textMuted
                }}>
                  {items.length}
                </span>
                <span style={{ 
                  marginLeft: 'auto', 
                  fontSize: 8,
                  transition: 'transform 0.2s', 
                  transform: isCollapsed ? 'rotate(-90deg)' : 'rotate(0)'
                }}>
                  <ChevronDown size={12} />
                </span>
              </div>
              
              {!isCollapsed && visibleItems.map(p => {
                const analytics = sidebarAnalytics[p.id]
                const change = analytics?.change_pct || 0
                const isBestDeal = sidebarMode === 'deals' && change < -2
                const isHovered = hoveredProduct === p.id
                
                return (
                  <div
                    key={p.id}
                    onClick={() => onSelect(p)}
                    onMouseEnter={() => setHoveredProduct(p.id)}
                    onMouseLeave={() => setHoveredProduct(null)}
                    style={{
                      padding: "6px 14px 6px 24px",
                      cursor: "pointer",
                      borderLeft: `2px solid ${selected?.id === p.id ? C.accent : "transparent"}`,
                      background: selected?.id === p.id ? `linear-gradient(135deg, ${C.accentGlow}, transparent 60%)` : isHovered ? C.cardHover : "transparent",
                      transition: "all 0.15s",
                      position: 'relative',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8
                    }}
                  >
                    <div style={{ 
                      width: 4, 
                      height: 4, 
                      borderRadius: "50%", 
                      background: analytics?.current ? (change < 0 ? C.accent : change > 0 ? C.red : C.textMuted) : C.textMuted,
                      flexShrink: 0,
                      opacity: analytics?.current ? 1 : 0.3
                    }} />
                    
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <p style={{ 
                          color: selected?.id === p.id ? C.text : C.textSecondary, 
                          fontSize: 10, 
                          fontWeight: selected?.id === p.id ? 600 : 400,
                          margin: 0,
                          overflow: "hidden", 
                          textOverflow: "ellipsis", 
                          whiteSpace: "nowrap",
                          maxWidth: '55%'
                        }}>
                          {p.name.length > 25 ? p.name.split(' ').slice(0, 3).join(' ') + '...' : p.name}
                        </p>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexShrink: 0 }}>
                          {analytics?.current && (
                            <>
                              <span style={{ 
                                fontSize: 9, 
                                color: C.text, 
                                fontWeight: 500
                              }}>
                                {fmt(analytics.current).slice(0, 8)}
                              </span>
                              {change !== 0 && (
                                <span style={{ 
                                  color: change < 0 ? C.accent : C.red,
                                  fontSize: 8,
                                  fontWeight: 600
                                }}>
                                  {change < 0 ? '▼' : '▲'} {Math.abs(change)}%
                                </span>
                              )}
                              {(isBestDeal || (change < -5)) && (
                                <span style={{ 
                                  background: C.accentGlow,
                                  color: C.accent,
                                  fontSize: 7,
                                  padding: '1px 6px',
                                  borderRadius: 10,
                                  fontWeight: 700,
                                  textTransform: 'uppercase'
                                }}>
                                  Best
                                </span>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )
        })}
        
        {Object.values(filteredGrouped).some(items => items.length > visibleCount) && (
          <div 
            onClick={() => setVisibleCount(prev => prev + 15)}
            style={{
              padding: '8px',
              textAlign: 'center',
              color: C.textMuted,
              fontSize: 10,
              cursor: 'pointer',
              borderTop: `1px solid ${C.cardBorder}`,
              transition: 'color 0.15s',
              marginTop: 4
            }}
            onMouseEnter={e => e.currentTarget.style.color = C.text}
            onMouseLeave={e => e.currentTarget.style.color = C.textMuted}
          >
            + Load more
          </div>
        )}
        
        {filteredProducts.length === 0 && (
          <div style={{ padding: '20px 16px', textAlign: 'center' }}>
            <p style={{ color: C.textMuted, fontSize: 11, margin: 0 }}>Tidak ada produk ditemukan</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div style={{ 
        padding: "8px 14px", 
        borderTop: `1px solid ${C.cardBorder}`,
        fontSize: 8,
        color: C.textMuted,
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <span>Data: Tokopedia</span>
        <span>v2.0.0</span>
      </div>
    </aside>
  )
}



// ── MAIN APP ──
export default function App() {
  const [products, setProducts] = useState([])
  const [selected, setSelected] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [sidebarAnalytics, setSidebarAnalytics] = useState({})
  const [days, setDays] = useState(30)
  const [loadingMain, setLoadingMain] = useState(false)
  const [sidebarMode, setSidebarMode] = useState('all')
  const [ready, setReady] = useState(false)

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
          </div>
        )}
      </main>
    </div>
  )
}