import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

os.makedirs("output", exist_ok=True)
os.makedirs("frames", exist_ok=True)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

font = ImageFont.truetype(font_path, 64)
small_font = ImageFont.truetype(font_path, 42)

voice_text = """
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
    "-s", "155",
    "-p", "50",
    "-a", "170",
    "-w", voice_file,
    voice_text
], check=True)

slides = [
    ("3 AMAZING FACTS", "ABOUT THE HUMAN BRAIN"),
    ("FACT #1", "Your brain uses about 20% of your body's energy."),
    ("FACT #2", "Your brain contains around 86 billion neurons."),
    ("FACT #3", "Your brain can create thousands of thoughts every day."),
]

for i, (title, text) in enumerate(slides):

    img = Image.new("RGB", (1080, 1920), (15, 25, 50))
    draw = ImageDraw.Draw(img)

    title_box = draw.textbbox((0, 0), title, font=font)
    title_width = title_box[2] - title_box[0]

    draw.text(
        ((1080 - title_width) / 2, 550),
        title,
        fill="white",
        font=font
    )

    lines = []
    words = text.split()
    line = ""

    for word in words:
        test_line = (line + " " + word).strip()

        box = draw.textbbox(
            (0, 0),
            test_line,
            font=small_font
        )

        width = box[2] - box[0]

        if width < 900:
            line = test_line
        else:
            lines.append(line)
            line = word

    if line:
        lines.append(line)

    y = 850

    for line in lines:

        box = draw.textbbox(
            (0, 0),
            line,
            font=small_font
        )

        width = box[2] - box[0]

        draw.text(
            ((1080 - width) / 2, y),
            line,
            fill="white",
            font=small_font
        )

        y += 80

    img.save(f"frames/frame{i}.png")

with open("frames/list.txt", "w") as f:

    for i in range(len(slides)):
        f.write(f"file 'frame{i}.png'\n")
        f.write("duration 6\n")

    f.write(f"file 'frame{len(slides)-1}.png'\n")

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

final_video = "output/short.mp4"

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

print("English Shorts video created successfully!")
print("Voice added successfully!")
print("Output: output/short.mp4")
