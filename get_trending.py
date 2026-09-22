import requests
import xml.etree.ElementTree as ET

URL = "https://trends.google.com/trending/rss?geo=US"

response = requests.get(URL, timeout=30)
response.raise_for_status()

root = ET.fromstring(response.text)

items = root.findall(".//item")

print("================================")
print("USA TRENDING TOPICS")
print("================================")

for i, item in enumerate(items[:10], 1):
    title = item.findtext("title")

    if title:
        print(f"{i}. {title}")

print("================================")
