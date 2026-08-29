import os
import subprocess
import sys
import re

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

# Clean text
text = re.sub(r"\s+", " ", text).strip()

# Keep captions manageable
words = text.split()

if len(words) > 105:
    words = words[:105]

# Split narration into several caption sections
chunk_size = 18
chunks = []

for i in range(0, len(words), chunk_size):
    chunk = " ".join(words[i:i + chunk_size])
    chunks.append(chunk)

if not chunks:
    chunks = ["USA News"]

print("================================")
print("Creating Dynamic USA Short")
print("================================")

print("Caption sections:", len(chunks))

# Escape FFmpeg text
def escape_text(value):
    return (
        value
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace(",", "\\,")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )

# Build animated visual filter
filters = []

# Main animated background
filters.append(
    "zoompan="
    "z='min(zoom+0.0008,1.15)':"
    "d=1:"
    "x='iw/2-(iw/zoom/2)':"
    "y='ih/2-(ih/zoom/2)':"
    "s=1080x1920:"
    "fps=30"
)

# USA DOSE title
filters.append(
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
    "text='USA DOSE':"
    "fontcolor=white:"
    "fontsize=92:"
    "x=(w-text_w)/2:"
    "y=220:"
    "shadowcolor=black@0.8:"
    "shadowx=4:"
    "shadowy=4"
)

# Add changing captions
section_count = len(chunks)

for index, chunk in enumerate(chunks):

    start = index * 4.0
    end = start + 4.8

    safe = escape_text(chunk)

    filters.append(
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"text='{safe}':"
        "fontcolor=white:"
        "fontsize=48:"
        "line_spacing=16:"
        "x=(w-text_w)/2:"
        "y=850:"
        "box=1:"
        "boxcolor=black@0.68:"
        "boxborderw=30:"
        f"enable='between(t,{start},{end})':"
        "shadowcolor=black@0.8:"
        "shadowx=3:"
        "shadowy=3"
    )

# Bottom branding
filters.append(
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
    "text='Follow for more USA facts':"
    "fontcolor=white:"
    "fontsize=38:"
    "x=(w-text_w)/2:"
    "y=1750:"
    "shadowcolor=black@0.8:"
    "shadowx=3:"
    "shadowy=3"
)

video_filter = ",".join(filters)

command = [
    "ffmpeg",
    "-y",

    # Animated background
    "-f",
    "lavfi",
    "-i",
    "color=c=0x071A3D:s=1080x1920:r=30",

    # Voice
    "-i",
    VOICE,

    # Video filter
    "-vf",
    video_filter,

    # Video encoding
    "-c:v",
    "libx264",
    "-profile:v",
    "high",
    "-level",
    "4.2",
    "-preset",
    "medium",
    "-crf",
    "20",
    "-pix_fmt",
    "yuv420p",
    "-r",
    "30",

    # Audio encoding
    "-c:a",
    "aac",
    "-b:a",
    "192k",
    "-ar",
    "48000",
    "-ac",
    "2",

    # YouTube compatibility
    "-movflags",
    "+faststart",

    # Voice determines duration
    "-shortest",

    OUTPUT
]

result = subprocess.run(
    command,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("================================")
    print("FFMPEG ERROR")
    print("================================")
    print(result.stderr)
    sys.exit(1)

if not os.path.exists(OUTPUT):
    print("ERROR: Video was not created")
    sys.exit(1)

# Check video
probe = subprocess.run(
    [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,width,height,pix_fmt,r_frame_rate",
        "-of",
        "default=noprint_wrappers=1",
        OUTPUT
    ],
    capture_output=True,
    text=True
)

print()
print("VIDEO INFORMATION")
print("==================")
print(probe.stdout)

print()
print("================================")
print("SUCCESS!")
print("Created:", OUTPUT)
print("================================")
