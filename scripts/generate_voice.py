import os
import sys
import requests

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

SCRIPT = "daily_script.txt"
OUTPUT = "voice.mp3"

API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY is missing")
    sys.exit(1)

if not os.path.exists(SCRIPT):
    print("ERROR: daily_script.txt not found")
    sys.exit(1)

with open(SCRIPT, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("ERROR: daily_script.txt is empty")
    sys.exit(1)

# Keep narration suitable for approximately 30–40 seconds
words = text.split()

if len(words) > 100:
    text = " ".join(words[:100])

print("================================")
print("Finding Free Female US Voice")
print("================================")

headers = {
    "xi-api-key": API_KEY
}

try:
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers=headers,
        params={"page_size": 100},
        timeout=30
    )
except Exception as e:
    print("Voice list request failed:")
    print(e)
    sys.exit(1)

if response.status_code != 200:
    print("Voice list ERROR:", response.status_code)
    print(response.text)
    sys.exit(1)

voices = response.json().get("voices", [])

selected_voice = None

# Find a female American voice that is allowed for the current account.
for voice in voices:
    labels = voice.get("labels") or {}

    gender = str(labels.get("gender", "")).lower()
    accent = str(labels.get("accent", "")).lower()
    free_allowed = voice.get("free_users_allowed")

    if (
        gender == "female"
        and (
            "american" in accent
            or "usa" in accent
            or accent == "us"
        )
        and free_allowed is True
    ):
        selected_voice = voice
        break

# If no female American voice is available, find any free female voice.
if selected_voice is None:
    for voice in voices:
        labels = voice.get("labels") or {}

        gender = str(labels.get("gender", "")).lower()
        free_allowed = voice.get("free_users_allowed")

        if gender == "female" and free_allowed is True:
            selected_voice = voice
            break

if selected_voice is None:
    print("================================")
    print("NO FREE FEMALE API VOICE FOUND")
    print("================================")
    print()
    print("Your current ElevenLabs account does not")
    print("provide a Free female voice through the API.")
    print()
    print("The workflow cannot continue with ElevenLabs")
    print("until an API-allowed voice is available.")
    sys.exit(1)

voice_id = selected_voice.get("voice_id")
voice_name = selected_voice.get("name")

print("Selected voice:", voice_name)
print("Voice ID:", voice_id)
print("Generating natural voice...")

try:
    client = ElevenLabs(api_key=API_KEY)

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id="eleven_flash_v2_5",
        output_format="mp3_44100_128",
        text=text,
        voice_settings=VoiceSettings(
            stability=0.45,
            similarity_boost=0.80,
            style=0.20,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )

    with open(OUTPUT, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)

except Exception as e:
    print("================================")
    print("ELEVENLABS ERROR")
    print("================================")
    print(e)
    sys.exit(1)

if not os.path.exists(OUTPUT):
    print("ERROR: voice.mp3 was not created")
    sys.exit(1)

size = os.path.getsize(OUTPUT)

if size < 1000:
    print("ERROR: voice.mp3 is too small")
    sys.exit(1)

print("================================")
print("VOICE SUCCESS!")
print("================================")
print("Voice:", voice_name)
print("Voice ID:", voice_id)
print("Created:", OUTPUT)
print("Size:", size, "bytes")
print("================================")
