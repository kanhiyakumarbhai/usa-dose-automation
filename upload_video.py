import os
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload


VIDEO_FILE = "usa_dose_short.mp4"

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")


def get_youtube_service():
    if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
        raise RuntimeError(
            "Missing YouTube API credentials. "
            "Check GitHub Secrets."
        )

    credentials = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload"
        ],
    )

    return build(
        "youtube",
        "v3",
        credentials=credentials
    )


def upload_video():
    if not os.path.isfile(VIDEO_FILE):
        raise FileNotFoundError(
            f"{VIDEO_FILE} not found."
        )

    youtube = get_youtube_service()

    title = "USA Dose | Amazing USA Fact #Shorts"

    description = (
        "Discover interesting facts, hidden stories and "
        "amazing places across the United States.\n\n"
        "Subscribe to USA Dose for more USA Shorts!"
    )

    tags = [
        "USA",
        "America",
        "USA facts",
        "American facts",
        "Did you know",
        "US history",
        "USA Dose",
        "Shorts",
    ]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",
        },

        # ==================================================
        # IMPORTANT:
        # PRIVATE ONLY
        # ==================================================
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        VIDEO_FILE,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024,
    )

    print("================================")
    print("UPLOADING USA DOSE SHORT")
    print("================================")
    print("Privacy: PRIVATE")
    print("Automatic PUBLIC publishing: OFF")
    print("")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None

    while response is None:
        status, response = request.next_chunk()

        if status:
            progress = int(status.progress() * 100)
            print(f"Upload progress: {progress}%")

    video_id = response.get("id")

    if not video_id:
        raise RuntimeError(
            "YouTube upload completed but no video ID was returned."
        )

    print("")
    print("================================")
    print("UPLOAD SUCCESS")
    print("================================")
    print(f"Video ID: {video_id}")
    print("Privacy: PRIVATE")
    print("PUBLIC publishing: DISABLED")
    print("================================")


if __name__ == "__main__":
    try:
        upload_video()

    except HttpError as e:
        print("================================")
        print("YOUTUBE API ERROR")
        print("================================")
        print(e)
        sys.exit(1)

    except Exception as e:
        print("================================")
        print("UPLOAD ERROR")
        print("================================")
        print(e)
        sys.exit(1)
