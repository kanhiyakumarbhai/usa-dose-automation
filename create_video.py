import os
import re
import subprocess
import sys
import random


VOICE_FILE = "voice.mp3"
OUTPUT_FILE = "usa_dose_short.mp4"
CLIPS_DIR = "clips"
SCRIPT_FILE = "daily_script.txt"

WIDTH = 1080
HEIGHT = 1920
FPS = 30


def run(cmd):
    print("Running:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if result.returncode != 0:
        print(result.stdout)
        raise RuntimeError("FFmpeg command failed.")

    return result.stdout


def get_duration(filename):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Could not read duration: {filename}"
        )

    return float(result.stdout.strip())


def clean_script(text):
    forbidden_patterns = [
        r"voice[\s_-]*over\s*:?",
        r"voiceover\s*:?",
        r"narration\s*:?",
        r"narrator\s*:?",
        r"script\s*:?",
        r"production\s*:?",
        r"scene\s*:?",
        r"on[\s_-]*screen\s*:?",
    ]

    for pattern in forbidden_patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def get_clips():
    if not os.path.isdir(CLIPS_DIR):
        raise RuntimeError(
            f"{CLIPS_DIR} folder not found."
        )

    files = []

    for filename in os.listdir(CLIPS_DIR):
        if filename.lower().endswith(
            (".mp4", ".mov", ".mkv", ".webm")
        ):
            files.append(
                os.path.join(CLIPS_DIR, filename)
            )

    if not files:
        raise RuntimeError(
            "No video clips found."
        )

    random.shuffle(files)

    return files


def make_clip_part(source, output, duration):
    filter_complex = (
        f"[0:v]"
        f"scale={WIDTH}:{HEIGHT}:"
        f"force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"setsar=1,"
        f"fps={FPS},"
        f"format=yuv420p"
        f"[v]"
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            source,
            "-t",
            str(duration),
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            output,
        ]
    )


def create_concat(parts, output):
    concat_file = "video_parts/concat.txt"

    os.makedirs("video_parts", exist_ok=True)

    with open(
        concat_file,
        "w",
        encoding="utf-8",
    ) as f:
        for part in parts:
            absolute = os.path.abspath(part)
            escaped = absolute.replace("'", "'\\''")
            f.write(
                f"file '{escaped}'\n"
            )

    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-movflags",
            "+faststart",
            output,
        ]
    )


def escape_drawtext(text):
    text = text.replace("\\", r"\\")
    text = text.replace(":", r"\:")
    text = text.replace("'", r"\'")
    text = text.replace("%", r"\%")
    text = text.replace("[", r"\[")
    text = text.replace("]", r"\]")
    text = text.replace(",", r"\,")

    return text


def make_captions(script):
    """
    Creates clean subtitle-style captions.

    It does NOT add:
    Voice Over:
    Narration:
    Script:
    etc.
    """

    script = clean_script(script)

    words = script.split()

    if not words:
        return ""

    chunks = []

    current = []

    for word in words:
        current.append(word)

        if len(current) >= 7:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks


def create_final_video(video, voice, script):
    duration = get_duration(voice)

    captions = make_captions(script)

    font_bold = (
        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSans-Bold.ttf"
    )

    caption_text = ""

    if captions:
        caption_text = captions[0]

    caption_text = escape_drawtext(
        caption_text
    )

    filters = []

    # ======================================================
    # USA DOSE BRANDING
    # ======================================================

    # Main channel name
    filters.append(
        "drawtext="
        f"fontfile={font_bold}:"
        "text='USA DOSE':"
        "fontcolor=white:"
        "fontsize=58:"
        "x=(w-text_w)/2:"
        "y=80:"
        "box=1:"
        "boxcolor=black@0.45:"
        "boxborderw=14"
    )

    # Subscribe text directly below channel name
    filters.append(
        "drawtext="
        f"fontfile={font_bold}:"
        "text='SUBSCRIBE':"
        "fontcolor=white:"
        "fontsize=30:"
        "x=(w-text_w)/2:"
        "y=155:"
        "box=1:"
        "boxcolor=black@0.40:"
        "boxborderw=9"
    )

    # ======================================================
    # CLEAN CAPTIONS
    # ======================================================

    if caption_text:
        filters.append(
            "drawtext="
            f"fontfile={font_bold}:"
            f"text='{caption_text}':"
            "fontcolor=white:"
            "fontsize=48:"
            "line_spacing=8:"
            "x=70:"
            "y=h-430:"
            "box=1:"
            "boxcolor=black@0.62:"
            "boxborderw=22:"
            "text_align=center"
        )

    filter_complex = (
        "[0:v]"
        + ",".join(filters)
        + "[v]"
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            video,
            "-i",
            voice,
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "1:a:0",
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-profile:v",
            "high",
            "-level",
            "4.2",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            OUTPUT_FILE,
        ]
    )


def main():
    print("================================")
    print("USA DOSE HD VIDEO CREATOR")
    print("================================")

    if not os.path.isfile(VOICE_FILE):
        print("ERROR: voice.mp3 not found.")
        sys.exit(1)

    if not os.path.isfile(SCRIPT_FILE):
        print("ERROR: daily_script.txt not found.")
        sys.exit(1)

    with open(
        SCRIPT_FILE,
        "r",
        encoding="utf-8",
    ) as f:
        script = f.read()

    script = clean_script(script)

    if not script:
        print("ERROR: Script is empty.")
        sys.exit(1)

    voice_duration = get_duration(
        VOICE_FILE
    )

    print(
        f"Voice duration: "
        f"{voice_duration:.2f} seconds"
    )

    clips = get_clips()

    print(
        f"Clips found: {len(clips)}"
    )

    # Use 5 different clips when possible.
    selected = clips[:5]

    part_duration = (
        voice_duration / len(selected)
    )

    os.makedirs(
        "video_parts",
        exist_ok=True
    )

    parts = []

    for index, clip in enumerate(
        selected,
        start=1
    ):
        output = (
            f"video_parts/"
            f"part_{index}.mp4"
        )

        print("")
        print("--------------------------------")
        print(f"Processing clip {index}")
        print(f"Source: {clip}")
        print(
            f"Duration: "
            f"{part_duration:.2f}"
        )
        print("--------------------------------")

        make_clip_part(
            clip,
            output,
            part_duration,
        )

        parts.append(output)

    joined_video = (
        "video_parts/joined.mp4"
    )

    print("")
    print("================================")
    print("JOINING MOVING CLIPS")
    print("================================")

    create_concat(
        parts,
        joined_video,
    )

    print("")
    print("================================")
    print("ADDING VOICE + BRANDING + CAPTIONS")
    print("================================")

    create_final_video(
        joined_video,
        VOICE_FILE,
        script,
    )

    if not os.path.isfile(
        OUTPUT_FILE
    ):
        print(
            "ERROR: Final video not created."
        )
        sys.exit(1)

    final_duration = get_duration(
        OUTPUT_FILE
    )

    print("")
    print("================================")
    print("HD VIDEO CREATED SUCCESSFULLY")
    print("================================")
    print(
        f"File: {OUTPUT_FILE}"
    )
    print(
        f"Resolution: "
        f"{WIDTH}x{HEIGHT}"
    )
    print(
        f"FPS: {FPS}"
    )
    print(
        f"Duration: "
        f"{final_duration:.2f} seconds"
    )
    print(
        "Quality: 1080x1920 HD"
    )
    print(
        "Captions: CLEAN"
    )
    print(
        "Branding: USA DOSE + SUBSCRIBE"
    )
    print(
        "Production labels: NONE"
    )
    print("================================")


if __name__ == "__main__":
    main()
