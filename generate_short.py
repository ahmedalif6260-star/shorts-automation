import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

os.makedirs("output", exist_ok=True)
os.makedirs("frames", exist_ok=True)

W, H = 1080, 1920

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title_font = ImageFont.truetype(font_path, 72)
big_font = ImageFont.truetype(font_path, 58)
small_font = ImageFont.truetype(font_path, 38)

# Get topic from GitHub Actions
topic = os.environ.get("SHORT_TOPIC", "").strip()

if not topic:
    topic = "Human Brain"

# Topic content
topics = {
    "human brain": [
        ("FACT #1", "20% OF YOUR ENERGY",
         "Your brain uses about 20% of your body's energy."),
        ("FACT #2", "86 BILLION NEURONS",
         "Your brain contains around 86 billion neurons."),
        ("FACT #3", "THOUSANDS OF THOUGHTS",
         "Your brain can create thousands of thoughts every day.")
    ],

    "space facts": [
        ("FACT #1", "SUNLIGHT TAKES 8 MINUTES",
         "Light from the Sun takes about 8 minutes to reach Earth."),
        ("FACT #2", "SPACE IS SILENT",
         "Sound cannot travel through the vacuum of outer space."),
        ("FACT #3", "JUPITER IS HUGE",
         "More than 1,300 Earths could fit inside Jupiter by volume.")
    ],

    "animal facts": [
        ("FACT #1", "OCTOPUSES HAVE THREE HEARTS",
         "An octopus has three hearts and blue blood."),
        ("FACT #2", "ELEPHANTS HAVE GREAT MEMORY",
         "Elephants can remember other elephants and important places."),
        ("FACT #3", "CHEETAHS ARE FAST",
         "Cheetahs can reach speeds of around 60 miles per hour.")
    ],

    "ocean facts": [
        ("FACT #1", "MOST OF EARTH IS OCEAN",
         "Oceans cover roughly seventy percent of Earth's surface."),
        ("FACT #2", "THE OCEAN IS DEEP",
         "The deepest parts of the ocean reach almost eleven kilometers."),
        ("FACT #3", "LIFE EXISTS DEEP DOWN",
         "Many unusual creatures live in the dark deep ocean.")
    ]
}

# Match topic
key = topic.lower()

if key in topics:
    slides = topics[key]
else:
    # Generic fallback instead of silently showing Human Brain
    slides = [
        ("TOPIC", topic.upper(),
         f"Discover interesting facts about {topic}."),
        ("FACT #2", "LEARN SOMETHING NEW",
         f"Explore the fascinating world of {topic}."),
        ("FACT #3", "FOLLOW FOR MORE",
         f"Follow for more amazing facts about {topic}.")
    ]

# Voice script
voice_text = f"Here are three amazing facts about {topic}."

for number, subtitle, caption in slides:
    voice_text += f" {number.replace('FACT #', 'Fact number ')}. {caption}"

voice_text += " Follow for more amazing facts."

voice_file = "output/voice.wav"

subprocess.run([
    "espeak-ng",
    "-v", "en-us",
    "-s", "150",
    "-p", "50",
    "-a", "170",
    "-w", voice_file,
    voice_text
], check=True)

# Create images
for i, (label, subtitle, caption) in enumerate(slides):

    img = Image.new("RGB", (W, H), (8, 15, 35))
    draw = ImageDraw.Draw(img)

    draw.ellipse((50, 150, 300, 400), fill=(25, 55, 100))
    draw.ellipse((800, 1450, 1060, 1710), fill=(20, 70, 100))
    draw.ellipse((850, 250, 1030, 430), fill=(30, 45, 90))

    # Topic
    topic_display = topic.upper()

    box = draw.textbbox((0, 0), topic_display, font=small_font)
    topic_width = box[2] - box[0]

    draw.text(
        ((W - topic_width) / 2, 250),
        topic_display,
        fill="white",
        font=small_font
    )

    # Label
    box = draw.textbbox((0, 0), label, font=title_font)
    label_width = box[2] - box[0]

    draw.text(
        ((W - label_width) / 2, 600),
        label,
        fill="white",
        font=title_font
    )

    # Subtitle
    box = draw.textbbox((0, 0), subtitle, font=big_font)
    subtitle_width = box[2] - box[0]

    draw.text(
        ((W - subtitle_width) / 2, 770),
        subtitle,
        fill="white",
        font=big_font
    )

    # Caption box
    draw.rounded_rectangle(
        (80, 1040, 1000, 1390),
        radius=35,
        fill=(20, 30, 55)
    )

    words = caption.split()
    lines = []
    line = ""

    for word in words:
        test_line = (line + " " + word).strip()

        box = draw.textbbox(
            (0, 0),
            test_line,
            font=small_font
        )

        if box[2] - box[0] < 760:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    y = 1110

    for line in lines:

        box = draw.textbbox(
            (0, 0),
            line,
            font=small_font
        )

        line_width = box[2] - box[0]

        draw.text(
            ((W - line_width) / 2, y),
            line,
            fill="white",
            font=small_font
        )

        y += 65

    # CTA
    cta = "FOLLOW FOR MORE"

    box = draw.textbbox(
        (0, 0),
        cta,
        font=small_font
    )

    cta_width = box[2] - box[0]

    draw.text(
        ((W - cta_width) / 2, 1540),
        cta,
        fill="white",
        font=small_font
    )

    img.save(f"frames/frame{i}.png")

# FFmpeg slideshow
with open("frames/list.txt", "w") as f:

    for i in range(len(slides)):
        f.write(f"file 'frame{i}.png'\n")
        f.write("duration 6\n")

    f.write(f"file 'frame{len(slides)-1}.png'\n")

silent_video = "output/silent.mp4"
final_video = "output/short.mp4"

subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", "frames/list.txt",
    "-vf", "scale=1080:1920",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    "-movflags", "+faststart",
    silent_video
], check=True)

# Add voice
subprocess.run([
    "ffmpeg", "-y",
    "-i", silent_video,
    "-i", voice_file,
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "128k",
    "-shortest",
    "-movflags", "+faststart",
    final_video
], check=True)

print("================================")
print("SHORTS CREATED SUCCESSFULLY")
print("Topic:", topic)
print("Output:", final_video)
print("================================")
