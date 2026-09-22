import requests
import os
import time

with open("topic.txt", "r", encoding="utf-8") as f:
    topic = f.read().strip()

if not topic:
    raise Exception("No topic found")

print("Searching visual for:", topic)

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; ShortsAutomation/1.0)"
}

url = "https://commons.wikimedia.org/w/api.php"

params = {
    "action": "query",
    "generator": "search",
    "gsrsearch": topic,
    "gsrnamespace": 6,
    "gsrlimit": 3,
    "prop": "imageinfo",
    "iiprop": "url",
    "iiurlwidth": 1080,
    "format": "json"
}

# Search Wikimedia
response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=30
)

response.raise_for_status()

data = response.json()
pages = data.get("query", {}).get("pages", {})

if not pages:
    raise Exception("No visual found for this topic")

image_url = None

for page in pages.values():
    info = page.get("imageinfo", [])

    if info:
        image_url = info[0].get("thumburl") or info[0].get("url")
        if image_url:
            break

if not image_url:
    raise Exception("No image URL found")

print("Visual URL found")

os.makedirs("visuals", exist_ok=True)

# Wait briefly before downloading
time.sleep(3)

image_headers = {
    "User-Agent": "Mozilla/5.0 (compatible; ShortsAutomation/1.0)",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
}

image_response = requests.get(
    image_url,
    headers=image_headers,
    timeout=60
)

if image_response.status_code == 429:
    raise Exception(
        "Wikimedia rate limit reached. Please run the workflow again later."
    )

image_response.raise_for_status()

with open("visuals/topic.jpg", "wb") as f:
    f.write(image_response.content)

print("================================")
print("VISUAL FOUND SUCCESSFULLY")
print("Topic:", topic)
print("Saved: visuals/topic.jpg")
print("================================")
