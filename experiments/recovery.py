"""
Crash recovery and backup system for PriceWatch scraper.
Handles database backups, checkpoint recovery, and graceful shutdown.
"""

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_PATH, BACKUP_DIR, PRODUCTS_JSON, ENABLE_BACKUP, ENABLE_CRASH_RECOVERY

class CrashRecovery:
    """Handle crash detection and recovery."""
    
    def __init__(self):
        self.checkpoint_file = Path(BACKUP_DIR) / "checkpoint.json"
        self.scraping_state_file = Path(BACKUP_DIR) / "scraping_state.json"
    
    def save_checkpoint(self, processed_products, current_product_index, session_id):
        """Save checkpoint for crash recovery."""
        checkpoint = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "current_index": current_product_index,
            "processed_count": processed_products,
            "status": "in_progress"
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def load_checkpoint(self):
        """Load last checkpoint if it exists."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load checkpoint: {e}")
        return None
    
    def mark_complete(self):
        """Mark session as complete."""
        if self.checkpoint_file.exists():
            checkpoint = json.load(open(self.checkpoint_file))
            checkpoint["status"] = "complete"
            checkpoint["completed_at"] = datetime.now().isoformat()
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2)
    
    def should_resume(self):
        """Check if we should resume from checkpoint."""
        checkpoint = self.load_checkpoint()
        if checkpoint and checkpoint.get("status") == "in_progress":
            age_seconds = (
                datetime.fromisoformat(datetime.now().isoformat()) -
                datetime.fromisoformat(checkpoint["timestamp"])
            ).total_seconds()
            
            # Resume if crash happened less than 2 hours ago
            if age_seconds < 7200:
                return True
        
        return False
    
    def get_resume_index(self):
        """Get product index to resume from."""
        checkpoint = self.load_checkpoint()
        if checkpoint:
            # Resume from next product
            return checkpoint.get("current_index", 0) + 1
        return 0


class BackupManager:
    """Manage database backups and recovery."""
    
    def __init__(self):
        self.backup_dir = Path(BACKUP_DIR)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, source_db=DB_PATH):
        """Create timestamped backup of database."""
        if not ENABLE_BACKUP:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"pricewatch_{timestamp}.db"
            
            # Copy database file
            shutil.copy2(source_db, backup_file)
            
            # Keep only last 10 backups
            backups = sorted(self.backup_dir.glob("pricewatch_*.db"))
            for old_backup in backups[:-10]:
                old_backup.unlink()
            
            print(f"✅ Backup created: {backup_file}")
            return str(backup_file)
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def restore_from_backup(self, backup_file=None):
        """Restore database from backup."""
        try:
            if backup_file is None:
                # Find latest backup
                backups = sorted(self.backup_dir.glob("pricewatch_*.db"), reverse=True)
                if not backups:
                    print("❌ No backups found")
                    return False
                backup_file = backups[0]
            
            if not Path(backup_file).exists():
                print(f"❌ Backup file not found: {backup_file}")
                return False
            
            # Create safety backup before restore
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_backup = self.backup_dir / f"pricewatch_before_restore_{timestamp}.db"
            shutil.copy2(DB_PATH, safety_backup)
            
            # Restore
            shutil.copy2(backup_file, DB_PATH)
            print(f"✅ Database restored from: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def backup_products_json(self):
        """Backup products.json file."""
        if not Path(PRODUCTS_JSON).exists():
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"products_{timestamp}.json"
            shutil.copy2(PRODUCTS_JSON, backup_file)
            
            # Keep only last 5 backups
            backups = sorted(self.backup_dir.glob("products_*.json"))
            for old_backup in backups[:-5]:
                old_backup.unlink()
            
            return str(backup_file)
        except Exception as e:
            print(f"⚠️ Failed to backup products.json: {e}")
            return None
    
    def verify_database(self):
        """Verify database integrity."""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA integrity_check")
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Database integrity check failed: {e}")
            return False
    
    def get_database_stats(self):
        """Get database statistics."""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute("SELECT COUNT(*) FROM products")
            product_count = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM price_history")
            history_count = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT product_id) FROM price_history")
            tracked_products = c.fetchone()[0]
            
            conn.close()
            
            return {
                "total_products": product_count,
                "total_history_records": history_count,
                "tracked_products": tracked_products,
                "avg_records_per_product": history_count / tracked_products if tracked_products > 0 else 0,
            }
        except Exception as e:
            print(f"⚠️ Failed to get database stats: {e}")
            return None


class GracefulShutdown:
    """Handle graceful shutdown on interruption or error."""
    
    def __init__(self):
        self.cleanup_handlers = []
    
    def register_handler(self, handler):
        """Register a cleanup handler to run on shutdown."""
        self.cleanup_handlers.append(handler)
    
    def execute_all(self):
        """Execute all registered cleanup handlers."""
        print("\n\n🛑 Graceful shutdown initiated...")
        for handler in self.cleanup_handlers:
            try:
                handler()
            except Exception as e:
                print(f"⚠️ Error during cleanup: {e}")
        print("✅ Shutdown complete")
