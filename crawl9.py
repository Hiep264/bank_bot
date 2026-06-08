"""
Agribank Crawl Pipeline
=======================
Một script khép kín: crawl → extract → clean → validate → save
Không cần xử lý file JSON trung gian.

Yêu cầu:
    pip install selenium beautifulsoup4 lxml

Cách chạy:
    python agribank_pipeline.py                  # chạy toàn bộ
    python agribank_pipeline.py --no-headless    # mở browser (debug)
    python agribank_pipeline.py --output out.jsonl
"""

import argparse
import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

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

PAGE_LOAD_WAIT   = 8     # giây chờ JS render
MIN_WORD_COUNT   = 30    # bản ghi hợp lệ tối thiểu
MAX_RETRIES      = 2     # số lần retry nếu trang lỗi
OUTPUT_FILE      = "agribank9.jsonl"
DEBUG_HTML_DIR   = Path("debug_html")

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("agribank")

# ─────────────────────────────────────────────────────────────────────────────
# DATA MODEL
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PageRecord:
    url:        str
    title:      str
    content:    str
    crawled_at: str = field(default_factory=lambda: datetime.now().isoformat())
    word_count: int = 0
    status:     str = "ok"           # ok | skip_short | skip_error | skip_blocked

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

# ─────────────────────────────────────────────────────────────────────────────
# CLEANER
# ─────────────────────────────────────────────────────────────────────────────

# Các dòng thuộc nav / menu / footer
_NAV_BLACKLIST: set[str] = {
    "Cá nhân", "Doanh nghiệp", "Định chế tài chính",
    "Về Agribank", "Tin tức", "Tuyển dụng", "Hỗ trợ",
    "Công cụ tiện ích", "Liên hệ", "Về chúng tôi",
    "Công bố thông tin", "Thư viện Agribank", "Tài sản bán đấu giá",
    "Agribank Plus", "khách hàng", "cá nhân",
    "Trang chủ", "Sơ đồ trang web", "Điều khoản sử dụng",
    "Chính sách bảo mật", "Câu hỏi thường gặp",
    "Web Content Viewer", "Component Action Menu", "Actions", "{}",
    "Xem thêm", "Chi tiết", "Đọc thêm", "Tải về",
}

# Patterns loại bỏ dòng nhiễu
_REMOVE_RE: list[re.Pattern] = [
    re.compile(r"Z\d+_[A-Z0-9_]+"),                   # Liferay portlet ID
    re.compile(r"\$\{.*?\}"),                          # Template placeholder
    re.compile(r"^1900[\s\d]{6,}"),                    # Hotline 1900
    re.compile(r"^0\d{9}$"),                           # SĐT di động
    re.compile(r"^02\d[\s\d]{7,}$"),                   # SĐT cố định
    re.compile(r"^©.*$", re.IGNORECASE),               # Copyright
    re.compile(r"^All rights reserved", re.IGNORECASE),
    re.compile(r"^https?://\S+$"),                     # URL đơn độc
    re.compile(r"^\W{1,3}$"),                          # Chỉ ký tự đặc biệt
]

_BREADCRUMB_SEP = re.compile(r"\s*[/›»>|]\s*")


def _is_breadcrumb(line: str) -> bool:
    """Nhận diện dòng breadcrumb: A / B / C"""
    parts = _BREADCRUMB_SEP.split(line)
    return len(parts) >= 3 and all(len(p.strip()) < 50 for p in parts)


def clean_text(raw: str) -> str:
    """
    Làm sạch text: loại nav, breadcrumb, hotline, trùng lặp.
    Trả về nội dung thuần tuý.
    """
    seen: set[str] = set()
    result: list[str] = []

    for line in raw.split("\n"):
        line = line.strip()

        if not line or len(line) < 3:
            continue

        if line in _NAV_BLACKLIST:
            continue

        if _is_breadcrumb(line):
            continue

        if any(p.search(line) for p in _REMOVE_RE):
            continue

        key = line.lower()
        if key in seen:
            continue
        seen.add(key)

        result.append(line)

    return "\n".join(result)

# ─────────────────────────────────────────────────────────────────────────────
# EXTRACTOR  (HTML → plain text)
# ─────────────────────────────────────────────────────────────────────────────

# CSS selectors ưu tiên lấy vùng nội dung chính
_CONTENT_SELECTORS = [
    "main",
    "article",
    "[role='main']",
    ".content",
    ".main-content",
    "#content",
    ".portal-content",
    ".portlet-body",
]

# Tags cần xoá trước khi lấy text
_STRIP_TAGS = [
    "script", "style", "noscript",
    "header", "footer", "nav", "aside",
    "form", "button", "input",
    # Agribank-specific boilerplate
    ".nav", ".navbar", ".menu", ".breadcrumb",
    ".footer", ".header", ".sidebar",
    ".portlet-topper",              # Liferay portlet header
    ".portlet-title",
]


def extract_main_content(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # Xoá tags không cần thiết
    for tag in soup(["script", "style", "noscript",
                     "header", "footer", "nav", "aside",
                     "form", "button"]):
        tag.decompose()

    # Xoá theo class/id đặc trưng Agribank / Liferay
    for selector in [".portlet-topper", ".portlet-title",
                     ".nav", ".navbar", ".breadcrumb",
                     ".footer", ".header", ".sidebar",
                     "#navigation", "#footer", "#header"]:
        for el in soup.select(selector):
            el.decompose()

    # Tìm vùng nội dung chính
    content_el = None
    for sel in _CONTENT_SELECTORS:
        content_el = soup.select_one(sel)
        if content_el:
            break

    target = content_el or soup.body or soup

    raw = target.get_text("\n", strip=True)
    return clean_text(raw)

# ─────────────────────────────────────────────────────────────────────────────
# VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────

_ERROR_SIGNALS = [
    "javascript is disabled",
    "enable javascript",
    "access denied",
    "403 forbidden",
    "404 not found",
    "cloudflare",
    "ddos protection",
]


def is_blocked_page(text: str) -> bool:
    t = text.lower()
    return any(s in t for s in _ERROR_SIGNALS)


def validate(record: PageRecord) -> tuple[bool, str]:
    """
    Trả về (ok: bool, reason: str).
    ok=False → bỏ qua bản ghi.
    """
    if is_blocked_page(record.content):
        return False, "blocked/error page"

    if record.word_count < MIN_WORD_COUNT:
        return False, f"too short ({record.word_count} words)"

    # Tỷ lệ ASCII quá cao → nội dung JS bị rò
    ascii_ratio = sum(c.isascii() for c in record.content) / max(len(record.content), 1)
    if ascii_ratio > 0.97 and record.word_count < 100:
        return False, f"likely JS garbage (ascii_ratio={ascii_ratio:.2f})"

    return True, ""

# ─────────────────────────────────────────────────────────────────────────────
# SELENIUM DRIVER
# ─────────────────────────────────────────────────────────────────────────────

def build_driver(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=opts)
    # Ẩn webdriver fingerprint
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def fetch_page(driver: webdriver.Chrome, url: str) -> tuple[str, str]:
    """
    Load trang, chờ body xuất hiện, trả về (title, html).
    """
    driver.get(url)
    try:
        WebDriverWait(driver, PAGE_LOAD_WAIT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception:
        pass
    # Thêm delay nhỏ cho JS render xong
    time.sleep(3)

    return driver.title, driver.page_source

# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def crawl_url(driver: webdriver.Chrome, url: str, index: int) -> Optional[PageRecord]:
    """
    Crawl 1 URL, trả về PageRecord hoặc None nếu thất bại hoàn toàn.
    Thử lại tối đa MAX_RETRIES lần.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.info(f"[{index}] Fetching (attempt {attempt}): {url}")
            title, html = fetch_page(driver, url)

            # Lưu HTML debug
            debug_path = DEBUG_HTML_DIR / f"page_{index}.html"
            debug_path.write_text(html, encoding="utf-8")

            content = extract_main_content(html)
            word_count = len(content.split())

            record = PageRecord(
                url=url,
                title=title,
                content=content,
                word_count=word_count,
            )

            ok, reason = validate(record)
            if not ok:
                record.status = f"skip_{reason.split()[0]}"
                log.warning(f"[{index}] SKIP — {reason}: {url}")
                # Chỉ retry nếu bị block (có thể tạm thời)
                if "blocked" in reason and attempt < MAX_RETRIES:
                    log.info(f"[{index}] Retry sau 5 giây...")
                    time.sleep(5)
                    continue
                return record  # trả về để ghi log, không save

            raw_size = len(html.split())
            log.info(
                f"[{index}] OK — {word_count} words "
                f"(từ {raw_size} HTML words, "
                f"-{round((1-word_count/max(raw_size,1))*100)}%): {url}"
            )
            return record

        except Exception as e:
            log.error(f"[{index}] Lỗi attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(3)

    log.error(f"[{index}] Bỏ qua sau {MAX_RETRIES} lần thất bại: {url}")
    return None


def run_pipeline(headless: bool = True, output: str = OUTPUT_FILE):
    DEBUG_HTML_DIR.mkdir(exist_ok=True)
    output_path = Path(output)

    log.info("=" * 60)
    log.info(f"Agribank Pipeline — {len(URLS)} URLs")
    log.info(f"Output: {output_path}")
    log.info("=" * 60)

    driver = build_driver(headless=headless)

    saved = 0
    skipped = 0
    failed = 0

    with output_path.open("w", encoding="utf-8") as fout:
        try:
            for i, url in enumerate(URLS, 1):
                record = crawl_url(driver, url, i)

                if record is None:
                    failed += 1
                    continue

                if record.status != "ok":
                    skipped += 1
                    continue

                fout.write(record.to_jsonl() + "\n")
                fout.flush()   # ghi ngay, không mất dữ liệu nếu crash
                saved += 1

                # Delay lịch sự giữa các request
                if i < len(URLS):
                    time.sleep(2)

        finally:
            driver.quit()

    log.info("=" * 60)
    log.info(f"Hoàn tất: {saved} saved | {skipped} skipped | {failed} failed")
    log.info(f"Output:   {output_path.resolve()}")
    log.info(f"Debug:    {DEBUG_HTML_DIR.resolve()}")
    log.info("=" * 60)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agribank crawl pipeline")
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Mở browser (dùng để debug)",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_FILE,
        help=f"File output JSONL (default: {OUTPUT_FILE})",
    )
    args = parser.parse_args()

    run_pipeline(
        headless=not args.no_headless,
        output=args.output,
    )