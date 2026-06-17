from apscheduler.schedulers.blocking import BlockingScheduler
from .scraper import scrape_product
from .database import init_db, save_product, save_price
from playwright.sync_api import sync_playwright, BrowserContext
from .logger import setup_logging, ScrapeMetrics, HealthCheck, ErrorTracker
from .recovery import CrashRecovery, BackupManager, GracefulShutdown
from .config import (
    MIN_DELAY, MAX_DELAY, ERROR_BACKOFF_BASE, MAX_RETRIES_PER_PRODUCT,
    PRODUCTS_PER_BATCH, CIRCUIT_BREAKER_THRESHOLD, CIRCUIT_BREAKER_COOLDOWN,
    ENABLE_BACKUP, ENABLE_CRASH_RECOVERY, SCRAPE_INTERVAL_HOURS,
    REQUEST_TIMEOUT, PAGE_LOAD_TIMEOUT, PRODUCTS_JSON
)
import json
import time
import random
import os
import signal
import uuid
from datetime import datetime

# Optional test mode: set env TEST_PRODUCTS to limit number of products for quick runs
TEST_PRODUCTS = int(os.environ.get("TEST_PRODUCTS", "0"))

# ============================================================================
# ANTI-DETECTION CONFIGURATION
# ============================================================================

USER_AGENTS = [
    # Chrome - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome - Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome - Linux (keep some for consistency)
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1600, "height": 900},
]

HTTP_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_random_user_agent():
    """Get random user agent to avoid detection."""
    return random.choice(USER_AGENTS)


def get_random_viewport():
    """Get random viewport size to vary request fingerprint."""
    return random.choice(VIEWPORTS)


def get_random_delay(min_seconds=2, max_seconds=8):
    """
    Get random delay with exponential distribution.
    Returns: delay in seconds (not linear, biased toward lower values)
    """
    # Exponential backoff: biased toward 2-4 seconds, sometimes longer
    delay = random.expovariate(0.5) + min_seconds
    return min(delay, max_seconds)


def smart_delay(product_index, total_products, error_count=0):
    """
    Calculate smart delay based on progress and error rate.
    - Earlier products: smaller delays
    - Later products: larger delays (to avoid rate limits)
    - After errors: exponential backoff
    """
    progress_ratio = product_index / max(total_products, 1)
    base_delay = 2 + (progress_ratio * 3)  # 2-5 seconds based on progress
    
    # Add exponential backoff for errors
    if error_count > 0:
        base_delay += (2 ** min(error_count, 4))  # 2, 4, 8, 16, 16...
    
    # Add random jitter (±0-2 seconds)
    jitter = random.uniform(0, 2)
    
    return base_delay + jitter


def create_context_with_stealth(browser, user_agent, viewport):
    """
    Create a browser context with anti-detection measures.
    This mimics real browser behavior more closely.
    """
    context = browser.new_context(
        user_agent=user_agent,
        viewport=viewport,
        locale="id-ID",  # Indonesian locale (for Tokopedia)
        timezone_id="Asia/Jakarta",
        geolocation={"latitude": -6.2088, "longitude": 106.8456},  # Jakarta
        permissions=["geolocation"],
        extra_http_headers=HTTP_HEADERS,
        # Anti-detection options
        ignore_https_errors=True,
    )
    
    # Inject anti-detection JavaScript to hide browser automation signals
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['id-ID', 'id', 'en-US', 'en'],
        });
        
        window.chrome = {
            runtime: {}
        };
    """)
    
    return context


def run_scraper(max_retries=MAX_RETRIES_PER_PRODUCT):
    """
    Main scraper function with production-grade reliability features:
    - Crash recovery with checkpoints
    - Database backups before/after
    - Health monitoring & circuit breaker
    - Comprehensive error tracking
    - Graceful shutdown handling
    """
    
    # Setup logging
    logger = setup_logging()
    session_id = str(uuid.uuid4())[:8]
    
    logger.info("=" * 70)
    logger.info(f"🚀 SCRAPE SESSION STARTED - ID: {session_id}")
    logger.info("=" * 70)
    
    # Initialize managers
    backup_manager = BackupManager()
    crash_recovery = CrashRecovery()
    metrics = ScrapeMetrics()
    health_check = HealthCheck(logger)
    error_tracker = ErrorTracker()
    graceful_shutdown = GracefulShutdown()
    
    metrics.start_time = datetime.now()
    
    # Health check
    if not backup_manager.verify_database():
        logger.error("❌ Database integrity check failed! Attempting to restore from backup...")
        if not backup_manager.restore_from_backup():
            logger.critical("❌ Cannot restore database. Aborting.")
            return
    
    # Create backup before scraping
    if ENABLE_BACKUP:
        logger.info("📦 Creating safety backup...")
        backup_manager.create_backup()
        backup_manager.backup_products_json()
    
    # Determine start index (crash recovery)
    start_index = 0
    if ENABLE_CRASH_RECOVERY and crash_recovery.should_resume():
        checkpoint = crash_recovery.load_checkpoint()
        start_index = checkpoint.get("current_index", 0)
        logger.warning(f"⚠️ RESUMING FROM CHECKPOINT - Index: {start_index}")
        logger.info(f"   Last session ID: {checkpoint.get('session_id')}")
        logger.info(f"   Last checkpoint: {checkpoint.get('timestamp')}")
    
    # Load products
    try:
        with open(PRODUCTS_JSON) as f:
            products = json.load(f)
    except Exception as e:
        logger.critical(f"❌ Failed to load products.json: {e}")
        return
    
    if not products:
        logger.warning("⚠️ No products to scrape")
        return
    # If in test mode, limit number of products to scan.
    if TEST_PRODUCTS and TEST_PRODUCTS > 0:
        products = products[:TEST_PRODUCTS]
        logger.info(f"🔬 Test mode: limiting products to {len(products)}")

    total_products = len(products)
    logger.info(f"📦 Total products to scrape: {total_products}")
    logger.info(f"🔄 Starting from index: {start_index}")

    # If start_index is beyond the current product list (e.g., resuming from
    # an old checkpoint) or if we're in TEST mode, reset start_index to 0 so
    # test runs actually iterate over the limited product set.
    if start_index >= total_products or (TEST_PRODUCTS and TEST_PRODUCTS > 0):
        if start_index >= total_products:
            logger.warning(f"⚠️ Checkpoint index {start_index} >= total products {total_products}; resetting start_index to 0 for this run")
        else:
            logger.info("🔬 Test mode active: ignoring previous checkpoint and starting from 0")
        start_index = 0
    
    # Register cleanup handlers
    def cleanup_database():
        if ENABLE_BACKUP:
            logger.info("📦 Creating final backup...")
            backup_manager.create_backup()
    
    def cleanup_checkpoint():
        if ENABLE_CRASH_RECOVERY and metrics.success_rate > 90:
            logger.info("✅ Session successful, clearing checkpoint")
            crash_recovery.mark_complete()
    
    graceful_shutdown.register_handler(cleanup_database)
    graceful_shutdown.register_handler(cleanup_checkpoint)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.info("\n⏸️ Interrupt signal received")
        graceful_shutdown.execute_all()
        metrics.end_time = datetime.now()
        metrics.log_summary(logger)
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, signal_handler)

    # ========================================================================
    # MAIN SCRAPING LOOP
    # ========================================================================

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--disable-component-extensions",
            ]
        )

        consecutive_errors = 0

        # Create initial browser context so resuming from a checkpoint
        # (start_index > 0) still has a valid context before the loop.
        user_agent = get_random_user_agent()
        viewport = get_random_viewport()
        context = create_context_with_stealth(browser, user_agent, viewport)
        logger.debug(f"🔄 Initial browser context created before loop")
        logger.debug(f"   UA: {user_agent[:50]}...")
        logger.debug(f"   Viewport: {viewport['width']}x{viewport['height']}")

        try:
            for product_idx in range(start_index, total_products):
                product = products[product_idx]
                
                # Create new context periodically (every N products).
                # Use offset from start_index so resuming doesn't immediately
                # recreate the context we just made above.
                if (product_idx - start_index) % PRODUCTS_PER_BATCH == 0 and product_idx != start_index:
                    if context:
                        context.close()
                    
                    user_agent = get_random_user_agent()
                    viewport = get_random_viewport()
                    context = create_context_with_stealth(browser, user_agent, viewport)
                    
                    logger.debug(f"🔄 New browser context")
                    logger.debug(f"   UA: {user_agent[:50]}...")
                    logger.debug(f"   Viewport: {viewport['width']}x{viewport['height']}")

                product_name = product.get("name", "Unknown")
                product_url = product.get("url", "")
                
                logger.info(f"[{product_idx + 1}/{total_products}] Scraping: {product_name[:50]}")

                retries = 0
                success = False

                while retries < max_retries:
                    try:
                        page = context.new_page()
                        # Production: do not enable verbose debug during normal runs
                        result = scrape_product(page, product_url, debug=False)
                        page.close()

                        if result and result.get("name"):
                            try:
                                product_id = save_product(result["name"], product_url)
                                save_price(product_id, result["price"], result["rating"], result["sold"], result["store"])
                                logger.debug(f"✅ Success: {result['name'][:40]}")
                                metrics.add_success()
                                health_check.record_success()
                                consecutive_errors = 0
                                success = True
                                break
                            except Exception as db_error:
                                logger.error(f"❌ Database error: {db_error}")
                                error_tracker.record(db_error, product_url)
                                metrics.add_failure("database_error")
                                retries += 1
                        else:
                            logger.warning(f"⚠️ No data extracted")
                            metrics.add_skip()
                            break

                    except Exception as e:
                        retries += 1
                        error_msg = str(e)[:100]
                        
                        logger.warning(f"❌ Error (retry {retries}/{max_retries}): {error_msg}")
                        error_tracker.record(e, product_url)
                        metrics.add_retry()
                        metrics.add_failure(type(e).__name__)
                        
                        # Check for critical errors
                        if "ERR_HTTP2_PROTOCOL_ERROR" in str(e):
                            health_check.record_error("HTTP2_PROTOCOL")
                            consecutive_errors += 1
                        elif "timeout" in error_msg.lower():
                            health_check.record_error("TIMEOUT")
                        else:
                            health_check.record_error("OTHER")

                        if retries >= max_retries:
                            logger.warning(f"🚫 Max retries reached for {product_name}")
                            metrics.add_failure("max_retries_exceeded")
                            break
                        
                        # Exponential backoff on retry
                        wait_time = (ERROR_BACKOFF_BASE ** retries) + random.uniform(0, 1)
                        logger.debug(f"⏳ Waiting {wait_time:.1f}s before retry...")
                        time.sleep(wait_time)

                # Save checkpoint after each product
                if ENABLE_CRASH_RECOVERY and (product_idx + 1) % 5 == 0:
                    crash_recovery.save_checkpoint(product_idx + 1, product_idx, session_id)

                # Circuit breaker: stop if too many consecutive errors
                if health_check.is_critical(CIRCUIT_BREAKER_THRESHOLD):
                    logger.critical(f"🔌 CIRCUIT BREAKER ACTIVATED - Too many errors")
                    break

                # Smart delay between requests
                if product_idx < total_products - 1:
                    delay = smart_delay(product_idx, total_products, consecutive_errors)
                    logger.debug(f"⏳ Waiting {delay:.1f}s before next request...")
                    time.sleep(delay)

        except KeyboardInterrupt:
            logger.info("⏸️ Scraping interrupted by user")
        except Exception as e:
            logger.critical(f"💥 Unexpected error in scraper: {e}")
            error_tracker.record(e, "unknown")
            raise
        finally:
            # Closing context may fail if it was already closed elsewhere
            try:
                if context:
                    context.close()
            except Exception:
                pass

            try:
                browser.close()
            except Exception:
                pass

    # ========================================================================
    # POST-SCRAPE PROCESSING
    # ========================================================================

    metrics.end_time = datetime.now()
    
    # Log final statistics
    metrics.log_summary(logger)
    
    # Log database stats
    db_stats = backup_manager.get_database_stats()
    if db_stats:
        logger.info("📊 DATABASE STATISTICS")
        logger.info(f"   Total products: {db_stats['total_products']}")
        logger.info(f"   Price history records: {db_stats['total_history_records']}")
        logger.info(f"   Tracked products: {db_stats['tracked_products']}")
        logger.info(f"   Avg records/product: {db_stats['avg_records_per_product']:.1f}")
    
    # Log error summary
    error_summary = error_tracker.get_summary()
    if error_summary['total_errors'] > 0:
        logger.warning("⚠️ ERROR SUMMARY")
        logger.warning(f"   Total errors: {error_summary['total_errors']}")
        logger.warning(f"   Error types: {error_summary['error_types']}")
        if error_summary['most_common']:
            logger.warning(f"   Most common: {error_summary['most_common']}")
    
    # Final backup
    if ENABLE_BACKUP:
        logger.info("📦 Creating final backup...")
        backup_manager.create_backup()
    
    # Clear checkpoint if successful
    if ENABLE_CRASH_RECOVERY and metrics.success_rate > 80:
        logger.info("✅ Session successful, clearing checkpoint")
        crash_recovery.mark_complete()
    elif ENABLE_CRASH_RECOVERY:
        logger.warning(f"⚠️ Session success rate {metrics.success_rate}% - keeping checkpoint for recovery")
    
    logger.info("=" * 70)
    logger.info("🏁 SCRAPE SESSION COMPLETE")
    logger.info("=" * 70)

if __name__ == "__main__":
    logger = setup_logging()
    
    try:
        # Initialize database
        init_db()
        logger.info("✅ Database initialized")
        
        # Initialize backup manager for pre-flight checks
        backup_manager = BackupManager()
        
        logger.info("\n" + "=" * 70)
        logger.info("🚀 PRICEWATCH SCHEDULER STARTING")
        logger.info("=" * 70)
        logger.info(f"Scrape interval: {SCRAPE_INTERVAL_HOURS} hours")
        logger.info(f"Backup enabled: {ENABLE_BACKUP}")
        logger.info(f"Crash recovery enabled: {ENABLE_CRASH_RECOVERY}")
        logger.info(f"Circuit breaker threshold: {CIRCUIT_BREAKER_THRESHOLD} errors")
        logger.info("=" * 70 + "\n")
        
        # Run first scrape immediately
        logger.info("▶️ Running first scrape now...")
        run_scraper()
        
        # Setup scheduler for periodic runs
        scheduler = BlockingScheduler()
        scheduler.add_job(
            run_scraper,
            "interval",
            hours=SCRAPE_INTERVAL_HOURS,
            max_instances=1,  # Prevent concurrent scraping
            misfire_grace_time=60
        )
        
        # Add periodic backup job
        if ENABLE_BACKUP:
            def backup_job():
                logger.info("📦 Running periodic backup...")
                backup_manager = BackupManager()
                backup_manager.create_backup()
            
            scheduler.add_job(
                backup_job,
                "interval",
                hours=24,
                max_instances=1
            )
        
        logger.info("⏰ Scheduler started. Waiting for next scheduled run...")
        logger.info(f"Next run in {SCRAPE_INTERVAL_HOURS} hours")
        
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("\n✋ Scheduler stopped by user")
    except Exception as e:
        logger.critical(f"💥 Scheduler crashed: {e}", exc_info=True)
        raise