import os
import sys
import re
import random
import time
import requests


# ==========================================================
# USA DOSE - SMART PEXELS CLIP DOWNLOADER
# ==========================================================

OUTPUT_DIR = "clips"
SCRIPT_FILE = "daily_script.txt"

PEXELS_API_URL = "https://api.pexels.com/videos/search"

MAX_CLIPS = 6
MIN_CLIPS = 3

REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 90


# ==========================================================
# HELPERS
# ==========================================================

def clean_query(text):

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    words = text.strip().split()

    # Keep search query reasonably short.
    words = words[:8]

    return " ".join(words)


def read_script():

    if not os.path.isfile(SCRIPT_FILE):

        print("")
        print("ERROR: daily_script.txt not found.")
        print("")
        sys.exit(1)

    with open(
        SCRIPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read().strip()

    if not text:

        print("")
        print("ERROR: daily_script.txt is empty.")
        print("")
        sys.exit(1)

    return text


def build_queries(script):

    # Extract useful words from the daily script.
    words = re.findall(
        r"[A-Za-z]{4,}",
        script.lower()
    )

    stopwords = {
        "about",
        "after",
        "again",
        "also",
        "because",
        "being",
        "could",
        "daily",
        "every",
        "from",
        "have",
        "into",
        "just",
        "more",
        "most",
        "only",
        "over",
        "said",
        "some",
        "that",
        "than",
        "their",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "today",
        "very",
        "what",
        "when",
        "where",
        "which",
        "while",
        "with",
        "would",
        "your",
        "news",
    }

    useful = []

    for word in words:

        if word in stopwords:
            continue

        if word not in useful:
            useful.append(word)

    queries = []

    # Most relevant query first.
    if useful:

        queries.append(
            clean_query(
                " ".join(useful[:5])
            )
        )

    if len(useful) >= 2:

        queries.append(
            clean_query(
                " ".join(useful[:3])
            )
        )

    # USA-oriented fallbacks.
    queries.extend([
        "United States America",
        "USA city",
        "American people",
        "United States business",
        "American technology",
        "New York USA",
        "Washington DC USA",
        "Los Angeles USA",
        "Chicago USA",
    ])

    # Remove duplicates.
    final_queries = []

    for query in queries:

        query = query.strip()

        if not query:
            continue

        if query.lower() not in [
            q.lower()
            for q in final_queries
        ]:

            final_queries.append(
                query
            )

    return final_queries


def clear_old_clips():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    removed = 0

    for filename in os.listdir(
        OUTPUT_DIR
    ):

        path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        if not os.path.isfile(path):
            continue

        if filename.lower().endswith(
            (
                ".mp4",
                ".mov",
                ".mkv",
                ".webm"
            )
        ):

            try:

                os.remove(path)

                removed += 1

            except Exception as error:

                print(
                    "Could not remove:",
                    path,
                    error
                )

    print(
        f"Old clips removed: {removed}"
    )


def get_video_file(video):

    files = video.get(
        "video_files",
        []
    )

    if not files:
        return None

    portrait = []
    usable = []

    for item in files:

        link = item.get("link")

        width = item.get(
            "width"
        ) or 0

        height = item.get(
            "height"
        ) or 0

        if not link:
            continue

        # Ignore extremely small files.
        if width < 480 or height < 480:
            continue

        usable.append(item)

        if height >= width:
            portrait.append(item)

    candidates = (
        portrait
        if portrait
        else usable
    )

    if not candidates:
        return None

    # Prefer a good HD-ish file without
    # downloading huge 4K files.
    def score(item):

        width = item.get(
            "width"
        ) or 0

        height = item.get(
            "height"
        ) or 0

        area = width * height

        # Prefer 720p-1080p range.
        if height >= 1080:
            penalty = abs(
                height - 1080
            )
        else:
            penalty = abs(
                height - 720
            )

        return (
            penalty,
            area
        )

    candidates.sort(
        key=score
    )

    return candidates[0]


def search_pexels(
    session,
    api_key,
    query
):

    print("")
    print("--------------------------------")
    print(
        f"Searching Pexels: {query}"
    )
    print("--------------------------------")

    headers = {
        "Authorization": api_key
    }

    params = {
        "query": query,
        "orientation": "portrait",
        "size": "medium",
        "per_page": 15,
    }

    try:

        response = session.get(
            PEXELS_API_URL,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

    except Exception as error:

        print(
            "Pexels request error:",
            error
        )

        return []

    if response.status_code != 200:

        print(
            "Pexels HTTP error:",
            response.status_code
        )

        print(
            response.text[:500]
        )

        return []

    try:

        data = response.json()

    except Exception:

        print(
            "ERROR: Invalid Pexels response."
        )

        return []

    videos = data.get(
        "videos",
        []
    )

    if not videos:

        print(
            "No videos found."
        )

        return []

    random.shuffle(
        videos
    )

    return videos


def download_video(
    session,
    url,
    filename
):

    temporary = (
        filename
        + ".part"
    )

    try:

        print(
            "Downloading:",
            filename
        )

        response = session.get(
            url,
            stream=True,
            timeout=DOWNLOAD_TIMEOUT
        )

        if response.status_code != 200:

            print(
                "Download failed:",
                response.status_code
            )

            return False

        with open(
            temporary,
            "wb"
        ) as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:

                    file.write(
                        chunk
                    )

        if not os.path.isfile(
            temporary
        ):

            return False

        size = os.path.getsize(
            temporary
        )

        # Reject broken/tiny files.
        if size < 50_000:

            print(
                "Downloaded file is too small."
            )

            try:
                os.remove(
                    temporary
                )
            except Exception:
                pass

            return False

        os.replace(
            temporary,
            filename
        )

        print(
            "Download successful:",
            f"{size:,} bytes"
        )

        return True

    except Exception as error:

        print(
            "Download error:",
            error
        )

        try:

            if os.path.isfile(
                temporary
            ):

                os.remove(
                    temporary
                )

        except Exception:
            pass

        return False


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("")
    print("================================")
    print("USA DOSE SMART CLIP DOWNLOADER")
    print("================================")

    api_key = os.getenv(
        "PEXELS_API_KEY"
    )

    if not api_key:

        print("")
        print(
            "ERROR: PEXELS_API_KEY is missing."
        )
        print("")
        print(
            "Add PEXELS_API_KEY in:"
        )
        print(
            "GitHub → Settings → Secrets and variables"
        )
        print(
            "→ Actions"
        )
        print("")

        sys.exit(1)

    script = read_script()

    print("")
    print("Daily script:")
    print("--------------------------------")
    print(script)
    print("--------------------------------")

    clear_old_clips()

    queries = build_queries(
        script
    )

    print("")
    print("Search queries:")
    print("--------------------------------")

    for query in queries:

        print(
            "-",
            query
        )

    print("--------------------------------")

    session = requests.Session()

    downloaded = 0

    used_video_ids = set()

    for query in queries:

        if downloaded >= MAX_CLIPS:
            break

        videos = search_pexels(
            session,
            api_key,
            query
        )

        for video in videos:

            if downloaded >= MAX_CLIPS:
                break

            video_id = video.get(
                "id"
            )

            if video_id in used_video_ids:
                continue

            selected = get_video_file(
                video
            )

            if not selected:
                continue

            url = selected.get(
                "link"
            )

            if not url:
                continue

            used_video_ids.add(
                video_id
            )

            filename = os.path.join(
                OUTPUT_DIR,
                f"clip_{downloaded + 1}.mp4"
            )

            success = download_video(
                session,
                url,
                filename
            )

            if success:

                downloaded += 1

                print(
                    f"Usable clips: "
                    f"{downloaded}/{MAX_CLIPS}"
                )

        # Small delay between searches.
        time.sleep(1)

    print("")
    print("================================")
    print("CLIP DOWNLOAD COMPLETE")
    print("================================")
    print(
        f"Usable clips: {downloaded}"
    )
    print(
        f"Required minimum: {MIN_CLIPS}"
    )
    print("================================")

    if downloaded < MIN_CLIPS:

        print("")
        print(
            "ERROR: Not enough usable clips."
        )

        print(
            "Video generation will stop safely."
        )

        print("")
        print(
            "Possible causes:"
        )
        print(
            "1. PEXELS_API_KEY is invalid."
        )
        print(
            "2. Pexels returned no suitable videos."
        )
        print(
            "3. Pexels API request was blocked."
        )

        sys.exit(1)

    print("")
    print(
        "Clips ready for create_video.py:"
    )

    for filename in sorted(
        os.listdir(OUTPUT_DIR)
    ):

        path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        if os.path.isfile(path):

            print(
                " -",
                path
            )

    print("")
    print(
        "Clip downloader: SUCCESS"
    )
    print(
        "create_video.py can continue."
    )


if __name__ == "__main__":

    main()
