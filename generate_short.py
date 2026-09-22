import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

os.makedirs("output", exist_ok=True)
os.makedirs("frames", exist_ok=True)

W, H = 1080, 1920

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

title_font = ImageFont.truetype(font_path, 72)
big_font = ImageFont.truetype(font_path, 48)
small_font = ImageFont.truetype(font_path, 38)

# Read generated script
with open("script.txt", "r", encoding="utf-8") as f:
    script = f.read().strip()

if not script:
    raise Exception("script.txt is empty")

# Read topic
topic = "Trending Story"

for line in script.splitlines():
    if line.startswith("HOOK:"):
        continue

# Extract sections
hook = ""
main_story = ""
ending = ""

if "HOOK:" in script:
    hook = script.split("HOOK:", 1)[1].split("MAIN STORY:", 1)[0].strip()

if "MAIN STORY:" in script:
    main_story = script.split("MAIN STORY:", 1)[1].split("ENDING:", 1)[0].strip()

if "ENDING:" in script:
    ending = script.split("ENDING:", 1)[1].strip()

if not hook:
    hook = "Here is what you need to know."

if not main_story:
    main_story = script

if not ending:
    ending = "Follow for more quick updates."

slides = [
    ("TRENDING NOW", hook),
    ("WHAT YOU NEED TO KNOW", main_story),
    ("FOLLOW FOR MORE", ending)
]

# Voice text
voice_text = f"""
{hook}

{main_story}

{ending}
"""

voice_file = "output/voice.wav"

subprocess.run([
    "espeak-ng",
    "-v", "en-us",
    "-s", "145",
    "-p", "50",
    "-a", "170",
    "-w", voice_file,
    voice_text
], check=True)

# Create video slides
for i, (title, text) in enumerate(slides):

    img = Image.new("RGB", (W, H), (8, 15, 35))
    draw = ImageDraw.Draw(img)

    # Decorative circles
    draw.ellipse(
        (40, 120, 280, 360),
        fill=(25, 55, 100)
    )

    draw.ellipse(
        (820, 1450, 1060, 1690),
        fill=(20, 70, 100)
    )

    # Title
    box = draw.textbbox((0, 0), title, font=title_font)
    title_width = box[2] - box[0]

    draw.text(
        ((W - title_width) / 2, 450),
        title,
        fill="white",
        font=title_font
    )

    # Text box
    draw.rounded_rectangle(
        (70, 750, 1010, 1400),
        radius=35,
        fill=(20, 30, 55)
    )

    # Wrap text
    words = text.split()
    lines = []
    line = ""

    for word in words:

        test_line = (line + " " + word).strip()

        box = draw.textbbox(
            (0, 0),
            test_line,
            font=big_font
        )

        if box[2] - box[0] < 820:
            line = test_line
        else:
            if line:
                lines.append(line)

            line = word

    if line:
        lines.append(line)

    # Draw lines
    y = 850

    for line in lines[:8]:

        box = draw.textbbox(
            (0, 0),
            line,
            font=big_font
        )

        line_width = box[2] - box[0]

        draw.text(
            ((W - line_width) / 2, y),
            line,
            fill="white",
            font=big_font
        )

        y += 70

    img.save(f"frames/frame{i}.png")

# Create slideshow
with open("frames/list.txt", "w") as f:

    for i in range(len(slides)):
        f.write(f"file 'frame{i}.png'\n")
        f.write("duration 6\n")

    f.write(f"file 'frame{len(slides)-1}.png'\n")

silent_video = "output/silent.mp4"
final_video = "output/short.mp4"

# Video
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

# Add voice
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

print("================================")
print("VIDEO CREATED SUCCESSFULLY")
print("================================")
print("Output:", final_video)
