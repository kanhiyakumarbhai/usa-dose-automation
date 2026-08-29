import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

VIDEO_FILE = "usa_dose_short.mp4"

client_id = os.getenv("YOUTUBE_CLIENT_ID")
client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

if not client_id:
    raise RuntimeError("YOUTUBE_CLIENT_ID is missing")

if not client_secret:
    raise RuntimeError("YOUTUBE_CLIENT_SECRET is missing")

if not refresh_token:
    raise RuntimeError("YOUTUBE_REFRESH_TOKEN is missing")

if not os.path.exists(VIDEO_FILE):
    raise RuntimeError(f"{VIDEO_FILE} not found")

credentials = Credentials(
    token=None,
    refresh_token=refresh_token,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=client_id,
    client_secret=client_secret,
    scopes=["https://www.googleapis.com/auth/youtube.upload"],
)

youtube = build("youtube", "v3", credentials=credentials)

body = {
    "snippet": {
        "title": "Amazing USA Fact! 🇺🇸 #Shorts",
        "description": """🇺🇸 USA Dose

Amazing facts and interesting stories about the United States.

Subscribe for daily USA Shorts!

#USA #America #Shorts #USAFacts
""",
        "tags": [
            "USA",
            "America",
            "United States",
            "USA facts",
            "American facts",
            "Shorts"
        ],
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

print("Starting YouTube upload...")

request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)

response = None

while response is None:
    status, response = request.next_chunk()

    if status:
        progress = int(status.progress() * 100)
        print(f"Upload progress: {progress}%")

video_id = response["id"]

print("================================")
print("YOUTUBE UPLOAD SUCCESSFUL")
print("================================")
print(f"Video ID: {video_id}")
print(f"https://www.youtube.com/watch?v={video_id}")
print("Privacy: PRIVATE")
print("================================")
