import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import logging

# Setup paths - absolute path handling
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "pricewatch.db"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="PriceWatchID API",
    version="0.1.0",
    description="E-commerce price intelligence platform for Indonesian skincare products"
)

# CORS configuration - more specific for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Database connection helper
def get_db():
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Health check endpoint
@app.get("/api/health")
def health():
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "database": "disconnected"}, 503

# Get all products
@app.get("/api/products")
def get_products(limit: int = 50, offset: int = 0):
    try:
        conn = get_db()
        products = conn.execute(
            "SELECT id, name, url FROM products LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) as count FROM products").fetchone()
        conn.close()
        
        return {
            "data": [dict(p) for p in products],
            "total": total["count"],
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")

# Get product details with price history
@app.get("/api/products/{product_id}")
def get_product_detail(product_id: int):
    try:
        conn = get_db()
        product = conn.execute(
            "SELECT id, name, url, created_at FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        prices = conn.execute(
            """
            SELECT price, rating, sold, store, timestamp
            FROM price_history
            WHERE product_id = ?
            ORDER BY timestamp DESC
            LIMIT 30
            """,
            (product_id,),
        ).fetchall()
        
        conn.close()
        
        return {
            "product": dict(product),
            "price_history": [dict(p) for p in prices]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product detail error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch product details")

# Get price history for a product
@app.get("/api/products/{product_id}/prices")
def get_price_history(product_id: int, limit: int = 50):
    try:
        conn = get_db()
        product = conn.execute(
            "SELECT id, name FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        prices = conn.execute(
            """
            SELECT price, rating, sold, store, timestamp
            FROM price_history
            WHERE product_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (product_id, limit),
        ).fetchall()

        conn.close()
        
        return {
            "product": dict(product),
            "prices": [dict(p) for p in prices]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get price history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch price history")

# Search products
@app.get("/api/search")
def search_products(q: str, limit: int = 20):
    try:
        if not q or len(q) < 2:
            raise HTTPException(status_code=400, detail="Search query too short (min 2 chars)")
        
        conn = get_db()
        results = conn.execute(
            """
            SELECT id, name, url FROM products 
            WHERE name LIKE ? 
            ORDER BY name 
            LIMIT ?
            """,
            (f"%{q}%", limit)
        ).fetchall()
        conn.close()
        
        return {"query": q, "results": [dict(r) for r in results]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

# Get statistics
@app.get("/api/stats")
def get_stats():
    try:
        conn = get_db()
        stats = {
            "total_products": conn.execute("SELECT COUNT(*) as count FROM products").fetchone()["count"],
            "total_records": conn.execute("SELECT COUNT(*) as count FROM price_history").fetchone()["count"],
            "recent_records": conn.execute(
                "SELECT COUNT(*) as count FROM price_history WHERE timestamp > datetime('now', '-24 hours')"
            ).fetchone()["count"],
        }
        conn.close()
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


@app.get("/products/{product_id}/analytics")
def get_analytics(product_id: int, days: int = 30):
    conn = get_db()

    product = conn.execute(
        "SELECT id, name, url FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    rows = conn.execute(
        """
        SELECT price, store, timestamp
        FROM price_history
        WHERE product_id = ?
          AND price IS NOT NULL
          AND timestamp >= datetime('now', ? || ' days')
        ORDER BY timestamp DESC
        """,
        (product_id, f"-{days}"),
    ).fetchall()

    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No price data found")

    price_list = [r["price"] for r in rows]

    current    = price_list[0]
    average    = sum(price_list) / len(price_list)
    lowest     = min(price_list)
    highest    = max(price_list)
    change_pct = ((current - average) / average) * 100

    if change_pct <= -5:
        recommendation = "good_buy"
        reason = f"Price is {abs(round(change_pct, 1))}% below {days}-day average"
    elif change_pct >= 5:
        recommendation = "wait"
        reason = f"Price is {round(change_pct, 1)}% above {days}-day average"
    else:
        recommendation = "neutral"
        reason = f"Price is close to {days}-day average"

    history = [
        {"price": r["price"], "store": r["store"], "timestamp": r["timestamp"]}
        for r in rows
    ]

    return {
        "product": dict(product),
        "period_days": days,
        "current": current,
        "average": round(average),
        "lowest": lowest,
        "highest": highest,
        "change_pct": round(change_pct, 1),
        "recommendation": recommendation,
        "reason": reason,
        "history": history,
    }