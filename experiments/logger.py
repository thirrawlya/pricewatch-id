"""
Logging and monitoring utilities for PriceWatch scraper.
Provides structured logging, error tracking, and health monitoring.
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from config import (
    LOG_FILE, LOG_LEVEL, LOG_MAX_BYTES, LOG_BACKUP_COUNT,
    LOGS_DIR, DEBUG_MODE
)

# ============================================================================
# SETUP LOGGING
# ============================================================================

def setup_logging():
    """Configure logging with both file and console handlers."""
    
    # Create logger
    logger = logging.getLogger("pricewatch")
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if not DEBUG_MODE else logging.DEBUG)
    
    # Formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# METRICS & STATISTICS
# ============================================================================

class ScrapeMetrics:
    """Track scraping statistics for monitoring and debugging."""
    
    def __init__(self):
        self.successful = 0
        self.failed = 0
        self.retried = 0
        self.skipped = 0
        self.errors = {}
        self.start_time = None
        self.end_time = None
    
    def add_success(self):
        self.successful += 1
    
    def add_failure(self, error_type="unknown"):
        self.failed += 1
        self.errors[error_type] = self.errors.get(error_type, 0) + 1
    
    def add_retry(self):
        self.retried += 1
    
    def add_skip(self):
        self.skipped += 1
    
    @property
    def total(self):
        return self.successful + self.failed + self.skipped
    
    @property
    def success_rate(self):
        if self.total == 0:
            return 0
        return (self.successful / self.total) * 100
    
    @property
    def duration_seconds(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    def get_summary(self):
        """Return summary as dict for logging."""
        return {
            "successful": self.successful,
            "failed": self.failed,
            "skipped": self.skipped,
            "retried": self.retried,
            "total": self.total,
            "success_rate_pct": round(self.success_rate, 1),
            "duration_seconds": round(self.duration_seconds, 1),
            "errors_by_type": self.errors,
        }
    
    def to_json(self):
        """Return metrics as JSON string."""
        summary = self.get_summary()
        summary["timestamp"] = datetime.now().isoformat()
        return json.dumps(summary, indent=2)
    
    def log_summary(self, logger):
        """Log summary to logger."""
        summary = self.get_summary()
        logger.info("=" * 60)
        logger.info("📊 SCRAPE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Successful: {summary['successful']}/{summary['total']}")
        logger.info(f"❌ Failed: {summary['failed']}/{summary['total']}")
        logger.info(f"⏭️  Skipped: {summary['skipped']}/{summary['total']}")
        logger.info(f"🔄 Retried: {summary['retried']}")
        logger.info(f"Success rate: {summary['success_rate_pct']}%")
        logger.info(f"Duration: {summary['duration_seconds']}s")
        if summary['errors_by_type']:
            logger.info(f"Error types: {summary['errors_by_type']}")
        logger.info("=" * 60)


# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthCheck:
    """Monitor system health and detect issues."""
    
    def __init__(self, logger):
        self.logger = logger
        self.consecutive_errors = 0
        self.is_healthy = True
    
    def record_error(self, error_type):
        """Record an error and check if system is unhealthy."""
        self.consecutive_errors += 1
        self.logger.warning(
            f"Health check: {self.consecutive_errors} consecutive errors "
            f"(type: {error_type})"
        )
    
    def record_success(self):
        """Reset error counter on success."""
        if self.consecutive_errors > 0:
            self.logger.info(f"System recovered from {self.consecutive_errors} errors")
        self.consecutive_errors = 0
    
    def is_critical(self, threshold=5):
        """Check if error rate is critical."""
        if self.consecutive_errors >= threshold:
            self.is_healthy = False
            self.logger.critical(
                f"⚠️ CRITICAL: {self.consecutive_errors} consecutive errors! "
                f"Consider stopping or investigating."
            )
            return True
        return False
    
    def check_database(self, db_path):
        """Check if database is accessible."""
        try:
            from pathlib import Path
            if not Path(db_path).exists():
                self.logger.warning(f"Database not found: {db_path}")
                return False
            
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            self.logger.debug("Database health check: OK")
            return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False


# ============================================================================
# ERROR TRACKING
# ============================================================================

class ErrorTracker:
    """Track and categorize errors for debugging."""
    
    ERROR_TYPES = {
        "ERR_HTTP2_PROTOCOL_ERROR": "HTTP/2 protocol error (rate limited?)",
        "TIMEOUT": "Request timeout",
        "SELECTOR_NOT_FOUND": "HTML selector not found",
        "NETWORK_ERROR": "Network/connection error",
        "PARSE_ERROR": "Failed to parse data",
        "DB_ERROR": "Database error",
        "UNKNOWN": "Unknown error",
    }
    
    def __init__(self):
        self.error_counts = {}
        self.error_details = []
    
    def categorize_error(self, error_message):
        """Categorize error by message."""
        error_msg_str = str(error_message).upper()
        
        for error_type, description in self.ERROR_TYPES.items():
            if error_type.replace("_", " ") in error_msg_str:
                return error_type, description
        
        if "timeout" in error_msg_str:
            return "TIMEOUT", self.ERROR_TYPES["TIMEOUT"]
        if "network" in error_msg_str or "connection" in error_msg_str:
            return "NETWORK_ERROR", self.ERROR_TYPES["NETWORK_ERROR"]
        if "selector" in error_msg_str:
            return "SELECTOR_NOT_FOUND", self.ERROR_TYPES["SELECTOR_NOT_FOUND"]
        if "sqlite" in error_msg_str or "database" in error_msg_str:
            return "DB_ERROR", self.ERROR_TYPES["DB_ERROR"]
        
        return "UNKNOWN", self.ERROR_TYPES["UNKNOWN"]
    
    def record(self, error_message, product_url=None):
        """Record an error."""
        error_type, description = self.categorize_error(error_message)
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        self.error_details.append({
            "type": error_type,
            "description": description,
            "message": str(error_message)[:200],
            "product": product_url,
            "timestamp": datetime.now().isoformat(),
        })
    
    def get_summary(self):
        """Get error summary."""
        return {
            "total_errors": len(self.error_details),
            "error_types": self.error_counts,
            "most_common": max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None,
        }


# Initialize logger
logger = setup_logging()
