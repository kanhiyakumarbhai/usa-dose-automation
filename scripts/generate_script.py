import os
import re
import sys
import time
from datetime import datetime

from google import genai
from google.genai import types


# ============================================================
# CONFIG
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY is missing.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.7-flash"

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"


# ============================================================
# FAST PROMPT
# ============================================================

PROMPT = """
You are the script writer for a YouTube Shorts channel called USA Dose.

Create ONE original, factual and interesting USA-related Short for a broad adult audience ages 18-70.

Requirements:
- 75-105 words for the spoken script.
- Start with a strong curiosity hook.
- Build suspense.
- Do not reveal the main answer immediately.
- Use simple natural English.
- Fast, engaging storytelling.
- Focus on one surprising USA fact, mystery, place, event, invention, law, history fact, money fact, or unusual discovery.
- Avoid politics unless absolutely necessary.
- Avoid fake facts and exaggerated claims.
- Do not use emojis in the spoken script.
- End naturally with a short question that encourages comments.

Return EXACTLY this format:

SCRIPT:
[spoken narration]

TITLE:
[a short curiosity-based title]

HASHTAGS:
#USA #America #Facts #Shorts
"""


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):
    text = text.strip()

    # Remove accidental markdown code fences
    text = re.sub(r"```(?:text|txt)?", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")

    return text.strip()


# ============================================================
# PARSE GEMINI RESPONSE
# ============================================================

def parse_response(text):
    text = clean_text(text)

    script_match = re.search(
        r"SCRIPT:\s*(.*?)(?=\n\s*TITLE:)",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    title_match = re.search(
        r"TITLE:\s*(.*?)(?=\n\s*HASHTAGS:)",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    hashtags_match = re.search(
        r"HASHTAGS:\s*(.*)$",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    if not script_match:
        raise ValueError("SCRIPT section missing.")

    if not title_match:
        raise ValueError("TITLE section missing.")

    if not hashtags_match:
        raise ValueError("HASHTAGS section missing.")

    script = clean_text(script_match.group(1))
    title = clean_text(title_match.group(1))
    hashtags = clean_text(hashtags_match.group(1))

    return script, title, hashtags


# ============================================================
# VALIDATE
# ============================================================

def validate_content(script, title, hashtags):

    words = len(script.split())

    print(f"Generated script words: {words}")

    if words < 60:
        raise ValueError(
            f"Script too short: {words} words."
        )

    if words > 120:
        raise ValueError(
            f"Script too long: {words} words."
        )

    if len(title) < 5:
        raise ValueError("Generated title is too short.")

    if "#USA" not in hashtags:
        hashtags += " #USA"

    if "#Shorts" not in hashtags:
        hashtags += " #Shorts"

    return script, title, hashtags


# ============================================================
# GEMINI GENERATION
# ============================================================

def generate_content():

    print("================================")
    print("USA DOSE FAST SCRIPT GENERATOR")
    print("================================")
    print(f"Model: {MODEL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("Generating daily script...")
    print()

    last_error = None

    # Only 2 attempts.
    # This prevents the workflow from getting stuck
    # in endless retries.
    for attempt in range(1, 3):

        print(f"Attempt {attempt}/2...")

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=PROMPT,
                config=types.GenerateContentConfig(
                    max_output_tokens=350,
                    thinking_config=types.ThinkingConfig(
                        thinking_level="low"
                    )
                )
            )

            if not response:
                raise ValueError("Empty Gemini response.")

            raw_text = getattr(response, "text", None)

            if not raw_text:
                raise ValueError("Gemini returned empty text.")

            print("Gemini response received.")

            script, title, hashtags = parse_response(raw_text)

            script, title, hashtags = validate_content(
                script,
                title,
                hashtags
            )

            return script, title, hashtags

        except Exception as e:

            last_error = e

            print(f"Attempt {attempt} failed:")
            print(str(e))

            if attempt < 2:
                print("Waiting 5 seconds before final retry...")
                time.sleep(5)

    raise RuntimeError(
        f"Gemini generation failed after 2 attempts: {last_error}"
    )


# ============================================================
# SAVE FILES
# ============================================================

def save_files(script, title, hashtags):

    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(script)

    with open(TITLE_FILE, "w", encoding="utf-8") as f:
        f.write(title)

    with open(HASHTAGS_FILE, "w", encoding="utf-8") as f:
        f.write(hashtags)

    print()
    print("Files saved:")
    print(f"- {SCRIPT_FILE}")
    print(f"- {TITLE_FILE}")
    print(f"- {HASHTAGS_FILE}")


# ============================================================
# MAIN
# ============================================================

def main():

    start_time = time.time()

    try:

        script, title, hashtags = generate_content()

        save_files(
            script,
            title,
            hashtags
        )

        elapsed = time.time() - start_time

        print()
        print("================================")
        print("SCRIPT GENERATION SUCCESS")
        print("================================")
        print(f"Generation time: {elapsed:.1f} seconds")
        print()
        print("TITLE:")
        print(title)
        print()
        print("SCRIPT:")
        print(script)
        print()
        print("HASHTAGS:")
        print(hashtags)

    except Exception as e:

        print()
        print("================================")
        print("SCRIPT GENERATION FAILED")
        print("================================")
        print(str(e))

        sys.exit(1)


if __name__ == "__main__":
    main()
