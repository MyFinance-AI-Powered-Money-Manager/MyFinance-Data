from playwright.sync_api import sync_playwright
import pandas as pd
import time

def get_products(browser, page, subcategory_link):
    product_list = []
    page.goto(subcategory_link)
    while True:
        page.wait_for_selector(".mb-0.px-2.product_name.text-default", timeout=10000)
        products = page.locator(".mb-0.px-2.product_name.text-default").all()
        for product in products:
            product_name = product.inner_text().strip()
            product_list.append(product_name)
        next_button = page.get_by_label("Go to next page")
        is_disabled = next_button.get_attribute("aria-disabled")

        if is_disabled == None:
            next_button.click()
        else:
            break
    
    return(product_list)

def main():
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://alfagift.id")
        # Mengambil content didalam element dengan class list-group-item dan list-lv1
        parent_containers = page.locator(".list-group-item.list-lv1").all()

        for parent in parent_containers:
            # Mengambil text didalam element span yang berada didalam element a
            category_name = parent.locator("> a span").inner_text().strip()
            # Mengambil content a didalam element li didalam element dengan class card dan sebmenu
            subcategories = parent.locator(".card.submenu li a").all()
            for subcategory in subcategories:
                subcategory_name = subcategory.inner_text().strip()
                if subcategory_name == "Rokok & Korek":
                    continue
                subcategory_link = subcategory.get_attribute("href")
                products = get_products(browser, page, f"https://alfagift.id{subcategory_link}")
                for product in products:
                    data.append({
                        "Category": category_name,
                        "Subcategory": subcategory_name,
                        "product": product
                    })
                time.sleep(2)
            
        
        df = pd.DataFrame(data)
        df.to_csv("alfagift_scrape.csv")
        browser.close()

if __name__ == "__main__":
    main()