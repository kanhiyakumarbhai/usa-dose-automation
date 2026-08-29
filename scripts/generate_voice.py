```text id="7k2mqa"
import os
import sys

from elevenlabs.client import ElevenLabs

# ==========================================
# SETTINGS
# ==========================================

API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Laura - Enthusiast, Quirky Attitude
# American female - Social Media
VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"

MODEL_ID = "eleven_multilingual_v2"

INPUT_FILE = "daily_script.txt"
OUTPUT_FILE = "voice.mp3"

print("================================")
print("Generating ElevenLabs Female Voice")
print("================================")
print("Voice: Laura")
print("Voice ID:", VOICE_ID)
print("Model:", MODEL_ID)
print("================================")

# ==========================================
# CHECK API KEY
# ==========================================

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY secret is missing.")
    sys.exit(1)

# ==========================================
# CHECK SCRIPT
# ==========================================

if not os.path.exists(INPUT_FILE):
    print("ERROR: daily_script.txt not found.")
    sys.exit(1)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("ERROR: daily_script.txt is empty.")
    sys.exit(1)

# ==========================================
# LIMIT SCRIPT
# ==========================================

# Keep the narration suitable for a 30–40 second Short.
if len(text) > 1100:
    text = text[:1100]

print("Characters:", len(text))
print()
print("Generating natural female narration...")

# ==========================================
# ELEVENLABS
# ==========================================

try:

    client = ElevenLabs(
        api_key=API_KEY
    )

    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        text=text,
        output_format="mp3_44100_128",
        voice_settings={
            "stability": 0.42,
            "similarity_boost": 0.78,
            "style": 0.35,
            "use_speaker_boost": True
        }
    )

    with open(OUTPUT_FILE, "wb") as f:

        for chunk in audio:
            if chunk:
                f.write(chunk)

except Exception as e:

    print()
    print("================================")
    print("ELEVENLABS ERROR")
    print("================================")
    print(str(e))
    print("================================")

    sys.exit(1)

# ==========================================
# VERIFY
# ==========================================

if not os.path.exists(OUTPUT_FILE):
    print("ERROR: voice.mp3 was not created.")
    sys.exit(1)

file_size = os.path.getsize(OUTPUT_FILE)

if file_size < 10000:
    print("ERROR: Generated audio file is too small.")
    sys.exit(1)

print()
print("================================")
print("VOICE SUCCESS!")
print("================================")
print("Voice: Laura")
print("Gender: Female")
print("Accent: American")
print("Output:", OUTPUT_FILE)
print("File size:", file_size, "bytes")
print("================================")
```
