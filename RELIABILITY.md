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

### 2. **Database Backups** 💾

- **Before scraping**: Safety snapshot created
- **During scraping**: No backups (performance)
- **After scraping**: Final backup created
- **Manual**: Call `BackupManager().create_backup()`
- **Retention**: Keeps last 10 backups
- **Restore**: Automatic restore from latest backup if corrupted

### 3. **Health Monitoring** 🏥

Tracks:
- Consecutive errors (alert if > 5)
- Success rate per scrape session
- Error categories (HTTP2, Timeout, Network, DB, etc)
- Database integrity
- Log file size & age

**Automatic actions**:
- Log warnings for 3+ consecutive errors
- Activate circuit breaker at 5+ errors
- Suggest recovery on low success rates

### 4. **Circuit Breaker** 🔌

Stops scraping if:
- 5 consecutive errors occur
- Success rate drops below threshold
- Database becomes inaccessible

This prevents hammering a broken target and accumulating bad data.

### 5. **Error Categorization** 📊

Errors automatically classified as:
- `ERR_HTTP2_PROTOCOL_ERROR` → Rate limiting detected
- `TIMEOUT` → Slow/unresponsive server
- `SELECTOR_NOT_FOUND` → Page structure changed
- `NETWORK_ERROR` → Connection issue
- `DB_ERROR` → Database problem
- `PARSE_ERROR` → Data extraction failed

### 6. **Transaction Safety** 🔒

Database operations use:
- `BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK`
- Foreign key constraints
- Timeout handling
- Unique constraints on URLs

**Result**: No orphaned records or data corruption on crashes

### 7. **Graceful Shutdown** 🛑

When you press Ctrl+C:
1. Finishes current product scraping
2. Saves checkpoint for recovery
3. Creates final backup
4. Closes database connections
5. Cleans up browser resources
6. Exits cleanly

### 8. **Rate Limiting** ⏱️

Implements multiple strategies:

```python
# Random delays (not fixed)
smart_delay(product_index, total_products, error_count)
# Returns: 2-5s base + jitter + error backoff

# User agent rotation (every 5 products)
Windows Chrome, Mac Chrome, Firefox, Edge, Linux Chrome

# Viewport rotation (every 5 products)
1920x1080, 1366x768, 1440x900, 1600x900

# Exponential backoff on errors
Retry 1: 2s + jitter
Retry 2: 4s + jitter
Retry 3: 8s + jitter
```

### 9. **Connection Pooling** 🔌

Database connection management:
- Timeout: 10 seconds per connection
- Busy wait: 5 seconds for locked database
- Foreign keys enabled for data integrity
- Automatic connection reuse

---

## 📊 Logging

Logs saved to `logs/scraper.log`:

```
2026-05-31 14:30:45 - INFO - ======================================================================
2026-05-31 14:30:45 - INFO - 🚀 SCRAPE SESSION STARTED - ID: a1b2c3d4
2026-05-31 14:30:45 - INFO - ======================================================================
2026-05-31 14:30:45 - INFO - 📦 Creating safety backup...
2026-05-31 14:30:46 - INFO - ✅ Backup created: data/backups/pricewatch_20260531_143046.db
2026-05-31 14:30:46 - INFO - 📦 Total products to scrape: 100
2026-05-31 14:30:47 - INFO - [1/100] Scraping: Gaming Mouse...
2026-05-31 14:30:50 - DEBUG - ✅ Success: Sony Gaming Mouse
2026-05-31 14:30:50 - DEBUG - ⏳ Waiting 3.2s before next request...
...
2026-05-31 14:35:22 - INFO - ============================================================
2026-05-31 14:35:22 - INFO - 📊 SCRAPE SUMMARY
2026-05-31 14:35:22 - INFO - ============================================================
2026-05-31 14:35:22 - INFO - ✅ Successful: 98/100
2026-05-31 14:35:22 - INFO - ❌ Failed: 2/100
2026-05-31 14:35:22 - INFO - Success rate: 98.0%
```

**Log rotation**: Keeps last 5 x 10MB logs (50MB total)

---

## 🚨 Troubleshooting

### Scraper stops after 10-15 products

**Cause**: Rate limiting (ERR_HTTP2_PROTOCOL_ERROR)

**Solutions**:
1. Increase delays: `MIN_DELAY = 3.0, MAX_DELAY = 10.0` in config
2. Check logs: `tail -f logs/scraper.log`
3. Use proxy: Add residential proxy to browser context
4. Wait 1 hour and retry (IP ban is temporary)

### Database file keeps growing

**Cause**: Old price history records accumulating

**Solutions**:
```python
# Clean old records (> 90 days)
from database import delete_old_records
delete_old_records(days=90)
```

Or backup the database after cleanup:
```bash
python monitor.py  # Check size
sqlite3 data/pricewatch.db "DELETE FROM price_history WHERE timestamp < datetime('now', '-90 days')"
```

### Checkpoint won't clear

**Cause**: Success rate < 80%

**Solution**: 
- Fix errors and run again, or
- Manually: `rm data/backups/checkpoint.json`

### Out of memory

**Cause**: Too many browser contexts open

**Solutions**:
1. Reduce `PRODUCTS_PER_BATCH` from 5 to 3
2. Close browser: `browser.close()` called in finally block
3. Check `--disable-dev-shm-usage` flag is set

---

## 📈 Performance Tips

1. **Increase batch size** (more products per browser context)
   ```python
   PRODUCTS_PER_BATCH = 10  # Default 5
   ```
   ⚠️ Risk: Uses more memory

2. **Reduce delays** (faster scraping)
   ```python
   MIN_DELAY = 1.0
   MAX_DELAY = 3.0
   ```
   ⚠️ Risk: Higher rate-limit chance

3. **Disable backups** (for testing)
   ```python
   ENABLE_BACKUP = False
   ```
   ⚠️ Risk: No safety net if crashes

4. **Run multiple instances** (multi-threading/multiprocessing)
   ```python
   scheduler.add_job(..., max_instances=1)  # Prevent concurrent runs
   ```

---

## 🔍 Monitoring in Production

### Setup continuous monitoring

```bash
# Watch logs in real-time
tail -f logs/scraper.log

# Check health every minute
watch -n 60 'python monitor.py'

# Check database size
watch -n 300 'du -sh data/'
```

### Set up alerts (optional)

```python
# In config.py, set thresholds:
ALERT_FAILURE_RATE = 0.3      # Alert if >30% fail
ALERT_CONSECUTIVE_ERRORS = 5  # Alert after 5 errors

# Check after scraping:
if metrics.success_rate < 80:
    send_email_alert("Low success rate!")
```

---

## 🎯 Next Steps

1. **Test locally**: `python scheduler.py` (watch first run)
2. **Monitor health**: `python monitor.py`
3. **Check logs**: `tail -f logs/scraper.log`
4. **Verify backups**: `ls -lh data/backups/`
5. **Deploy to server**: Run via cron or systemd
6. **Set up alerts**: Email/Slack notifications on errors
7. **Tune config**: Adjust delays/retries based on real data

---

## 📝 License & Notes

- Production-ready but still Phase 0 (data validation)
- All data saved safely with ACID compliance
- Logs include full error stack traces for debugging
- Backups never deleted automatically (you control cleanup)
- Recovery is automatic on crash (checkpoint-based)

**Questions?** Check logs first! They're detailed and verbose.
