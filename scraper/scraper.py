from playwright.sync_api import Page
from .parser import parse_price, parse_rating, parse_sold


def extract_text(page: Page, selectors_list, timeout=5000, debug=False):
    """Try multiple selectors in order until one succeeds."""
    for selector in selectors_list:
        try:
            text = page.locator(selector).first.inner_text(timeout=timeout)
            if text and text.strip():
                if debug:
                    print(f"  ✓ Found with: {selector}")
                return text.strip()
        except Exception:
            if debug:
                print(f"  ✗ Failed: {selector}")
            continue

    if debug:
        print("  ⚠️ All selectors failed")
    return None


def scrape_product(page: Page, url: str, debug=False):
    """Scrape product detail page and return parsed product data."""
    # Load page; if navigation fails, abort. But if selector wait times out,
    # continue to fallback extraction attempts.
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        if debug:
            print(f"❌ Failed to navigate to page: {e}")
        return None

    try:
        page.wait_for_selector("h1, [data-testid*='Product']", timeout=20000)
    except Exception as e:
        if debug:
            print(f"⚠️ wait_for_selector timed out, will attempt extraction anyway: {e}")

    # Give some extra time for JS-rendered content
    try:
        page.wait_for_timeout(5000)
    except Exception:
        # non-fatal if wait_for_timeout fails
        pass

    data = {}

    name_selectors = [
        '[data-testid="lblPDPDetailProductName"]',
        'h1[data-testid*="ProductName"]',
        'h1',
        '[class*=\"product-name\"]',
        '[class*=\"pdp-detail-title\"]',
    ]
    data["name"] = extract_text(page, name_selectors, debug=debug)

    price_selectors = [
        '[data-testid="lblPDPDetailProductPrice"]',
        '[data-testid*=\"Price\"]',
        '[class*=\"price\"]',
        'span[aria-label*=\"Rp\"]',
    ]
    data["raw_price"] = extract_text(page, price_selectors, debug=debug)
    data["price"] = parse_price(data["raw_price"])

    rating_selectors = [
        '[data-testid="lblPDPDetailProductRatingNumber"]',
        '[data-testid*=\"Rating\"]',
        '[class*=\"rating-score\"]',
    ]
    data["raw_rating"] = extract_text(page, rating_selectors, debug=debug)
    data["rating"] = parse_rating(data["raw_rating"])

    sold_selectors = [
        '[data-testid="lblPDPDetailProductSoldCounter"]',
        '[data-testid*=\"Sold\"]',
        '[class*=\"sold\"]',
    ]
    data["raw_sold"] = extract_text(page, sold_selectors, debug=debug)
    data["sold"] = parse_sold(data["raw_sold"])

    store_selectors = [
        '[data-testid="llbPDPFooterShopName"]',
        '[data-testid*=\"ShopName\"]',
        '[data-testid*=\"Shop\"]',
        'a[href*=\"/shop/\"]',
    ]
    data["store"] = extract_text(page, store_selectors, debug=debug)
    data["currency"] = "IDR"

    if debug:
        print(f"\n📊 Parsed data: {data}")

    return data
