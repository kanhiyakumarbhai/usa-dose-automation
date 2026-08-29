import os
import sys
import requests
import random

OUTPUT_DIR = "clips"
API_KEY = os.getenv("PEXELS_API_KEY")

if not API_KEY:
    print("ERROR: PEXELS_API_KEY is missing")
    sys.exit(1)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# USA-related searches.
queries = [
    "United States America city",
    "New York USA",
    "American highway",
    "USA city skyline",
    "American people",
    "United States business",
    "American technology",
    "Washington DC USA",
    "Los Angeles USA",
    "Chicago USA",
]

random.shuffle(queries)

headers = {
    "Authorization": API_KEY
}

print("================================")
print("Downloading USA Stock Videos")
print("================================")

downloaded = 0

for query in queries:

    if downloaded >= 5:
        break

    print()
    print("Searching:", query)

    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={
                "query": query,
                "orientation": "portrait",
                "size": "medium",
                "per_page": 10
            },
            timeout=30
        )
    except Exception as e:
        print("Request error:", e)
        continue

    if response.status_code != 200:
        print("Pexels error:", response.status_code)
        print(response.text)
        continue

    videos = response.json().get("videos", [])

    if not videos:
        print("No videos found.")
        continue

    random.shuffle(videos)

    for video in videos:

        if downloaded >= 5:
            break

        files = video.get("video_files", [])

        # Prefer portrait files.
        suitable = []

        for file in files:
            width = file.get("width") or 0
            height = file.get("height") or 0
            link = file.get("link")

            if not link:
                continue

            if height > width:
                suitable.append(file)

        # If no portrait file exists, use the best available file.
        if not suitable:
            suitable = [
                f for f in files
                if f.get("link")
            ]

        if not suitable:
            continue

        # Prefer smaller files for GitHub Actions.
        suitable.sort(
            key=lambda f: (
                (f.get("width") or 99999) *
                (f.get("height") or 99999)
            )
        )

        selected = suitable[0]
        url = selected.get("link")

        filename = os.path.join(
            OUTPUT_DIR,
            f"clip_{downloaded + 1}.mp4"
        )

        print("Downloading:", filename)

        try:
            r = requests.get(
                url,
                stream=True,
                timeout=60
            )

            if r.status_code != 200:
                print("Download failed:", r.status_code)
                continue

            with open(filename, "wb") as f:
                for chunk in r.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if chunk:
                        f.write(chunk)

            if os.path.getsize(filename) < 10000:
                os.remove(filename)
                continue

            print("Downloaded successfully.")
            downloaded += 1

        except Exception as e:
            print("Download error:", e)

print()
print("================================")
print("DOWNLOAD COMPLETE")
print("================================")
print("Videos downloaded:", downloaded)

if downloaded < 3:
    print("ERROR: Less than 3 usable videos downloaded.")
    sys.exit(1)

for filename in sorted(os.listdir(OUTPUT_DIR)):
    print(" -", filename)

print("================================")
