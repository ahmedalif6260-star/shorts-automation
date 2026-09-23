import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

os.makedirs("output", exist_ok=True)
os.makedirs("frames", exist_ok=True)

W, H = 1080, 1920

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

title_font = ImageFont.truetype(font_path, 70)
text_font = ImageFont.truetype(font_path, 46)
small_font = ImageFont.truetype(font_path, 34)

# Read topic
with open("topic.txt", "r", encoding="utf-8") as f:
    topic = f.read().strip()

# Read script
with open("script.txt", "r", encoding="utf-8") as f:
    script = f.read().strip()

# Read visual
visual_path = "visuals/topic.jpg"

if not os.path.exists(visual_path):
    raise Exception("Visual image not found")

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
    hook = f"Here is what you need to know about {topic}."

if not main_story:
    main_story = script

if not ending:
    ending = "Follow for more updates."

slides = [
    ("TRENDING NOW", hook),
    ("WHAT YOU NEED TO KNOW", main_story),
    ("FOLLOW FOR MORE", ending)
]

# Prepare visual
base = Image.open(visual_path).convert("RGB")

# Voice text
voice_text = f"""
{hook}

{main_story}

{ending}
"""

voice_file = "output/voice.wav"

# Create voice
subprocess.run([
    "espeak-ng",
    "-v", "en-us",
    "-s", "145",
    "-p", "50",
    "-a", "170",
    "-w", voice_file,
    voice_text
], check=True)

# Create slides
for i, (title, text) in enumerate(slides):

    img = base.copy()

    # Crop to 9:16
    img_ratio = img.width / img.height
    target_ratio = W / H

    if img_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop(
            (left, 0, left + new_width, img.height)
        )
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop(
            (0, top, img.width, top + new_height)
        )

    img = img.resize((W, H))
        else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop(
            (0, top, img.width, top + new_height)
        )

    img = img.resize((W, H))

    # Slow cinematic zoom
    zoom = 1.08 + (i * 0.04)

    crop_w = int(W / zoom)
    crop_h = int(H / zoom)

    left = (W - crop_w) // 2
    top = (H - crop_h) // 2

    img = img.crop(
        (left, top, left + crop_w, top + crop_h)
    )

    img = img.resize((W, H))

    # Dark overlay
# Slow cinematic movement
zoom = 1.08 + (i * 0.04)

crop_w = int(W / zoom)
crop_h = int(H / zoom)

left = (W - crop_w) // 2
top = (H - crop_h) // 2

img = img.crop(
    (left, top, left + crop_w, top + crop_h)
)

img = img.resize((W, H))
    # Dark overlay
    overlay = Image.new(
        "RGBA",
        (W, H),
        (0, 0, 0, 75)
    )

    img = Image.alpha_composite(
        img.convert("RGBA"),
        overlay
    ).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Topic
    topic_text = topic.upper()

    box = draw.textbbox(
        (0, 0),
        topic_text,
        font=small_font
    )

    topic_width = box[2] - box[0]

    draw.text(
        ((W - topic_width) / 2, 180),
        topic_text,
        fill="white",
        font=small_font
    )

    # Title box
    draw.rounded_rectangle(
        (50, 450, 1030, 620),
        radius=30,
        fill=(0, 0, 0)
    )

    box = draw.textbbox(
        (0, 0),
        title,
        font=title_font
    )

    title_width = box[2] - box[0]

    draw.text(
        ((W - title_width) / 2, 490),
        title,
        fill="white",
        font=title_font
    )

    # Caption box
    draw.rounded_rectangle(
        (55, 900, 1025, 1450),
        radius=35,
        fill=(0, 0, 0)
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
            font=text_font
        )

        if box[2] - box[0] < 850:
            line = test_line
        else:
            if line:
                lines.append(line)

            line = word

    if line:
        lines.append(line)

    y = 990

    for line in lines[:7]:

        box = draw.textbbox(
            (0, 0),
            line,
            font=text_font
        )

        line_width = box[2] - box[0]

        draw.text(
            ((W - line_width) / 2, y),
            line,
            fill="white",
            font=text_font
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
        ((W - cta_width) / 2, 1680),
        cta,
        fill="white",
        font=small_font
    )

    img.save(f"frames/frame{i}.png")

# Create slideshow list
with open("frames/list.txt", "w") as f:

    for i in range(len(slides)):
        f.write(f"file 'frame{i}.png'\n")
        f.write("duration 8\n")

    f.write(f"file 'frame{len(slides)-1}.png'\n")

silent_video = "output/silent.mp4"
final_video = "output/short.mp4"

# Create silent video
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
voice_video = "output/voice_video.mp4"

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
    voice_video
], check=True)

# Add original generated background music
subprocess.run([
    "ffmpeg",
    "-y",
    "-i", voice_video,
    "-f", "lavfi",
    "-i", "sine=frequency=196:duration=60",
    "-f", "lavfi",
    "-i", "sine=frequency=246.94:duration=60",
    "-f", "lavfi",
    "-i", "sine=frequency=293.66:duration=60",

    "-filter_complex",
    "[1:a]volume=0.035[a];"
    "[2:a]volume=0.025[b];"
    "[3:a]volume=0.018[c];"
    "[a][b][c]amix=inputs=3:duration=longest[music];"
    "[0:a]volume=1.0[voice];"
    "[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",

    "-map", "0:v:0",
    "-map", "[aout]",

    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "128k",
    "-shortest",
    "-movflags", "+faststart",

    final_video
], check=True)

print("================================")
print("SHORT CREATED SUCCESSFULLY")
print("Topic:", topic)
print("Visual:", visual_path)
print("Voice: YES")
print("Background Music: YES")
print("Output:", final_video)
print("================================")
