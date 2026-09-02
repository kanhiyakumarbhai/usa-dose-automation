import os
import re
import sys
import time
from datetime import datetime

from google import genai

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY is missing.")
    sys.exit(1)

print("Creating Gemini client...", flush=True)

client = genai.Client(
    api_key=API_KEY
)

MODEL = "gemini-3.7-flash"

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"


PROMPT = """
Write ONE original USA-related YouTube Short.

Audience: adults 18-70.

Rules:
- 75-105 words.
- Strong curiosity hook in the first sentence.
- One surprising factual USA story.
- Build suspense.
- Do not reveal the answer immediately.
- Simple natural American English.
- Fast storytelling.
- No politics.
- No fake or exaggerated claims.
- No emojis.
- End with a natural question.

Return ONLY this:

SCRIPT:
[75-105 word narration]

TITLE:
[short curiosity title]

HASHTAGS:
#USA #America #Facts #Shorts
"""


def clean(text):
    text = text.strip()
    text = text.replace("```text", "")
    text = text.replace("```txt", "")
    text = text.replace("```", "")
    return text.strip()


def parse_response(text):
    text = clean(text)

    script_match = re.search(
        r"SCRIPT:\s*(.*?)(?=\n\s*TITLE:)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    title_match = re.search(
        r"TITLE:\s*(.*?)(?=\n\s*HASHTAGS:)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    hashtags_match = re.search(
        r"HASHTAGS:\s*(.*)$",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not script_match:
        raise ValueError("SCRIPT section missing.")

    if not title_match:
        raise ValueError("TITLE section missing.")

    if not hashtags_match:
        raise ValueError("HASHTAGS section missing.")

    script = clean(script_match.group(1))
    title = clean(title_match.group(1))
    hashtags = clean(hashtags_match.group(1))

    return script, title, hashtags


def validate(script, title, hashtags):

    word_count = len(script.split())

    print(f"Generated words: {word_count}", flush=True)

    if word_count < 60:
        raise ValueError(
            f"Script too short: {word_count} words"
        )

    if word_count > 120:
        raise ValueError(
            f"Script too long: {word_count} words"
        )

    if "#USA" not in hashtags:
        hashtags += " #USA"

    if "#Shorts" not in hashtags:
        hashtags += " #Shorts"

    return script, title, hashtags


def generate():

    print("================================", flush=True)
    print("USA DOSE SCRIPT GENERATOR", flush=True)
    print("================================", flush=True)

    print(
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        flush=True
    )

    print(
        f"Model: {MODEL}",
        flush=True
    )

    print(
        "Starting Gemini request...",
        flush=True
    )

    start = time.time()

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=PROMPT
        )

    except Exception as e:

        print(
            "Gemini API ERROR:",
            repr(e),
            flush=True
        )

        raise

    elapsed = time.time() - start

    print(
        f"Gemini response received in {elapsed:.1f} seconds.",
        flush=True
    )

    if response is None:
        raise ValueError("Gemini returned no response.")

    text = getattr(response, "text", None)

    if not text:
        raise ValueError(
            "Gemini returned empty text."
        )

    print("Parsing Gemini response...", flush=True)

    script, title, hashtags = parse_response(text)

    script, title, hashtags = validate(
        script,
        title,
        hashtags
    )

    return script, title, hashtags


def save(script, title, hashtags):

    with open(
        SCRIPT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(script)

    with open(
        TITLE_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(title)

    with open(
        HASHTAGS_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(hashtags)

    print("", flush=True)

    print("FILES CREATED:", flush=True)
    print(f"✓ {SCRIPT_FILE}", flush=True)
    print(f"✓ {TITLE_FILE}", flush=True)
    print(f"✓ {HASHTAGS_FILE}", flush=True)


def main():

    total_start = time.time()

    try:

        script, title, hashtags = generate()

        save(
            script,
            title,
            hashtags
        )

        total_time = time.time() - total_start

        print("", flush=True)
        print("================================", flush=True)
        print("SCRIPT GENERATION SUCCESS", flush=True)
        print("================================", flush=True)

        print(
            f"Total time: {total_time:.1f} seconds",
            flush=True
        )

        print("", flush=True)
        print("TITLE:", flush=True)
        print(title, flush=True)

        print("", flush=True)
        print("SCRIPT:", flush=True)
        print(script, flush=True)

        print("", flush=True)
        print("HASHTAGS:", flush=True)
        print(hashtags, flush=True)

    except Exception as e:

        print("", flush=True)
        print("================================", flush=True)
        print("SCRIPT GENERATION FAILED", flush=True)
        print("================================", flush=True)

        print(
            repr(e),
            flush=True
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
