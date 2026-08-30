import os
import re
import sys

from google import genai


# ==========================================================
# USA DOSE - DAILY SHORT SCRIPT GENERATOR
# ==========================================================

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not API_KEY:
    print("ERROR: GEMINI_API_KEY / GOOGLE_API_KEY is missing.")
    sys.exit(1)


client = genai.Client(api_key=API_KEY)


# ==========================================================
# PROMPT
# ==========================================================

PROMPT = """
You create original YouTube Shorts for a channel called USA Dose.

Create ONE completely new and factual short video about the United States.

TOPIC:
Choose an interesting US topic such as:
- surprising American history
- unusual US laws
- amazing places
- geography
- inventions
- science
- American culture
- strange but real facts
- famous landmarks
- unusual events

IMPORTANT:
- The topic must be different from previous videos when possible.
- Do not repeat the same fact.
- Do not invent information.
- Keep the information factual and easy to understand.
- Target a US audience.
- Use natural American English.

SCRIPT:
- 40-55 spoken words.
- Approximately 20-25 seconds.
- Strong hook in the first sentence.
- Interesting and engaging.
- Natural conversational style.
- End with a short question when appropriate.
- The script must contain ONLY words that should be spoken.

NEVER put these words or production labels inside the spoken script:

voice over
voice-over
voiceover
narration
narrator
production
script
scene
on screen
visual
caption
subtitle
AI
camera direction
music direction

Do NOT write:
"Voice Over:"
"Narration:"
"Scene:"
"Script:"
"On Screen:"

TITLE:
- Create one unique YouTube Shorts title.
- The title must directly match the actual topic.
- Make it interesting without misleading clickbait.
- Do not reuse generic titles.

HASHTAGS:
- Minimum 7 hashtags.
- Make hashtags directly related to the topic.
- Always include #Shorts.
- Do not use exactly the same hashtag list every time.

OUTPUT EXACTLY IN THIS FORMAT:

TITLE: <title>

HASHTAGS: <hashtag1> <hashtag2> <hashtag3> <hashtag4> <hashtag5> <hashtag6> <hashtag7>

SCRIPT:
<40-55 word spoken script>
"""


# ==========================================================
# HELPERS
# ==========================================================

def clean_script(text):
    forbidden_patterns = [
        r"voice[\s_-]*over\s*:?",
        r"voiceover\s*:?",
        r"narration\s*:?",
        r"narrator\s*:?",
        r"production\s*:?",
        r"on[\s_-]*screen\s*:?",
        r"visual\s*:?",
        r"caption\s*:?",
        r"subtitle\s*:?",
        r"scene\s*:?",
    ]

    for pattern in forbidden_patterns:
        text = re.sub(
            pattern,
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


def extract_section(text, section_name):
    pattern = (
        rf"{section_name}\s*:\s*"
        rf"(.*?)(?=\n[A-Z][A-Z _-]*\s*:|$)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return ""


def get_hashtags(text):
    hashtags = re.findall(
        r"#[A-Za-z0-9_]+",
        text
    )

    # Remove duplicates while keeping order.
    unique = []

    for tag in hashtags:
        if tag.lower() not in [
            x.lower() for x in unique
        ]:
            unique.append(tag)

    return unique


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("================================")
    print("USA DOSE SCRIPT GENERATOR")
    print("================================")
    print("Model: Gemini 3.6 Flash")
    print("Target: 40-55 words")
    print("Target duration: 20-25 seconds")
    print("================================")

    # ------------------------------------------------------
    # GEMINI
    # ------------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=PROMPT
        )

        result = response.text.strip()

    except Exception as e:

        print("")
        print("================================")
        print("GEMINI ERROR")
        print("================================")
        print(e)
        sys.exit(1)

    # ------------------------------------------------------
    # EXTRACT DATA
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

    title = clean_script(title)
    script = clean_script(script)

    hashtags = get_hashtags(
        hashtags_raw
    )

    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    if not title:

        print("ERROR: Title was not generated.")
        sys.exit(1)

    if not script:

        print("ERROR: Script was not generated.")
        sys.exit(1)

    if len(hashtags) < 7:

        print(
            "ERROR: Less than 7 hashtags generated."
        )
        sys.exit(1)

    word_count = len(
        script.split()
    )

    character_count = len(script)

    print("")
    print("================================")
    print("GENERATED CONTENT")
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
    print("SCRIPT CHECK")
    print("================================")
    print(f"Words: {word_count}")
    print(f"Characters: {character_count}")
    print("================================")

    # ------------------------------------------------------
    # WORD LIMIT
    # ------------------------------------------------------

    if word_count < 40:

        print("")
        print(
            "ERROR: Script is too short."
        )
        print(
            "Minimum: 40 words."
        )
        sys.exit(1)

    if word_count > 55:

        print("")
        print(
            "ERROR: Script is too long."
        )
        print(
            "Maximum: 55 words."
        )
        print(
            "Voice generation cancelled."
        )
        sys.exit(1)

    # ------------------------------------------------------
    # CHARACTER SAFETY
    # ------------------------------------------------------

    if character_count > 350:

        print("")
        print(
            "ERROR: Script exceeds 350 characters."
        )
        print(
            "Voice generation cancelled."
        )
        sys.exit(1)

    # ------------------------------------------------------
    # FORBIDDEN TEXT CHECK
    # ------------------------------------------------------

    forbidden = [
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
        "scene",
    ]

    lower_script = script.lower()

    for phrase in forbidden:

        if phrase in lower_script:

            print("")
            print(
                "ERROR: Forbidden production text found:"
            )
            print(
                phrase
            )
            sys.exit(1)

    # ------------------------------------------------------
    # SAVE SPOKEN SCRIPT
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
    # SUCCESS
    # ------------------------------------------------------

    print("")
    print("================================")
    print("SCRIPT READY")
    print("================================")
    print(
        f"Title saved: {TITLE_FILE}"
    )
    print(
        f"Script saved: {SCRIPT_FILE}"
    )
    print(
        f"Hashtags saved: {HASHTAGS_FILE}"
    )
    print(
        f"Words: {word_count}"
    )
    print(
        f"Characters: {character_count}"
    )
    print(
        f"Hashtags: {len(hashtags)}"
    )
    print("================================")


if __name__ == "__main__":
    main()
