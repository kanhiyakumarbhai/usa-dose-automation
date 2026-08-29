import os
import requests
import sys

API_KEY = os.getenv("ELEVENLABS_API_KEY")

print("================================")
print("ELEVENLABS API VOICE FINDER")
print("================================")

if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY secret is missing.")
    sys.exit(1)

url = "https://api.elevenlabs.io/v2/voices"

headers = {
    "xi-api-key": API_KEY
}

params = {
    "page_size": 100
}

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

print("API status:", response.status_code)

if response.status_code != 200:
    print()
    print("ELEVENLABS API ERROR")
    print(response.text)
    sys.exit(1)

data = response.json()

voices = data.get("voices", [])

print()
print("Total API voices returned:", len(voices))
print()

if not voices:
    print("NO API VOICES FOUND")
    sys.exit(1)

print("================================")
print("AVAILABLE API VOICES")
print("================================")

for voice in voices:

    voice_id = voice.get("voice_id", "")
    name = voice.get("name", "Unknown")

    labels = voice.get("labels") or {}

    gender = labels.get("gender", "")
    accent = labels.get("accent", "")
    age = labels.get("age", "")
    use_case = labels.get("use_case", "")
    description = labels.get("description", "")

    category = voice.get("category", "")

    print()
    print("--------------------------------")
    print("Name       :", name)
    print("Voice ID   :", voice_id)
    print("Category   :", category)
    print("Gender     :", gender)
    print("Accent     :", accent)
    print("Age        :", age)
    print("Use case   :", use_case)
    print("Description:", description)
    print("--------------------------------")

print()
print("================================")
print("POSSIBLE US MALE VOICES")
print("================================")

matches = []

for voice in voices:

    labels = voice.get("labels") or {}

    gender = str(labels.get("gender", "")).lower()
    accent = str(labels.get("accent", "")).lower()
    use_case = str(labels.get("use_case", "")).lower()
    name = str(voice.get("name", "")).lower()

    is_male = "male" in gender

    is_us = (
        "american" in accent
        or "usa" in accent
        or "united states" in accent
        or "us" == accent
    )

    is_narration = (
        "narration" in use_case
        or "narrative" in use_case
        or "story" in use_case
    )

    if is_male and (is_us or is_narration):
        matches.append(voice)

if not matches:
    print()
    print("No obvious US male voice found.")
    print()
    print("Use the AVAILABLE API VOICES list above.")
else:

    for voice in matches:

        labels = voice.get("labels") or {}

        print()
        print("Name     :", voice.get("name"))
        print("Voice ID :", voice.get("voice_id"))
        print("Gender   :", labels.get("gender"))
        print("Accent   :", labels.get("accent"))
        print("Use case :", labels.get("use_case"))

print()
print("================================")
print("VOICE SEARCH COMPLETE")
print("================================")
