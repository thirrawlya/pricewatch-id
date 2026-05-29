from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    
    page.goto("https://www.tokopedia.com/duniacom-srv/sony-wh-1000xm5-wh1000-xm5-wh1000xm5-noise-cancelling-headphones-1731634446228227779?extParam=ivf%3Dtrue%26keyword%3Dsony+wh-1000xm5%26search_id%3D20260529110317DB8E1AF0CB3ACA33CUSJ%26src%3Dsearch&t_id=1780052602103&t_st=1&t_pp=search_result&t_efo=search_pure_goods_card&t_ef=goods_search&t_sm=&t_spt=search_result", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    
    title = page.title()
    print("TITLE:", title)
    
    # coba ambil harga
    try:
        price = page.locator('[data-testid="lblPDPDetailProductPrice"]').first.inner_text()
        print("PRICE:", price)
    except:
        print("PRICE: not found")
    
    # coba ambil nama produk
    try:
        name = page.locator('[data-testid="lblPDPDetailProductName"]').first.inner_text()
        print("NAME:", name)
    except:
        print("NAME: not found")

    browser.close()