from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
import time

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
                data.append({
                    "kategori": category,
                    "nama_produk": nama_produk
                    })
        browser.close()

    for data in data:
        print(f"kategori: {data['kategori']}\nnama_produk: {data['nama_produk']}")
    
    df = pd.DataFrame(data)
    df.to_csv("tokopedia_scrape.csv")

if __name__ == "__main__":
    main()