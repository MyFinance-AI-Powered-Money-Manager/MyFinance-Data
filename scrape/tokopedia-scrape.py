from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
import time

def belajar_scrape(browser, link):
    data = []
    page = browser.new_page()
    page.goto(link)
    containers = page.locator('.css-4ki2fa').all()

    products = page.locator('.css-4ki2fa').all()
    for product in products:
         product_name = product.inner_text()
         data.append(product_name)
    
    page.close()
    return data

def voucher_scrape(browser, link):
    data = []
    page = browser.new_page()
    page.goto(link)

    popup_out_button = page.locator('div[class="absolute right-0 top-0 z-40 flex h-6 w-6 cursor-pointer items-center justify-center rounded-full bg-[#FCFCFD]"]')
    popup_out_button.click()

    expand_buttons = page.locator('button:has-text("Lihat lebih banyak")').all()
    for button in expand_buttons:
        if button.is_visible():
            button.click()
        else:
            None

    containers = page.locator('div[class="mb-5 px-3 md:mb-10 md:px-0"]').all()
    for container in containers:
        subcategory = container.locator('h2').inner_text()
        if subcategory == 'Populer':
            continue
        products = container.locator('h3').all()
        for product in products:
            product_name = product.inner_text()
            data.append({
                'subcategory' : subcategory,
                'nama_produk': product_name
            })
    page.close()
    return data

def streaming_scrape(browser, link):
    data =[]
    page = browser.new_page()
    page.goto(link)
    time.sleep(3)

    products = page.locator('.c_label').all()
    for product in products:
         product_name = product.inner_text()
         data.append(product_name)

    page.close()
    return data

def main():
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.tokopedia.com/top-up-tagihan")

        parent_containers = page.locator('div[data-testid="DYNAMIC_ICONS"]').all()

        for parent in parent_containers:
            category = parent.locator("h3").inner_text()
            products = parent.locator(".c_label").all()
            for product in products:
                nama_produk = product.inner_text()
                if nama_produk == "Belajar":
                    parent_element = product.locator("xpath=..")
                    href = parent_element.get_attribute("href")
                    belajar_products = belajar_scrape(browser, href)
                    for product in belajar_products:
                        data.append({
                            "category": category,
                            "subcategory": nama_produk,
                            "nama_produk": product
                        })
                    
                elif nama_produk == "Voucher Games":
                    parent_element = product.locator("xpath=..")
                    href = parent_element.get_attribute("href")
                    voucher_products = voucher_scrape(browser, href)
                    for product in voucher_products:
                        data.append({
                            "category": nama_produk,
                            "subcategory": product['subcategory'],
                            "nama_produk": product['nama_produk']
                        })
                elif nama_produk == "Streaming":
                    parent_element = product.locator("xpath=..")
                    href = parent_element.get_attribute("href")
                    streaming_products = streaming_scrape(browser, href)
                    for product in streaming_products:
                        data.append({
                            "category": category,
                            "subcategory": nama_produk,
                            "nama_produk": product
                        })
                else:
                    data.append({
                        "category": category,
                        "subcategory": np.nan,
                        "nama_produk": nama_produk
                        })
        browser.close()
    
    df = pd.DataFrame(data)
    df.drop_duplicates(subset='nama_produk', inplace=True)
    df.to_csv("scrape/scrape-result/tokopedia_scrape.csv")

if __name__ == "__main__":
    main()