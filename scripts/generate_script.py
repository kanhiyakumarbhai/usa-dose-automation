import os
import re
import sys
import time
from datetime import datetime

from google import genai

# ==========================================
# CONFIG
# ==========================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY is missing.", flush=True)
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

# Primary + fallback models
MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
]

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"


# ==========================================
# PROMPT
# ==========================================

PROMPT = """
Write ONE original USA-related YouTube Short.

Audience: adults ages 18-70.

Requirements:
- 75-105 words.
- Strong curiosity hook in the first sentence.
- One surprising factual USA story.
- Build suspense.
- Do not reveal the answer immediately.
- Simple natural American English.
- Fast storytelling.
- Universal topic that can interest both younger and older adults.
- Focus on one surprising USA fact, mystery, place, history fact,
  invention, money fact, unusual event, law, or discovery.
- Avoid politics.
- Do not invent facts.
- Do not exaggerate.
- No emojis in narration.
- End with a natural question encouraging comments.

Return ONLY this format:

SCRIPT:
[75-105 word narration]

TITLE:
[short curiosity title]

HASHTAGS:
#USA #America #Facts #Shorts
"""


# ==========================================
# CLEAN TEXT
# ==========================================

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


# ==========================================
# PARSE RESPONSE
# ==========================================

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


# ==========================================
# VALIDATE
# ==========================================

def validate(script, title, hashtags):

    word_count = len(script.split())

    print(
        f"Generated script words: {word_count}",
        flush=True
    )

    if word_count < 60:
        raise ValueError(
            f"Script too short: {word_count} words."
        )

    if word_count > 120:
        raise ValueError(
            f"Script too long: {word_count} words."
        )

    if len(title.strip()) < 5:
        raise ValueError(
            "Generated title is too short."
        )

    if "#USA" not in hashtags:
        hashtags += " #USA"

    if "#Shorts" not in hashtags:
        hashtags += " #Shorts"

    return script, title, hashtags


# ==========================================
# GEMINI REQUEST
# ==========================================

def request_model(model):

    print(
        f"Trying model: {model}",
        flush=True
    )

    start_time = time.time()

    response = client.models.generate_content(
        model=model,
        contents=PROMPT
    )

    elapsed = time.time() - start_time

    print(
        f"Response received from {model} "
        f"in {elapsed:.1f} seconds.",
        flush=True
    )

    if response is None:
        raise ValueError(
            f"{model} returned no response."
        )

    text = getattr(response, "text", None)

    if not text:
        raise ValueError(
            f"{model} returned empty text."
        )

    return text


# ==========================================
# GENERATE WITH RETRIES + FALLBACK
# ==========================================

def generate():

    print("================================", flush=True)
    print("USA DOSE SCRIPT GENERATOR", flush=True)
    print("================================", flush=True)

    print(
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        flush=True
    )

    print(
        "Starting Gemini generation...",
        flush=True
    )

    last_error = None

    # --------------------------------------
    # MODEL LOOP
    # --------------------------------------

    for model_index, model in enumerate(MODELS):

        print("", flush=True)

        print(
            f"MODEL {model_index + 1}/{len(MODELS)}",
            flush=True
        )

        # ----------------------------------
        # RETRY EACH MODEL TWICE
        # ----------------------------------

        for attempt in range(1, 3):

            print(
                f"Attempt {attempt}/2",
                flush=True
            )

            try:

                raw_text = request_model(model)

                print(
                    "Parsing Gemini response...",
                    flush=True
                )

                script, title, hashtags = parse_response(
                    raw_text
                )

                script, title, hashtags = validate(
                    script,
                    title,
                    hashtags
                )

                print(
                    f"SUCCESS: {model}",
                    flush=True
                )

                return script, title, hashtags

            except Exception as error:

                last_error = error

                error_text = str(error)

                print(
                    f"ERROR from {model}:",
                    flush=True
                )

                print(
                    error_text,
                    flush=True
                )

                # ----------------------------------
                # WAIT BEFORE RETRY
                # ----------------------------------

                if attempt < 2:

                    delay = 8

                    print(
                        f"Waiting {delay} seconds before retry...",
                        flush=True
                    )

                    time.sleep(delay)

        # --------------------------------------
        # MOVE TO FALLBACK MODEL
        # --------------------------------------

        if model_index < len(MODELS) - 1:

            print("", flush=True)

            print(
                f"{model} failed.",
                flush=True
            )

            print(
                "Moving to fallback model...",
                flush=True
            )

    # ======================================
    # EVERYTHING FAILED
    # ======================================

    raise RuntimeError(
        "All Gemini models failed. "
        f"Last error: {last_error}"
    )


# ==========================================
# SAVE FILES
# ==========================================

def save(script, title, hashtags):

    with open(
        SCRIPT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(script)

    with open(
        TITLE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(title)

    with open(
        HASHTAGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(hashtags)

    print("", flush=True)

    print(
        "Generated files saved:",
        flush=True
    )

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


# ==========================================
# MAIN
# ==========================================

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

        print(
            "================================",
            flush=True
        )

        print(
            "SCRIPT GENERATION SUCCESS",
            flush=True
        )

        print(
            "================================",
            flush=True
        )

        print(
            f"Total generation time: "
            f"{total_time:.1f} seconds",
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

        print(
            "================================",
            flush=True
        )

        print(
            "SCRIPT GENERATION FAILED",
            flush=True
        )

        print(
            "================================",
            flush=True
        )

        print(
            str(error),
            flush=True
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
