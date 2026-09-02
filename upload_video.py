import os
import re
import sys

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


# ============================================================
# CONFIGURATION
# ============================================================

VIDEO_FILE = "usa_dose_short.mp4"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"

PRIVACY_STATUS = "private"

CATEGORY_ID = "25"


# ============================================================
# YOUTUBE AUTH
# ============================================================

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")


if not CLIENT_ID:
    print("ERROR: YOUTUBE_CLIENT_ID is missing.", flush=True)
    sys.exit(1)

if not CLIENT_SECRET:
    print("ERROR: YOUTUBE_CLIENT_SECRET is missing.", flush=True)
    sys.exit(1)

if not REFRESH_TOKEN:
    print("ERROR: YOUTUBE_REFRESH_TOKEN is missing.", flush=True)
    sys.exit(1)


# ============================================================
# FILE CHECK
# ============================================================

print("================================", flush=True)
print("USA DOSE YOUTUBE AUTO PUBLISHER", flush=True)
print("================================", flush=True)

if not os.path.isfile(VIDEO_FILE):
    print(f"ERROR: {VIDEO_FILE} not found.", flush=True)
    sys.exit(1)

if not os.path.isfile(TITLE_FILE):
    print(f"ERROR: {TITLE_FILE} not found.", flush=True)
    sys.exit(1)

if not os.path.isfile(HASHTAGS_FILE):
    print(f"ERROR: {HASHTAGS_FILE} not found.", flush=True)
    sys.exit(1)


# ============================================================
# READ TITLE
# ============================================================

with open(
    TITLE_FILE,
    "r",
    encoding="utf-8"
) as f:
    title = f.read().strip()


if not title:
    print("ERROR: video_title.txt is empty.", flush=True)
    sys.exit(1)


# ============================================================
# READ GEMINI HASHTAGS
# ============================================================

with open(
    HASHTAGS_FILE,
    "r",
    encoding="utf-8"
) as f:
    generated_hashtags = f.read().strip()


# ============================================================
# HASHTAG BUILDER
# ============================================================

BASE_HASHTAGS = [
    "#USA",
    "#America",
    "#AmericanFacts",
    "#USAHistory",
    "#DidYouKnow",
    "#InterestingFacts",
    "#Facts",
    "#Shorts"
]


def extract_hashtags(text):

    found = re.findall(
        r"#[A-Za-z0-9_]+",
        text
    )

    result = []

    for hashtag in found:

        hashtag = hashtag.strip()

        if hashtag.lower() not in [
            item.lower() for item in result
        ]:

            result.append(hashtag)

    return result


generated_list = extract_hashtags(
    generated_hashtags
)


# ============================================================
# COMBINE HASHTAGS
# ============================================================

hashtags = []

# First add Gemini hashtags
for hashtag in generated_list:

    if hashtag.lower() not in [
        item.lower() for item in hashtags
    ]:

        hashtags.append(hashtag)


# Then add our guaranteed hashtags
for hashtag in BASE_HASHTAGS:

    if hashtag.lower() not in [
        item.lower() for item in hashtags
    ]:

        hashtags.append(hashtag)


# Keep a safe number
hashtags = hashtags[:12]


# Make absolutely sure minimum 7 exist
if len(hashtags) < 7:

    for hashtag in BASE_HASHTAGS:

        if hashtag not in hashtags:

            hashtags.append(hashtag)

        if len(hashtags) >= 7:

            break


# ============================================================
# FINAL HASHTAGS
# ============================================================

final_hashtags = " ".join(hashtags)


print("", flush=True)

print("HASHTAG CHECK", flush=True)
print("--------------------------------", flush=True)

print(
    f"Generated hashtags: {generated_list}",
    flush=True
)

print(
    f"Final hashtag count: {len(hashtags)}",
    flush=True
)

print(
    f"Final hashtags: {final_hashtags}",
    flush=True
)


if len(hashtags) < 7:

    print(
        "ERROR: Could not create 7 hashtags.",
        flush=True
    )

    sys.exit(1)


# ============================================================
# DESCRIPTION
# ============================================================

description = f"""🇺🇸 USA Dose

Discover surprising facts, hidden stories, strange places, inventions, history, and fascinating moments from America.

New USA facts and stories every day.

{final_hashtags}

#Shorts
"""


# ============================================================
# YOUTUBE CREDENTIALS
# ============================================================

credentials = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=[
        "https://www.googleapis.com/auth/youtube.upload"
    ]
)


# ============================================================
# YOUTUBE SERVICE
# ============================================================

print("", flush=True)

print(
    "Connecting to YouTube...",
    flush=True
)

youtube = build(
    "youtube",
    "v3",
    credentials=credentials
)


# ============================================================
# VIDEO UPLOAD
# ============================================================

print("", flush=True)

print("UPLOAD INFORMATION", flush=True)
print("--------------------------------", flush=True)

print(
    f"Title: {title}",
    flush=True
)

print(
    f"Privacy: {PRIVACY_STATUS}",
    flush=True
)

print(
    f"Category: {CATEGORY_ID}",
    flush=True
)

print(
    f"Hashtags: {len(hashtags)}",
    flush=True
)

print("", flush=True)

print(
    "Starting YouTube upload...",
    flush=True
)


body = {
    "snippet": {
        "title": title,
        "description": description,
        "categoryId": CATEGORY_ID,
        "tags": hashtags
    },

    "status": {
        "privacyStatus": PRIVACY_STATUS,
        "selfDeclaredMadeForKids": False
    }
}


media = MediaFileUpload(
    VIDEO_FILE,
    mimetype="video/mp4",
    resumable=True
)


request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)


response = None


try:

    while response is None:

        status, response = request.next_chunk()

        if status:

            progress = int(
                status.progress() * 100
            )

            print(
                f"Upload progress: {progress}%",
                flush=True
            )

except Exception as error:

    print("", flush=True)

    print(
        "================================",
        flush=True
    )

    print(
        "YOUTUBE UPLOAD FAILED",
        flush=True
    )

    print(
        "================================",
        flush=True
    )

    print(
        repr(error),
        flush=True
    )

    sys.exit(1)


# ============================================================
# SUCCESS
# ============================================================

video_id = response.get("id")


if not video_id:

    print(
        "ERROR: YouTube did not return a video ID.",
        flush=True
    )

    print(
        response,
        flush=True
    )

    sys.exit(1)


print("", flush=True)

print(
    "================================",
    flush=True
)

print(
    "YOUTUBE UPLOAD SUCCESS",
    flush=True
)

print(
    "================================",
    flush=True
)

print(
    f"Video ID: {video_id}",
    flush=True
)

print(
    f"Privacy: {PRIVACY_STATUS}",
    flush=True
)

print(
    f"Hashtags: {len(hashtags)}",
    flush=True
)

print("", flush=True)

print(
    "Video uploaded successfully.",
    flush=True
)

print(
    "================================",
    flush=True
)
