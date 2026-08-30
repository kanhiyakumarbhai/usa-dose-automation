import os
import re
import sys
from google import genai

OUTPUT_FILE = "daily_script.txt"

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY / GOOGLE_API_KEY is missing.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

PROMPT = r"""
You create original YouTube Shorts for a channel called USA Dose.

Create ONE completely new and factual video about the United States.

IMPORTANT:
- Choose a different topic every time.
- Do not repeat previous topics or facts.
- Focus on surprising US history, places, laws, inventions, people,
  mysteries, geography, culture, science or unusual facts.
- The information must be factual.
- Do not invent facts.
- Write approximately 25-30 seconds of natural spoken American English.
- Aim for roughly 65-80 spoken words.
- Strong hook in the first sentence.
- Make it interesting for a US audience.
- End naturally, preferably with a short question.
- No stage directions.
- No camera directions.
- No production instructions.
- No AI references.

NEVER use these words or phrases in the spoken script:
"voice over"
"voiceover"
"voice-over"
"narration"
"narrator"
"narrated"
"production"
"script"
"scene"
"on screen"
"visual"
"caption"
"subtitle"

Do not put labels inside the spoken script.

OUTPUT EXACTLY:

TITLE: <unique title>

HASHTAGS: <at least 7 relevant hashtags>

SCRIPT:
<25-30 second spoken narration>

TITLE RULES:
- Unique every time.
- Directly related to the actual topic.
- Interesting but truthful.
- Suitable for YouTube Shorts.
- Do not use the same title repeatedly.

HASHTAG RULES:
- Minimum 7 hashtags.
- They must relate to the specific topic.
- Include #Shorts.
- Do not use the exact same hashtag list every time.

SCRIPT RULES:
- 65-80 words approximately.
- Natural American English.
- Conversational.
- Strong hook.
- Only words that should actually be spoken.
"""

def clean_text(text):
    forbidden = [
        r"voice[\s_-]*over",
        r"voiceover",
        r"narration",
        r"narrator",
        r"narrated",
        r"production",
        r"on[\s_-]*screen",
        r"visual",
        r"caption",
        r"subtitle",
    ]

    for pattern in forbidden:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_section(text, name):
    pattern = rf"{name}\s*:\s*(.*?)(?=\n[A-Z][A-Z_ ]*\s*:|$)"

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return ""


def main():
    print("================================")
    print("USA DOSE SCRIPT GENERATOR")
    print("================================")
    print("Target duration: 25-30 seconds")
    print("Target words: 65-80")
    print("")

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=PROMPT
        )

        result = response.text.strip()

    except Exception as e:
        print("GEMINI ERROR")
        print(e)
        sys.exit(1)

    title = extract_section(result, "TITLE")
    hashtags = extract_section(result, "HASHTAGS")
    script = extract_section(result, "SCRIPT")

    title = clean_text(title)
    script = clean_text(script)

    hashtags = re.sub(
        r"^(HASHTAGS)\s*:\s*",
        "",
        hashtags,
        flags=re.IGNORECASE
    ).strip()

    hashtag_list = re.findall(
        r"#[A-Za-z0-9_]+",
        hashtags
    )

    if not title:
        print("ERROR: Title missing.")
        sys.exit(1)

    if not script:
        print("ERROR: Script missing.")
        sys.exit(1)

    if len(hashtag_list) < 7:
        print("ERROR: Less than 7 hashtags generated.")
        sys.exit(1)

    word_count = len(script.split())

    print("TITLE:")
    print(title)
    print("")

    print("HASHTAGS:")
    print(" ".join(hashtag_list))
    print("")

    print("SCRIPT:")
    print(script)
    print("")

    print(f"Word count: {word_count}")

    # Safety check
    forbidden_check = [
        "voice over",
        "voiceover",
        "voice-over",
        "narration",
        "narrator",
        "production",
        "on screen",
        "visual",
        "caption",
        "subtitle",
    ]

    lowered = script.lower()

    for phrase in forbidden_check:
        if phrase in lowered:
            print(
                f"ERROR: Forbidden phrase detected: {phrase}"
            )
            sys.exit(1)

    # Keep script compact enough for 25-30 sec narration.
    if word_count > 90:
        print("ERROR: Script is too long.")
        sys.exit(1)

    # Save spoken words only.
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(script)

    # Save metadata for YouTube.
    with open(
        "video_title.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(title)

    with open(
        "video_hashtags.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(" ".join(hashtag_list))

    print("")
    print("================================")
    print("SCRIPT READY")
    print("================================")


if __name__ == "__main__":
    main()
