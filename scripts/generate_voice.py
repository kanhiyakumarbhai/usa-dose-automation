```python
import os
import sys

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

# 30–40 second Short के लिए script को लगभग 75–100 words रखें
words = text.split()

if len(words) > 100:
    text = " ".join(words[:100])

client = ElevenLabs(api_key=API_KEY)

print("================================")
print("Generating ElevenLabs Female Voice")
print("================================")

audio = client.text_to_speech.convert(
    voice_id="9AlK0yDktVLRiFaf5EgC",
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

if not os.path.exists(OUTPUT):
    print("ERROR: voice.mp3 was not created")
    sys.exit(1)

print("================================")
print("VOICE SUCCESS!")
print("Created:", OUTPUT)
print("================================")
```
