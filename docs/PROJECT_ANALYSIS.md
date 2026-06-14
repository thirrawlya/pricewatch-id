# 📊 PRICEWATCH-ID: COMPREHENSIVE PROJECT ANALYSIS
## Isi, Tujuan, Manfaat, dan Kekurangan

---

## 🎯 **1. TUJUAN / PURPOSE**

### **Core Vision**
Membantu konsumen Indonesia membuat keputusan pembelian yang lebih percaya diri melalui **price intelligence** - bukan hanya mencari harga termurah, tapi membuat **keputusan yang lebih informed** (informed buying decisions), dengan fokus pada produk skincare.

### **Target Market**
- **Primary**: Konsumen e-commerce Indonesia (Tokopedia user) yang mencari produk perawatan kulit
- **Secondary**: Sellers yang ingin analisis kompetitor di kategori skincare
- **Future**: Multi-marketplace comparison

### **Problem Statement**
```
Sebelum PriceWatch:
  ❌ Konsumen bingung harga berfluktuasi atau stabil
  ❌ Tidak tahu kapan waktu terbaik beli
  ❌ Tidak bisa compare harga across stores
  ❌ Worried tentang kualitas store
  
Sesudah PriceWatch:
  ✅ Lihat price history 3-6 bulan ke belakang
  ✅ Predict best time to buy berdasarkan data
  ✅ Compare semua toko yang jual produk yang sama
  ✅ Trust signals dari rating/sold count trends
```

### **Core Premise**
> "Consumers don't need the cheapest option. They need the most confident buying decision."

---

## 🏗️ **2. ARCHITECTURE & STRUKTUR**

### **Phase-Based Development**

```
Phase 0 (NOW)        ← Data Collection & Validation
├─ Web Scraping      (Tokopedia products - skincare)
├─ Data Extraction   (price, rating, sold, store)
├─ Data Storage      (SQLite database)
└─ Validation        (reliability testing)
     ↓
Phase 1 (Q3 2026)    ← MVP Application
├─ Product Detail UI (price chart, comparisons)
├─ User Accounts     (minimal, for watchlist)
├─ Price Alerts      (email notifications)
└─ Migrate to PostgreSQL
     ↓
Phase 2 (Q4 2026)    ← Advanced Features
├─ ML Price Prediction
├─ Sentiment Analysis (reviews)
├─ Multi-marketplace (Shopee, Lazada, etc)
├─ Browser Extension
└─ Admin Dashboard   (seller analytics)
```

### **Current Status (Phase 0)**
- ✅ **DONE**: Scraper infrastructure (Playwright-based)
- ✅ **DONE**: Data extraction pipeline
- ✅ **DONE**: SQLite database schema
- ✅ **DONE**: Scheduled collection (APScheduler)
- ✅ **DONE**: Production reliability layer (crashes, backups, recovery)
- 🔄 **IN PROGRESS**: Data validation & quality assurance
- ⏳ **PENDING**: Frontend MVP
- ⏳ **PENDING**: Backend API (FastAPI)

**Key principle**: "Intentionally block app development until data reliability is proven" - fokus quality data dulu sebelum build UI.

---

## 📁 **3. COMPONENT BREAKDOWN**

### **A. SCRAPING LAYER** (experiments/)

#### **1. tokopedia_test.py** (80 lines)
**Tujuan**: Extract data dari Tokopedia product pages (skincare product pages)

**Apa yang dia lakukan**:
```python
scrape_product(page, url)
├─ Load product page dengan Playwright
├─ Extract: name, price, rating, sold count, store
├─ Handle multiple selector fallbacks
├─ Retry jika selector tidak ditemukan
└─ Return structured data dict
```

**Input**: Tokopedia product URL  
**Output**: 
```json
{
  "name": "Skintific Niacinamide Serum",
  "price": "Rp 120.000",
  "rating": "4.6",
  "sold": "1.2K",
  "store": "SkintificOfficial"
}
```

**Kelebihan**:
- ✅ Handles dynamic content (JavaScript-rendered)
- ✅ Multiple fallback selectors (robust)
- ✅ 5-second timeout (fast enough)

**Kekurangan**:
- ❌ Hanya untuk Tokopedia (hardcoded selectors)
- ❌ Perlu update kalau Tokopedia ubah DOM structure
- ❌ Tidak bisa handle infinite scroll products

---

#### **2. search_scraper.py** (100+ lines)
**Tujuan**: Search Tokopedia dan collect product URLs

**Apa yang dia lakukan**:
```python
scrape_search_results(page, keyword, max_products=20)
├─ Navigate ke Tokopedia search
├─ Scroll untuk trigger lazy loading
├─ Extract semua product links dari page
├─ Filter valid URLs (exclude ads, banners)
└─ Return list of product URLs
```

**Input**: Search keyword (e.g., "serum vitamin c")  
**Output**: List of 10-20 product URLs

**Kelebihan**:
- ✅ Automated product discovery
- ✅ Handles lazy loading (scroll 10x)
- ✅ Blacklist filtering (exclude invalid URLs)

**Kekurangan**:
- ❌ Hardcoded keywords (tidak dynamic)
- ❌ Hanya ambil 20 per keyword max
- ❌ Bisa duplikat across keywords

---

### **B. DATA PERSISTENCE LAYER** (experiments/database.py)

**Tujuan**: Save & retrieve data safely

**Database Schema**:
```sql
products
  id (PRIMARY KEY)
  name TEXT
  url TEXT (UNIQUE)
  created_at DATETIME
  updated_at DATETIME

price_history
  id (PRIMARY KEY)
  product_id (FOREIGN KEY)
  price TEXT
  rating TEXT
  sold TEXT
  store TEXT
  timestamp DATETIME (indexed)
```

**Functions**:
```python
init_db()                      # Create tables & indexes
save_product(name, url)        # Insert/get product ID
save_price(...)                # Insert price history record
get_product_history(id, limit) # Retrieve historical data
get_all_products(limit)        # Bulk product retrieval
delete_old_records(days)       # Cleanup old data
```

**Kelebihan**:
- ✅ Transaction-safe (ACID compliance)
- ✅ Foreign key constraints (data integrity)
- ✅ Indexed on frequently-queried fields
- ✅ Error handling & rollback

**Kekurangan**:
- ❌ SQLite (single-file, not production-grade)
- ❌ Perlu migrate ke PostgreSQL untuk multi-user
- ❌ Concurrency limited (file-based locking)

---

### **C. SCHEDULING & ORCHESTRATION** (experiments/scheduler.py)

**Tujuan**: Run scraper pada interval tertentu (setiap 6 jam)

**Apa yang dia lakukan**:
```
06:00 AM ─┬─ Run scraper
          │  ├─ Rotate browser UA & viewport
          │  ├─ Smart delays (2-8s random)
          │  ├─ Exponential backoff on errors
          │  ├─ Checkpoint recovery
          │  ├─ Create backups
          │  └─ Log everything
          │
12:00 PM ─┼─ Run scraper (same flow)
          │
06:00 PM ─┼─ Run scraper (same flow)
          │
12:00 AM ─┴─ Run scraper (same flow)
```

**Features**:
- 🔄 APScheduler (blocking scheduler)
- 🔁 Every 6 hours automatic
- ⏸️ Single instance (prevent concurrent runs)
- 📊 Metrics tracking (success rate, errors)
- 🛑 Graceful shutdown handling

**Kelebihan**:
- ✅ Reliable scheduling (proven library)
- ✅ Anti-rate-limiting (smart delays + UA rotation)
- ✅ Circuit breaker (stop after 5 errors)
- ✅ Crash recovery (checkpoint-based)

**Kekurangan**:
- ❌ Blocking (ties up one process)
- ❌ Perlu systemd/docker untuk prod deployment
- ❌ Sulit scale ke multiple scrapers

---

### **D. MONITORING & RELIABILITY LAYER**

#### **3. config.py** (60 lines)
**Tujuan**: Centralized configuration management

```python
# Delays
MIN_DELAY = 2.0              # ← Adjust untuk rate limiting
MAX_DELAY = 8.0

# Retry
MAX_RETRIES_PER_PRODUCT = 3
CIRCUIT_BREAKER_THRESHOLD = 5

# Scheduling
SCRAPE_INTERVAL_HOURS = 6

# Feature flags
ENABLE_BACKUP = True         # ← Toggle backup system
ENABLE_CRASH_RECOVERY = True
ENABLE_CIRCUIT_BREAKER = True
```

**Kelebihan**:
- ✅ Single source of truth
- ✅ Easy tuning without code changes
- ✅ Feature flags untuk A/B testing

**Kekurangan**:
- ❌ Hardcoded values (not dynamic)
- ❌ No environment-based config

---

#### **4. logger.py** (220 lines)
**Tujuan**: Structured logging & metrics tracking

**Components**:
```python
setup_logging()        # Configure file + console logging
ScrapeMetrics()        # Track success/fail/retry counts
HealthCheck()          # Monitor consecutive errors
ErrorTracker()         # Categorize error types
```

**Output**:
```
2026-05-31 14:30:45 - INFO - [1/100] Scraping: Serum Vitamin C...
2026-05-31 14:30:50 - DEBUG - ✅ Success: Skintific Niacinamide Serum
2026-05-31 14:30:50 - DEBUG - ⏳ Waiting 3.2s before next request...
2026-05-31 14:35:22 - INFO - Success rate: 98.0%
```

**Kelebihan**:
- ✅ Log rotation (5 x 10MB)
- ✅ Structured format
- ✅ Full error categorization

**Kekurangan**:
- ❌ Logs hanya lokal (tidak centralized)
- ❌ Tidak ada real-time alerting

---

#### **5. recovery.py** (200 lines)
**Tujuan**: Crash recovery & database backup

**Components**:
```python
CrashRecovery()        # Checkpoint system (resume from crash)
BackupManager()        # Database backups & restore
GracefulShutdown()     # Clean exit handlers
```

**Cara kerja**:
```
1. Sebelum scrape:
   ├─ Check database integrity
   ├─ Create backup snapshot
   └─ Load checkpoint (jika ada)

2. Saat scraping:
   ├─ Save checkpoint setiap 5 produk
   └─ Log progress

3. Jika crash:
   ├─ On restart, load checkpoint
   ├─ Resume dari product index N+1
   └─ Keep all data collected so far

4. Sesudah scrape:
   ├─ Create final backup
   ├─ Clear checkpoint (success)
   └─ Log final metrics
```

**Backup strategy**:
```
Before scrape:        pricewatch_20260531_143000.db  ← Safety copy
Data collection...
After scrape:         pricewatch_20260531_143500.db  ← Final snapshot
Keep last 10 backups, auto-cleanup oldest
```

**Kelebihan**:
- ✅ No data loss on crashes
- ✅ Automatic recovery
- ✅ Point-in-time restore capability

**Kekurangan**:
- ❌ Backups stored locally (no remote)
- ❌ Checkpoint only works within 2 hours
- ❌ Manual restore process

---

#### **6. monitor.py** (280 lines)
**Tujuan**: Real-time system health monitoring

**Dashboard shows**:
```
📦 DATABASE
  Total Products: 150
  Total Records: 450
  Recent (24h): 120
  
📝 LOGS
  File Size: 5.25 MB
  Last Modified: 120s ago
  Recent Errors: 0
  
💾 BACKUPS
  Total Backups: 12
  Latest Age: 0.5h
  
🔄 CRASH RECOVERY
  Status: NO_CHECKPOINT (healthy)
```

**Kelebihan**:
- ✅ One-command health check
- ✅ Comprehensive overview
- ✅ Easy troubleshooting

**Kekurangan**:
- ❌ CLI-only (no web dashboard)
- ❌ Point-in-time only (not historical trends)

---

### **E. DEPLOYMENT & SETUP**

#### **7. setup.sh** (60 lines)
**Tujuan**: One-command project initialization

```bash
bash setup.sh
├─ Check Python version
├─ Install dependencies (playwright, apscheduler)
├─ Download Chromium
├─ Initialize database
├─ Create directories
└─ Show configuration
```

**Kelebihan**:
- ✅ Automated setup
- ✅ Dependency management
