from playwright.sync_api import sync_playwright

def scrape_product(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        data = {}

        try:
            data["name"] = page.locator('[data-testid="lblPDPDetailProductName"]').first.inner_text()
        except:
            data["name"] = None

        try:
            data["price"] = page.locator('[data-testid="lblPDPDetailProductPrice"]').first.inner_text()
        except:
            data["price"] = None

        try:
            data["rating"] = page.locator('[data-testid="lblPDPDetailProductRatingNumber"]').first.inner_text()
        except:
            data["rating"] = None

        try:
            data["sold"] = page.locator('[data-testid="lblPDPDetailProductSoldCounter"]').first.inner_text()
        except:
            data["sold"] = None

        try:
            data["store"] = page.locator('[data-testid="llbPDPFooterShopName"]').first.inner_text()
        except:
            data["store"] = None

        browser.close()
        return data

if __name__ == "__main__":
    from database import init_db, save_product, save_price

    init_db()

    url = "https://www.tokopedia.com/duniacom-srv/sony-wh-1000xm5-wh1000-xm5-wh1000xm5-noise-cancelling-headphones-1731634446228227779"
    result = scrape_product(url)
    
    product_id = save_product(result["name"], url)
    save_price(product_id, result["price"], result["rating"], result["sold"], result["store"])