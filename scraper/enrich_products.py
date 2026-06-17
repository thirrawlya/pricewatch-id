from playwright.sync_api import sync_playwright
from .scraper import scrape_product
import json
import time
import random

PRODUCTS_JSON = "data/products.json"


def load_products():
    with open(PRODUCTS_JSON) as f:
        return json.load(f)


def save_products(products):
    with open(PRODUCTS_JSON, "w") as f:
        json.dump(products, f, indent=2)


if __name__ == "__main__":
    products = load_products()
    total = len(products)
    updated = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        try:
            for idx, prod in enumerate(products, 1):
                if prod.get("name") and prod.get("name") != "Unknown":
                    continue

                url = prod.get("url")
                if not url:
                    continue

                page = context.new_page()
                result = None
                try:
                    result = scrape_product(page, url, debug=False)
                except Exception as e:
                    print(f"[ {idx}/{total} ] Error scraping {url}: {e}")
                finally:
                    try:
                        page.close()
                    except:
                        pass

                if result and result.get("name"):
                    prod["name"] = result["name"]
                    updated += 1
                    print(f"[ {idx}/{total} ] Updated: {result['name']}")
                else:
                    print(f"[ {idx}/{total} ] Skipped: no name found")

                # save incrementally so we can resume
                if idx % 10 == 0:
                    save_products(products)

                time.sleep(random.uniform(2, 3))

        finally:
            save_products(products)
            try:
                context.close()
            except:
                pass
            browser.close()

    print(f"\nDone. Updated {updated} out of {total} products.")
