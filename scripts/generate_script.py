import os
import re
import sys

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

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not API_KEY:
    print("ERROR: GEMINI_API_KEY / GOOGLE_API_KEY is missing.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)


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
    "script:",
]


# ==========================================================
# CLEAN TEXT
# ==========================================================

def clean_text(text):

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
        text
    )

    unique = []

    for tag in tags:

        if tag.lower() not in [
            x.lower() for x in unique
        ]:
            unique.append(tag)

    return unique


# ==========================================================
# GENERATE CONTENT
# ==========================================================

def generate_content():

    prompt = f"""
You are the writer for a YouTube Shorts channel called USA Dose.

Create ONE completely original and factual short video about the United States.

Choose an interesting topic such as:
US history, geography, unusual places, inventions,
American culture, strange facts, landmarks, science,
or surprising events.

The topic should be different from previous videos when possible.

IMPORTANT SCRIPT RULES:

- Write ONLY 40 to 55 spoken words.
- NEVER exceed 55 words.
- Keep the script UNDER 350 characters.
- Aim for approximately 45-50 words.
- Natural American English.
- Strong hook in the first sentence.
- Informative and entertaining.
- Suitable for approximately 20-25 seconds.
- The spoken script must contain ONLY words that Laura should speak.
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

- Create one unique title.
- Title must match the actual video topic.
- Interesting but not misleading.
- Do not use the same generic title repeatedly.

HASHTAG RULES:

- At least 7 hashtags.
- Relevant to the actual topic.
- Include #Shorts.
- Do not use the exact same hashtag list every time.

OUTPUT EXACTLY:

TITLE: <unique title>

HASHTAGS: <at least 7 relevant hashtags>

SCRIPT:
<40-55 words and under 350 characters>
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text.strip()


# ==========================================================
# SHORTEN SCRIPT
# ==========================================================

def shorten_script(script):

    prompt = f"""
Rewrite the following USA Dose YouTube Shorts narration.

STRICT RULES:

- Keep the SAME factual topic.
- Keep the important fact.
- Make it natural American English.
- Exactly 40-55 words.
- UNDER 350 characters.
- Target approximately 45-50 words.
- Spoken narration only.
- No title.
- No hashtags.
- No labels.
- No voice-over instructions.
- No narration instructions.
- Do not add new facts.

SCRIPT TO SHORTEN:

{script}

Return ONLY the final spoken narration.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return clean_text(
        response.text.strip()
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("================================")
    print("USA DOSE SCRIPT GENERATOR")
    print("================================")
    print("Model: Gemini 3.6 Flash")
    print("Target: 40-55 words")
    print("Character limit: 350")
    print("Automatic shortening: ACTIVE")
    print("================================")

    # ------------------------------------------------------
    # FIRST GENERATION
    # ------------------------------------------------------

    try:

        result = generate_content()

    except Exception as e:

        print("")
        print("================================")
        print("GEMINI ERROR")
        print("================================")
        print(e)
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
        print("ERROR: Title was not generated.")
        sys.exit(1)

    if not script:
        print("ERROR: Script was not generated.")
        sys.exit(1)

    # ------------------------------------------------------
    # AUTOMATIC SHORTENING
    # ------------------------------------------------------

    for attempt in range(1, 4):

        word_count = len(
            script.split()
        )

        character_count = len(
            script
        )

        print("")
        print("================================")
        print(
            f"SCRIPT VALIDATION ATTEMPT {attempt}"
        )
        print("================================")
        print(
            f"Words: {word_count}"
        )
        print(
            f"Characters: {character_count}"
        )
        print("================================")

        if (
            MIN_WORDS <= word_count <= MAX_WORDS
            and
            character_count <= MAX_CHARACTERS
        ):
            print("")
            print("SCRIPT VALIDATION: PASSED")
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

        except Exception as e:

            print("")
            print(
                "ERROR while shortening script:"
            )
            print(e)
            sys.exit(1)

    else:

        print("")
        print("================================")
        print("SCRIPT VALIDATION FAILED")
        print("================================")
        print(
            "Could not create a safe-length script."
        )
        print(
            "Voice generation should not continue."
        )
        sys.exit(1)

    # ------------------------------------------------------
    # FINAL CHECK
    # ------------------------------------------------------

    word_count = len(
        script.split()
    )

    character_count = len(
        script
    )

    if word_count < MIN_WORDS:
        print("ERROR: Final script is too short.")
        sys.exit(1)

    if word_count > MAX_WORDS:
        print("ERROR: Final script is still too long.")
        sys.exit(1)

    if character_count > MAX_CHARACTERS:
        print(
            "ERROR: Final script still exceeds 350 characters."
        )
        sys.exit(1)

    # ------------------------------------------------------
    # FORBIDDEN CHECK
    # ------------------------------------------------------

    lower_script = script.lower()

    for phrase in FORBIDDEN:

        if phrase in lower_script:

            print("")
            print(
                "ERROR: Forbidden production text found:"
            )
            print(phrase)
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

    if len(hashtags) < 7:

        print("")
        print(
            "ERROR: Fewer than 7 hashtags."
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

        f.write(
            script
        )

    # ------------------------------------------------------
    # SAVE TITLE
    # ------------------------------------------------------

    with open(
        TITLE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            title
        )

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
    print(
        f"Words: {word_count}"
    )
    print(
        f"Characters: {character_count}"
    )
    print(
        f"Hashtags: {len(hashtags)}"
    )
    print("Voice safety: PASSED")
    print("================================")


if __name__ == "__main__":
    main()
