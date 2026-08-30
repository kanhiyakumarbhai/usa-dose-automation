import os
import re
import sys
from google import genai


OUTPUT_FILE = "daily_script.txt"

API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not API_KEY:
    print("ERROR: GEMINI_API_KEY / GOOGLE_API_KEY is missing.")
    sys.exit(1)


client = genai.Client(api_key=API_KEY)


PROMPT = r"""
You create original YouTube Shorts for a channel called USA Dose.

Create ONE completely new video about the United States.

IMPORTANT:
- Pick a different topic each time.
- Do NOT repeat the same fact, story, wording, or topic used recently.
- The topic must be genuinely interesting to a US audience.
- Use factual information.
- Do not invent facts.
- Keep the narration around 30-40 seconds.
- Write natural spoken American English.
- Make the opening hook strong but not misleading.
- The narration must match the topic exactly.
- Do not write stage directions.
- Do not write camera directions.
- Do not write production instructions.
- Do not mention AI.
- Do not mention automation.
- NEVER use these words or phrases:
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
- Do not include labels such as:
  Voice Over:
  Narration:
  Scene:
  Title:
  Hashtags:

The output MUST use exactly this format:

TITLE: <unique video title>

HASHTAGS: <at least 7 relevant hashtags>

SCRIPT:
<the complete spoken narration>

Rules for TITLE:
- Must be different from previous videos.
- Must directly relate to this video's topic.
- Must be interesting without fake clickbait.
- Keep it suitable for a YouTube Short.

Rules for HASHTAGS:
- At least 7 hashtags.
- They must be relevant to this specific video.
- Do not use the exact same hashtag set every time.

Rules for SCRIPT:
- 30-40 seconds when spoken naturally.
- Original wording.
- Interesting hook in the first sentence.
- Clear and conversational.
- End with a natural engagement question when appropriate.
"""


def clean_text(text):
    replacements = {
        "voice over": "",
        "voiceover": "",
        "voice-over": "",
        "Voice Over": "",
        "Voiceover": "",
        "Voice-over": "",
        "narration": "",
        "Narration": "",
        "narrator": "",
        "Narrator": "",
        "production": "",
        "Production": "",
        "script": "",
        "Script": "",
        "scene": "",
        "Scene": "",
        "on screen": "",
        "On screen": "",
        "visual": "",
        "Visual": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()


def extract_section(text, name):
    pattern = rf"{name}\s*:\s*(.*?)(?=\n[A-Z_ ]+\s*:|$)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(1).strip()

    return ""


def main():
    print("================================")
    print("USA DOSE SCRIPT GENERATOR")
    print("================================")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=PROMPT,
        )

        result = response.text.strip()

    except Exception as e:
        print("ERROR generating script:")
        print(e)
        sys.exit(1)

    result = clean_text(result)

    title = extract_section(result, "TITLE")
    hashtags = extract_section(result, "HASHTAGS")
    script = extract_section(result, "SCRIPT")

    if not title:
        print("ERROR: Title was not generated.")
        sys.exit(1)

    if not script:
        print("ERROR: Script was not generated.")
        sys.exit(1)

    # Remove accidental labels from generated text
    title = re.sub(
        r"^(title)\s*:\s*",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    hashtags = re.sub(
        r"^(hashtags)\s*:\s*",
        "",
        hashtags,
        flags=re.IGNORECASE,
    ).strip()

    script = re.sub(
        r"^(script)\s*:\s*",
        "",
        script,
        flags=re.IGNORECASE,
    ).strip()

    # Make sure there are at least 5 hashtags.
    hashtag_list = re.findall(r"#\w+", hashtags)

    if len(hashtag_list) < 5:
        print("ERROR: Fewer than 5 hashtags generated.")
        sys.exit(1)

    # Final forbidden-word safety check
    forbidden = [
        "voice over",
        "voiceover",
        "voice-over",
        "narration",
        "narrator",
        "narrated",
        "production",
        "on screen",
    ]

    lowered = script.lower()

    for word in forbidden:
        if word in lowered:
            print(f"ERROR: Forbidden phrase found: {word}")
            sys.exit(1)

    # Save only the actual spoken script.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(script)

    # Save metadata separately for the video uploader.
    with open("video_title.txt", "w", encoding="utf-8") as f:
        f.write(title)

    with open("video_hashtags.txt", "w", encoding="utf-8") as f:
        f.write(" ".join(hashtag_list))

    print("")
    print("================================")
    print("SCRIPT GENERATED SUCCESSFULLY")
    print("================================")
    print("")
    print("TITLE:")
    print(title)
    print("")
    print("HASHTAGS:")
    print(" ".join(hashtag_list))
    print("")
    print("SCRIPT:")
    print(script)
    print("")
    print("================================")


if __name__ == "__main__":
    main()
