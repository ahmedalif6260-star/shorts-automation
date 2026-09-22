import requests
import xml.etree.ElementTree as ET

URL = "https://trends.google.com/trending/rss?geo=US"

response = requests.get(URL, timeout=30)
response.raise_for_status()

root = ET.fromstring(response.text)

items = root.findall(".//item")

topics = []

for item in items:
    title = item.findtext("title")

    if title:
        topics.append(title.strip())

print("================================")
print("USA TRENDING TOPICS")
print("================================")

for i, topic in enumerate(topics[:10], 1):
    print(f"{i}. {topic}")

if not topics:
    raise Exception("No trending topics found")

# Select the first trending topic
selected_topic = topics[0]

with open("topic.txt", "w", encoding="utf-8") as f:
    f.write(selected_topic)

print("================================")
print("SELECTED TOPIC:")
print(selected_topic)
print("================================")
