
import json
import logging
import re
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import trafilatura

from bs4 import BeautifulSoup
from readability import Document

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =============================================================================
# CONFIG
# =============================================================================

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

    # --- MỞ RỘNG: Nhóm Tiện ích, Số liệu tài chính & Tra cứu nhanh ---
    "https://www.agribank.com.vn/vn/ty-gia",                         # Bảng tỷ giá ngoại tệ cập nhật hàng ngày
    "https://www.agribank.com.vn/vn/lien-he/mang-luoi-atm",          # Danh sách mạng lưới chi nhánh, PGD và cây ATM
    "https://www.agribank.com.vn/vn/bieu-phi-dich-vu",               # Toàn bộ biểu phí dịch vụ thẻ, tài khoản
    "https://www.agribank.com.vn/vn/cong-cu-tinh-toan",              # Công cụ tính toán lãi tiền gửi và tiền vay

    # --- MỞ RỘNG: Nhóm Khách hàng Cá nhân (Retail Banking) ---
    "https://www.agribank.com.vn/vn/khach-hang-ca-nhan",             # Trang chủ phân hệ khách hàng cá nhân
    "https://www.agribank.com.vn/vn/khach-hang-ca-nhan/tien-gui",     # Các gói tiền gửi tiết kiệm cá nhân
    "https://www.agribank.com.vn/vn/khach-hang-ca-nhan/tin-dung",     # Các gói vay vốn (tiêu dùng, kinh doanh, mua nhà)
    "https://www.agribank.com.vn/vn/khach-hang-ca-nhan/the",          # Thông tin các loại thẻ tín dụng, thẻ ghi nợ
    "https://www.agribank.com.vn/vn/khach-hang-ca-nhan/thanh-toan-chuyen-tien", # Dịch vụ thanh toán nội địa và quốc tế
    "https://www.agribank.com.vn/vn/khach-hang-ca-nhan/ngan-hang-so", # Ứng dụng Agribank Plus, Internet Banking
    "https://www.agribank.com.vn/vn/khach-hang-ca-nhan/bao-hiem",     # Các sản phẩm bảo hiểm liên kết bancassurance
    "https://www.agribank.com.vn/vn/khach-hang-ca-nhan/khuyen-mai",   # Các chương trình ưu đãi, trúng thưởng cho cá nhân

    # --- MỞ RỘNG: Nhóm Khách hàng Doanh nghiệp (Corporate Banking) ---
    "https://www.agribank.com.vn/vn/khach-hang-doanh-nghiep",          # Trang chủ phân hệ doanh nghiệp
    "https://www.agribank.com.vn/vn/khach-hang-doanh-nghiep/tien-gui",  # Quản lý dòng tiền, tiền gửi thanh toán DN
    "https://www.agribank.com.vn/vn/khach-hang-doanh-nghiep/tin-dung",  # Tài trợ thương mại, cho vay thấu chi, vốn lưu động
    "https://www.agribank.com.vn/vn/khach-hang-doanh-nghiep/bao-lanh",  # Dịch vụ bảo lãnh trong nước và quốc tế
    "https://www.agribank.com.vn/vn/khach-hang-doanh-nghiep/thanh-toan-chuyen-tien", # Dịch vụ thanh toán lương, nộp thuế điện tử
    "https://www.agribank.com.vn/vn/khach-hang-doanh-nghiep/the",       # Các dòng thẻ ghi nợ/tín dụng dành cho DN
    "https://www.agribank.com.vn/vn/khach-hang-doanh-nghiep/ngan-hang-so", # Nền tảng Agribank Digital/E-Banking doanh nghiệp

    # --- MỞ RỘNG: Nhóm Định chế Tài chính & Thị trường vốn ---
    "https://www.agribank.com.vn/vn/dinh-che-tai-chinh",              # Cổng thông tin cho các tổ chức tài chính
    "https://www.agribank.com.vn/vn/dinh-che-tai-chinh/ngan-hang-dai-ly", # Hệ thống ngân hàng đại lý toàn cầu
    "https://www.agribank.com.vn/vn/dinh-che-tai-chinh/kinh-doanh-ngoai-te", # Giao dịch thị trường liên ngân hàng, FX, phái sinh

    # --- MỞ RỘNG: Minh bạch thông tin pháp lý & Tài sản thanh lý (Dữ liệu giá trị cao) ---
    "https://www.agribank.com.vn/vn/ve-agribank/cong-bo-thong-tin",   # Công bố thông tin hoạt động, báo cáo quản trị
    "https://www.agribank.com.vn/vn/ve-agribank/bao-cao-tai-chinh",   # Lưu trữ file BCTC kiểm toán các năm (thường có PDF)
    "https://www.agribank.com.vn/vn/ve-agribank/bao-cao-thuong-nien",  # Tải xuống các file Báo cáo thường niên định kỳ
    "https://www.agribank.com.vn/vn/ve-agribank/tai-san-ban-dau-gia", # Danh sách tài sản phát mãi, đấu giá, thu hồi nợ
    "https://www.agribank.com.vn/vn/ve-agribank/dau-thau",            # Thông tin mời thầu, mua sắm vật tư thiết bị công
    "https://www.agribank.com.vn/vn/ve-agribank/phat-trien-ben-vung",  # Báo cáo chiến lược ESG (Môi trường - Xã hội)

    # --- MỞ RỘNG: Trung tâm Truyền thông & Tin tức mở rộng ---
    "https://www.agribank.com.vn/vn/goc-truyen-thong/tin-agribank",   # Tin tức chi tiết về hoạt động toàn hệ thống
    "https://www.agribank.com.vn/vn/goc-truyen-thong/thong-tin-bao-chi", # Các thông cáo báo chí chính thức của ngân hàng
    "https://www.agribank.com.vn/vn/goc-truyen-thong/agribank-vi-cong-dong", # Hoạt động từ thiện, an sinh xã hội
]

OUTPUT_FILE = "agribank10.jsonl"

PAGE_LOAD_WAIT = 10
REQUEST_DELAY = 2
MIN_WORD_COUNT = 50

MAX_RETRIES = 3

DEBUG_DIR = Path("debug_html")


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

log = logging.getLogger("crawler")


# =============================================================================
# DATA MODEL
# =============================================================================

@dataclass
class PageRecord:
    url: str
    title: str
    content: str

    crawled_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    word_count: int = 0

    status: str = "ok"

    def to_jsonl(self):
        return json.dumps(asdict(self), ensure_ascii=False)


# =============================================================================
# CLEANING
# =============================================================================

BLACKLIST_LINES = {
    "Trang chủ",
    "Xem thêm",
    "Đọc thêm",
    "Chi tiết",
    "Tải xuống",
    "Tải về",
    "Điều khoản sử dụng",
    "Chính sách bảo mật",
    "Sơ đồ trang",
    
}

REMOVE_PATTERNS = [
    re.compile(r"^\d+$"),
    re.compile(r"^https?://"),
    re.compile(r"^©"),
    re.compile(r"all rights reserved", re.I),
]


def is_noise(line: str) -> bool:

    if len(line) < 20:
        return True

    if len(line.split()) < 4:
        return True

    if line in BLACKLIST_LINES:
        return True

    for p in REMOVE_PATTERNS:
        if p.search(line):
            return True

    return False


def clean_text(text: str) -> str:

    seen = set()

    cleaned = []

    for line in text.split("\n"):

        line = re.sub(r"\s+", " ", line).strip()

        if not line:
            continue

        if is_noise(line):
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)

        cleaned.append(line)

    return "\n".join(cleaned)


# =============================================================================
# EXTRACTORS
# =============================================================================

REMOVE_SELECTORS = [
    "header",
    "footer",
    "nav",
    "aside",

    ".navbar",
    ".menu",
    ".sidebar",
    ".breadcrumb",

    ".footer",
    ".header",
    ".navigation",

    ".social-share",
    ".related-posts",
]


def bs4_cleanup(html: str) -> str:

    soup = BeautifulSoup(html, "lxml")

    for selector in REMOVE_SELECTORS:

        for el in soup.select(selector):
            el.decompose()

    return str(soup)


def extract_with_trafilatura(html: str) -> Optional[str]:

    try:

        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )

        return text

    except Exception:
        return None


def extract_with_readability(html: str) -> Optional[str]:

    try:

        doc = Document(html)

        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "lxml")

        text = soup.get_text("\n", strip=True)

        return text

    except Exception:
        return None


def extract_main_content(html: str) -> str:

    html = bs4_cleanup(html)

    # -------------------------------------------------------------------------
    # METHOD 1: TRAFILATURA
    # -------------------------------------------------------------------------

    text = extract_with_trafilatura(html)

    if text and len(text.split()) > 50:

        return clean_text(text)

    # -------------------------------------------------------------------------
    # METHOD 2: READABILITY
    # -------------------------------------------------------------------------

    text = extract_with_readability(html)

    if text and len(text.split()) > 50:

        return clean_text(text)

    # -------------------------------------------------------------------------
    # METHOD 3: FALLBACK BS4
    # -------------------------------------------------------------------------

    soup = BeautifulSoup(html, "lxml")

    main = (
        soup.select_one("main")
        or soup.select_one("article")
        or soup.select_one(".content")
        or soup.body
    )

    if not main:
        return ""

    text = main.get_text("\n", strip=True)

    return clean_text(text)


# =============================================================================
# VALIDATION
# =============================================================================

ERROR_PATTERNS = [
    "403 forbidden",
    "404 not found",
    "access denied",
    "enable javascript",
    "cloudflare",
]


def validate_content(text: str):

    if not text:
        return False, "empty"

    if len(text.split()) < MIN_WORD_COUNT:
        return False, "too_short"

    lower = text.lower()

    for e in ERROR_PATTERNS:

        if e in lower:
            return False, "blocked"

    return True, "ok"


# =============================================================================
# SELENIUM
# =============================================================================

def build_driver(headless=True):

    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")

    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument("--no-sandbox")

    options.add_argument("--disable-dev-shm-usage")

    options.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def fetch_page(driver, url):

    driver.get(url)

    WebDriverWait(driver, PAGE_LOAD_WAIT).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    time.sleep(3)

    return driver.title, driver.page_source


# =============================================================================
# CRAWLER
# =============================================================================

def crawl_page(driver, url, idx):

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            log.info(f"[{idx}] Fetching {url}")

            title, html = fetch_page(driver, url)

            DEBUG_DIR.mkdir(exist_ok=True)

            debug_path = DEBUG_DIR / f"page_{idx}.html"

            debug_path.write_text(html, encoding="utf-8")

            content = extract_main_content(html)

            ok, reason = validate_content(content)

            if not ok:

                log.warning(f"[{idx}] Skip: {reason}")

                return None

            record = PageRecord(
                url=url,
                title=title,
                content=content,
                word_count=len(content.split()),
            )

            log.info(
                f"[{idx}] OK | {record.word_count} words"
            )

            return record

        except Exception as e:

            log.error(
                f"[{idx}] Attempt {attempt} failed: {e}"
            )

            time.sleep(3)

    return None


# =============================================================================
# PIPELINE
# =============================================================================

def run_pipeline():

    driver = build_driver(headless=True)

    output = Path(OUTPUT_FILE)

    saved = 0

    try:

        with output.open("w", encoding="utf-8") as f:

            for idx, url in enumerate(URLS, 1):

                record = crawl_page(driver, url, idx)

                if not record:
                    continue

                f.write(record.to_jsonl() + "\n")

                f.flush()

                saved += 1

                time.sleep(REQUEST_DELAY)

    finally:

        driver.quit()

    log.info(f"Saved: {saved}")


# =============================================================================
# ENTRY
# =============================================================================

if __name__ == "__main__":

    run_pipeline()