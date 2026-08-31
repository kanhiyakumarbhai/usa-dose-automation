import os
import sys
import re

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


# ==========================================================
# USA DOSE - YOUTUBE AUTO PUBLISHER
# ==========================================================

VIDEO_FILE = "usa_dose_short.mp4"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"

# ==========================================================
# PUBLISH SETTING
# ==========================================================
# Video will be PUBLIC immediately after upload.
PRIVACY_STATUS = "public"


# ==========================================================
# READ FILE
# ==========================================================

def read_file(filename):

    if not os.path.isfile(filename):
        print(f"ERROR: {filename} not found.")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()


# ==========================================================
# CLEAN TITLE
# ==========================================================

def clean_title(title):

    title = title.replace("\n", " ")
    title = re.sub(r"\s+", " ", title)
    title = title.strip()

    if len(title) > 100:
        title = title[:97] + "..."

    return title


# ==========================================================
# CLEAN HASHTAGS
# ==========================================================

def clean_hashtags(text):

    hashtags = re.findall(
        r"#[A-Za-z0-9_]+",
        text
    )

    unique = []
    seen = set()

    for tag in hashtags:

        key = tag.lower()

        if key not in seen:
            seen.add(key)
            unique.append(tag)

    # Always include Shorts
    if "#shorts" not in seen:
        unique.append("#Shorts")

    return unique


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("================================")
    print("USA DOSE YOUTUBE AUTO PUBLISHER")
    print("================================")

    # ------------------------------------------------------
    # CHECK VIDEO
    # ------------------------------------------------------

    if not os.path.isfile(VIDEO_FILE):

        print(f"ERROR: {VIDEO_FILE} not found.")
        sys.exit(1)

    if os.path.getsize(VIDEO_FILE) == 0:

        print(f"ERROR: {VIDEO_FILE} is empty.")
        sys.exit(1)

    # ------------------------------------------------------
    # CHECK CREDENTIALS
    # ------------------------------------------------------

    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not client_id:
        print("ERROR: YOUTUBE_CLIENT_ID missing.")
        sys.exit(1)

    if not client_secret:
        print("ERROR: YOUTUBE_CLIENT_SECRET missing.")
        sys.exit(1)

    if not refresh_token:
        print("ERROR: YOUTUBE_REFRESH_TOKEN missing.")
        sys.exit(1)

    # ------------------------------------------------------
    # READ TITLE
    # ------------------------------------------------------

    title = read_file(TITLE_FILE)
    title = clean_title(title)

    if not title:

        print("ERROR: YouTube title is empty.")
        sys.exit(1)

    # ------------------------------------------------------
    # READ HASHTAGS
    # ------------------------------------------------------

    hashtags_raw = read_file(HASHTAGS_FILE)
    hashtags = clean_hashtags(hashtags_raw)

    if len(hashtags) < 7:

        print(
            f"ERROR: Only {len(hashtags)} hashtags found."
        )
        print("At least 7 hashtags are required.")
        sys.exit(1)

    # ------------------------------------------------------
    # DESCRIPTION
    # ------------------------------------------------------

    hashtag_text = " ".join(hashtags)

    description = (
        "🇺🇸 USA Dose\n\n"
        "Discover surprising facts, history, "
        "places, inventions and stories from "
        "the United States.\n\n"
        f"{hashtag_text}"
    )

    # ------------------------------------------------------
    # DISPLAY INFORMATION
    # ------------------------------------------------------

    print("")
    print("================================")
    print("VIDEO INFORMATION")
    print("================================")
    print(f"Title: {title}")
    print(f"Hashtags: {hashtag_text}")
    print(f"Hashtag count: {len(hashtags)}")
    print(f"Privacy: {PRIVACY_STATUS}")
    print("================================")

    # ------------------------------------------------------
    # YOUTUBE AUTHENTICATION
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
        print("================================")
        print("YOUTUBE AUTHENTICATION ERROR")
        print("================================")
        print(e)
        sys.exit(1)

    # ------------------------------------------------------
    # UPLOAD
    # ------------------------------------------------------

    print("")
    print("================================")
    print("UPLOADING AND PUBLISHING SHORT")
    print("================================")
    print("")
    print("Privacy: PUBLIC")
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

                    # People & Blogs
                    "categoryId": "22",

                    "tags": [
                        tag.lstrip("#")
                        for tag in hashtags
                    ],
                },

                "status": {

                    # IMPORTANT:
                    # Publish immediately
                    "privacyStatus": "public",

                    "selfDeclaredMadeForKids": False,
                },
            },

            media_body=MediaFileUpload(
                VIDEO_FILE,
                mimetype="video/mp4",
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
    # VIDEO ID
    # ------------------------------------------------------

    video_id = response.get("id")

    if not video_id:

        print("")
        print("ERROR: YouTube did not return a video ID.")
        sys.exit(1)

    # ------------------------------------------------------
    # FINAL SUCCESS
    # ------------------------------------------------------

    print("")
    print("================================")
    print("YOUTUBE PUBLISH SUCCESS")
    print("================================")
    print("")
    print(f"Video ID: {video_id}")
    print(f"Title: {title}")
    print("Privacy: PUBLIC")
    print("")
    print("Video has been uploaded and published.")
    print("")
    print(
        f"https://www.youtube.com/watch?v={video_id}"
    )
    print("")
    print("================================")


if __name__ == "__main__":
    main()
