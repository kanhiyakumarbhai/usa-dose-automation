import os
import subprocess
import sys
import textwrap

VOICE = "voice.mp3"
SCRIPT = "daily_script.txt"
OUTPUT = "usa_dose_short.mp4"

if not os.path.exists(VOICE):
    print("ERROR: voice.mp3 not found")
    sys.exit(1)

if not os.path.exists(SCRIPT):
    print("ERROR: daily_script.txt not found")
    sys.exit(1)

with open(SCRIPT, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("ERROR: daily_script.txt is empty")
    sys.exit(1)

# Escape text for FFmpeg
safe_text = (
    text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace("\n", " ")
)

# Create a vertical 1080x1920 video.
# The voice determines the final duration.
video_filter = (
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
    "text='USA DOSE':"
    "fontcolor=white:"
    "fontsize=100:"
    "x=(w-text_w)/2:"
    "y=260,"
    
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
    f"text='{safe_text}':"
    "fontcolor=white:"
    "fontsize=48:"
    "line_spacing=18:"
    "x=80:"
    "y=650:"
    "box=1:"
    "boxcolor=black@0.55:"
    "boxborderw=35:"
    "text_align=center"
)

command = [
    "ffmpeg",
    "-y",
    "-f", "lavfi",
    "-i", "color=c=0x071A3D:s=1080x1920:r=30",
    "-i", VOICE,
    "-vf", video_filter,
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "128k",
    "-shortest",
    OUTPUT
]

print("Creating USA Dose Short...")

result = subprocess.run(
    command,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("FFmpeg ERROR:")
    print(result.stderr)
    sys.exit(1)

if not os.path.exists(OUTPUT):
    print("ERROR: Video was not created")
    sys.exit(1)

print("SUCCESS!")
print(f"Created: {OUTPUT}")
