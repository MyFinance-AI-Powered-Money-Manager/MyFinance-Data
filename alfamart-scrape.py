from playwright.sync_api import sync_playwright
import pandas as pd

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
                data.append({
                    "Category": category_name,
                    "Subcategory": subcategory_name
                })
            
        
        df = pd.DataFrame(data)
        print(df)
        browser.close()

if __name__ == "__main__":
    main()