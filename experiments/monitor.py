"""
Real-time monitoring and status dashboard for PriceWatch scraper.
Provides system health visibility and debugging information.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from config import DB_PATH, LOGS_DIR, BACKUP_DIR
from database import get_connection

class SystemMonitor:
    """Monitor system health and generate status reports."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.logs_dir = Path(LOGS_DIR)
        self.backup_dir = Path(BACKUP_DIR)
    
    def get_database_health(self):
        """Check database health and statistics."""
        try:
            conn = get_connection()
            c = conn.cursor()
            
            # Get basic stats
            c.execute("SELECT COUNT(*) FROM products")
            total_products = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM price_history")
            total_records = c.fetchone()[0]
            
            # Get recent activity (last 24 hours)
            c.execute("""
                SELECT COUNT(*) FROM price_history
                WHERE timestamp > datetime('now', '-1 day')
            """)
            recent_records = c.fetchone()[0]
            
            # Get tracked products (with history)
            c.execute("""
                SELECT COUNT(DISTINCT product_id) FROM price_history
            """)
            tracked_products = c.fetchone()[0]
            
            conn.close()
            
            return {
                "status": "OK" if total_products > 0 else "EMPTY",
                "total_products": total_products,
                "total_records": total_records,
                "tracked_products": tracked_products,
                "recent_records_24h": recent_records,
                "avg_records_per_product": round(total_records / tracked_products, 2) if tracked_products > 0 else 0,
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    def get_log_health(self):
        """Check log file health."""
        try:
            log_file = self.logs_dir / "scraper.log"
            if not log_file.exists():
                return {"status": "NO_LOGS", "message": "Log file not created yet"}
            
            file_size = log_file.stat().st_size
            modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            time_since_modified = (datetime.now() - modified_time).total_seconds()
            
            # Read last 20 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()[-20:]
            
            last_errors = [l for l in lines if "ERROR" in l or "CRITICAL" in l]
            
            return {
                "status": "OK",
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "last_modified_seconds_ago": int(time_since_modified),
                "recent_errors": len(last_errors),
                "last_error": last_errors[-1].strip() if last_errors else None,
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def get_backup_health(self):
        """Check backup system health."""
        try:
            backup_files = list(self.backup_dir.glob("pricewatch_*.db"))
            backup_files.sort(reverse=True)
            
            latest_backup = None
            if backup_files:
                latest_file = backup_files[0]
                latest_backup = {
                    "file": latest_file.name,
                    "size_mb": round(latest_file.stat().st_size / 1024 / 1024, 2),
                    "age_hours": round((datetime.now() - datetime.fromtimestamp(latest_file.stat().st_mtime)).total_seconds() / 3600, 1),
                }
            
            return {
                "status": "OK" if latest_backup else "NO_BACKUPS",
                "total_backups": len(backup_files),
                "latest_backup": latest_backup,
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def get_checkpoint_status(self):
        """Get crash recovery checkpoint status."""
        try:
            checkpoint_file = self.backup_dir / "checkpoint.json"
            
            if not checkpoint_file.exists():
                return {"status": "NO_CHECKPOINT", "message": "No active checkpoint"}
            
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            
            checkpoint_age = (datetime.now() - datetime.fromisoformat(checkpoint['timestamp'])).total_seconds()
            
            return {
                "status": checkpoint.get("status", "unknown"),
                "session_id": checkpoint.get("session_id"),
                "last_index": checkpoint.get("current_index"),
                "age_seconds": int(checkpoint_age),
                "created_at": checkpoint.get("timestamp"),
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def generate_full_report(self):
        """Generate complete system health report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "database": self.get_database_health(),
            "logs": self.get_log_health(),
            "backups": self.get_backup_health(),
            "checkpoint": self.get_checkpoint_status(),
        }
        
        # Determine overall health
        statuses = [
            report["database"].get("status"),
            report["logs"].get("status"),
            report["backups"].get("status"),
        ]
        
        if all(s == "OK" for s in statuses if s):
            report["overall_status"] = "HEALTHY"
        elif any(s == "ERROR" for s in statuses):
            report["overall_status"] = "CRITICAL"
        else:
            report["overall_status"] = "WARNING"
        
        return report
    
    def print_report(self):
        """Print formatted health report to console."""
        report = self.generate_full_report()
        
        print("\n" + "=" * 70)
        print("📊 PRICEWATCH SYSTEM HEALTH REPORT")
        print("=" * 70)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Overall Status: {report['overall_status']}")
        print("=" * 70)
        
        print("\n📦 DATABASE")
        db = report["database"]
        print(f"  Status: {db.get('status')}")
        print(f"  Total Products: {db.get('total_products', 'N/A')}")
        print(f"  Total Records: {db.get('total_records', 'N/A')}")
        print(f"  Recent (24h): {db.get('recent_records_24h', 'N/A')}")
        print(f"  Tracked Products: {db.get('tracked_products', 'N/A')}")
        
        print("\n📝 LOGS")
        logs = report["logs"]
        print(f"  Status: {logs.get('status')}")
        print(f"  File Size: {logs.get('file_size_mb', 'N/A')} MB")
        print(f"  Last Modified: {logs.get('last_modified_seconds_ago', 'N/A')}s ago")
        print(f"  Recent Errors: {logs.get('recent_errors', 'N/A')}")
        
        print("\n💾 BACKUPS")
        backup = report["backups"]
        print(f"  Status: {backup.get('status')}")
        print(f"  Total Backups: {backup.get('total_backups', 0)}")
        if backup.get("latest_backup"):
            print(f"  Latest: {backup['latest_backup']['file']}")
            print(f"  Size: {backup['latest_backup']['size_mb']} MB")
            print(f"  Age: {backup['latest_backup']['age_hours']}h")
        
        print("\n🔄 CRASH RECOVERY")
        checkpoint = report["checkpoint"]
        print(f"  Status: {checkpoint.get('status')}")
        if checkpoint.get('session_id'):
            print(f"  Session ID: {checkpoint['session_id']}")
            print(f"  Last Index: {checkpoint.get('last_index', 'N/A')}")
            print(f"  Age: {checkpoint.get('age_seconds', 'N/A')}s")
        
        print("\n" + "=" * 70 + "\n")
        
        return report


if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.print_report()
