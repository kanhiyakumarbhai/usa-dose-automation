```python
import os
import sys
import requests

API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY is missing")
    sys.exit(1)

url = "https://api.elevenlabs.io/v1/voices"

headers = {
    "xi-api-key": API_KEY
}

params = {
    "page_size": 100
}

print("================================")
print("Checking ElevenLabs Voices")
print("================================")

try:
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )
except Exception as e:
    print("REQUEST ERROR:")
    print(e)
    sys.exit(1)

if response.status_code != 200:
    print("ELEVENLABS ERROR:", response.status_code)
    print(response.text)
    sys.exit(1)

data = response.json()
voices = data.get("voices", [])

print("Total voices returned:", len(voices))
print()

found = 0

for voice in voices:
    labels = voice.get("labels") or {}

    gender = str(labels.get("gender", "")).lower()
    accent = str(labels.get("accent", "")).lower()

    free_allowed = voice.get("free_users_allowed")

    if gender == "female" and (
        "american" in accent
        or "usa" in accent
        or "us" == accent
    ):
        print("--------------------------------")
        print("Name:", voice.get("name"))
        print("Voice ID:", voice.get("voice_id"))
        print("Accent:", labels.get("accent"))
        print("Gender:", labels.get("gender"))
        print("Category:", voice.get("category"))
        print("Free allowed:", free_allowed)
        print("Available tiers:", voice.get("available_for_tiers"))

        found += 1

print()
print("================================")
print("Female American voices found:", found)
print("================================")

if found == 0:
    print("No female American voice was found.")
    print()
    print("The account may not have any Free API voice available.")
```
