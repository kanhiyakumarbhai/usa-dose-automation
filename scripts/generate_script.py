import os
import re
import sys
import time

from google import genai


# ==========================================================
# USA DOSE - DAILY SCRIPT GENERATOR
# ==========================================================

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"

MIN_WORDS = 40
MAX_WORDS = 55
MAX_CHARACTERS = 350

MODEL = "gemini-3.6-flash"

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not API_KEY:
    print("ERROR: GEMINI_API_KEY / GOOGLE_API_KEY is missing.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)


# ==========================================================
# FORBIDDEN WORDS
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
    "script:",
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

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# EXTRACT SECTION
# ==========================================================

def extract_section(text, name):

    pattern = (
        rf"^\s*{re.escape(name)}\s*:\s*(.*?)"
        rf"(?=^\s*[A-Z][A-Z _-]*\s*:|\Z)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL
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
    seen = set()

    for tag in tags:

        key = tag.lower()

        if key not in seen:
            seen.add(key)
            unique.append(tag)

    return unique


# ==========================================================
# GEMINI REQUEST WITH RETRY
# ==========================================================

def gemini_generate(prompt, attempts=4):

    last_error = None

    for attempt in range(1, attempts + 1):

        try:

            print(
                f"Gemini request attempt {attempt}/{attempts}..."
            )

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            text = getattr(response, "text", None)

            if not text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return text.strip()

        except Exception as e:

            last_error = e

            print("")
            print(
                f"Gemini attempt {attempt} failed:"
            )
            print(e)

            if attempt < attempts:

                wait_time = attempt * 5

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

    raise RuntimeError(
        f"Gemini failed after {attempts} attempts: {last_error}"
    )


# ==========================================================
# GENERATE CONTENT
# ==========================================================

def generate_content():

    prompt = """
You are the writer for a YouTube Shorts channel called USA Dose.

Create ONE completely original and factual short video about the United States.

Choose an interesting topic from areas such as:

- unusual American history
- strange American places
- surprising US geography
- forgotten events
- unusual inventions
- American landmarks
- fascinating science in the US
- unusual laws or traditions
- surprising facts about American cities
- hidden stories from the United States

IMPORTANT:

The topic should feel fresh and different from generic repeated facts.

The first sentence MUST create curiosity immediately.

The viewer should want to keep watching to discover the answer.

SCRIPT RULES:

- Exactly 40 to 55 spoken words.
- Never exceed 55 words.
- Under 350 characters.
- Aim for approximately 45-50 words.
- Natural American English.
- Strong curiosity hook in the first sentence.
- No introduction.
- No "Welcome to USA Dose".
- No "Did you know" unless genuinely necessary.
- Informative and entertaining.
- Suitable for approximately 18-25 seconds.
- Spoken narration only.
- Every word must be something the female voice can speak naturally.
- Do not include production instructions.
- Do not include labels inside SCRIPT.
- Do not include scene directions.
- Do not include visual directions.

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

- Create one unique title.
- Title must match the actual topic.
- Make it curiosity-driven.
- Do not make false claims.
- Do not repeat generic titles.

HASHTAG RULES:

- Generate 7 to 10 hashtags.
- Include #Shorts.
- Hashtags must match the actual topic.
- Do not use the exact same hashtag list every day.

OUTPUT EXACTLY:

TITLE: <unique title>

HASHTAGS: <7-10 relevant hashtags>

SCRIPT:
<40-55 spoken words, under 350 characters>
"""

    return gemini_generate(prompt)


# ==========================================================
# SHORTEN SCRIPT
# ==========================================================

def shorten_script(script):

    prompt = f"""
Rewrite this USA Dose YouTube Shorts narration.

Keep the SAME factual topic and important fact.

STRICT RULES:

- 40 to 55 words.
- Never exceed 55 words.
- Under 350 characters.
- Aim for 45-50 words.
- Natural American English.
- Strong hook.
- Spoken narration only.
- No title.
- No hashtags.
- No labels.
- No production instructions.
- Do not add new facts.
- Do not change the factual meaning.

Return ONLY the final spoken narration.

SCRIPT:

{script}
"""

    return clean_text(
        gemini_generate(prompt)
    )


# ==========================================================
# VALIDATE SCRIPT
# ==========================================================

def validate_script(script):

    script = clean_text(script)

    word_count = len(script.split())
    character_count = len(script)

    if word_count < MIN_WORDS:
        return False, word_count, character_count

    if word_count > MAX_WORDS:
        return False, word_count, character_count

    if character_count > MAX_CHARACTERS:
        return False, word_count, character_count

    lower_script = script.lower()

    for phrase in FORBIDDEN:

        if phrase in lower_script:
            return False, word_count, character_count

    return True, word_count, character_count


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("================================")
    print("USA DOSE SCRIPT GENERATOR")
    print("================================")
    print(f"Model: {MODEL}")
    print("Target: 40-55 words")
    print("Character limit: 350")
    print("Strong hook: ACTIVE")
    print("Retry protection: ACTIVE")
    print("================================")

    # ------------------------------------------------------
    # GENERATE CONTENT
    # ------------------------------------------------------

    try:

        result = generate_content()

    except Exception as e:

        print("")
        print("================================")
        print("GEMINI ERROR")
        print("================================")
        print(e)
        print("================================")

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

    title = clean_text(title)
    script = clean_text(script)

    hashtags = extract_hashtags(
        hashtags_raw
    )

    # ------------------------------------------------------
    # BASIC CHECK
    # ------------------------------------------------------

    if not title:

        print("ERROR: Title was not generated.")
        sys.exit(1)

    if not script:

        print("ERROR: Script was not generated.")
        sys.exit(1)

    # ------------------------------------------------------
    # AUTOMATIC SCRIPT VALIDATION
    # ------------------------------------------------------

    valid = False

    for attempt in range(1, 4):

        valid, word_count, character_count = validate_script(
            script
        )

        print("")
        print("================================")
        print(
            f"SCRIPT VALIDATION {attempt}/3"
        )
        print("================================")
        print(f"Words: {word_count}")
        print(f"Characters: {character_count}")
        print("================================")

        if valid:

            print("")
            print("SCRIPT VALIDATION: PASSED")
            break

        if attempt < 3:

            print("")
            print("Script is outside safe limits.")
            print("Automatically rewriting...")

            try:

                script = shorten_script(
                    script
                )

            except Exception as e:

                print("")
                print(
                    "ERROR while rewriting script:"
                )
                print(e)

                sys.exit(1)

    # ------------------------------------------------------
    # FINAL VALIDATION
    # ------------------------------------------------------

    valid, word_count, character_count = validate_script(
        script
    )

    if not valid:

        print("")
        print("================================")
        print("SCRIPT VALIDATION FAILED")
        print("================================")
        print(
            f"Words: {word_count}"
        )
        print(
            f"Characters: {character_count}"
        )
        print("")
        print(
            "Video generation will NOT continue."
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

    # Remove duplicates again
    final_hashtags = []
    seen = set()

    for tag in hashtags:

        key = tag.lower()

        if key not in seen:

            seen.add(key)
            final_hashtags.append(tag)

    hashtags = final_hashtags

    if len(hashtags) < 7:

        print("")
        print(
            "ERROR: Fewer than 7 hashtags generated."
        )
        print(
            f"Hashtags found: {len(hashtags)}"
        )

        sys.exit(1)

    # ------------------------------------------------------
    # SAVE SCRIPT
    # ------------------------------------------------------

    with open(
        SCRIPT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(script)

    # ------------------------------------------------------
    # SAVE TITLE
    # ------------------------------------------------------

    with open(
        TITLE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(title)

    # ------------------------------------------------------
    # SAVE HASHTAGS
    # ------------------------------------------------------

    with open(
        HASHTAGS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            " ".join(hashtags)
        )

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
    print(" ".join(hashtags))

    print("")
    print("SCRIPT:")
    print(script)

    print("")
    print("================================")
    print("FINAL CHECK")
    print("================================")
    print(f"Words: {word_count}")
    print(f"Characters: {character_count}")
    print(f"Hashtags: {len(hashtags)}")
    print("Hook: ACTIVE")
    print("Voice safety: PASSED")
    print("================================")


if __name__ == "__main__":
    main()
