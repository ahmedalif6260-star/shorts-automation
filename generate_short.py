import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

os.makedirs("output", exist_ok=True)
os.makedirs("frames", exist_ok=True)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

font = ImageFont.truetype(font_path, 64)
small_font = ImageFont.truetype(font_path, 42)

slides = [
    (
        "3 AMAZING FACTS",
        "ABOUT THE HUMAN BRAIN"
    ),
    (
        "FACT #1",
        "Your brain uses about 20% of your body's energy."
    ),
    (
        "FACT #2",
        "Your brain contains around 86 billion neurons."
    ),
    (
        "FACT #3",
        "Your brain can create thousands of thoughts every day."
    ),
]

for i, (title, text) in enumerate(slides):

    img = Image.new(
        "RGB",
        (1080, 1920),
        (15, 25, 50)
    )

    draw = ImageDraw.Draw(img)

    # Title
    title_box = draw.textbbox(
        (0, 0),
        title,
        font=font
    )

    title_width = title_box[2] - title_box[0]

    draw.text(
        ((1080 - title_width) / 2, 550),
        title,
        fill="white",
        font=font
    )

    # Wrap text
    lines = []
    words = text.split()
    line = ""

    for word in words:

        test_line = (
            line + " " + word
        ).strip()

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

    # Main text
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

    frame_path = f"frames/frame{i}.png"

    img.save(frame_path)


# Create FFmpeg file list
with open("frames/list.txt", "w") as f:

    for i in range(len(slides)):

        f.write(
            f"file 'frame{i}.png'\n"
        )

        f.write(
            "duration 6\n"
        )

    f.write(
        f"file 'frame{len(slides)-1}.png'\n"
    )


# Create vertical video
cmd = [
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
    "output/short.mp4"
]

subprocess.run(
    cmd,
    check=True
)

print(
    "English Shorts video created successfully!"
)
