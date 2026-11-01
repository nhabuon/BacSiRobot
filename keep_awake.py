"""Danh thuc app Streamlit Community Cloud: mo trang bang trinh duyet that,
neu thay nut 'Yes, get this app back up' thi bam, roi cho app tai xong."""
import os, sys, time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL = os.environ.get("STREAMLIT_APP_URL", "https://bacsirobot.streamlit.app/")
WAKE_TEXT = "get this app back up"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        print("Mo:", URL)
        page.goto(URL, wait_until="domcontentloaded", timeout=90_000)
        time.sleep(8)
        btn = page.get_by_role("button", name=WAKE_TEXT, exact=False)
        if btn.count() > 0:
            print("App dang ngu -> bam nut danh thuc")
            btn.first.click()
            try:
                btn.first.wait_for(state="detached", timeout=180_000)
                print("Da danh thuc xong")
            except PWTimeout:
                print("LOI: bam roi nhung app chua day sau 3 phut")
                browser.close(); sys.exit(1)
        else:
            print("Khong thay nut danh thuc -> app dang thuc")
        # o lai mot luc de Streamlit ghi nhan co phien truy cap that
        time.sleep(20)
        title = page.title()
        print("Tieu de trang:", title)
        browser.close()

if __name__ == "__main__":
    main()
