from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    
    page.goto("https://www.tokopedia.com/duniacom-srv/sony-wh-1000xm5-wh1000-xm5-wh1000xm5-noise-cancelling-headphones-1731634446228227779", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    
    try:
        name = page.locator('[data-testid="lblPDPDetailProductName"]').first.inner_text()
        print("NAME:", name)
    except:
        print("NAME: not found")

    try:
        price = page.locator('[data-testid="lblPDPDetailProductPrice"]').first.inner_text()
        print("PRICE:", price)
    except:
        print("PRICE: not found")

    try:
        rating = page.locator('[data-testid="lblPDPDetailProductRatingNumber"]').first.inner_text()
        print("RATING:", rating)
    except:
        print("RATING: not found")

    browser.close()