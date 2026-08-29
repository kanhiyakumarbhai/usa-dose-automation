import os
import sys
import subprocess
import random
import math

VOICE = "voice.mp3"
SCRIPT = "daily_script.txt"
CLIPS_DIR = "clips"
OUTPUT = "usa_dose_short.mp4"
WORK_DIR = "video_parts"

WIDTH = 1080
HEIGHT = 1920
FPS = 30

# ==========================================
# CHECK FILES
# ==========================================

print("================================")
print("USA DOSE VIDEO CREATOR")
print("================================")

if not os.path.exists(VOICE):
    print("ERROR: voice.mp3 not found")
    sys.exit(1)

if not os.path.exists(SCRIPT):
    print("ERROR: daily_script.txt not found")
    sys.exit(1)

if not os.path.isdir(CLIPS_DIR):
    print("ERROR: clips directory not found")
    sys.exit(1)

with open(SCRIPT, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("ERROR: daily_script.txt is empty")
    sys.exit(1)

clips = []

for filename in sorted(os.listdir(CLIPS_DIR)):
    if filename.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
        clips.append(os.path.join(CLIPS_DIR, filename))

if len(clips) < 3:
    print("ERROR: At least 3 video clips are required.")
    print("Found:", len(clips))
    sys.exit(1)

print("Voice:", VOICE)
print("Clips found:", len(clips))

# ==========================================
# GET VOICE DURATION
# ==========================================

probe = subprocess.run(
    [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        VOICE
    ],
    capture_output=True,
    text=True
)

try:
    voice_duration = float(probe.stdout.strip())
except:
    print("ERROR: Could not read voice duration")
    sys.exit(1)

print("Voice duration:", round(voice_duration, 2), "seconds")

# Keep final video between approximately 30–40 seconds.
TARGET_DURATION = max(30.0, min(40.0, voice_duration))

print("Target duration:", round(TARGET_DURATION, 2), "seconds")

# ==========================================
# PREPARE WORK DIRECTORY
# ==========================================

if os.path.exists(WORK_DIR):
    subprocess.run(
        ["rm", "-rf", WORK_DIR],
        check=False
    )

os.makedirs(WORK_DIR, exist_ok=True)

# Randomize clips so each run can look different.
random.shuffle(clips)

# Use up to 5 clips.
clips = clips[:5]

print()
print("Selected clips:")

for clip in clips:
    print(" -", clip)

# ==========================================
# CALCULATE CLIP DURATIONS
# ==========================================

clip_count = len(clips)

# Divide the voice duration between clips.
base_duration = TARGET_DURATION / clip_count

# ==========================================
# CREATE EACH VIDEO PART
# ==========================================

parts = []

for index, clip in enumerate(clips):

    output_part = os.path.join(
        WORK_DIR,
        f"part_{index + 1}.mp4"
    )

    duration = base_duration

    print()
    print("--------------------------------")
    print("Processing clip", index + 1)
    print("Source:", clip)
    print("Duration:", round(duration, 2))
    print("--------------------------------")

    # Different starting point for each clip.
    # -stream_loop allows short clips to repeat if necessary.
    command = [
        "ffmpeg",
        "-y",

        "-stream_loop", "-1",
        "-i", clip,

        "-t", str(duration),

        "-vf",
        (
            f"scale={WIDTH}:{HEIGHT}:"
            "force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},"
            "setsar=1,"
            f"fps={FPS}"
        ),

        "-an",

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "21",

        "-pix_fmt", "yuv420p",

        "-movflags", "+faststart",

        output_part
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("FFmpeg clip ERROR:")
        print(result.stderr)
        sys.exit(1)

    if not os.path.exists(output_part):
        print("ERROR: Part was not created")
        sys.exit(1)

    parts.append(output_part)

# ==========================================
# CREATE CONCAT FILE
# ==========================================

concat_file = os.path.join(
    WORK_DIR,
    "concat.txt"
)

with open(concat_file, "w", encoding="utf-8") as f:
    for part in parts:
        absolute_path = os.path.abspath(part)
        f.write(
            "file '" +
            absolute_path.replace("'", "'\\''") +
            "'\n"
        )

# ==========================================
# PREPARE CAPTION TEXT
# ==========================================

# Keep caption reasonably short.
caption = " ".join(text.split())

if len(caption) > 850:
    caption = caption[:850] + "..."

# Escape FFmpeg drawtext special characters.
caption = (
    caption
    .replace("\\", "\\\\")
    .replace(":", "\\:")
    .replace("'", "\\'")
    .replace("%", "\\%")
    .replace("[", "\\[")
    .replace("]", "\\]")
    .replace(",", "\\,")
)

# ==========================================
# JOIN CLIPS + ADD VOICE + TEXT
# ==========================================

print()
print("================================")
print("Joining moving clips...")
print("Adding voice...")
print("Adding captions...")
print("================================")

filter_complex = (
    "[0:v]"
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
    "text='USA DOSE':"
    "fontcolor=white:"
    "fontsize=88:"
    "x=(w-text_w)/2:"
    "y=170:"
    "box=1:"
    "boxcolor=black@0.45:"
    "boxborderw=18"
    ","
    "drawtext="
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
    f"text='{caption}':"
    "fontcolor=white:"
    "fontsize=43:"
    "line_spacing=12:"
    "x=70:"
    "y=h-620:"
    "box=1:"
    "boxcolor=black@0.65:"
    "boxborderw=30:"
    "text_align=center"
    "[v]"
)

final_command = [
    "ffmpeg",
    "-y",

    "-f", "concat",
    "-safe", "0",
    "-i", concat_file,

    "-i", VOICE,

    "-filter_complex",
    filter_complex,

    "-map", "[v]",
    "-map", "1:a:0",

    "-t", str(TARGET_DURATION),

    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "20",

    "-profile:v", "high",
    "-level", "4.2",

    "-pix_fmt", "yuv420p",
    "-r", str(FPS),

    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "48000",
    "-ac", "2",

    "-movflags", "+faststart",

    OUTPUT
]

result = subprocess.run(
    final_command,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("================================")
    print("FINAL VIDEO ERROR")
    print("================================")
    print(result.stderr)
    sys.exit(1)

# ==========================================
# VERIFY OUTPUT
# ==========================================

if not os.path.exists(OUTPUT):
    print("ERROR: Final video was not created")
    sys.exit(1)

file_size = os.path.getsize(OUTPUT)

if file_size < 100000:
    print("ERROR: Final video file is too small")
    sys.exit(1)

print()
print("================================")
print("FINAL VIDEO INFORMATION")
print("================================")

probe = subprocess.run(
    [
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "format=duration,size",
        "-show_entries",
        "stream=codec_name,width,height,pix_fmt",
        "-of", "default=noprint_wrappers=1",
        OUTPUT
    ],
    capture_output=True,
    text=True
)

print(probe.stdout)

print("================================")
print("VIDEO SUCCESS!")
print("================================")
print("Created:", OUTPUT)
print("Size:", file_size, "bytes")
print("Moving clips:", len(clips))
print("================================")
