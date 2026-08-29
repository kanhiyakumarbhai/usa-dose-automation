import os
import subprocess
import sys

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

# Clean text for FFmpeg drawtext
safe_text = (
    text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace("\n", " ")
        .replace("[", "\\[")
        .replace("]", "\\]")
)

# Limit very long scripts
safe_text = safe_text[:900]

# YouTube Shorts: 1080x1920, 30 FPS
video_filter = (
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
    "text='USA DOSE':"
    "fontcolor=white:"
    "fontsize=100:"
    "x=(w-text_w)/2:"
    "y=250,"
    
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
    f"text='{safe_text}':"
    "fontcolor=white:"
    "fontsize=46:"
    "line_spacing=18:"
    "x=90:"
    "y=620:"
    "box=1:"
    "boxcolor=black@0.60:"
    "boxborderw=35:"
    "text_align=center"
)

command = [
    "ffmpeg",
    "-y",

    # Generate vertical background
    "-f", "lavfi",
    "-i", "color=c=0x071A3D:s=1080x1920:r=30",

    # Voice
    "-i", VOICE,

    # Video filter
    "-vf", video_filter,

    # YouTube-compatible video
    "-c:v", "libx264",
    "-profile:v", "high",
    "-level", "4.2",
    "-preset", "medium",
    "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-r", "30",

    # Audio
    "-c:a", "aac",
    "-profile:a", "aac_low",
    "-b:a", "192k",
    "-ar", "48000",
    "-ac", "2",

    # MP4 compatibility
    "-movflags", "+faststart",

    # Stop when voice ends
    "-shortest",

    OUTPUT
]

print("================================")
print("Creating USA Dose YouTube Short")
print("================================")

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

# Verify video file
probe = subprocess.run(
    [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries",
        "stream=codec_name,width,height,pix_fmt,r_frame_rate",
        "-of", "default=noprint_wrappers=1",
        OUTPUT
    ],
    capture_output=True,
    text=True
)

print()
print("VIDEO INFORMATION:")
print(probe.stdout)

print("================================")
print("SUCCESS!")
print(f"Created: {OUTPUT}")
print("================================")
