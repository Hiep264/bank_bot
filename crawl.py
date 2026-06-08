import requests
from bs4 import BeautifulSoup
import json

url = "https://www.agribank.com.vn/vn/ve-agribank2"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

title = soup.title.get_text(strip=True)

text = soup.get_text("\n", strip=True)

data = {
    "url": url,
    "title": title,
    "content": text
}

with open("agribank.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done")