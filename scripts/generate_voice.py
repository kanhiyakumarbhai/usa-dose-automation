import os
import sys
import subprocess
import requests

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

SCRIPT = "daily_script.txt"
OUTPUT = "voice.mp3"

API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not os.path.exists(SCRIPT):
    print("ERROR: daily_script.txt not found")
    sys.exit(1)

with open(SCRIPT, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("ERROR: daily_script.txt is empty")
    sys.exit(1)

# Keep Shorts around 30–40 seconds.
words = text.split()

if len(words) > 100:
    text = " ".join(words[:100])

print("================================")
print("Generating Voice")
print("================================")

# ==========================================
# Try ElevenLabs first
# ==========================================

if API_KEY:
    print("Checking ElevenLabs Free API voices...")

    try:
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": API_KEY},
            params={"page_size": 100},
            timeout=30
        )

        if response.status_code == 200:
            voices = response.json().get("voices", [])
            selected_voice = None

            # Prefer free male American voice.
            for voice in voices:
                labels = voice.get("labels") or {}

                gender = str(labels.get("gender", "")).lower()
                accent = str(labels.get("accent", "")).lower()
                free_allowed = voice.get("free_users_allowed")

                if (
                    gender == "male"
                    and (
                        "american" in accent
                        or "usa" in accent
                        or accent == "us"
                    )
                    and free_allowed is True
                ):
                    selected_voice = voice
                    break

            # Otherwise any free male voice.
            if selected_voice is None:
                for voice in voices:
                    labels = voice.get("labels") or {}
                    gender = str(labels.get("gender", "")).lower()
                    free_allowed = voice.get("free_users_allowed")

                    if gender == "male" and free_allowed is True:
                        selected_voice = voice
                        break

            if selected_voice:
                voice_id = selected_voice.get("voice_id")
                voice_name = selected_voice.get("name")

                print("ElevenLabs voice:", voice_name)
                print("Voice ID:", voice_id)

                try:
                    client = ElevenLabs(api_key=API_KEY)

                    audio = client.text_to_speech.convert(
                        voice_id=voice_id,
                        model_id="eleven_flash_v2_5",
                        output_format="mp3_44100_128",
                        text=text,
                        voice_settings=VoiceSettings(
                            stability=0.50,
                            similarity_boost=0.80,
                            style=0.15,
                            use_speaker_boost=True,
                            speed=1.0,
                        ),
                    )

                    with open(OUTPUT, "wb") as f:
                        for chunk in audio:
                            if chunk:
                                f.write(chunk)

                    if os.path.exists(OUTPUT) and os.path.getsize(OUTPUT) > 1000:
                        print("================================")
                        print("ELEVENLABS VOICE SUCCESS")
                        print("================================")
                        print("Created:", OUTPUT)
                        sys.exit(0)

                except Exception as e:
                    print("ElevenLabs generation failed:")
                    print(e)

            else:
                print("No Free ElevenLabs male voice available.")

        else:
            print("ElevenLabs API returned:", response.status_code)

    except Exception as e:
        print("ElevenLabs request failed:")
        print(e)

# ==========================================
# FREE FALLBACK VOICE
# ==========================================

print()
print("================================")
print("Using Free System Male Voice")
print("================================")

# Check espeak-ng.
check = subprocess.run(
    ["which", "espeak-ng"],
    capture_output=True,
    text=True
)

if check.returncode != 0:
    print("ERROR: espeak-ng is not installed.")
    print("Add this to daily.yml before running this script:")
    print("sudo apt-get install -y ffmpeg espeak-ng")
    sys.exit(1)

wav_file = "voice_temp.wav"

command = [
    "espeak-ng",
    "-v", "en-us",
    "-s", "155",
    "-p", "35",
    "-a", "170",
    "-w", wav_file,
    text
]

result = subprocess.run(
    command,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("espeak-ng ERROR:")
    print(result.stderr)
    sys.exit(1)

# Convert WAV to MP3.
result = subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i", wav_file,
        "-codec:a", "libmp3lame",
        "-b:a", "128k",
        OUTPUT
    ],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("FFmpeg audio conversion ERROR:")
    print(result.stderr)
    sys.exit(1)

if os.path.exists(wav_file):
    os.remove(wav_file)

if not os.path.exists(OUTPUT):
    print("ERROR: voice.mp3 was not created")
    sys.exit(1)

if os.path.getsize(OUTPUT) < 1000:
    print("ERROR: voice.mp3 is too small")
    sys.exit(1)

print("================================")
print("VOICE SUCCESS")
print("================================")
print("Voice: Free US English Male")
print("Created:", OUTPUT)
print("Size:", os.path.getsize(OUTPUT), "bytes")
print("================================")
