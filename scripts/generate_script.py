import os
import re
import sys
import time
import random

from google import genai


# ==========================================================
# USA DOSE - DAILY SCRIPT GENERATOR
# ROBUST GEMINI RETRY + FALLBACK
# ==========================================================

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"

MIN_WORDS = 40
MAX_WORDS = 55
MAX_CHARACTERS = 350

# Primary model + fallback models.
# If your account does not support one model, the next
# available model will be tried.
MODELS = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
]

MAX_RETRIES_PER_MODEL = 3

BASE_RETRY_DELAY = 5

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not API_KEY:
    print(
        "ERROR: GEMINI_API_KEY / GOOGLE_API_KEY is missing."
    )
    sys.exit(1)


# ==========================================================
# CLIENT
# ==========================================================

try:

    client = genai.Client(
        api_key=API_KEY,
        http_options={
            "timeout": 120000
        }
    )

except Exception as error:

    print("")
    print("GEMINI CLIENT ERROR")
    print(error)
    sys.exit(1)


# ==========================================================
# FORBIDDEN PRODUCTION WORDS
# ==========================================================

FORBIDDEN = [
    "voice over",
    "voice-over",
    "voiceover",
    "narration",
    "narrator",
    "production",
    "on screen",
    "visual",
    "caption",
    "subtitle",
    "scene:",
    "scene",
    "script:",
    "script",
]


# ==========================================================
# CLEAN TEXT
# ==========================================================

def clean_text(text):

    if not text:
        return ""

    for phrase in FORBIDDEN:

        text = re.sub(
            re.escape(phrase),
            "",
            text,
            flags=re.IGNORECASE
        )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================================
# EXTRACT SECTION
# ==========================================================

def extract_section(text, name):

    if not text:
        return ""

    pattern = (
        rf"{name}\s*:\s*(.*?)"
        rf"(?=\n[A-Z][A-Z _-]*\s*:|$)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:

        return match.group(1).strip()

    return ""


# ==========================================================
# HASHTAGS
# ==========================================================

def extract_hashtags(text):

    tags = re.findall(
        r"#[A-Za-z0-9_]+",
        text or ""
    )

    unique = []

    for tag in tags:

        if tag.lower() not in [
            x.lower()
            for x in unique
        ]:

            unique.append(tag)

    return unique


# ==========================================================
# GEMINI RETRY DETECTION
# ==========================================================

def is_temporary_error(error):

    message = str(error).lower()

    temporary_words = [
        "503",
        "unavailable",
        "server disconnected",
        "connection reset",
        "connection aborted",
        "timed out",
        "timeout",
        "temporarily unavailable",
        "internal server error",
        "502",
        "504",
        "overloaded",
        "high demand",
    ]

    return any(
        word in message
        for word in temporary_words
    )


# ==========================================================
# GEMINI CALL
# ==========================================================

def call_gemini(prompt):

    last_error = None

    for model in MODELS:

        print("")
        print("================================")
        print(
            f"TRYING GEMINI MODEL: {model}"
        )
        print("================================")

        for attempt in range(
            1,
            MAX_RETRIES_PER_MODEL + 1
        ):

            print(
                f"Attempt {attempt}/"
                f"{MAX_RETRIES_PER_MODEL}"
            )

            try:

                # --------------------------------------------------
                # Interactions API
                # --------------------------------------------------

                interaction = client.interactions.create(
                    model=model,
                    input=prompt
                )

                output = getattr(
                    interaction,
                    "output_text",
                    None
                )

                if not output:

                    # Some SDK versions expose output
                    # differently. Fall back safely.
                    output = str(
                        interaction
                    )

                output = str(
                    output
                ).strip()

                if not output:

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                print("")
                print(
                    f"Gemini success: {model}"
                )

                return output

            except Exception as error:

                last_error = error

                print("")
                print(
                    f"GEMINI {model} ERROR:"
                )
                print(error)

                temporary = (
                    is_temporary_error(
                        error
                    )
                )

                # --------------------------------------------------
                # RETRY TEMPORARY ERRORS
                # --------------------------------------------------

                if temporary and attempt < MAX_RETRIES_PER_MODEL:

                    delay = (
                        BASE_RETRY_DELAY
                        * (2 ** (attempt - 1))
                    )

                    # Small random jitter so repeated
                    # workflows do not all retry together.
                    delay += random.uniform(
                        0,
                        2
                    )

                    print("")
                    print(
                        "Temporary Gemini/server error."
                    )
                    print(
                        f"Retrying in "
                        f"{delay:.1f} seconds..."
                    )

                    time.sleep(
                        delay
                    )

                    continue

                # --------------------------------------------------
                # NON-TEMPORARY ERROR
                # --------------------------------------------------

                if not temporary:

                    print("")
                    print(
                        "This does not look like a "
                        "temporary connection error."
                    )

                    break

        print("")
        print(
            f"Gemini model failed: {model}"
        )

        print(
            "Trying next available model..."
        )

    print("")
    print("================================")
    print("ALL GEMINI MODELS FAILED")
    print("================================")

    if last_error:

        print(
            "Last error:"
        )
        print(
            last_error
        )

    raise RuntimeError(
        "Gemini generation failed after "
        "all retries and fallback models."
    )


# ==========================================================
# GENERATE CONTENT
# ==========================================================

def generate_content():

    prompt = """
You are the writer for a YouTube Shorts channel called USA Dose.

Create ONE completely original and factual short video
about the United States.

Choose an interesting topic such as:

US history,
US geography,
unusual American places,
American inventions,
American culture,
strange facts,
landmarks,
science,
surprising events,
or little-known facts.

IMPORTANT:

The topic should be substantially different from recent
videos whenever possible.

Do not use a generic repeated topic.

SCRIPT RULES:

- Write ONLY 40 to 55 spoken words.
- NEVER exceed 55 words.
- Keep the script UNDER 350 characters.
- Aim for approximately 45-50 words.
- Natural American English.
- Strong hook in the first sentence.
- Informative.
- Entertaining.
- Suitable for approximately 20-25 seconds.
- The spoken script must contain ONLY words Laura should speak.
- Do NOT include production instructions.
- Do NOT include labels inside the script.
- Do NOT write voice-over instructions.

NEVER put these inside SCRIPT:

voice over
voice-over
voiceover
narration
narrator
production
scene
on screen
visual
caption
subtitle
script

TITLE RULES:

- Create ONE unique title.
- Title must match the actual video topic.
- Interesting but not misleading.
- Do not use a generic repeated title.
- Do not simply use "USA Dose" as the title.

HASHTAG RULES:

- Create at least 7 hashtags.
- Hashtags must be relevant to the actual topic.
- Include #Shorts.
- Do not use exactly the same hashtag list every time.

OUTPUT EXACTLY:

TITLE: <unique title>

HASHTAGS: <at least 7 relevant hashtags>

SCRIPT:
<40-55 words and under 350 characters>
"""

    return call_gemini(
        prompt
    )


# ==========================================================
# SHORTEN SCRIPT
# ==========================================================

def shorten_script(script):

    prompt = f"""
Rewrite the following USA Dose YouTube Shorts narration.

STRICT RULES:

- Keep the SAME factual topic.
- Keep the important fact.
- Do not add new facts.
- Natural American English.
- Exactly 40-55 words.
- UNDER 350 characters.
- Target approximately 45-50 words.
- Spoken narration only.
- No title.
- No hashtags.
- No labels.
- No voice-over instructions.
- No narration instructions.
- No production instructions.

Return ONLY the final spoken narration.

SCRIPT TO SHORTEN:

{script}
"""

    result = call_gemini(
        prompt
    )

    return clean_text(
        result
    )


# ==========================================================
# VALIDATE SCRIPT
# ==========================================================

def validate_script(script):

    script = clean_text(
        script
    )

    words = len(
        script.split()
    )

    characters = len(
        script
    )

    if words < MIN_WORDS:

        return False

    if words > MAX_WORDS:

        return False

    if characters > MAX_CHARACTERS:

        return False

    lower_script = script.lower()

    for phrase in FORBIDDEN:

        if phrase in lower_script:

            return False

    return True


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("================================")
    print("USA DOSE SCRIPT GENERATOR")
    print("================================")
    print(
        "Primary model: Gemini 3.6 Flash"
    )
    print(
        "Fallback model: Gemini 3.7 Flash"
    )
    print(
        f"Target: {MIN_WORDS}-{MAX_WORDS} words"
    )
    print(
        f"Character limit: {MAX_CHARACTERS}"
    )
    print(
        "Automatic shortening: ACTIVE"
    )
    print(
        "Automatic retry: ACTIVE"
    )
    print(
        "Model fallback: ACTIVE"
    )
    print("================================")

    # ------------------------------------------------------
    # FIRST GENERATION
    # ------------------------------------------------------

    try:

        result = generate_content()

    except Exception as error:

        print("")
        print("================================")
        print("GEMINI GENERATION FAILED")
        print("================================")
        print(error)
        print("")
        print(
            "Voice/video generation will NOT continue."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------

    title = extract_section(
        result,
        "TITLE"
    )

    hashtags_raw = extract_section(
        result,
        "HASHTAGS"
    )

    script = extract_section(
        result,
        "SCRIPT"
    )

    title = clean_text(
        title
    )

    script = clean_text(
        script
    )

    hashtags = extract_hashtags(
        hashtags_raw
    )

    if not title:

        print(
            "ERROR: Title was not generated."
        )

        sys.exit(1)

    if not script:

        print(
            "ERROR: Script was not generated."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # AUTOMATIC SHORTENING
    # ------------------------------------------------------

    validation_passed = False

    for attempt in range(
        1,
        4
    ):

        word_count = len(
            script.split()
        )

        character_count = len(
            script
        )

        print("")
        print("================================")
        print(
            f"SCRIPT VALIDATION "
            f"ATTEMPT {attempt}"
        )
        print("================================")
        print(
            f"Words: {word_count}"
        )
        print(
            f"Characters: {character_count}"
        )
        print("================================")

        if validate_script(
            script
        ):

            print("")
            print(
                "SCRIPT VALIDATION: PASSED"
            )

            validation_passed = True

            break

        print("")
        print(
            "Script is outside the safe limit."
        )
        print(
            "Automatically shortening..."
        )

        try:

            script = shorten_script(
                script
            )

        except Exception as error:

            print("")
            print(
                "ERROR while shortening script:"
            )
            print(error)

            sys.exit(1)

    if not validation_passed:

        print("")
        print("================================")
        print("SCRIPT VALIDATION FAILED")
        print("================================")
        print(
            "Could not create a safe-length script."
        )
        print(
            "Voice generation should NOT continue."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # FINAL CHECK
    # ------------------------------------------------------

    script = clean_text(
        script
    )

    word_count = len(
        script.split()
    )

    character_count = len(
        script
    )

    if not validate_script(
        script
    ):

        print("")
        print(
            "ERROR: Final script failed safety validation."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # HASHTAG SAFETY
    # ------------------------------------------------------

    if "#shorts" not in [
        tag.lower()
        for tag in hashtags
    ]:

        hashtags.append(
            "#Shorts"
        )

    # Remove duplicate hashtags.
    final_hashtags = []

    for tag in hashtags:

        if tag.lower() not in [
            x.lower()
            for x in final_hashtags
        ]:

            final_hashtags.append(
                tag
            )

    hashtags = final_hashtags

    if len(hashtags) < 7:

        print("")
        print(
            "ERROR: Fewer than 7 hashtags."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # SAVE SCRIPT
    # ------------------------------------------------------

    try:

        with open(
            SCRIPT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                script
            )

        with open(
            TITLE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                title
            )

        with open(
            HASHTAGS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                " ".join(
                    hashtags
                )
            )

    except Exception as error:

        print("")
        print(
            "ERROR SAVING GENERATED CONTENT"
        )
        print(error)

        sys.exit(1)

    # ------------------------------------------------------
    # FINAL OUTPUT
    # ------------------------------------------------------

    print("")
    print("================================")
    print("USA DOSE CONTENT READY")
    print("================================")

    print("")
    print("TITLE:")
    print(title)

    print("")
    print("HASHTAGS:")
    print(
        " ".join(
            hashtags
        )
    )

    print("")
    print("SCRIPT:")
    print(script)

    print("")
    print("================================")
    print("FINAL CHECK")
    print("================================")
    print(
        f"Words: {word_count}"
    )
    print(
        f"Characters: {character_count}"
    )
    print(
        f"Hashtags: {len(hashtags)}"
    )
    print(
        "Voice safety: PASSED"
    )
    print(
        "Gemini retry protection: ACTIVE"
    )
    print(
        "Gemini model fallback: ACTIVE"
    )
    print("================================")


if __name__ == "__main__":

    main()
