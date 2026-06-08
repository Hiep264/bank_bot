import json
import re
import time
from pathlib import Path

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
    "https://www.agribank.com.vn/vn/lai-suat",
]


def create_driver():
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    return webdriver.Chrome(options=options)


def is_error_page(text: str) -> bool:

    patterns = [
        "javascript is disabled",
        "enable javascript",
        "error:",
        "access denied",
    ]

    text = text.lower()

    return any(p in text for p in patterns)


def clean_text(text: str) -> str:

    text = re.sub(r"Z\d+_[A-Z0-9_]+", "", text)

    text = re.sub(r"\$\{.*?\}", "", text)

    text = re.sub(r"\n+", "\n", text)

    blacklist = {
        "Web Content Viewer",
        "Component Action Menu",
        "Actions",
        "{}",
    }

    seen = set()
    result = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if line in blacklist:
            continue

        if len(line) < 3:
            continue

        if line in seen:
            continue

        seen.add(line)

        result.append(line)

    return "\n".join(result)


def extract_content(html: str) -> str:

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "header",
            "footer",
            "nav",
            "aside",
        ]
    ):
        tag.decompose()

    selectors = [
        "main",
        "article",
        "[role='main']",
        ".content",
        ".main-content",
    ]

    content = None

    for selector in selectors:
        content = soup.select_one(selector)

        if content:
            break

    if content is None:
        content = soup.body

    if content is None:
        return ""

    text = content.get_text("\n", strip=True)

    return clean_text(text)


def crawl_page(driver, url):

    driver.get(url)

    time.sleep(8)

    html = driver.page_source

    text_preview = html[:3000]

    if "Javascript is disabled" in text_preview:
        print(
            f"[WARNING] {url} trả về trang lỗi Javascript"
        )

    title = driver.title

    content = extract_content(html)

    return {
        "url": url,
        "title": title,
        "content": content,
        "html": html,
    }


def main():

    Path("debug_html").mkdir(exist_ok=True)

    driver = create_driver()

    results = []

    try:

        for i, url in enumerate(URLS):

            print(f"Crawling {url}")

            data = crawl_page(driver, url)

            with open(
                f"debug_html/page_{i}.html",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(data["html"])

            del data["html"]

            if is_error_page(data["content"]):
                print(
                    f"Skip error page: {url}"
                )
                continue

            if len(data["content"].split()) < 30:
                print(
                    f"Skip short page: {url}"
                )
                continue

            results.append(data)

    finally:
        driver.quit()

    with open(
        "agribank8.jsonl",
        "w",
        encoding="utf-8",
    ) as f:

        for item in results:
            f.write(
                json.dumps(
                    item,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(
        f"Saved {len(results)} documents"
    )


if __name__ == "__main__":
    main()