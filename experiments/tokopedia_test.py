from playwright.sync_api import sync_playwright
from database import init_db, save_product, save_price
import json
import time

def extract_text(page, selectors_list, timeout=5000, debug=False):
    """
    Try multiple selectors in order until one succeeds.
    This handles cases where selectors change or are unavailable.
    """
    for selector in selectors_list:
        try:
            text = page.locator(selector).first.inner_text(timeout=timeout)
            if text and text.strip():
                if debug:
                    print(f"  ✓ Found with: {selector}")
                return text.strip()
        except Exception as e:
            if debug:
                print(f"  ✗ Failed: {selector} - {type(e).__name__}")
            continue
    
    if debug:
        print(f"  ⚠️ All selectors failed")
    return None


def scrape_product(page, url, debug=False):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # Wait for page to fully load - wait for main content
        page.wait_for_selector("h1, [data-testid*='Product']", timeout=10000)
        page.wait_for_timeout(3000)  # Additional stability wait
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        return None

    data = {}

    # Product Name - Multiple selector strategies
    print("Extracting product name...")
    name_selectors = [
        '[data-testid="lblPDPDetailProductName"]',
        'h1[data-testid*="ProductName"]',
        'h1',
        '[class*="product-name"]',
        '[class*="pdp-detail-title"]',
    ]
    data["name"] = extract_text(page, name_selectors, debug=debug)
    if not data["name"]:
        print(f"⚠️ Product name not extracted from {url}")

    # Price - Multiple selector strategies
    print("Extracting price...")
    price_selectors = [
        '[data-testid="lblPDPDetailProductPrice"]',
        '[data-testid*="Price"]',
        '[class*="price"]',
        'span[aria-label*="Rp"]',
    ]
    data["price"] = extract_text(page, price_selectors, debug=debug)

    # Rating - Multiple selector strategies
    print("Extracting rating...")
    rating_selectors = [
        '[data-testid="lblPDPDetailProductRatingNumber"]',
        '[data-testid*="Rating"]',
        '[class*="rating-score"]',
    ]
    data["rating"] = extract_text(page, rating_selectors, debug=debug)

    # Sold count - Multiple selector strategies
    print("Extracting sold count...")
    sold_selectors = [
        '[data-testid="lblPDPDetailProductSoldCounter"]',
        '[data-testid*="Sold"]',
        '[class*="sold"]',
    ]
    data["sold"] = extract_text(page, sold_selectors, debug=debug)

    # Store name - Multiple selector strategies
    print("Extracting store name...")
    store_selectors = [
        '[data-testid="llbPDPFooterShopName"]',
        '[data-testid*="ShopName"]',
        '[data-testid*="Shop"]',
        'a[href*="/shop/"]',
    ]
    data["store"] = extract_text(page, store_selectors, debug=debug)

    if debug:
        print(f"\n📊 Extracted data: {data}")

    return data

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