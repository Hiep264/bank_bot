import json
import re
import time

import trafilatura
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


def fallback_extract(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup([
        "script",
        "style",
        "noscript",
        "header",
        "footer",
        "nav",
        "aside",
        "iframe",
        "svg",
        "form"
    ]):
        tag.decompose()

    content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile("content", re.I))
        or soup.find(class_=re.compile("content", re.I))
        or soup.body
    )

    if not content:
        return ""

    return content.get_text("\n", strip=True)


def clean_text(text: str) -> str:
    if not text:
        return ""

    # Portal ID
    text = re.sub(
        r"Z\d+_[A-Z0-9_]+",
        "",
        text
    )

    # ${title}
    text = re.sub(
        r"\$\{.*?\}",
        "",
        text
    )

    # chuẩn hóa khoảng trắng
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n+", "\n", text)

    blacklist = {
        "Web Content Viewer",
        "Component Action Menu",
        "Actions",
        "Error:\nJavascript is disabled in this browser. This page requires Javascript. Modify your browser's settings to allow Javascript to execute. See your browser's documentation for specific instructions.",
        "{}",
    }

    lines = []
    seen = set()

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if line in blacklist:
            continue

        # hotline đơn lẻ
        if re.fullmatch(r"[\d\s\/\-]{8,}", line):
            continue

        # ký tự vô nghĩa
        if re.fullmatch(r"[\W_]+", line):
            continue

        # quá ngắn
        if len(line) < 3:
            continue

        # loại dòng lặp
        if line in seen:
            continue

        seen.add(line)
        lines.append(line)

    return "\n".join(lines)


def extract_content(html: str) -> str:

    try:
        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True
        )

        if content:
            return clean_text(content)

    except Exception:
        pass

    return clean_text(
        fallback_extract(html)
    )


def create_driver():

    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)


def main():

    driver = create_driver()

    results = []

    try:

        for url in URLS:

            try:

                print(f"Crawling: {url}")

                driver.get(url)

                time.sleep(5)

                html = driver.page_source

                soup = BeautifulSoup(
                    html,
                    "html.parser"
                )

                title = ""

                if soup.title:
                    title = soup.title.get_text(
                        strip=True
                    )

                content = extract_content(html)

                # bỏ trang gần như rỗng
                if len(content.split()) < 30:

                    print(
                        f"Skip (too short): {url}"
                    )

                    continue

                results.append(
                    {
                        "url": url,
                        "title": title,
                        "content": content
                    }
                )

                print(
                    f"Done ({len(content.split())} words)"
                )

            except Exception as e:

                print(
                    f"Error crawling {url}"
                )

                print(e)

    finally:

        driver.quit()

    with open(
        "agribank7.jsonl",
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

    print(
        f"\nSaved {len(results)} documents"
    )


if __name__ == "__main__":
    main()