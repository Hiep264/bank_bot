import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import json

BASE_URL = "https://www.agribank.com.vn"

visited = set()
queue = deque(["https://www.agribank.com.vn"])

documents = []

while queue:
    url = queue.popleft()

    if url in visited:
        continue

    visited.add(url)

    try:
        print("Crawling:", url)

        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        if r.status_code != 200:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.get_text(strip=True) if soup.title else ""

        content = soup.get_text("\n", strip=True)

        documents.append({
            "url": url,
            "title": title,
            "content": content
        })

        for link in soup.find_all("a", href=True):
            href = link["href"]

            full_url = urljoin(BASE_URL, href)

            parsed = urlparse(full_url)

            if "agribank.com.vn" in parsed.netloc:
                full_url = parsed.scheme + "://" + parsed.netloc + parsed.path

                if full_url not in visited:
                    queue.append(full_url)

    except Exception as e:
        print(e)

with open("agribank2.jsonl", "w", encoding="utf-8") as f:
    for doc in documents:
        f.write(json.dumps(doc, ensure_ascii=False) + "\n")