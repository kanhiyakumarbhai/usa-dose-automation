import os
import re
import sys
import time
import requests
from datetime import datetime

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY is missing.", flush=True)
    sys.exit(1)

MODEL = "gemini-3.7-flash"

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    + MODEL
    + ":generateContent"
)

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"

PROMPT = """
Write ONE original USA-related YouTube Short.

Audience: adults ages 18-70.

Requirements:
- 75-105 words.
- Strong curiosity hook immediately.
- One surprising factual USA story.
- Build suspense.
- Do not reveal the answer immediately.
- Simple natural American English.
- Fast engaging storytelling.
- Universal topic.
- No politics.
- No fake facts.
- No exaggeration.
- No emojis.
- End with a natural question.

Return ONLY:

SCRIPT:
[75-105 word narration]

TITLE:
[short curiosity title]

HASHTAGS:
#USA #America #Facts #Shorts
"""


def clean(text):
    text = text.strip()
    text = re.sub(
        r"```(?:text|txt)?",
        "",
        text,
        flags=re.IGNORECASE
    )
    text = text.replace("```", "")
    return text.strip()


def parse_response(text):
    text = clean(text)

    script_match = re.search(
        r"SCRIPT:\s*(.*?)(?=\n\s*TITLE:)",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    title_match = re.search(
        r"TITLE:\s*(.*?)(?=\n\s*HASHTAGS:)",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    hashtags_match = re.search(
        r"HASHTAGS:\s*(.*)$",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if not script_match:
        raise ValueError("SCRIPT section missing.")

    if not title_match:
        raise ValueError("TITLE section missing.")

    if not hashtags_match:
        raise ValueError("HASHTAGS section missing.")

    return (
        clean(script_match.group(1)),
        clean(title_match.group(1)),
        clean(hashtags_match.group(1))
    )


def validate(script, title, hashtags):
    words = len(script.split())

    print(f"Generated words: {words}", flush=True)

    if words < 60:
        raise ValueError(
            f"Script too short: {words} words."
        )

    if words > 120:
        raise ValueError(
            f"Script too long: {words} words."
        )

    if len(title) < 5:
        raise ValueError("Title is too short.")

    if "#USA" not in hashtags:
        hashtags += " #USA"

    if "#Shorts" not in hashtags:
        hashtags += " #Shorts"

    return script, title, hashtags


def call_gemini():
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": PROMPT
                    }
                ]
            }
        ]
    }

    print("Sending direct Gemini REST request...", flush=True)

    response = requests.post(
        API_URL,
        params={
            "key": API_KEY
        },
        headers=headers,
        json=payload,
        timeout=45
    )

    print(
        f"Gemini HTTP status: {response.status_code}",
        flush=True
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Gemini API error {response.status_code}: "
            f"{response.text[:1000]}"
        )

    data = response.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(
            "Gemini returned an unexpected response: "
            + str(data)[:1500]
        )

    if not text.strip():
        raise RuntimeError(
            "Gemini returned empty text."
        )

    return text


def generate():
    print("================================", flush=True)
    print("USA DOSE DIRECT GEMINI GENERATOR", flush=True)
    print("================================", flush=True)

    print(
        datetime.now().strftime(
            "Time: %Y-%m-%d %H:%M:%S"
        ),
        flush=True
    )

    last_error = None

    for attempt in range(1, 4):

        print("", flush=True)

        print(
            f"Gemini attempt {attempt}/3",
            flush=True
        )

        try:
            raw = call_gemini()

            print(
                "Gemini response received.",
                flush=True
            )

            script, title, hashtags = parse_response(raw)

            return validate(
                script,
                title,
                hashtags
            )

        except Exception as error:

            last_error = error

            print(
                f"Attempt {attempt} failed:",
                flush=True
            )

            print(
                repr(error),
                flush=True
            )

            if attempt < 3:

                wait = attempt * 8

                print(
                    f"Waiting {wait} seconds...",
                    flush=True
                )

                time.sleep(wait)

    raise RuntimeError(
        "Gemini generation failed after 3 attempts: "
        + repr(last_error)
    )


def save_files(script, title, hashtags):

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

    print("Files saved successfully:", flush=True)
    print(f"OK {SCRIPT_FILE}", flush=True)
    print(f"OK {TITLE_FILE}", flush=True)
    print(f"OK {HASHTAGS_FILE}", flush=True)


def main():

    start = time.time()

    try:

        script, title, hashtags = generate()

        save_files(
            script,
            title,
            hashtags
        )

        elapsed = time.time() - start

        print("", flush=True)
        print("================================", flush=True)
        print("SCRIPT GENERATION SUCCESS", flush=True)
        print("================================", flush=True)

        print(
            f"Generation time: {elapsed:.1f} seconds",
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

    except Exception as error:

        print("", flush=True)
        print("================================", flush=True)
        print("SCRIPT GENERATION FAILED", flush=True)
        print("================================", flush=True)

        print(
            repr(error),
            flush=True
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
