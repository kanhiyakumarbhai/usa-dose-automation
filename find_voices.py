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

response = requests.get(
url,
headers=headers,
params=params,
timeout=30
)

if response.status_code != 200:
print("ERROR:", response.status_code)
print(response.text)
sys.exit(1)

data = response.json()

voices = data.get("voices", [])

print("Total voices returned:", len(voices))
print()

found = 0

for voice in voices:
labels = voice.get("labels", {})

```
gender = str(labels.get("gender", "")).lower()
accent = str(labels.get("accent", "")).lower()

if gender == "female" and ("american" in accent or "us" in accent):
    print("--------------------------------")
    print("Name:", voice.get("name"))
    print("Voice ID:", voice.get("voice_id"))
    print("Accent:", labels.get("accent"))
    print("Gender:", labels.get("gender"))
    print("Category:", voice.get("category"))
    print("Free allowed:", voice.get("free_users_allowed"))
    print("Available tiers:", voice.get("available_for_tiers"))
    found += 1
```

print()
print("================================")
print("Female American voices found:", found)
print("================================")

if found == 0:
print("No female American voice was found in the current API list.")
