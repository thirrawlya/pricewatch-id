"""
Configuration and constants for PriceWatch scraper system.
This centralizes all configuration to make it easy to adjust settings.
"""

import os
from pathlib import Path

# ============================================================================
# PATHS & DIRECTORIES
# ============================================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
BACKUPS_DIR = DATA_DIR / "backups"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(exist_ok=True)

DB_PATH = str(DATA_DIR / "pricewatch.db")
PRODUCTS_JSON = str(DATA_DIR / "products.json")
BACKUP_DIR = str(BACKUPS_DIR)

# ============================================================================
# SCRAPER SETTINGS
# ============================================================================

# Delays and timeouts (in seconds)
MIN_DELAY = 2.0
MAX_DELAY = 8.0
ERROR_BACKOFF_BASE = 2.0
REQUEST_TIMEOUT = 30
PAGE_LOAD_TIMEOUT = 10
SELECTOR_TIMEOUT = 5

# Retry configuration
MAX_RETRIES_PER_PRODUCT = 3
MAX_RETRIES_CONNECTION = 2

# Rate limiting
PRODUCTS_PER_BATCH = 5  # New browser context every N products
CIRCUIT_BREAKER_THRESHOLD = 5  # Fail after N consecutive errors
CIRCUIT_BREAKER_COOLDOWN = 300  # 5 minutes

# ============================================================================
# SCHEDULER SETTINGS
# ============================================================================

SCRAPE_INTERVAL_HOURS = 6
BACKUP_INTERVAL_HOURS = 24

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = LOGS_DIR / "scraper.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5  # Keep 5 backup logs

# ============================================================================
# DATABASE SETTINGS
# ============================================================================

# Connection pool (for future PostgreSQL migration)
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10
DB_POOL_RECYCLE = 3600  # Recycle connections every hour

# ============================================================================
# MONITORING SETTINGS
# ============================================================================

# Health check interval (seconds)
HEALTH_CHECK_INTERVAL = 60

# Alert thresholds
ALERT_FAILURE_RATE = 0.3  # Alert if >30% products fail
ALERT_CONSECUTIVE_ERRORS = 5  # Alert after N consecutive errors

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_BACKUP = True
ENABLE_HEALTH_CHECK = True
ENABLE_CIRCUIT_BREAKER = True
ENABLE_CRASH_RECOVERY = True

# Debug mode
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
