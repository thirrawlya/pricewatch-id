import sqlite3
import os
from config import DB_PATH

def get_connection():
    """Get database connection with safety settings."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    # Set timeout
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn

def init_db():
    """Initialize database with proper schema and indexes."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    c = conn.cursor()

    # Create tables with constraints
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price TEXT,
            rating TEXT,
            sold TEXT,
            store TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)

    # Create indexes for better query performance
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_url ON products(url)
    """)
    
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id)
    """)
    
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)
    """)

    conn.commit()
    conn.close()

def save_product(name, url):
    """Save product with transaction safety and error handling."""
    if not name or not url:
        raise ValueError("Product name and URL cannot be empty")
    
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO products (name, url) VALUES (?, ?)",
            (name, url)
        )
        conn.commit()
        
        result = c.execute("SELECT id FROM products WHERE url = ?", (url,)).fetchone()
        if result:
            return result[0]
        else:
            raise Exception(f"Failed to retrieve product ID for {url}")
    except sqlite3.IntegrityError as e:
        raise Exception(f"Product integrity error: {e}")
    except Exception as e:
        raise Exception(f"Failed to save product: {e}")
    finally:
        conn.close()

def save_price(product_id, price, rating, sold, store):
    """Save price history with transaction safety."""
    if not product_id:
        raise ValueError("Product ID cannot be empty")
    
    conn = get_connection()
    try:
        c = conn.cursor()
        
        # Verify product exists
        c.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if not c.fetchone():
            raise ValueError(f"Product ID {product_id} does not exist")
        
        # Insert price history
        c.execute("""
            INSERT INTO price_history (product_id, price, rating, sold, store)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, price, rating, sold, store))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to save price: {e}")
    finally:
        conn.close()

def get_product_history(product_id, limit=100):
    """Get price history for a product."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            SELECT price, rating, sold, store, timestamp
            FROM price_history
            WHERE product_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (product_id, limit))
        return c.fetchall()
    finally:
        conn.close()

def get_all_products(limit=None):
    """Get all products from database."""
    conn = get_connection()
    try:
        c = conn.cursor()
        if limit:
            c.execute("SELECT id, name, url FROM products LIMIT ?", (limit,))
        else:
            c.execute("SELECT id, name, url FROM products")
        return c.fetchall()
    finally:
        conn.close()

def delete_old_records(days=90):
    """Delete price history records older than N days."""
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            DELETE FROM price_history
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """, (days,))
        deleted = c.rowcount
        conn.commit()
        return deleted
    finally:
        conn.close()