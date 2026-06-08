import json
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URLS = [
    "https://www.agribank.com.vn/vn/home",
    "https://www.agribank.com.vn/vn/ve-agribank/gioi-thieu-agribank",
    "https://www.agribank.com.vn/vn/ve-agribank/lich-su-dinh-huong",
    "https://www.agribank.com.vn/vn/ve-agribank2",
    "https://www.agribank.com.vn/vn/ve-agribank/ban-lanh-dao",
    "https://www.agribank.com.vn/vn/ve-agribank/van-hoa-agribank",
    "https://www.agribank.com.vn/vn/ve-agribank/tin-tuc",
    "https://www.agribank.com.vn/vn/ve-agribank/giai-thuong",
    "https://www.agribank.com.vn/vn/tuyen-dung",
    "https://www.agribank.com.vn/vn/lai-suat"
]

options = Options()

# chạy ẩn
options.add_argument("--headless=new")

# tránh lỗi trên server
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

results = []

for url in URLS:
    try:
        print(f"Crawling: {url}")

        driver.get(url)

        # đợi javascript render
        time.sleep(5)

        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")

        # loại bỏ script và style
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)

        text = soup.get_text(separator="\n")

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        clean_text = "\n".join(lines)

        results.append(
            {
                "url": url,
                "title": title,
                "content": clean_text,
            }
        )

        print(f"Done: {url}")

    except Exception as e:
        print(f"Error: {url}")
        print(e)

driver.quit()

with open(
    "agribank5.jsonl",
    "w",
    encoding="utf-8"
) as f:

    for item in results:
        f.write(
            json.dumps(
                item,
                ensure_ascii=False
            )
            + "\n"
        )

print(f"Saved {len(results)} documents")