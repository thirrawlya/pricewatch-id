from playwright.sync_api import sync_playwright
from database import init_db, save_product, save_price
import json
import time

def scrape_product(page, url):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        return None

    data = {}

    try:
        data["name"] = page.locator('[data-testid="lblPDPDetailProductName"]').first.inner_text(timeout=5000)
    except:
        data["name"] = None

    try:
        data["price"] = page.locator('[data-testid="lblPDPDetailProductPrice"]').first.inner_text(timeout=5000)
    except:
        data["price"] = None

    try:
        data["rating"] = page.locator('[data-testid="lblPDPDetailProductRatingNumber"]').first.inner_text(timeout=5000)
    except:
        data["rating"] = None

    try:
        data["sold"] = page.locator('[data-testid="lblPDPDetailProductSoldCounter"]').first.inner_text(timeout=5000)
    except:
        data["sold"] = None

    try:
        data["store"] = page.locator('[data-testid="llbPDPFooterShopName"]').first.inner_text(timeout=5000)
    except:
        data["store"] = None

    return data

if __name__ == "__main__":
    init_db()

    with open("data/products.json") as f:
        products = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        for product in products:
            print(f"\nScraping: {product['name']}...")
            try:
                page = context.new_page()
                result = scrape_product(page, product["url"])
                page.close()

                if result is None:
                    print(f"⚠️ Skipped: {product['name']}")
                    continue

                product_id = save_product(result["name"] or product["name"], product["url"])
                save_price(product_id, result["price"], result["rating"], result["sold"], result["store"])
            except Exception as e:
                print(f"❌ Error on {product['name']}: {e}")
                continue

            time.sleep(3)

        browser.close()