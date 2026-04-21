from playwright.sync_api import sync_playwright
import pandas as pd

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://alfagift.id")
        # Mengambil lokasi dari html element dengan class list-group-item dan list-1v1 
        # Setelahnya mencari span yang terdapat didalam element a
        target_spans = page.locator(".list-group-item.list-lv1 > a span")
        span_texts = target_spans.all_inner_texts()
        df = pd.DataFrame({"category": span_texts})
        print(df)
        browser.close()

if __name__ == "__main__":
    main()