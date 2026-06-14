import { useState, useEffect } from "react"

export default function App() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("http://localhost:8000/products")
      .then(res => res.json())
      .then(data => {
        setProducts(data)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">PriceWatchID</h1>
        <p className="text-gray-400 mb-8">Buying intelligence for Indonesian shoppers</p>

        {loading ? (
          <p className="text-gray-500">Loading products...</p>
        ) : (
          <div className="grid gap-3">
            {products.map(p => (
              <div key={p.id} className="bg-gray-900 rounded-xl p-4 flex justify-between items-center hover:bg-gray-800 cursor-pointer transition">
                <div>
                  <p className="font-medium text-sm line-clamp-1">{p.name}</p>
                  <p className="text-xs text-gray-500 mt-1">ID #{p.id}</p>
                </div>
                <span className="text-xs text-gray-600">→</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}