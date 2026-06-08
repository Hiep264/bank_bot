"""
Agribank Website Crawler
Crawl thông tin sơ bộ từ các trang chính của agribank.com.vn

Lưu ý: Trang Agribank chặn bot cơ bản (HTTP 403).
Script này có 2 chế độ:
  1. requests + header nâng cao (nhanh, đôi khi bị chặn)
  2. Selenium (chậm hơn nhưng vượt được anti-bot cơ bản)

Cài đặt:
  pip install requests beautifulsoup4 selenium webdriver-manager
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import argparse

BASE_URL = "https://www.agribank.com.vn"

# ── Headers giả trình duyệt thật ─────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "Referer": "https://www.google.com/",
}

# ── Danh sách các trang chính cần crawl ──────────────────────────────────────
MAIN_PAGES = {
    "home": "/vn/home",
    "ve_agribank": "/vn/ve-agribank2",
    "ca_nhan": "/vn/ca-nhan",
    "doanh_nghiep": "/vn/doanh-nghiep",
    "dinh_che_tai_chinh": "/vn/dinh-che-tai-chinh",
    "tin_tuc": "/vn/ve-agribank/tin-tuc",
    "lai_suat_gui": "/vn/lai-suat",
    "lai_suat_cho_vay": "/vn/lai-suat-cho-vay-agribank",
    "ty_gia": "/vn/ty-gia",
    "gia_vang": "/vn/gia-vang",
    "bieu_phi": "/vn/bieu-phi",
    "tuyen_dung": "/vn/tuyen-dung",
    "lien_he": "/vn/lien-he",
    "atm_chi_nhanh": "/vn/atm-chi-nhanh",
    "ngan_hang_so": "/vn/ca-nhan/san-pham/ngan-hang-so",
}


# ══════════════════════════════════════════════════════════════════════════════
# CHẾ ĐỘ 1: requests (không cần trình duyệt)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_with_requests(path: str) -> BeautifulSoup | None:
    url = BASE_URL + path
    session = requests.Session()
    # Lấy cookie bằng cách ghé thăm trang chủ trước
    try:
        session.get(BASE_URL, headers=HEADERS, timeout=15)
        time.sleep(random.uniform(0.5, 1.5))
        resp = session.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
        print(f"  [WARN] HTTP {resp.status_code} — {url}")
        return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# CHẾ ĐỘ 2: Selenium (dành cho khi bị 403 liên tục)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_with_selenium(path: str, driver=None) -> BeautifulSoup | None:
    """Dùng Selenium headless Chrome để vượt anti-bot."""
    url = BASE_URL + path
    try:
        driver.get(url)
        time.sleep(random.uniform(2, 4))          # Chờ JS render
        html = driver.page_source
        return BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"  [ERROR Selenium] {e}")
        return None


def create_selenium_driver():
    """Khởi tạo Chrome headless."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


# ══════════════════════════════════════════════════════════════════════════════
# TRÍCH XUẤT DỮ LIỆU
# ══════════════════════════════════════════════════════════════════════════════

def extract_info(soup: BeautifulSoup, page_key: str) -> dict:
    info = {
        "page": page_key,
        "url": BASE_URL + MAIN_PAGES[page_key],
        "crawled_at": datetime.now().isoformat(),
        "title": "",
        "meta_description": "",
        "headings": [],
        "nav_links": [],
        "content_links": [],
        "text_preview": "",
        "tables_found": 0,
    }

    # Title
    t = soup.find("title")
    info["title"] = t.get_text(strip=True) if t else ""

    # Meta description
    m = soup.find("meta", attrs={"name": "description"})
    if m:
        info["meta_description"] = m.get("content", "")

    # Headings h1–h3
    seen_h = set()
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 2 and text not in seen_h:
            seen_h.add(text)
            info["headings"].append(text)
    info["headings"] = info["headings"][:20]

    # Nav links (menu)
    nav = soup.find("nav")
    if nav:
        for a in nav.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if text and href.startswith("/vn/"):
                info["nav_links"].append({"text": text, "url": BASE_URL + href})
    info["nav_links"] = info["nav_links"][:20]

    # Content links
    seen_l = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if (
            (href.startswith("/vn/") or href.startswith("http"))
            and text
            and len(text) > 3
            and href not in seen_l
        ):
            seen_l.add(href)
            url = href if href.startswith("http") else BASE_URL + href
            info["content_links"].append({"text": text, "url": url})
    info["content_links"] = info["content_links"][:30]

    # Text preview
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > 60:
            info["text_preview"] = text[:400]
            break

    # Số bảng (hữu ích cho lãi suất, tỷ giá)
    info["tables_found"] = len(soup.find_all("table"))

    return info


# ══════════════════════════════════════════════════════════════════════════════
# HÀM CRAWL CHÍNH
# ══════════════════════════════════════════════════════════════════════════════

def crawl_all(use_selenium: bool = False) -> list[dict]:
    results = []
    driver = None

    if use_selenium:
        print("🌐 Khởi động Chrome headless...\n")
        try:
            driver = create_selenium_driver()
        except Exception as e:
            print(f"[ERROR] Không thể khởi động Selenium: {e}")
            print("Quay về chế độ requests...\n")
            use_selenium = False

    total = len(MAIN_PAGES)
    for i, (key, path) in enumerate(MAIN_PAGES.items(), 1):
        print(f"[{i}/{total}] ▶ {key:25s} {path}")
        if use_selenium and driver:
            soup = fetch_with_selenium(path, driver)
        else:
            soup = fetch_with_requests(path)

        if soup:
            data = extract_info(soup, key)
            results.append(data)
            title_short = (data["title"] or "(no title)")[:55]
            print(f"         ✓ {title_short}")
            print(f"           headings={len(data['headings'])} | links={len(data['content_links'])} | tables={data['tables_found']}")
        else:
            results.append({
                "page": key,
                "url": BASE_URL + path,
                "crawled_at": datetime.now().isoformat(),
                "error": "Failed to fetch (HTTP 403 or timeout)",
                "suggestion": "Thử chạy lại với --selenium hoặc dùng VPN/proxy",
            })
            print(f"         ✗ FAILED")

        # Delay ngẫu nhiên tránh bị block
        delay = random.uniform(2.0, 4.0) if use_selenium else random.uniform(1.0, 2.5)
        time.sleep(delay)

    if driver:
        driver.quit()

    return results


def save_results(results: list[dict], filename: str = "agribank_data.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Đã lưu kết quả → {filename}")


def print_summary(results: list[dict]):
    ok = [r for r in results if "error" not in r]
    fail = [r for r in results if "error" in r]
    print("\n" + "═" * 60)
    print(f"  TỔNG KẾT  ✓ {len(ok)} trang  ✗ {len(fail)} trang")
    print("═" * 60)
    for r in ok:
        print(f"\n📄 {r['page']}")
        print(f"   Title   : {r.get('title','')[:65]}")
        hs = r.get("headings", [])[:3]
        print(f"   Headings: {hs}")
        print(f"   Links   : {len(r.get('content_links',[]))} | Tables: {r.get('tables_found',0)}")
    if fail:
        print("\n❌ Trang bị lỗi:")
        for r in fail:
            print(f"   - {r['page']}: {r.get('error')}")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agribank Crawler")
    parser.add_argument(
        "--selenium", action="store_true",
        help="Dùng Selenium headless Chrome (vượt anti-bot tốt hơn, cần cài chromedriver)"
    )
    parser.add_argument(
        "--output", default="agribank_data.json",
        help="File JSON đầu ra (mặc định: agribank_data.json)"
    )
    args = parser.parse_args()

    print("🚀 Bắt đầu crawl Agribank\n")
    if not args.selenium:
        print("💡 Tip: Nếu bị 403, chạy lại với: python agribank_crawler.py --selenium\n")

    results = crawl_all(use_selenium=args.selenium)
    print_summary(results)
    save_results(results, args.output)