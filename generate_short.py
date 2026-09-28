import os
import subprocess
import wave
from PIL import Image, ImageDraw, ImageFont

os.makedirs("output", exist_ok=True)
os.makedirs("frames", exist_ok=True)

W, H = 1080, 1920

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

title_font = ImageFont.truetype(font_path, 70)
text_font = ImageFont.truetype(font_path, 46)
small_font = ImageFont.truetype(font_path, 34)

# =========================
# READ TOPIC
# =========================

with open("topic.txt", "r", encoding="utf-8") as f:
    topic = f.read().strip()

if not topic:
    raise Exception("No topic found")

# =========================
# READ SCRIPT
# =========================

with open("script.txt", "r", encoding="utf-8") as f:
    script = f.read().strip()

# =========================
# READ VISUAL
# =========================

visual_path = "visuals/topic.jpg"

if not os.path.exists(visual_path):
    raise Exception("Visual image not found")

# =========================
# EXTRACT SCRIPT
# =========================

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

# =========================
# VOICE
# =========================

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

# =========================
# CREATE VISUAL FRAMES
# =========================

base = Image.open(visual_path).convert("RGB")

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

    # Zoom
    zoom = 1.0 + (i * 0.04)

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

    # Title
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

    img.save(
        f"frames/frame{i}.png"
    )

# =========================
# FRAME LIST
# =========================

with open("frames/list.txt", "w") as f:

    for i in range(len(slides)):

        f.write(f"file 'frame{i}.png'\n")
        f.write("duration 8\n")

    f.write(
        f"file 'frame{len(slides)-1}.png'\n"
    )

# =========================
# CREATE SILENT VIDEO
# =========================

silent_video = "output/silent.mp4"

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

# =========================
# ADD VOICE
# =========================

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

# =========================
# BACKGROUND MUSIC
# =========================

music_video = "output/music_video.mp4"

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
    music_video
], check=True)

# =========================
# CREATE TIMED CAPTIONS
# =========================

with wave.open(voice_file, "rb") as wav:

    duration = (
        wav.getnframes()
        / float(wav.getframerate())
    )

caption_text = f"{hook} {main_story} {ending}"

words = caption_text.split()

if words:

    time_per_word = duration / len(words)

else:

    time_per_word = 0.5

srt_file = "output/captions.srt"

def srt_time(seconds):

    milliseconds = int(
        (seconds - int(seconds)) * 1000
    )

    total = int(seconds)

    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{milliseconds:03d}"
    )

with open(
    srt_file,
    "w",
    encoding="utf-8"
) as f:

    chunk_size = 4

    caption_number = 1

    for start_index in range(
        0,
        len(words),
        chunk_size
    ):

        chunk = words[
            start_index:
            start_index + chunk_size
        ]

        start = start_index * time_per_word

        end = min(
            (start_index + len(chunk))
            * time_per_word,
            duration
        )

        text = " ".join(chunk)

        f.write(
            f"{caption_number}\n"
        )

        f.write(
            f"{srt_time(start)} --> "
            f"{srt_time(end)}\n"
        )

        f.write(
            text.upper() + "\n\n"
        )

        caption_number += 1

# =========================
# BURN ANIMATED-STYLE CAPTIONS
# =========================

final_video = "output/short.mp4"

subprocess.run([
    "ffmpeg",
    "-y",
    "-i", music_video,
    "-vf",
    "subtitles=output/captions.srt:"
    "force_style="
    "'FontName=DejaVu Sans,"
    "FontSize=20,"
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "Outline=3,"
    "Shadow=1,"
    "Alignment=2,"
    "MarginV=520'",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "23",
    "-c:a", "copy",
    "-movflags", "+faststart",
    final_video
], check=True)

print("================================")
print("SHORT CREATED SUCCESSFULLY")
print("================================")
print("Topic:", topic)
print("Voice: YES")
print("Music: YES")
print("Zoom: YES")
print("Captions: YES")
print("Format: 1080x1920")
print("Output:", final_video)
print("================================")
