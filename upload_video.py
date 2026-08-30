import os
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload


VIDEO_FILE = "usa_dose_short.mp4"


def read_file(filename, fallback=""):
    if not os.path.isfile(filename):
        return fallback

    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_youtube_service():
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError(
            "YouTube API credentials are missing."
        )

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload"
        ],
    )

    return build(
        "youtube",
        "v3",
        credentials=credentials,
    )


def upload_video():
    if not os.path.isfile(VIDEO_FILE):
        raise FileNotFoundError(
            f"{VIDEO_FILE} not found."
        )

    title = read_file(
        "video_title.txt",
        "USA Dose - Amazing USA Fact",
    )

    hashtags_text = read_file(
        "video_hashtags.txt",
        "#USA #America #USAFacts #DidYouKnow #Shorts",
    )

    hashtags = hashtags_text.split()

    # Make sure there are at least 5 tags.
    if len(hashtags) < 5:
        raise RuntimeError(
            "At least 5 relevant hashtags are required."
        )

    description = (
        "Discover fascinating facts, hidden stories, "
        "history and surprising places across America.\n\n"
        + hashtags_text
        + "\n\n"
        "Subscribe to USA Dose for more interesting "
        "stories about the United States."
    )

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": hashtags,
            "categoryId": "27",
        },

        # PRIVATE ONLY
        # Automatic public publishing is OFF.
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
        },
    }

    youtube = get_youtube_service()

    media = MediaFileUpload(
        VIDEO_FILE,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024,
    )

    print("================================")
    print("UPLOADING USA DOSE SHORT")
    print("================================")
    print(f"TITLE: {title}")
    print(f"HASHTAGS: {hashtags_text}")
    print("PRIVACY: PRIVATE")
    print("PUBLIC: OFF")
    print("================================")

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
            "Upload finished but YouTube returned no video ID."
        )

    print("")
    print("================================")
    print("UPLOAD SUCCESS")
    print("================================")
    print(f"Video ID: {video_id}")
    print("Privacy: PRIVATE")
    print("Automatic PUBLIC: OFF")
    print("================================")


if __name__ == "__main__":
    try:
        upload_video()

    except HttpError as e:
        print("YouTube API ERROR:")
        print(e)
        sys.exit(1)

    except Exception as e:
        print("ERROR:")
        print(e)
        sys.exit(1)
