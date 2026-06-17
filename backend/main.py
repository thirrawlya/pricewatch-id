import os
import sys
import random
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Setup paths
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

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema and sample data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create price_history table (ini yang penting!)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            store TEXT,
            rating REAL,
            sold INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_product_timestamp ON price_history(product_id, timestamp)")
    
    # Check if we have data
    cursor.execute("SELECT COUNT(*) as count FROM products")
    count = cursor.fetchone()["count"]
    
    if count == 0:
        logger.info("Inserting sample data...")
        
        # Sample products (ambil dari data yang ada di response)
        sample_products = [
            ("Sony WH-1000XM5 Headphones", "https://tokopedia.com/sony-wh-1000xm5"),
            ("LG UltraGear 24G411A-B Monitor", "https://tokopedia.com/lg-ultragear-24g411a"),
            ("MADLIONS MAD60 V2 Keyboard", "https://tokopedia.com/madlions-mad60-v2"),
            ("EndGame Gear XM2We Mouse", "https://tokopedia.com/endgame-xm2we"),
            ("Logitech G PRO X SUPERLIGHT 2", "https://tokopedia.com/logitech-g-pro-x-superlight-2"),
            ("Razer DeathAdder Essential", "https://tokopedia.com/razer-deathadder-essential"),
            ("Keychron V1 Mechanical Keyboard", "https://tokopedia.com/keychron-v1"),
            ("Wooting 60HE Keyboard", "https://tokopedia.com/wooting-60he"),
            ("Fantech Helios II XD3 V2", "https://tokopedia.com/fantech-helios-xd3"),
            ("ASUS TUF Gaming VG249Q3A", "https://tokopedia.com/asus-tuf-vg249q3a"),
        ]
        
        for name, url in sample_products:
            cursor.execute("INSERT INTO products (name, url) VALUES (?, ?)", (name, url))
        
        # Get product IDs
        cursor.execute("SELECT id FROM products")
        product_ids = [row["id"] for row in cursor.fetchall()]
        
        # Add sample price data
        stores = ["Tokopedia", "Shopee", "Lazada", "Blibli"]
        
        for pid in product_ids:
            base_price = random.randint(1000000, 5000000)
            for i in range(90):
                variation = random.randint(-500000, 500000)
                price = max(100000, base_price + variation)
                timestamp = datetime.now() - timedelta(days=89-i)
                store = random.choice(stores)
                rating = round(random.uniform(4.0, 5.0), 1)
                sold = random.randint(10, 1000)
                
                cursor.execute(
                    """INSERT INTO price_history 
                       (product_id, price, store, rating, sold, timestamp) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (pid, price, store, rating, sold, timestamp)
                )
        
        conn.commit()
        logger.info(f"Inserted {len(sample_products)} products with price history")
    
    conn.close()

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    init_db()
    logger.info(f"Database ready at {DB_PATH}")
    yield
    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="PriceWatchID API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ROUTES =====

@app.get("/api/health")
def health():
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "database": "disconnected"}

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

@app.get("/api/products/{product_id}/analytics")
def get_analytics(product_id: int, days: int = 30):
    """Analytics endpoint - FIXED: ada prefix /api dan di dalam app"""
    try:
        conn = get_db()

        product = conn.execute(
            "SELECT id, name, url FROM products WHERE id = ?", (product_id,)
        ).fetchone()

        if not product:
            conn.close()
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
            return {
                "product": dict(product),
                "period_days": days,
                "current": 0,
                "average": 0,
                "lowest": 0,
                "highest": 0,
                "change_pct": 0,
                "recommendation": "wait",
                "reason": "Belum ada data harga untuk periode ini",
                "history": []
            }

        price_list = [r["price"] for r in rows]

        current    = price_list[0]
        average    = sum(price_list) / len(price_list)
        lowest     = min(price_list)
        highest    = max(price_list)
        change_pct = ((current - average) / average) * 100

        if change_pct <= -5:
            recommendation = "buy"
            reason = f"Harga turun {abs(round(change_pct, 1))}% dari rata-rata {days} hari"
        elif change_pct >= 5:
            recommendation = "wait"
            reason = f"Harga naik {round(change_pct, 1)}% dari rata-rata {days} hari"
        else:
            recommendation = "consider"
            reason = f"Harga stabil dalam {days} hari terakhir"

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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

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

@app.get("/")
def root():
    return {
        "message": "PriceWatchID API",
        "docs": "/docs",
        "endpoints": [
            "/api/health",
            "/api/products",
            "/api/products/{id}",
            "/api/products/{id}/prices",
            "/api/products/{id}/analytics",
            "/api/search",
            "/api/stats"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )