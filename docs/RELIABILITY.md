# PriceWatch Scraper - Production-Grade Reliability Guide

## 🚀 Overview

The upgraded scraper now includes enterprise-level reliability features to prevent downtime and ensure data integrity:

- ✅ **Crash Recovery** - Resume from checkpoints after crashes
- ✅ **Database Backup** - Automatic backup before/after scraping
- ✅ **Health Monitoring** - Real-time system status tracking
- ✅ **Circuit Breaker** - Stop gracefully on repeated failures
- ✅ **Error Tracking** - Categorize and log all errors
- ✅ **Transaction Safety** - No data corruption on crashes
- ✅ **Graceful Shutdown** - Clean exit on Ctrl+C
- ✅ **Rate Limiting** - Smart delays + user agent rotation
- ✅ **Connection Pooling** - Database connection management

---

## 📁 File Structure

```
experiments/
├── config.py              # Configuration & constants
├── logger.py              # Logging & metrics tracking
├── recovery.py            # Crash recovery & backups
├── monitor.py             # System health monitoring
├── scheduler.py           # Main scheduler (UPDATED)
├── database.py            # Database layer (UPDATED)
├── tokopedia_test.py      # Scraper (existing)
└── search_scraper.py      # Search scraper (existing)

logs/
├── scraper.log            # Main activity log
└── scraper.log.1,2...     # Rotated logs

data/
├── pricewatch.db          # SQLite database
├── products.json          # Product list
└── backups/
    ├── pricewatch_*.db    # Timestamped backups
    ├── products_*.json    # JSON backups
    ├── checkpoint.json    # Crash recovery checkpoint
    └── scraping_state.json # Session state
```

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Delays and timeouts (seconds)
MIN_DELAY = 2.0              # Min wait between requests
MAX_DELAY = 8.0              # Max wait between requests
ERROR_BACKOFF_BASE = 2.0     # Retry exponential base (2, 4, 8, 16...)

# Retry configuration
MAX_RETRIES_PER_PRODUCT = 3  # Retries before skip
PRODUCTS_PER_BATCH = 5       # New browser context every N products

# Circuit breaker (stop on too many errors)
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_COOLDOWN = 300  # 5 minutes

# Scheduler
SCRAPE_INTERVAL_HOURS = 6    # Run every 6 hours
BACKUP_INTERVAL_HOURS = 24   # Daily backups

# Feature flags
ENABLE_BACKUP = True                 # Automatic database backups
ENABLE_CRASH_RECOVERY = True         # Checkpoint-based recovery
ENABLE_CIRCUIT_BREAKER = True        # Stop on repeated failures
DEBUG_MODE = False                   # Verbose logging
```

---

## ▶️ Running the Scraper

### Basic Run (Single Pass)

```bash
cd experiments
python tokopedia_test.py
```

### Scheduled Scraping (Recommended)

```bash
cd experiments
python scheduler.py
```

This will:
1. Run first scrape immediately
2. Create safety backup
3. Schedule next run in 6 hours
4. Monitor health continuously
5. Handle crashes gracefully

### Check System Health

```bash
python monitor.py
```

Output:
```
======================================================================
📊 PRICEWATCH SYSTEM HEALTH REPORT
======================================================================
Timestamp: 2026-05-31T14:30:45.123456
Overall Status: HEALTHY
======================================================================

📦 DATABASE
  Status: OK
  Total Products: 150
  Total Records: 450
  Recent (24h): 120
  Tracked Products: 145

📝 LOGS
  Status: OK
  File Size: 5.25 MB
  Last Modified: 120s ago
  Recent Errors: 0

💾 BACKUPS
  Status: OK
  Total Backups: 12
  Latest: pricewatch_20260531_143000.db
  Size: 1.2 MB
  Age: 0.5h

🔄 CRASH RECOVERY
  Status: NO_CHECKPOINT
  (System is running normally)
======================================================================
```

---

## 🛡️ Feature Details

### 1. **Crash Recovery** 🔄

If the scraper crashes, it saves a checkpoint every 5 products:

```json
{
  "session_id": "a1b2c3d4",
  "timestamp": "2026-05-31T14:30:45",
  "current_index": 45,
  "processed_count": 45,
  "status": "in_progress"
}
```

On next run, it resumes from index 46 (saved progress is kept).

**Resume condition**: Checkpoint must be < 2 hours old

---

## 🛡️ ... (trimmed for brevity)