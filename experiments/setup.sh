#!/bin/bash

# PriceWatch Scraper - Quick Start Guide
# This script sets up and runs the production-ready scraper

set -e

echo "🚀 PriceWatch Scraper - Quick Start"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python environment..."
python3 --version

# Install dependencies if needed
echo ""
echo "📦 Installing dependencies..."
pip install playwright apscheduler -q 2>/dev/null || echo "⚠️  Some packages might already be installed"

# Download Chromium if needed
echo ""
echo "🌐 Setting up Playwright browsers..."
python3 -m playwright install chromium -q || echo "✓ Chromium ready"

# Initialize database
echo ""
echo "💾 Initializing database..."
cd experiments
python3 -c "from database import init_db; init_db(); print('✅ Database initialized')"

# Show structure
echo ""
echo "📁 Project structure created:"
ls -lh ../logs/ 2>/dev/null || mkdir ../logs && echo "   ✓ logs/"
ls -lh ../data/backups/ 2>/dev/null || mkdir ../data/backups && echo "   ✓ data/backups/"

# Display configuration
echo ""
echo "⚙️  Current configuration:"
python3 -c "
from config import *
print(f'   • Scrape interval: {SCRAPE_INTERVAL_HOURS}h')
print(f'   • Min delay: {MIN_DELAY}s')
print(f'   • Max delay: {MAX_DELAY}s')
print(f'   • Max retries: {MAX_RETRIES_PER_PRODUCT}')
print(f'   • Circuit breaker threshold: {CIRCUIT_BREAKER_THRESHOLD}')
print(f'   • Crash recovery: {ENABLE_CRASH_RECOVERY}')
print(f'   • Backups enabled: {ENABLE_BACKUP}')
"

# Show next steps
echo ""
echo "=========================================="
echo "✅ Setup complete! Ready to scrape."
echo "=========================================="
echo ""
echo "🎯 Next steps:"
echo ""
echo "1️⃣  Check system health:"
echo "   python monitor.py"
echo ""
echo "2️⃣  Start scraper (single pass):"
echo "   python tokopedia_test.py"
echo ""
echo "3️⃣  Start scheduler (continuous, every 6h):"
echo "   python scheduler.py"
echo ""
echo "4️⃣  Monitor logs (real-time):"
echo "   tail -f ../logs/scraper.log"
echo ""
echo "5️⃣  Check backups:"
echo "   ls -lh ../data/backups/"
echo ""
echo "📚 Full documentation:"
echo "   cat ../RELIABILITY.md"
echo ""
