from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI(title="PriceWatchID API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "data/pricewatch.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/products")
def get_products():
    conn = get_db()
    products = conn.execute("SELECT id, name, url FROM products").fetchall()
    conn.close()
    return [dict(p) for p in products]

@app.get("/products/{product_id}/prices")
def get_prices(product_id: int):
    conn = get_db()
    product = conn.execute("SELECT id, name FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    prices = conn.execute(
        "SELECT price, rating, sold, store, timestamp FROM price_history WHERE product_id = ? ORDER BY timestamp DESC",
        (product_id,)
    ).fetchall()
    conn.close()
    return {"product": dict(product), "prices": [dict(p) for p in prices]}