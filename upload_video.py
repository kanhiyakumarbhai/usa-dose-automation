import os
import sys

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


# ==========================================================
# USA DOSE - YOUTUBE UPLOADER
# ==========================================================

VIDEO_FILE = "usa_dose_short.mp4"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"

# IMPORTANT:
# Keep videos PRIVATE.
PRIVACY_STATUS = "private"


# ==========================================================
# READ FILE
# ==========================================================

def read_file(filename):

    if not os.path.isfile(filename):

        print(f"ERROR: {filename} not found.")
        sys.exit(1)

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read().strip()


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("================================")
    print("USA DOSE YOUTUBE UPLOADER")
    print("================================")

    # ------------------------------------------------------
    # CHECK VIDEO
    # ------------------------------------------------------

    if not os.path.isfile(VIDEO_FILE):

        print(
            f"ERROR: {VIDEO_FILE} not found."
        )
        sys.exit(1)

    # ------------------------------------------------------
    # YOUTUBE CREDENTIALS
    # ------------------------------------------------------

    client_id = os.getenv(
        "YOUTUBE_CLIENT_ID"
    )

    client_secret = os.getenv(
        "YOUTUBE_CLIENT_SECRET"
    )

    refresh_token = os.getenv(
        "YOUTUBE_REFRESH_TOKEN"
    )

    if not client_id:

        print(
            "ERROR: YOUTUBE_CLIENT_ID missing."
        )
        sys.exit(1)

    if not client_secret:

        print(
            "ERROR: YOUTUBE_CLIENT_SECRET missing."
        )
        sys.exit(1)

    if not refresh_token:

        print(
            "ERROR: YOUTUBE_REFRESH_TOKEN missing."
        )
        sys.exit(1)

    # ------------------------------------------------------
    # READ TITLE
    # ------------------------------------------------------

    title = read_file(
        TITLE_FILE
    )

    # ------------------------------------------------------
    # READ HASHTAGS
    # ------------------------------------------------------

    hashtags = read_file(
        HASHTAGS_FILE
    )

    if not title:

        print(
            "ERROR: YouTube title is empty."
        )
        sys.exit(1)

    if not hashtags:

        print(
            "ERROR: YouTube hashtags are empty."
        )
        sys.exit(1)

    # ------------------------------------------------------
    # CLEAN TITLE
    # ------------------------------------------------------

    title = title.replace(
        "\n",
        " "
    ).strip()

    if len(title) > 100:

        title = title[:97] + "..."

    # ------------------------------------------------------
    # DESCRIPTION
    # ------------------------------------------------------

    description = (
        "🇺🇸 USA Dose\n\n"
        "Discover surprising facts, history, "
        "places, inventions and stories from "
        "the United States.\n\n"
        f"{hashtags}\n\n"
        "#Shorts"
    )

    # ------------------------------------------------------
    # YOUTUBE CLIENT
    # ------------------------------------------------------

    print("")
    print("Connecting to YouTube...")

    try:

        credentials = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[
                "https://www.googleapis.com/auth/youtube.upload"
            ],
        )

        youtube = build(
            "youtube",
            "v3",
            credentials=credentials
        )

    except Exception as e:

        print("")
        print("YOUTUBE AUTHENTICATION ERROR")
        print(e)
        sys.exit(1)

    # ------------------------------------------------------
    # UPLOAD
    # ------------------------------------------------------

    print("")
    print("================================")
    print("UPLOADING SHORT")
    print("================================")
    print("")
    print(f"Title: {title}")
    print("")
    print(f"Hashtags: {hashtags}")
    print("")
    print(f"Privacy: {PRIVACY_STATUS}")
    print("")
    print("Uploading...")
    print("")

    try:

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "categoryId": "25",
                    "tags": [
                        tag.replace(
                            "#",
                            ""
                        )
                        for tag in hashtags.split()
                        if tag.startswith("#")
                    ],
                },
                "status": {
                    "privacyStatus": PRIVACY_STATUS,
                    "selfDeclaredMadeForKids": False,
                },
            },
            media_body=MediaFileUpload(
                VIDEO_FILE,
                chunksize=-1,
                resumable=True
            ),
        )

        response = request.execute()

    except Exception as e:

        print("")
        print("================================")
        print("YOUTUBE UPLOAD ERROR")
        print("================================")
        print(e)
        sys.exit(1)

    # ------------------------------------------------------
    # RESULT
    # ------------------------------------------------------

    video_id = response.get(
        "id"
    )

    if not video_id:

        print(
            "ERROR: YouTube did not return a video ID."
        )
        sys.exit(1)

    print("")
    print("================================")
    print("UPLOAD SUCCESS")
    print("================================")
    print("")
    print(f"Video ID: {video_id}")
    print(f"Title: {title}")
    print(f"Privacy: {PRIVACY_STATUS}")
    print("")
    print(
        "Video uploaded as PRIVATE."
    )
    print("")
    print("================================")


if __name__ == "__main__":
    main()
