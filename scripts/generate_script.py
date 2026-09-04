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


PRIMARY_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

# Preferred fallback order.
# The script will verify availability before using them.
FALLBACK_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
]

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"


# ============================================================
# RETRY CONFIGURATION
# ============================================================

MAX_ATTEMPTS_PER_MODEL = 3

RETRY_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}

REQUEST_TIMEOUT = (15, 40)

RETRY_WAIT_SECONDS = [
    5,
    15,
    30,
]


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

    hashtags_list = hashtags.split()

    required_hashtags = [
        "#USA",
        "#America",
        "#Facts",
        "#Shorts",
    ]

    for hashtag in required_hashtags:

        if hashtag not in hashtags_list:
            hashtags_list.append(hashtag)

    hashtags = " ".join(hashtags_list)

    return script, title, hashtags


# ============================================================
# API URL
# ============================================================

def get_api_url(model):

    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + model
        + ":generateContent"
    )


# ============================================================
# LIST AVAILABLE MODELS
# ============================================================

def get_available_models():

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models"
    )

    print("================================", flush=True)
    print("CHECKING AVAILABLE GEMINI MODELS", flush=True)
    print("================================", flush=True)

    try:

        response = requests.get(
            url,
            params={"key": API_KEY},
            timeout=(10, 20)
        )

        print(
            f"Model list HTTP status: "
            f"{response.status_code}",
            flush=True
        )

        if response.status_code != 200:

            print(
                "WARNING: Could not retrieve model list.",
                flush=True
            )

            print(
                response.text[:1000],
                flush=True
            )

            return set()

        data = response.json()

        models = data.get("models", [])

        available = set()

        for model in models:

            name = model.get("name", "")

            supported_methods = model.get(
                "supportedGenerationMethods",
                []
            )

            if (
                name.startswith("models/")
                and "generateContent"
                in supported_methods
            ):

                clean_name = name.replace(
                    "models/",
                    "",
                    1
                )

                available.add(clean_name)

        print(
            f"GenerateContent models found: "
            f"{len(available)}",
            flush=True
        )

        # Show relevant Flash models
        relevant = sorted(
            [
                model
                for model in available
                if "flash" in model.lower()
            ]
        )

        if relevant:

            print(
                "Available Flash models:",
                flush=True
            )

            for model in relevant:
                print(
                    f"  - {model}",
                    flush=True
                )

        return available

    except Exception as error:

        print(
            "WARNING: Model discovery failed:",
            flush=True
        )

        print(
            repr(error),
            flush=True
        )

        return set()


# ============================================================
# BUILD MODEL ORDER
# ============================================================

def build_model_order(available_models):

    candidates = [
        PRIMARY_MODEL
    ] + FALLBACK_MODELS

    final_models = []

    for model in candidates:

        if model in final_models:
            continue

        # If model discovery worked, only use models
        # that actually support generateContent.
        if available_models:

            if model not in available_models:

                print(
                    f"Skipping unavailable model: "
                    f"{model}",
                    flush=True
                )

                continue

        final_models.append(model)

    return final_models


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
        f"Gemini HTTP status: "
        f"{response.status_code}",
        flush=True
    )

    if response.status_code in RETRY_STATUS_CODES:

        raise RuntimeError(
            f"RETRYABLE:{response.status_code}:"
            f"{response.text[:1500]}"
        )

    if response.status_code != 200:

        raise RuntimeError(
            f"Gemini API error "
            f"{response.status_code}: "
            f"{response.text[:1500]}"
        )

    try:

        data = response.json()

    except ValueError:

        raise RuntimeError(
            "Gemini returned invalid JSON: "
            + response.text[:1500]
        )

    try:

        candidates = data["candidates"]

        if not candidates:

            raise RuntimeError(
                "Gemini returned no candidates."
            )

        parts = (
            candidates[0]
            ["content"]
            ["parts"]
        )

        text_parts = []

        for part in parts:

            if "text" in part:

                text_parts.append(
                    part["text"]
                )

        text = "\n".join(text_parts)

    except (
        KeyError,
        IndexError,
        TypeError
    ):

        raise RuntimeError(
            "Gemini returned an unexpected "
            "response: "
            + str(data)[:1500]
        )

    if not text.strip():

        raise RuntimeError(
            "Gemini returned empty text."
        )

    return text


# ============================================================
# GENERATE WITH ONE MODEL
# ============================================================

def generate_with_model(model):

    last_error = None

    for attempt in range(
        1,
        MAX_ATTEMPTS_PER_MODEL + 1
    ):

        print("", flush=True)

        print(
            f"{model} attempt "
            f"{attempt}/"
            f"{MAX_ATTEMPTS_PER_MODEL}",
            flush=True
        )

        try:

            raw = call_gemini(model)

            print(
                "Gemini response received.",
                flush=True
            )

            script, title, hashtags = (
                parse_response(raw)
            )

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

            error_text = str(error)

            print(
                "Attempt failed:",
                flush=True
            )

            print(
                repr(error),
                flush=True
            )

            # Permanent error: do not waste retries.
            if not error_text.startswith(
                "RETRYABLE:"
            ):

                raise

        except (
            ValueError,
            Exception
        ) as error:

            last_error = error

            print(
                "Generation/validation failed:",
                flush=True
            )

            print(
                repr(error),
                flush=True
            )

        if attempt < MAX_ATTEMPTS_PER_MODEL:

            wait = RETRY_WAIT_SECONDS[
                min(
                    attempt - 1,
                    len(RETRY_WAIT_SECONDS) - 1
                )
            ]

            print(
                f"Waiting {wait} seconds "
                f"before retry...",
                flush=True
            )

            time.sleep(wait)

    raise RuntimeError(
        f"{model} failed after "
        f"{MAX_ATTEMPTS_PER_MODEL} attempts: "
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
        f"Primary model: {PRIMARY_MODEL}",
        flush=True
    )

    # --------------------------------------------------------
    # DISCOVER AVAILABLE MODELS
    # --------------------------------------------------------

    available_models = (
        get_available_models()
    )

    model_order = build_model_order(
        available_models
    )

    # If discovery failed completely, still try
    # the configured primary/fallback list.
    if not model_order:

        print(
            "WARNING: No models confirmed by "
            "discovery.",
            flush=True
        )

        print(
            "Using configured model order.",
            flush=True
        )

        model_order = []

        for model in (
            [PRIMARY_MODEL]
            + FALLBACK_MODELS
        ):

            if model not in model_order:
                model_order.append(model)

    print("", flush=True)

    print(
        "MODEL FAILOVER ORDER:",
        flush=True
    )

    for index, model in enumerate(
        model_order,
        start=1
    ):

        print(
            f"{index}. {model}",
            flush=True
        )

    # --------------------------------------------------------
    # TRY MODELS
    # --------------------------------------------------------

    all_errors = []

    for model in model_order:

        print("", flush=True)

        print(
            "================================",
            flush=True
        )

        print(
            f"TRYING MODEL: {model}",
            flush=True
        )

        print(
            "================================",
            flush=True
        )

        try:

            result = generate_with_model(
                model
            )

            print("", flush=True)

            print(
                f"SUCCESS WITH MODEL: {model}",
                flush=True
            )

            return result

        except Exception as error:

            all_errors.append(
                f"{model}: {repr(error)}"
            )

            print("", flush=True)

            print(
                f"MODEL FAILED: {model}",
                flush=True
            )

            print(
                repr(error),
                flush=True
            )

            print(
                "Moving to next available model...",
                flush=True
            )

    # --------------------------------------------------------
    # EVERYTHING FAILED
    # --------------------------------------------------------

    raise RuntimeError(
        "All Gemini models failed.\n\n"
        + "\n".join(all_errors)
    )


# ============================================================
# SAVE FILES
# ============================================================

def save_files(
    script,
    title,
    hashtags
):

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
            f"Generation time: "
            f"{elapsed:.1f} seconds",
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
