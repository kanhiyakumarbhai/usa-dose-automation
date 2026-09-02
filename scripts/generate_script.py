import os
import re
import sys
import time
import requests
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY is missing.", flush=True)
    sys.exit(1)


MODEL = "gemini-3.5-flash-lite"

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    + MODEL
    + ":generateContent"
)

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"


# ============================================================
# PROMPT
# ============================================================

PROMPT = """
Create ONE original YouTube Shorts narration for USA Dose.

Audience:
Adults ages 18-70.

Topic:
One surprising, true and interesting fact or story about the USA.

IMPORTANT:
The narration MUST be between 65 and 75 words.
Do not write more than 75 words.

Requirements:
- Strong curiosity hook immediately.
- Build suspense.
- Do not reveal the answer immediately.
- Simple natural American English.
- Fast storytelling.
- One clear topic.
- Interesting for a broad adult audience.
- No politics.
- No fake facts.
- No exaggeration.
- No emojis.
- No unnecessary introduction.
- End with a natural question.

Return EXACTLY:

SCRIPT:
[65-75 word narration]

TITLE:
[short curiosity title]

HASHTAGS:
#USA #America #AmericanFacts #DidYouKnow #Facts #Shorts
"""


# ============================================================
# CLEAN TEXT
# ============================================================

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


# ============================================================
# PARSE RESPONSE
# ============================================================

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

    script = clean(script_match.group(1))
    title = clean(title_match.group(1))
    hashtags = clean(hashtags_match.group(1))

    return script, title, hashtags


# ============================================================
# VALIDATE SCRIPT
# ============================================================

def validate(script, title, hashtags):

    words = len(script.split())

    print("================================", flush=True)
    print("SCRIPT CHECK", flush=True)
    print("================================", flush=True)

    print(f"Words: {words}", flush=True)
    print(f"Characters: {len(script)}", flush=True)

    # Compatible with female voice generator.
    if words < 65:
        raise ValueError(
            f"Script is too short. Minimum words: 65. "
            f"Generated: {words}"
        )

    if words > 75:
        raise ValueError(
            f"Script is too long. Maximum words: 75. "
            f"Generated: {words}"
        )

    if len(title) < 5:
        raise ValueError("Title is too short.")

    if "#USA" not in hashtags:
        hashtags += " #USA"

    if "#America" not in hashtags:
        hashtags += " #America"

    if "#Facts" not in hashtags:
        hashtags += " #Facts"

    if "#Shorts" not in hashtags:
        hashtags += " #Shorts"

    return script, title, hashtags


# ============================================================
# CALL GEMINI
# ============================================================

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
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 160
        }
    }

    print(
        f"Sending request to {MODEL}...",
        flush=True
    )

    response = requests.post(
        API_URL,
        params={"key": API_KEY},
        headers=headers,
        json=payload,
        timeout=(10, 25)
    )

    print(
        f"Gemini HTTP status: {response.status_code}",
        flush=True
    )

    if response.status_code != 200:

        error_text = response.text[:1500]

        raise RuntimeError(
            f"Gemini API error {response.status_code}: "
            f"{error_text}"
        )

    data = response.json()

    try:

        text = (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

    except (
        KeyError,
        IndexError,
        TypeError
    ):

        raise RuntimeError(
            "Gemini returned an unexpected response: "
            + str(data)[:1500]
        )

    if not text.strip():

        raise RuntimeError(
            "Gemini returned empty text."
        )

    return text


# ============================================================
# GENERATE
# ============================================================

def generate():

    print("================================", flush=True)
    print("USA DOSE FAST GEMINI GENERATOR", flush=True)
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

                wait = 3

                print(
                    f"Waiting {wait} seconds...",
                    flush=True
                )

                time.sleep(wait)

    raise RuntimeError(
        "Gemini generation failed after 3 attempts: "
        + repr(last_error)
    )


# ============================================================
# SAVE FILES
# ============================================================

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

    print("================================", flush=True)
    print("FILES SAVED", flush=True)
    print("================================", flush=True)

    print(
        f"OK: {SCRIPT_FILE}",
        flush=True
    )

    print(
        f"OK: {TITLE_FILE}",
        flush=True
    )

    print(
        f"OK: {HASHTAGS_FILE}",
        flush=True
    )


# ============================================================
# MAIN
# ============================================================

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


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
