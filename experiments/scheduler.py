from apscheduler.schedulers.blocking import BlockingScheduler
from tokopedia_test import scrape_product
from database import init_db, save_product, save_price
from playwright.sync_api import sync_playwright
import json

def run_scraper():
    print("\n🔄 Running scheduled scrape...")
    with open("data/products.json") as f:
        products = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        for product in products:
            print(f"Scraping: {product['name']}...")
            try:
                page = context.new_page()
                result = scrape_product(page, product["url"])
                page.close()
                if result:
                    product_id = save_product(result["name"] or product["name"], product["url"])
                    save_price(product_id, result["price"], result["rating"], result["sold"], result["store"])
            except Exception as e:
                print(f"❌ {product['name']}: {e}")

        browser.close()

if __name__ == "__main__":
    init_db()
    pip_install = __import__("os").system("pip install apscheduler -q")
    
    scheduler = BlockingScheduler()
    scheduler.add_job(run_scraper, "interval", hours=6)
    
    print("⏰ Scheduler started. Running every 6 hours.")
    print("🔄 Running first scrape now...")
    run_scraper()
    scheduler.start()