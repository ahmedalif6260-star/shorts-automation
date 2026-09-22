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

# Topic can be changed from GitHub Actions later
topic = os.environ.get("SHORT_TOPIC", "Human Brain")

# Current test content
slides = [
    (
        "3 AMAZING",
        "BRAIN FACTS",
        "Did you know these facts about the human brain?"
    ),
    (
        "FACT #1",
        "20% OF YOUR ENERGY",
        "Your brain uses about 20% of your body's energy."
    ),
    (
        "FACT #2",
        "86 BILLION NEURONS",
        "Your brain contains around 86 billion neurons."
    ),
    (
        "FACT #3",
        "THOUSANDS OF THOUGHTS",
        "Your brain can create thousands of thoughts every day."
    ),
]

voice_text = f"""
Here are three amazing facts about the human brain.

Fact number one.
Your brain uses about twenty percent of your body's energy.

Fact number two.
Your brain contains around eighty-six billion neurons.

Fact number three.
Your brain can create thousands of thoughts every day.

Follow for more amazing facts.
"""

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

for i, (title, subtitle, caption) in enumerate(slides):

    img = Image.new("RGB", (W, H), (8, 15, 35))
    draw = ImageDraw.Draw(img)

    draw.ellipse((60, 150, 300, 390), fill=(25, 55, 100))
    draw.ellipse((800, 1450, 1050, 1700), fill=(20, 70, 100))
    draw.ellipse((850, 250, 1020, 420), fill=(30, 45, 90))

    label = topic.upper()
    box = draw.textbbox((0, 0), label, font=small_font)
    label_w = box[2] - box[0]

    draw.text(
        ((W - label_w) / 2, 260),
        label,
        fill="white",
        font=small_font
    )

    box = draw.textbbox((0, 0), title, font=title_font)
    title_w = box[2] - box[0]

    draw.text(
        ((W - title_w) / 2, 620),
        title,
        fill="white",
        font=title_font
    )

    box = draw.textbbox((0, 0), subtitle, font=big_font)
    sub_w = box[2] - box[0]

    draw.text(
        ((W - sub_w) / 2, 780),
        subtitle,
        fill="white",
        font=big_font
    )

    draw.rounded_rectangle(
        (90, 1050, 990, 1370),
        radius=35,
        fill=(20, 30, 55)
    )

    words = caption.split()
    lines = []
    line = ""

    for word in words:
        test = (line + " " + word).strip()

        box = draw.textbbox(
            (0, 0),
            test,
            font=small_font
        )

        if box[2] - box[0] < 760:
            line = test
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    y = 1120

    for line in lines:

        box = draw.textbbox(
            (0, 0),
            line,
            font=small_font
        )

        line_w = box[2] - box[0]

        draw.text(
            ((W - line_w) / 2, y),
            line,
            fill="white",
            font=small_font
        )

        y += 65

    cta = "FOLLOW FOR MORE"
    box = draw.textbbox((0, 0), cta, font=small_font)
    cta_w = box[2] - box[0]

    draw.text(
        ((W - cta_w) / 2, 1530),
        cta,
        fill="white",
        font=small_font
    )

    img.save(f"frames/frame{i}.png")

with open("frames/list.txt", "w") as f:

    for i in range(len(slides)):
        f.write(f"file 'frame{i}.png'\n")
        f.write("duration 6\n")

    f.write(f"file 'frame{len(slides)-1}.png'\n")

silent_video = "output/silent.mp4"
final_video = "output/short.mp4"

subprocess.run([
    "ffmpeg",
    "-y",
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

subprocess.run([
    "ffmpeg",
    "-y",
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

print("SHORTS CREATED SUCCESSFULLY")
print("Topic:", topic)
print("Output:", final_video)
