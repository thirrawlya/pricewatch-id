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
    products = conn.execute(
        "SELECT id, name, url FROM products"
    ).fetchall()
    conn.close()
    return [dict(p) for p in products]


@app.get("/products/{product_id}/prices")
def get_prices(product_id: int):
    conn = get_db()
    product = conn.execute(
        "SELECT id, name FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prices = conn.execute(
        """
        SELECT price, rating, sold, store, timestamp
        FROM price_history
        WHERE product_id = ?
        ORDER BY timestamp DESC
        """,
        (product_id,),
    ).fetchall()

    conn.close()
    return {"product": dict(product), "prices": [dict(p) for p in prices]}


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