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


# Primary Gemini model
MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

# Optional fallback model.
# Leave empty if you don't want to use one.
FALLBACK_MODEL = os.getenv(
    "GEMINI_FALLBACK_MODEL",
    ""
)

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"


# ============================================================
# RETRY CONFIGURATION
# ============================================================

MAX_ATTEMPTS = 6

# Retry these temporary/server errors
RETRY_STATUS_CODES = {
    429,  # Rate limit
    500,  # Internal server error
    502,  # Bad gateway
    503,  # Service unavailable
    504,  # Gateway timeout
}

# Connection timeout, read timeout
REQUEST_TIMEOUT = (15, 40)


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

    # Normalize hashtags
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
# CREATE API URL
# ============================================================

def get_api_url(model):

    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + model
        + ":generateContent"
    )


# ============================================================
# CALL GEMINI
# ============================================================

def call_gemini(model):

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

    api_url = get_api_url(model)

    print(
        f"Sending request to {model}...",
        flush=True
    )

    response = requests.post(
        api_url,
        params={"key": API_KEY},
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT
    )

    print(
        f"Gemini HTTP status: {response.status_code}",
        flush=True
    )

    # --------------------------------------------------------
    # TEMPORARY SERVER / RATE LIMIT ERRORS
    # --------------------------------------------------------

    if response.status_code in RETRY_STATUS_CODES:

        error_text = response.text[:1500]

        raise RuntimeError(
            f"RETRYABLE Gemini API error "
            f"{response.status_code}: {error_text}"
        )

    # --------------------------------------------------------
    # PERMANENT API ERROR
    # --------------------------------------------------------

    if response.status_code != 200:

        error_text = response.text[:1500]

        raise RuntimeError(
            f"Gemini API error {response.status_code}: "
            f"{error_text}"
        )

    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:

        data = response.json()

    except ValueError:

        raise RuntimeError(
            "Gemini returned invalid JSON: "
            + response.text[:1500]
        )

    # --------------------------------------------------------
    # EXTRACT TEXT
    # --------------------------------------------------------

    try:

        candidates = data["candidates"]

        if not candidates:
            raise RuntimeError(
                "Gemini returned no candidates."
            )

        text = (
            candidates[0]
            ["content"]
            ["parts"][0]
            ["text"]
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

    if not text or not text.strip():

        raise RuntimeError(
            "Gemini returned empty text."
        )

    return text


# ============================================================
# RETRY WAIT TIME
# ============================================================

def get_wait_time(attempt):

    # 5, 10, 20, 30, 45 seconds
    waits = [
        5,
        10,
        20,
        30,
        45
    ]

    index = min(
        attempt - 1,
        len(waits) - 1
    )

    return waits[index]


# ============================================================
# GENERATE WITH MODEL
# ============================================================

def generate_with_model(model):

    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):

        print("", flush=True)

        print(
            f"{model} attempt "
            f"{attempt}/{MAX_ATTEMPTS}",
            flush=True
        )

        try:

            raw = call_gemini(model)

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

        except requests.exceptions.Timeout as error:

            last_error = error

            print(
                "Request timed out.",
                flush=True
            )

            print(
                repr(error),
                flush=True
            )

        except requests.exceptions.ConnectionError as error:

            last_error = error

            print(
                "Connection error.",
                flush=True
            )

            print(
                repr(error),
                flush=True
            )

        except RuntimeError as error:

            last_error = error

            print(
                "Attempt failed:",
                flush=True
            )

            print(
                repr(error),
                flush=True
            )

            # Only retry temporary/server errors
            if not any(
                f" {code}:" in str(error)
                for code in RETRY_STATUS_CODES
            ):
                raise

        except Exception as error:

            last_error = error

            print(
                "Attempt failed:",
                flush=True
            )

            print(
                repr(error),
                flush=True
            )

            # Parsing / validation errors can be retried,
            # because another generation may be valid.

        if attempt < MAX_ATTEMPTS:

            wait = get_wait_time(attempt)

            print(
                f"Waiting {wait} seconds before retry...",
                flush=True
            )

            time.sleep(wait)

    raise RuntimeError(
        f"{model} generation failed after "
        f"{MAX_ATTEMPTS} attempts: "
        + repr(last_error)
    )


# ============================================================
# GENERATE
# ============================================================

def generate():

    print("================================", flush=True)
    print("USA DOSE GEMINI GENERATOR", flush=True)
    print("================================", flush=True)

    print(
        datetime.now().strftime(
            "Time: %Y-%m-%d %H:%M:%S"
        ),
        flush=True
    )

    print(
        f"Primary model: {MODEL}",
        flush=True
    )

    if FALLBACK_MODEL:

        print(
            f"Fallback model: {FALLBACK_MODEL}",
            flush=True
        )

    else:

        print(
            "Fallback model: disabled",
            flush=True
        )

    # --------------------------------------------------------
    # PRIMARY MODEL
    # --------------------------------------------------------

    try:

        return generate_with_model(MODEL)

    except Exception as primary_error:

        print("", flush=True)

        print(
            "PRIMARY MODEL FAILED",
            flush=True
        )

        print(
            repr(primary_error),
            flush=True
        )

        # ----------------------------------------------------
        # FALLBACK MODEL
        # ----------------------------------------------------

        if FALLBACK_MODEL:

            # Prevent accidentally using the same model twice
            if FALLBACK_MODEL == MODEL:

                raise RuntimeError(
                    "Fallback model is identical to "
                    "primary model. Configure a different "
                    "GEMINI_FALLBACK_MODEL."
                )

            print("", flush=True)

            print(
                "================================",
                flush=True
            )

            print(
                "TRYING FALLBACK MODEL",
                flush=True
            )

            print(
                "================================",
                flush=True
            )

            try:

                return generate_with_model(
                    FALLBACK_MODEL
                )

            except Exception as fallback_error:

                raise RuntimeError(
                    "Both Gemini models failed.\n"
                    f"Primary: {repr(primary_error)}\n"
                    f"Fallback: {repr(fallback_error)}"
                )

        raise


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
