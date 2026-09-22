import requests
import os

# Read trending topic
with open("topic.txt", "r", encoding="utf-8") as f:
    topic = f.read().strip()

if not topic:
    raise Exception("No topic found")

print("Searching visual for:", topic)

headers = {
    "User-Agent": "ShortsAutomation/1.0"
}

url = "https://commons.wikimedia.org/w/api.php"

params = {
    "action": "query",
    "generator": "search",
    "gsrsearch": topic,
    "gsrnamespace": 6,
    "gsrlimit": 5,
    "prop": "imageinfo",
    "iiprop": "url",
    "iiurlwidth": 1080,
    "format": "json"
}

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

# Take first result
page = list(pages.values())[0]

imageinfo = page.get("imageinfo", [])

if not imageinfo:
    raise Exception("No image information found")

image_url = imageinfo[0].get("thumburl") or imageinfo[0].get("url")

if not image_url:
    raise Exception("No image URL found")

os.makedirs("visuals", exist_ok=True)

image_response = requests.get(
    image_url,
    headers=headers,
    timeout=30
)

image_response.raise_for_status()

with open("visuals/topic.jpg", "wb") as f:
    f.write(image_response.content)

print("================================")
print("VISUAL FOUND SUCCESSFULLY")
print("Topic:", topic)
print("Saved: visuals/topic.jpg")
print("================================")
