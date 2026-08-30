import os
import sys

from elevenlabs.client import ElevenLabs


# ==========================================================
# USA DOSE - ELEVENLABS FEMALE VOICE
# ==========================================================

VOICE_NAME = "Laura"
VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"

MODEL_ID = "eleven_multilingual_v2"

SCRIPT_FILE = "daily_script.txt"
OUTPUT_FILE = "voice.mp3"

# ==========================================================
# QUOTA PROTECTION
# ==========================================================
# Keep scripts short so ElevenLabs credits are not wasted.
MAX_CHARACTERS = 350
MIN_WORDS = 55
MAX_WORDS = 85


def main():

    print("================================")
    print("USA DOSE FEMALE VOICE")
    print("================================")
    print(f"Voice: {VOICE_NAME}")
    print(f"Voice ID: {VOICE_ID}")
    print(f"Model: {MODEL_ID}")
    print("================================")

    # ------------------------------------------------------
    # CHECK API KEY
    # ------------------------------------------------------

    api_key = os.getenv("ELEVENLABS_API_KEY")

    if not api_key:
        print("")
        print("ELEVENLABS ERROR")
        print("ELEVENLABS_API_KEY is missing.")
        sys.exit(1)

    # ------------------------------------------------------
    # CHECK SCRIPT
    # ------------------------------------------------------

    if not os.path.isfile(SCRIPT_FILE):
        print("")
        print("ERROR: daily_script.txt not found.")
        sys.exit(1)

    with open(
        SCRIPT_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        text = f.read().strip()

    if not text:
        print("")
        print("ERROR: daily_script.txt is empty.")
        sys.exit(1)

    # ------------------------------------------------------
    # CLEAN TEXT
    # ------------------------------------------------------

    forbidden_phrases = [
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
        "script:",
        "scene:",
    ]

    lowered = text.lower()

    for phrase in forbidden_phrases:

        if phrase in lowered:

            print("")
            print("ERROR: Forbidden production text found.")
            print(f"Found: {phrase}")
            print("")
            print("Voice generation cancelled.")
            sys.exit(1)

    # ------------------------------------------------------
    # WORD COUNT
    # ------------------------------------------------------

    word_count = len(text.split())

    print("")
    print("================================")
    print("SCRIPT CHECK")
    print("================================")
    print(f"Words: {word_count}")
    print(f"Characters: {len(text)}")
    print("================================")

    if word_count < MIN_WORDS:

        print("")
        print(
            f"ERROR: Script is too short."
        )
        print(
            f"Minimum words: {MIN_WORDS}"
        )
        sys.exit(1)

    if word_count > MAX_WORDS:

        print("")
        print(
            f"ERROR: Script is too long."
        )
        print(
            f"Maximum words: {MAX_WORDS}"
        )
        print("")
        print(
            "Voice generation cancelled to save credits."
        )
        sys.exit(1)

    # ------------------------------------------------------
    # CHARACTER LIMIT
    # ------------------------------------------------------

    character_count = len(text)

    print("")
    print("================================")
    print("ELEVENLABS QUOTA PROTECTION")
    print("================================")
    print(f"Characters required: {character_count}")
    print(f"Maximum allowed: {MAX_CHARACTERS}")
    print("================================")

    if character_count > MAX_CHARACTERS:

        print("")
        print(
            "ERROR: Script exceeds the ElevenLabs "
            "character safety limit."
        )
        print("")
        print(
            "Voice generation cancelled."
        )
        print(
            "No ElevenLabs credits were intentionally spent."
        )

        sys.exit(1)

    print("")
    print("Quota check: PASSED")

    # ------------------------------------------------------
    # CREATE CLIENT
    # ------------------------------------------------------

    try:

        client = ElevenLabs(
            api_key=api_key
        )

    except Exception as e:

        print("")
        print("ELEVENLABS CLIENT ERROR")
        print(e)
        sys.exit(1)

    # ------------------------------------------------------
    # GENERATE VOICE
    # ------------------------------------------------------

    print("")
    print("================================")
    print("GENERATING NATURAL FEMALE VOICE")
    print("================================")
    print("")
    print("Voice: Laura")
    print("Gender: Female")
    print("Accent: American")
    print("")
    print("Generating...")
    print("")

    try:

        audio = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            text=text,
            output_format="mp3_44100_128",
        )

    except Exception as e:

        print("")
        print("================================")
        print("ELEVENLABS ERROR")
        print("================================")
        print(e)
        sys.exit(1)

    # ------------------------------------------------------
    # SAVE MP3
    # ------------------------------------------------------

    try:

        with open(
            OUTPUT_FILE,
            "wb"
        ) as f:

            for chunk in audio:

                if chunk:

                    f.write(chunk)

    except Exception as e:

        print("")
        print("ERROR SAVING VOICE")
        print(e)
        sys.exit(1)

    # ------------------------------------------------------
    # VERIFY FILE
    # ------------------------------------------------------

    if not os.path.isfile(OUTPUT_FILE):

        print("")
        print("ERROR: voice.mp3 was not created.")
        sys.exit(1)

    file_size = os.path.getsize(
        OUTPUT_FILE
    )

    if file_size == 0:

        print("")
        print("ERROR: voice.mp3 is empty.")
        sys.exit(1)

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print("")
    print("================================")
    print("VOICE CREATED SUCCESSFULLY")
    print("================================")
    print(f"Voice: {VOICE_NAME}")
    print("Gender: Female")
    print("Accent: American")
    print(f"Characters: {character_count}")
    print(f"Words: {word_count}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"File size: {file_size} bytes")
    print("Quota protection: ACTIVE")
    print("================================")


if __name__ == "__main__":
    main()
