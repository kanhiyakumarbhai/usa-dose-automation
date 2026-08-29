import os
import subprocess
import sys

VOICE = "voice.mp3"
OUTPUT = "usa_dose_short.mp4"

if not os.path.exists(VOICE):
    print("ERROR: voice.mp3 not found")
    sys.exit(1)

# Create a simple vertical background video with FFmpeg.
# The generated voice determines the video duration.

command = [
    "ffmpeg",
    "-y",
    "-f", "lavfi",
    "-i", "color=c=0x071A3D:s=1080x1920:r=30",
    "-i", VOICE,
    "-vf",
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
    "text='USA DOSE':"
    "fontcolor=white:"
    "fontsize=110:"
    "x=(w-text_w)/2:"
    "y=350,"
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
    "text='YOUR DAILY DOSE OF USA':"
    "fontcolor=white:"
    "fontsize=55:"
    "x=(w-text_w)/2:"
    "y=520",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "128k",
    "-shortest",
    OUTPUT
]

result = subprocess.run(command, capture_output=True, text=True)

if result.returncode != 0:
    print("FFmpeg ERROR:")
    print(result.stderr)
    sys.exit(1)

if not os.path.exists(OUTPUT):
    print("ERROR: Video was not created")
    sys.exit(1)

print("SUCCESS: USA Dose Short created!")
print(f"File: {OUTPUT}")
