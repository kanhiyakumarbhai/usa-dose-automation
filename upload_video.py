import os
import sys
import re

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


VIDEO_FILE = "usa_dose_short.mp4"
SCRIPT_FILE = "daily_script.txt"

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")


# ==========================================
# CHECK REQUIRED FILES / SECRETS
# ==========================================

if not CLIENT_ID:
    print("ERROR: YOUTUBE_CLIENT_ID is missing")
    sys.exit(1)

if not CLIENT_SECRET:
    print("ERROR: YOUTUBE_CLIENT_SECRET is missing")
    sys.exit(1)

if not REFRESH_TOKEN:
    print("ERROR: YOUTUBE_REFRESH_TOKEN is missing")
    sys.exit(1)

if not os.path.exists(VIDEO_FILE):
    print(f"ERROR: {VIDEO_FILE} not found")
    sys.exit(1)

if not os.path.exists(SCRIPT_FILE):
    print(f"ERROR: {SCRIPT_FILE} not found")
    sys.exit(1)


# ==========================================
# READ DAILY SCRIPT
# ==========================================

with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
    script = f.read().strip()

if not script:
    print("ERROR: daily_script.txt is empty")
    sys.exit(1)


# ==========================================
# CREATE DYNAMIC TITLE
# ==========================================

clean_script = re.sub(r"\s+", " ", script).strip()

# Remove common opening phrases
title_text = re.sub(
    r"^(did you know|here's a fact|here is a fact|welcome to|"
    r"you won't believe|did you know that)\s*[:,!-]?\s*",
    "",
    clean_script,
    flags=re.IGNORECASE,
)

# Use first sentence / first part
parts = re.split(r"(?<=[.!?])\s+", title_text)

title_text = parts[0].strip()

# Remove trailing punctuation
title_text = title_text.rstrip(".!?,")

# Limit title length
if len(title_text) > 65:
    title_text = title_text[:65].rsplit(" ", 1)[0]

if not title_text:
    title_text = "Amazing USA Fact You Probably Didn't Know"


title = f"{title_text} 🇺🇸 #Shorts"


# ==========================================
# CREATE DESCRIPTION
# ==========================================

description = f"""🇺🇸 USA Dose

{clean_script}

Discover more interesting facts, history, mysteries and surprising stories about America.

Subscribe for daily USA Shorts!

#Shorts #USA #America #USAFacts #DidYouKnow
"""


# ==========================================
# CREATE RELEVANT TAGS
# ==========================================

lower_script = clean_script.lower()

tags = [
    "USA",
    "America",
    "USA facts",
    "American facts",
    "Did You Know",
    "USA Dose",
    "Shorts",
]


# Topic-based tags
topic_keywords = {
    "history": ["USA history", "American history", "history facts"],
    "president": ["US presidents", "American presidents", "president facts"],
    "government": ["US government", "American government"],
    "war": ["American history", "US war history", "war facts"],
    "city": ["US cities", "American cities", "city facts"],
    "town": ["American towns", "US towns", "town facts"],
    "state": ["US states", "American states", "state facts"],
    "texas": ["Texas", "Texas facts"],
    "california": ["California", "California facts"],
    "new york": ["New York", "New York facts"],
    "pennsylvania": ["Pennsylvania", "Pennsylvania facts"],
    "florida": ["Florida", "Florida facts"],
    "science": ["USA science", "science facts", "interesting science"],
    "space": ["NASA", "space facts", "American space"],
    "nasa": ["NASA", "space facts", "American space"],
    "military": ["US military", "military facts", "American military"],
    "crime": ["crime facts", "US crime", "American crime"],
    "mystery": ["USA mysteries", "American mysteries", "mystery facts"],
    "ghost": ["ghost towns", "USA ghost towns", "American mysteries"],
    "food": ["American food", "USA food", "food facts"],
    "money": ["US money", "American money", "money facts"],
    "dollar": ["US dollar", "American money", "dollar facts"],
    "building": ["American landmarks", "US buildings", "USA landmarks"],
    "landmark": ["USA landmarks", "American landmarks", "US places"],
    "road": ["American roads", "US roads", "road facts"],
    "highway": ["US highways", "American highways", "highway facts"],
}

for keyword, keyword_tags in topic_keywords.items():
    if keyword in lower_script:
        for tag in keyword_tags:
            if tag not in tags:
                tags.append(tag)


# Limit tags
tags = tags[:15]


# ==========================================
# YOUTUBE AUTHENTICATION
# ==========================================

print("================================")
print("UPLOADING SHORT TO YOUTUBE")
print("================================")
print("Privacy: PUBLIC")
print("================================")
print("Generated title:")
print(title)
print("================================")
print("Generated tags:")
print(", ".join(tags))
print("================================")


SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload"
]


credentials = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=SCOPES,
)


youtube = build(
    "youtube",
    "v3",
    credentials=credentials,
    cache_discovery=False,
)


# ==========================================
# YOUTUBE UPLOAD DATA
# ==========================================

request_body = {
    "snippet": {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": "25",
        "defaultLanguage": "en",
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": False,
    },
}


# ==========================================
# UPLOAD VIDEO
# ==========================================

media = MediaFileUpload(
    VIDEO_FILE,
    mimetype="video/mp4",
    resumable=True,
)


request = youtube.videos().insert(
    part="snippet,status",
    body=request_body,
    media_body=media,
)


print("Uploading...")

response = request.execute()

video_id = response.get("id")

if not video_id:
    print("ERROR: YouTube did not return a video ID")
    sys.exit(1)


# ==========================================
# SUCCESS
# ==========================================

print("")
print("================================")
print("YOUTUBE UPLOAD SUCCESS")
print("================================")
print("Video ID:", video_id)
print("Privacy: PUBLIC")
print("Title:", title)
print("Tags:", ", ".join(tags))
print("================================")
print("Video uploaded successfully.")
print("================================")
