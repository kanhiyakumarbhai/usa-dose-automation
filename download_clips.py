import os
import re
import sys
import time
import requests
from urllib.parse import quote

# ============================================================
# USA DOSE - SMART TOPIC BASED PEXELS CLIP DOWNLOADER
# ============================================================

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

if not PEXELS_API_KEY:
    print("ERROR: PEXELS_API_KEY is missing.")
    sys.exit(1)

SCRIPT_FILE = "daily_script.txt"
CLIPS_DIR = "clips"

PEXELS_URL = "https://api.pexels.com/v1/videos/search"

HEADERS = {
    "Authorization": PEXELS_API_KEY
}

# Number of clips to download
TARGET_CLIPS = 5

# Minimum clips required for video creation
MIN_CLIPS = 3

# Pexels settings
PER_PAGE = 15
VIDEO_ORIENTATION = "portrait"


# ============================================================
# READ DAILY SCRIPT
# ============================================================

def read_script():

    if not os.path.exists(SCRIPT_FILE):
        print(f"ERROR: {SCRIPT_FILE} not found.")
        sys.exit(1)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read().strip()

    if not script:
        print("ERROR: daily_script.txt is empty.")
        sys.exit(1)

    print()
    print("========================================")
    print("TODAY'S SCRIPT")
    print("========================================")
    print(script)
    print()

    return script


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = text.lower()

    # Remove URLs
    text = re.sub(r"https?://\S+", " ", text)

    # Remove punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "about",
    "after",
    "again",
    "almost",
    "also",
    "because",
    "being",
    "before",
    "between",
    "could",
    "every",
    "from",
    "going",
    "have",
    "into",
    "just",
    "like",
    "more",
    "most",
    "never",
    "only",
    "other",
    "over",
    "people",
    "really",
    "some",
    "than",
    "that",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "very",
    "what",
    "when",
    "where",
    "which",
    "while",
    "will",
    "with",
    "would",
    "your",
    "you",
    "once",
    "still",
    "story",
    "thing",
    "things",
    "today",
    "american",
    "america",
    "united",
    "states",
    "usa",
}


# ============================================================
# TOPIC KEYWORD EXTRACTION
# ============================================================

def extract_keywords(script):

    cleaned = clean_text(script)

    words = cleaned.split()

    # Count words
    frequency = {}

    for word in words:

        if len(word) < 4:
            continue

        if word in STOP_WORDS:
            continue

        frequency[word] = frequency.get(word, 0) + 1

    # Sort by frequency
    sorted_words = sorted(
        frequency.items(),
        key=lambda x: (-x[1], -len(x[0]))
    )

    keywords = []

    for word, count in sorted_words:

        if word not in keywords:
            keywords.append(word)

        if len(keywords) >= 8:
            break

    print("Extracted keywords:")
    print(", ".join(keywords))
    print()

    return keywords


# ============================================================
# TOPIC TYPE DETECTION
# ============================================================

def detect_topic_type(script):

    text = clean_text(script)

    topic_types = []

    categories = {

        "city": [
            "city",
            "town",
            "village",
            "population",
            "downtown",
            "street",
            "neighborhood"
        ],

        "history": [
            "history",
            "historical",
            "century",
            "war",
            "president",
            "ancient",
            "historic",
            "founded"
        ],

        "building": [
            "building",
            "house",
            "hotel",
            "tower",
            "bridge",
            "prison",
            "school",
            "church",
            "museum"
        ],

        "disaster": [
            "disaster",
            "fire",
            "flood",
            "storm",
            "hurricane",
            "earthquake",
            "explosion",
            "crash",
            "accident"
        ],

        "technology": [
            "technology",
            "computer",
            "internet",
            "machine",
            "invention",
            "invention",
            "robot",
            "engineering",
            "software"
        ],

        "business": [
            "business",
            "company",
            "money",
            "market",
            "store",
            "factory",
            "industry",
            "corporation"
        ],

        "road": [
            "road",
            "highway",
            "traffic",
            "car",
            "truck",
            "route",
            "driving"
        ],

        "nature": [
            "mountain",
            "forest",
            "desert",
            "river",
            "lake",
            "ocean",
            "waterfall",
            "canyon"
        ],

        "people": [
            "man",
            "woman",
            "person",
            "people",
            "family",
            "worker",
            "soldier",
            "president"
        ]
    }

    for category, words in categories.items():

        for word in words:

            if word in text:
                topic_types.append(category)
                break

    # Default
    if not topic_types:
        topic_types.append("general")

    print("Detected topic type:")
    print(", ".join(topic_types))
    print()

    return topic_types


# ============================================================
# BUILD SEARCH QUERIES
# ============================================================

def build_queries(script, keywords, topic_types):

    queries = []

    # --------------------------------------------------------
    # Main keyword combinations
    # --------------------------------------------------------

    if len(keywords) >= 2:

        queries.append(
            f"{keywords[0]} {keywords[1]} USA"
        )

    if len(keywords) >= 3:

        queries.append(
            f"{keywords[0]} {keywords[1]} {keywords[2]}"
        )

    # --------------------------------------------------------
    # Topic-specific searches
    # --------------------------------------------------------

    for topic in topic_types:

        if keywords:

            queries.append(
                f"{keywords[0]} {topic} USA"
            )

        if len(keywords) >= 2:

            queries.append(
                f"{keywords[1]} {topic} USA"
            )

    # --------------------------------------------------------
    # Strong generic fallback based on topic
    # --------------------------------------------------------

    if "city" in topic_types:

        queries.extend([
            "American city skyline",
            "American small town",
            "USA downtown street"
        ])

    if "history" in topic_types:

        queries.extend([
            "American history",
            "historic America",
            "old American town"
        ])

    if "building" in topic_types:

        queries.extend([
            "historic American building",
            "old building America",
            "American architecture"
        ])

    if "disaster" in topic_types:

        queries.extend([
            "storm USA",
            "flood America",
            "disaster aftermath"
        ])

    if "technology" in topic_types:

        queries.extend([
            "American technology",
            "modern technology",
            "technology machine"
        ])

    if "business" in topic_types:

        queries.extend([
            "American business",
            "American factory",
            "American shopping"
        ])

    if "road" in topic_types:

        queries.extend([
            "American highway",
            "USA road driving",
            "American traffic"
        ])

    if "nature" in topic_types:

        queries.extend([
            "American landscape",
            "USA mountains",
            "American nature"
        ])

    if "people" in topic_types:

        queries.extend([
            "American people",
            "American workers",
            "people USA"
        ])

    # --------------------------------------------------------
    # General fallback
    # --------------------------------------------------------

    queries.extend([
        "USA city",
        "United States",
        "American landscape"
    ])

    # Remove duplicates
    final_queries = []

    for query in queries:

        query = query.strip()

        if not query:
            continue

        if query.lower() not in [
            q.lower() for q in final_queries
        ]:
            final_queries.append(query)

    print("Pexels search queries:")
    for q in final_queries:
        print(" -", q)

    print()

    return final_queries


# ============================================================
# SEARCH PEXELS
# ============================================================

def search_pexels(query):

    params = {
        "query": query,
        "orientation": VIDEO_ORIENTATION,
        "size": "medium",
        "per_page": PER_PAGE
    }

    try:

        response = requests.get(
            PEXELS_URL,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        if response.status_code != 200:

            print(
                f"Pexels error {response.status_code} "
                f"for query: {query}"
            )

            return []

        data = response.json()

        return data.get("videos", [])

    except requests.RequestException as e:

        print(f"Pexels request failed: {e}")

        return []


# ============================================================
# CHOOSE VIDEO FILE
# ============================================================

def choose_video_file(video):

    files = video.get("video_files", [])

    if not files:
        return None

    candidates = []

    for file in files:

        width = file.get("width") or 0
        height = file.get("height") or 0
        link = file.get("link")

        if not link:
            continue

        # Prefer portrait
        portrait = height > width

        # Prefer reasonable resolution
        if height >= 1000:
            quality_score = 3
        elif height >= 700:
            quality_score = 2
        else:
            quality_score = 1

        score = (
            100 if portrait else 0
        ) + quality_score

        candidates.append(
            (score, height, link)
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (x[0], x[1]),
        reverse=True
    )

    return candidates[0][2]


# ============================================================
# DOWNLOAD FILE
# ============================================================

def download_file(url, output_path):

    try:

        response = requests.get(
            url,
            stream=True,
            timeout=60
        )

        if response.status_code != 200:

            print(
                f"Download failed: HTTP "
                f"{response.status_code}"
            )

            return False

        with open(output_path, "wb") as f:

            for chunk in response.iter_content(
                chunk_size=1024 * 256
            ):

                if chunk:
                    f.write(chunk)

        # Check file size
        size = os.path.getsize(output_path)

        if size < 10000:

            print(
                f"Downloaded file is too small: "
                f"{size} bytes"
            )

            os.remove(output_path)

            return False

        return True

    except requests.RequestException as e:

        print(f"Download error: {e}")

        if os.path.exists(output_path):
            os.remove(output_path)

        return False


# ============================================================
# CLEAR OLD CLIPS
# ============================================================

def clear_old_clips():

    os.makedirs(CLIPS_DIR, exist_ok=True)

    removed = 0

    for filename in os.listdir(CLIPS_DIR):

        path = os.path.join(
            CLIPS_DIR,
            filename
        )

        if os.path.isfile(path):

            try:

                os.remove(path)
                removed += 1

            except OSError as e:

                print(
                    f"Could not remove {filename}: {e}"
                )

    print(
        f"Removed {removed} old clips."
    )

    print()


# ============================================================
# DOWNLOAD SMART CLIPS
# ============================================================

def download_clips(script):

    keywords = extract_keywords(script)

    topic_types = detect_topic_type(script)

    queries = build_queries(
        script,
        keywords,
        topic_types
    )

    downloaded = []

    seen_ids = set()

    clip_number = 1

    # --------------------------------------------------------
    # Search every query until enough clips are found
    # --------------------------------------------------------

    for query in queries:

        if len(downloaded) >= TARGET_CLIPS:
            break

        print("========================================")
        print(f"SEARCHING: {query}")
        print("========================================")

        videos = search_pexels(query)

        print(
            f"Found {len(videos)} videos."
        )

        for video in videos:

            if len(downloaded) >= TARGET_CLIPS:
                break

            video_id = video.get("id")

            if video_id in seen_ids:
                continue

            seen_ids.add(video_id)

            video_url = choose_video_file(video)

            if not video_url:
                continue

            output_file = os.path.join(
                CLIPS_DIR,
                f"clip_{clip_number:02d}.mp4"
            )

            print(
                f"Downloading clip "
                f"{clip_number}: {query}"
            )

            success = download_file(
                video_url,
                output_file
            )

            if success:

                downloaded.append(
                    output_file
                )

                print(
                    f"✓ Saved: {output_file}"
                )

                clip_number += 1

            else:

                print("✗ Download failed.")

            print()

            # Small delay to avoid hammering API
            time.sleep(0.5)

    return downloaded


# ============================================================
# VALIDATE CLIPS
# ============================================================

def validate_clips(downloaded):

    valid_files = []

    for path in downloaded:

        if not os.path.exists(path):
            continue

        try:

            size = os.path.getsize(path)

            if size >= 10000:
                valid_files.append(path)

        except OSError:
            continue

    print()
    print("========================================")
    print("CLIP VALIDATION")
    print("========================================")
    print(
        f"Usable clips: "
        f"{len(valid_files)}"
    )
    print()

    if len(valid_files) < MIN_CLIPS:

        print(
            f"ERROR: Only {len(valid_files)} "
            f"usable clips downloaded."
        )

        print(
            f"At least {MIN_CLIPS} clips are required."
        )

        return False

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("========================================")
    print("USA DOSE SMART PEXELS DOWNLOADER")
    print("========================================")
    print()

    script = read_script()

    clear_old_clips()

    downloaded = download_clips(
        script
    )

    if not validate_clips(downloaded):

        print()
        print(
            "Clip download failed."
        )

        sys.exit(1)

    print("========================================")
    print("CLIP DOWNLOAD SUCCESSFUL")
    print("========================================")

    for clip in downloaded:
        print("✓", clip)

    print()
    print(
        f"Total clips downloaded: "
        f"{len(downloaded)}"
    )

    print()
    print(
        "USA Dose smart clip download "
        "completed successfully."
    )


if __name__ == "__main__":
    main()
