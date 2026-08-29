```python
import os
import sys

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


VIDEO_FILE = "usa_dose_short.mp4"

CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

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


print("================================")
print("UPLOADING SHORT TO YOUTUBE")
print("================================")
print("Privacy: PUBLIC")
print("Video:", VIDEO_FILE)
print("================================")


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

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


title = "USA Dose 🇺🇸 | Did You Know This?"

description = """🇺🇸 USA Dose

Interesting facts, history, mysteries and surprising stories from America.

Subscribe for daily USA Shorts!

#Shorts #USA #America #USAFacts #DidYouKnow
"""

tags = [
    "USA",
    "America",
    "USA facts",
    "American facts",
    "did you know",
    "interesting facts",
    "USA Dose",
    "shorts",
]


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


print("")
print("================================")
print("YOUTUBE UPLOAD SUCCESS")
print("================================")
print("Video ID:", video_id)
print("Privacy: PUBLIC")
print("================================")
print("Video uploaded successfully.")
print("================================")
```
