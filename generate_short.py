import os
import subprocess

os.makedirs("output", exist_ok=True)

cmd = [
    "ffmpeg",
    "-y",
    "-f", "lavfi",
    "-i", "color=c=blue:s=1080x1920:d=8",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "output/short.mp4"
]

subprocess.run(cmd, check=True)

print("VIDEO CREATED SUCCESSFULLY")
