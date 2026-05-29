import sqlite3
import os

DB_PATH = "data/pricewatch.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT UNIQUE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price TEXT,
            rating TEXT,
            sold TEXT,
            store TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_product(name, url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO products (name, url) VALUES (?, ?)", (name, url))
    conn.commit()
    product_id = c.execute("SELECT id FROM products WHERE url = ?", (url,)).fetchone()[0]
    conn.close()
    return product_id

def save_price(product_id, price, rating, sold, store):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO price_history (product_id, price, rating, sold, store)
        VALUES (?, ?, ?, ?, ?)
    """, (product_id, price, rating, sold, store))
    conn.commit()
    conn.close()
    print(f"✅ Saved: {price} at {store}")