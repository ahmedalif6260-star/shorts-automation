import requests
import urllib.parse

# Read the trending topic
with open("topic.txt", "r", encoding="utf-8") as f:
    topic = f.read().strip()

if not topic:
    raise Exception("No topic found")

print("================================")
print("TRENDING TOPIC:")
print(topic)
print("================================")

# Search Wikipedia for information about the topic
search_url = "https://en.wikipedia.org/w/api.php"

params = {
    "action": "query",
    "list": "search",
    "srsearch": topic,
    "format": "json",
    "utf8": 1,
    "srlimit": 3
}

response = requests.get(search_url, params=params, timeout=30)
response.raise_for_status()

data = response.json()
results = data.get("query", {}).get("search", [])

if not results:
    summary = f"People are currently searching for {topic}."
else:
    page_title = results[0]["title"]

    summary_params = {
        "action": "query",
        "prop": "extracts",
        "exintro": 1,
        "explaintext": 1,
        "titles": page_title,
        "format": "json",
        "formatversion": 2
    }

    summary_response = requests.get(
        search_url,
        params=summary_params,
        timeout=30
    )

    summary_response.raise_for_status()

    summary_data = summary_response.json()
    pages = summary_data.get("query", {}).get("pages", [])

    if pages and pages[0].get("extract"):
        summary = pages[0]["extract"]
    else:
        summary = f"People are currently searching for {topic}."

# Keep the script short
summary = summary.replace("\n", " ").strip()

if len(summary) > 900:
    summary = summary[:900]

# Create Shorts script
script = f"""
HOOK:
Here is what you need to know about {topic}.

MAIN STORY:
{summary}

ENDING:
Follow for more quick updates and interesting stories.
"""

with open("script.txt", "w", encoding="utf-8") as f:
    f.write(script)

print("================================")
print("SCRIPT CREATED SUCCESSFULLY")
print("Topic:", topic)
print("================================")
print(script)
