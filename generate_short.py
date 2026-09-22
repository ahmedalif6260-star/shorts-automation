import os
import subprocess

os.makedirs("output", exist_ok=True)

text = """আজকের মজার তথ্য:
অক্টোপাসের তিনটি হৃদপিণ্ড থাকে!
আর তার রক্তের রং নীল।
এমন আরও মজার তথ্য জানতে আমাদের সাথে থাকুন।"""

with open("output/script.txt", "w", encoding="utf-8") as f:
    f.write(text)

cmd = [
    "ffmpeg",
    "-y",
    "-f", "lavfi",
    "-i", "color=c=black:s=1080x1920:d=10",
    "-vf",
    "drawtext=text='আজকের মজার তথ্য':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=700",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "output/short.mp4"
]

subprocess.run(cmd, check=True)

print("Short video created successfully!")
