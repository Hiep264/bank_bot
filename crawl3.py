import requests
from bs4 import BeautifulSoup

xml = requests.get(
    "https://www.agribank.com.vn/sitemap.xml"
).text

soup = BeautifulSoup(xml, "xml")

urls = [loc.text for loc in soup.find_all("loc")]

print(len(urls))