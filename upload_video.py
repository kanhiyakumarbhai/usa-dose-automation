import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

VIDEO_FILE = "usa_dose_short.mp4"

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")

if not CLIENT_ID:
    raise RuntimeError("YOUTUBE_CLIENT_ID is missing")

if not CLIENT_SECRET:
    raise RuntimeError("YOUTUBE_CLIENT_SECRET is missing")

if not REFRESH_TOKEN:
    raise RuntimeError("YOUTUBE_REFRESH_TOKEN is missing")

if not os.path.exists(VIDEO_FILE):
    raise RuntimeError(f"{VIDEO_FILE} not found")

credentials = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=["https://www.googleapis.com/auth/youtube.upload"],
)

youtube = build("youtube", "v3", credentials=credentials)

title = "You Won't Believe This USA Fact! 🇺🇸 #Shorts"

description = """🇺🇸 Welcome to USA Dose!

Discover interesting facts, stories and amazing things about the United States.

Subscribe for daily USA Shorts!

#USA #America #Shorts #USA Dose
"""

tags = [
    "USA",
    "United States",
    "America",
    "USA facts",
    "American facts",
    "interesting facts",
    "shorts",
    "USA Dose"
]

body = {
    "snippet": {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": "24"
    },
    "status": {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": False
    }
}

media = MediaFileUpload(
    VIDEO_FILE,
    mimetype="video/mp4",
    resumable=True
)

print("Uploading video to YouTube...")

request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)

response = None

while response is None:
    status, response = request.next_chunk()

    if status:
        print(
            f"Upload progress: "
            f"{int(status.progress() * 100)}%"
        )

video_id = response["id"]

print()
print("================================")
print("YOUTUBE UPLOAD SUCCESSFUL")
print("================================")
print(f"Video ID: {video_id}")
print(f"https://www.youtube.com/watch?v={video_id}")
print("Privacy: PRIVATE")
print("================================")
