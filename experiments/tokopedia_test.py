from playwright.sync_api import sync_playwright
from database import init_db, save_product, save_price
from scraper import scrape_product
import json
import time



if __name__ == "__main__":
    init_db()

    with open("data/products.json") as f:
        products = json.load(f)

    # Set to True to see detailed debugging output
    DEBUG_MODE = True
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        for idx, product in enumerate(products[:3], 1):  # Test with first 3 products
            print(f"\n{'='*60}")
            print(f"[{idx}] Scraping: {product['url']}")
            print(f"{'='*60}")
            try:
                page = context.new_page()
                result = scrape_product(page, product["url"], debug=DEBUG_MODE)
                page.close()

                if result is None:
                    print(f"⚠️ Skipped: {product['url']}")
                    continue

                print(f"✅ Success!")
                print(f"  Name: {result['name']}")
                print(f"  Price: {result['price']}")
                print(f"  Rating: {result['rating']}")
                print(f"  Sold: {result['sold']}")
                print(f"  Store: {result['store']}")

                product_id = save_product(result["name"] or "Unknown", product["url"])
                save_price(product_id, result["price"], result["rating"], result["sold"], result["store"])
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                time.sleep(3)

        browser.close()