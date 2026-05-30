from playwright.sync_api import sync_playwright
from database import init_db, save_product, save_price
import json
import time

BLACKLIST = [
    "seller.tokopedia.com",
    "tokopedia.com/mobile-apps",
    "tokopedia.com/help",
    "tokopedia.com/discovery",
    "tokopedia.com/promo",
    "tokopedia.com/people",
    "tokopedia.com/mitra",
    "tokopedia.com/cart",
    "tokopedia.com/login",
    "tokopedia.com/register",
    "tokopedia.com/edu",
]

def valid_product_url(url):
    if not url:
        return False
    for bad in BLACKLIST:
        if bad in url:
            return False
    path = url.replace("https://www.tokopedia.com/", "")
    parts = path.split("/")
    return len(parts) >= 2 and parts[1] != ""

KEYWORDS = [
    "gaming mouse",
]


def scrape_search_results(page, keyword, max_products=20):
    url = f"https://www.tokopedia.com/search?q={keyword.replace(' ', '+')}"

    print(f"\n🔍 Searching: {keyword}")

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(8000)

    except Exception as e:
        print(f"❌ Failed search page: {e}")
        return []

    # scroll biar lazy load jalan
    for i in range(10):
        try:
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1500)
        except:
            pass

    print("✅ Search page loaded")

    products = []
    seen = set()

    try:
        # ambil semua href dari page
        hrefs = page.eval_on_selector_all(
            "a",
            """
            elements => elements.map(el => el.href)
            """
        )

        print(f"🔗 Total raw hrefs: {len(hrefs)}")

        for href in hrefs:

            if not href:
                continue

            # filter cuma product tokopedia
            if "tokopedia.com" not in href:
                continue

            # skip non-product
            blocked = [
                "/search",
                "/help",
                "/about",
                "/promo",
                "/discovery",
                "/people",
                "/mitra",
                "/cart",
                "/login",
                "/register",
            ]

            if any(x in href for x in blocked):
                continue

            # bersihin query params
            clean_url = href.split("?")[0]

            # skip duplicate
            if clean_url in seen:
                continue

            seen.add(clean_url)

            if valid_product_url(clean_url):
                products.append({
                    "name": "Unknown",
                    "url": clean_url
                })

        print(f"✅ Parsed products: {len(products)}")

    except Exception as e:
        print(f"❌ Failed parsing links: {e}")

    return products[:max_products]


def scrape_product(page, url):

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(5000)

    except Exception as e:
        print(f"❌ Failed load product: {e}")
        return None

    data = {
        "name": None,
        "price": None,
        "rating": None,
        "sold": None,
        "store": None
    }

    try:
        data["name"] = page.locator(
            '[data-testid="lblPDPDetailProductName"]'
        ).first.inner_text(timeout=5000)
    except:
        pass

    try:
        data["price"] = page.locator(
            '[data-testid="lblPDPDetailProductPrice"]'
        ).first.inner_text(timeout=5000)
    except:
        pass

    try:
        data["rating"] = page.locator(
            '[data-testid="lblPDPDetailProductRatingNumber"]'
        ).first.inner_text(timeout=5000)
    except:
        pass

    try:
        data["sold"] = page.locator(
            '[data-testid="lblPDPDetailProductSoldCounter"]'
        ).first.inner_text(timeout=5000)
    except:
        pass

    try:
        data["store"] = page.locator(
            '[data-testid="llbPDPFooterShopName"]'
        ).first.inner_text(timeout=5000)
    except:
        pass

    return data


if __name__ == "__main__":

    init_db()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        all_products = []

        # ==========================================
        # STEP 1 — SEARCH & COLLECT LINKS
        # ==========================================

        search_page = context.new_page()

        for keyword in KEYWORDS:

            try:
                found_products = scrape_search_results(
                    search_page,
                    keyword,
                    max_products=20
                )

                all_products.extend(found_products)

            except Exception as e:
                print(f"❌ Search error: {e}")

            time.sleep(3)

        search_page.close()

        # remove duplicate global
        unique_products = []
        seen_urls = set()

        for product in all_products:

            if product["url"] in seen_urls:
                continue

            seen_urls.add(product["url"])
            unique_products.append(product)

        print(f"\n📦 FINAL UNIQUE PRODUCTS: {len(unique_products)}")

        # ==========================================
        # SAVE AUTO TO JSON
        # ==========================================

        try:
            with open("data/products.json", "w") as f:
                json.dump(
                    unique_products,
                    f,
                    indent=2
                )

            print("✅ products.json updated")

        except Exception as e:
            print(f"❌ Failed save JSON: {e}")

        # ==========================================
        # STEP 2 — SCRAPE PRODUCT DETAILS
        # ==========================================

        print("\n🔄 Scraping product details...")

        for product in unique_products:

            print(f"\n🛒 {product['url']}")

            try:

                page = context.new_page()

                result = scrape_product(
                    page,
                    product["url"]
                )

                page.close()

                if not result:
                    print("⚠️ Failed scrape")
                    continue

                if not result["price"]:
                    print("⚠️ No price found")
                    continue

                product_id = save_product(
                    result["name"] or product["name"],
                    product["url"]
                )

                save_price(
                    product_id,
                    result["price"],
                    result["rating"],
                    result["sold"],
                    result["store"]
                )

                print(f"✅ Saved: {result['price']}")

            except Exception as e:
                print(f"❌ Product scrape error: {e}")

            time.sleep(2)

        browser.close()

        print("\n🔥 DONE.")