import requests
import os
import time
import re

with open("topic.txt", "r", encoding="utf-8") as f:
    topic = f.read().strip()

if not topic:
    raise Exception("No topic found")

print("Searching visual for:", topic)

headers = {
    "User-Agent": "ShortsAutomation/1.0 (GitHub Actions)"
}

commons_url = "https://commons.wikimedia.org/w/api.php"

def search_commons(query):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": 5,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 1080,
        "format": "json"
    }

    r = requests.get(
        commons_url,
        params=params,
        headers=headers,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()
    pages = data.get("query", {}).get("pages", {})

    for page in pages.values():
        info = page.get("imageinfo", [])

        if info:
            image_url = info[0].get("thumburl") or info[0].get("url")

            if image_url:
                return image_url

    return None


# 1. Exact topic search
image_url = search_commons(topic)

# 2. Simplified topic search
if not image_url:
    words = re.findall(r"[A-Za-z0-9]+", topic)

    stop_words = {
        "the", "and", "for", "with", "update",
        "latest", "news", "today", "what", "about"
    }

    important_words = [
        word for word in words
        if word.lower() not in stop_words
    ]

    simplified = " ".join(important_words[:4])

    if simplified:
        print("Trying simplified search:", simplified)
        time.sleep(2)
        image_url = search_commons(simplified)


# 3. Wikipedia thumbnail fallback
if not image_url:
    print("Trying Wikipedia image fallback...")

    wiki_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": topic,
        "gsrlimit": 1,
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": 1080,
        "format": "json"
    }

    r = requests.get(
        wiki_url,
        params=params,
        headers=headers,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()
    pages = data.get("query", {}).get("pages", {})

    for page in pages.values():
        thumbnail = page.get("thumbnail", {})
        image_url = thumbnail.get("source")

        if image_url:
            break


if not image_url:
    raise Exception("No visual found for this topic")


print("Visual URL found:")
print(image_url)

os.makedirs("visuals", exist_ok=True)

time.sleep(2)

image_headers = {
    "User-Agent": "ShortsAutomation/1.0 (GitHub Actions)"
}

image_response = requests.get(
    image_url,
    headers=image_headers,
    timeout=60
)

if image_response.status_code == 429:
    raise Exception(
        "Visual source rate limit reached. Please run again later."
    )

image_response.raise_for_status()

with open("visuals/topic.jpg", "wb") as f:
    f.write(image_response.content)

print("================================")
print("VISUAL FOUND SUCCESSFULLY")
print("Topic:", topic)
print("Saved: visuals/topic.jpg")
print("================================")
