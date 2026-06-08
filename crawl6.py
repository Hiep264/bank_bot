import json
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import re


BLACKLIST_EXACT = {
    "Web Content Viewer",
    "Component Action Menu",
    "Actions",
    "${title}",
    "${loading}",
    "{}",
    "Về Agribank",
    "Tin tức",
    "Tuyển dụng",
    "Mạng lưới",
    "Hỗ trợ",
    "Lãi suất tiền gửi",
    "Lãi suất cho vay",
    "Phát triển bền vững",
}


def clean_text(text: str) -> str:

    # xóa portal id kiểu:
    # Z6_MO5I1441PO2K40658DVR2S04A6
    text = re.sub(
        r"Z\d+_[A-Z0-9_]+",
        "",
        text
    )

    # xóa placeholder
    text = re.sub(r"\$\{.*?\}", "", text)

    # chuẩn hóa xuống dòng
    text = re.sub(r"\n+", "\n", text)

    cleaned_lines = []
    seen = set()

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # blacklist
        if line in BLACKLIST_EXACT:
            continue

        # hotline
        if re.match(r"^\d{8,}", line):
            continue

        # dòng toàn ký tự đặc biệt
        if re.fullmatch(r"[\W_]+", line):
            continue

        # loại dòng quá ngắn
        if len(line) < 3:
            continue

        # bỏ trùng
        if line in seen:
            continue

        seen.add(line)

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

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

        # text = soup.get_text(separator="\n")

        # lines = [
        #     line.strip()
        #     for line in text.splitlines()
        #     if line.strip()
        # ]

        # clean_text = "\n".join(lines)

        raw_text = soup.get_text(separator="\n")

        cleaned_content = clean_text(raw_text)

        results.append(
            {
                "url": url,
                "title": title,
                "content": cleaned_content,
            }
        )

        print(f"Done: {url}")

    except Exception as e:
        print(f"Error: {url}")
        print(e)

driver.quit()

with open(
    "agribank6.jsonl",
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