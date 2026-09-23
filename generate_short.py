import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
# Add voice + generated background music
subprocess.run([
    "ffmpeg",
    "-y",
    "-i", silent_video,
    "-i", voice_file,
    "-f", "lavfi",
    "-i", "sine=frequency=196:duration=60",
    "-f", "lavfi",
    "-i", "sine=frequency=246.94:duration=60",
    "-f", "lavfi",
    "-i", "sine=frequency=293.66:duration=60",

    "-filter_complex",
    "[2:a]volume=0.035[a];"
    "[3:a]volume=0.025[b];"
    "[4:a]volume=0.018[c];"
    "[a][b][c]amix=inputs=3:duration=longest[music];"
    "[1:a]volume=1.0[voice];"
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
print("SHORT WITH GENERATED MUSIC CREATED")
print("Topic:", topic)
print("Output:", final_video)
print("================================")
