import requests
import os
from PIL import Image, ImageDraw, ImageFont

# =========================
# READ TOPIC
# =========================

with open("topic.txt", "r", encoding="utf-8") as f:
    topic = f.read().strip()

if not topic:
    raise Exception("No topic found")

print("================================")
print("Searching visual for:", topic)
print("================================")

os.makedirs("visuals", exist_ok=True)

# =========================
# HEADERS
# =========================

headers = {
    "User-Agent": "ShortsAutomation/1.0 (GitHub Actions)"
}

image_url = None

# =========================
# 1. WIKIMEDIA COMMONS
# =========================

try:

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

    for page in pages.values():

        info = page.get("imageinfo", [])

        if info:

            image_url = (
                info[0].get("thumburl")
                or info[0].get("url")
            )

            if image_url:
                print("Wikimedia image found")
                break

except Exception as e:

    print("Wikimedia search failed:", e)


# =========================
# 2. WIKIPEDIA IMAGE
# =========================

if not image_url:

    try:

        print("Trying Wikipedia image...")

        wiki_url = "https://en.wikipedia.org/w/api.php"

        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": topic,
            "srlimit": 3,
            "format": "json"
        }

        search_response = requests.get(
            wiki_url,
            params=search_params,
            headers=headers,
            timeout=30
        )

        search_response.raise_for_status()

        search_data = search_response.json()

        results = (
            search_data
            .get("query", {})
            .get("search", [])
        )

        if results:

            page_title = results[0]["title"]

            image_params = {
                "action": "query",
                "prop": "pageimages",
                "titles": page_title,
                "pithumbsize": 1080,
                "format": "json"
            }

            image_response = requests.get(
                wiki_url,
                params=image_params,
                headers=headers,
                timeout=30
            )

            image_response.raise_for_status()

            image_data = image_response.json()

            pages = (
                image_data
                .get("query", {})
                .get("pages", {})
            )

            for page in pages.values():

                thumbnail = page.get("thumbnail", {})

                if thumbnail.get("source"):

                    image_url = thumbnail["source"]

                    print("Wikipedia image found")
                    break

    except Exception as e:

        print("Wikipedia image search failed:", e)


# =========================
# 3. DOWNLOAD IMAGE
# =========================

if image_url:

    try:

        print("Downloading visual...")

        image_headers = {
            "User-Agent": "ShortsAutomation/1.0",
            "Accept": "image/*"
        }

        image_response = requests.get(
            image_url,
            headers=image_headers,
            timeout=60
        )

        image_response.raise_for_status()

        content_type = image_response.headers.get(
            "content-type",
            ""
        )

        if "image" not in content_type.lower():

            raise Exception("Downloaded file is not an image")

        with open(
            "visuals/topic.jpg",
            "wb"
        ) as f:

            f.write(image_response.content)

        # Verify image
        test_image = Image.open(
            "visuals/topic.jpg"
        )

        test_image.verify()

        print("================================")
        print("VISUAL FOUND SUCCESSFULLY")
        print("Topic:", topic)
        print("Saved: visuals/topic.jpg")
        print("================================")

    except Exception as e:

        print("Image download failed:", e)

        image_url = None


# =========================
# 4. FALLBACK VISUAL
# =========================

if not image_url:

    print("No online image found.")
    print("Creating fallback visual...")

    W = 1080
    H = 1920

    img = Image.new(
        "RGB",
        (W, H),
        (25, 25, 30)
    )

    draw = ImageDraw.Draw(img)

    # Try several fonts
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]

    font_path = None

    for path in font_paths:

        if os.path.exists(path):

            font_path = path
            break

    if font_path:

        title_font = ImageFont.truetype(
            font_path,
            72
        )

        topic_font = ImageFont.truetype(
            font_path,
            48
        )

    else:

        title_font = None
        topic_font = None

    # Background shapes
    draw.rectangle(
        (0, 0, W, H),
        fill=(20, 24, 32)
    )

    draw.ellipse(
        (-300, 200, 700, 1200),
        fill=(45, 55, 80)
    )

    draw.ellipse(
        (500, 900, 1400, 1900),
        fill=(55, 45, 75)
    )

    title = "TRENDING NOW"

    if title_font:

        box = draw.textbbox(
            (0, 0),
            title,
            font=title_font
        )

        title_width = box[2] - box[0]

        draw.text(
            (
                (W - title_width) / 2,
                550
            ),
            title,
            fill="white",
            font=title_font
        )

    if topic_font:

        words = topic.split()

        lines = []

        line = ""

        for word in words:

            test = (
                line + " " + word
            ).strip()

            box = draw.textbbox(
                (0, 0),
                test,
                font=topic_font
            )

            if box[2] - box[0] < 850:

                line = test

            else:

                if line:
                    lines.append(line)

                line = word

        if line:
            lines.append(line)

        y = 800

        for line in lines[:5]:

            box = draw.textbbox(
                (0, 0),
                line,
                font=topic_font
            )

            width = box[2] - box[0]

            draw.text(
                (
                    (W - width) / 2,
                    y
                ),
                line,
                fill="white",
                font=topic_font
            )

            y += 80

    img.save(
        "visuals/topic.jpg",
        quality=95
    )

    print("================================")
    print("FALLBACK VISUAL CREATED")
    print("Topic:", topic)
    print("Saved: visuals/topic.jpg")
    print("================================")
