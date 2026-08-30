import os
import sys
import re

from elevenlabs.client import ElevenLabs


VOICE_NAME = "Laura"
VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"
MODEL_ID = "eleven_multilingual_v2"

SCRIPT_FILE = "daily_script.txt"
OUTPUT_FILE = "voice.mp3"

MAX_CHARACTERS = 350
MIN_WORDS = 40
MAX_WORDS = 55


def get_api_keys():

    keys = []

    for i in range(1, 6):

        key = os.getenv(
            f"ELEVENLABS_API_KEY_{i}"
        )

        if key:
            key = key.strip()

            if key:
                keys.append(
                    (i, key)
                )

    # Old secret support
    if not keys:

        old_key = os.getenv(
            "ELEVENLABS_API_KEY"
        )

        if old_key:
            keys.append(
                (1, old_key.strip())
            )

    return keys


def clean_text(text):

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
        "scene:",
        "script:",
    ]

    for phrase in forbidden:

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


def main():

    print("================================")
    print("USA DOSE FEMALE VOICE")
    print("================================")
    print(f"Voice: {VOICE_NAME}")
    print(f"Voice ID: {VOICE_ID}")
    print(f"Model: {MODEL_ID}")
    print("================================")

    api_keys = get_api_keys()

    print(
        f"API keys available: {len(api_keys)}"
    )

    if not api_keys:

        print("")
        print(
            "ERROR: No ElevenLabs API keys found."
        )

        sys.exit(1)

    if not os.path.isfile(
        SCRIPT_FILE
    ):

        print(
            "ERROR: daily_script.txt not found."
        )

        sys.exit(1)

    with open(
        SCRIPT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        text = f.read().strip()

    if not text:

        print(
            "ERROR: daily_script.txt is empty."
        )

        sys.exit(1)

    text = clean_text(text)

    word_count = len(
        text.split()
    )

    character_count = len(text)

    print("")
    print("================================")
    print("SCRIPT CHECK")
    print("================================")
    print(
        f"Words: {word_count}"
    )
    print(
        f"Characters: {character_count}"
    )
    print("================================")

    if word_count < MIN_WORDS:

        print(
            f"ERROR: Script is too short."
        )

        print(
            f"Minimum words: {MIN_WORDS}"
        )

        sys.exit(1)

    if word_count > MAX_WORDS:

        print(
            f"ERROR: Script is too long."
        )

        print(
            f"Maximum words: {MAX_WORDS}"
        )

        sys.exit(1)

    print("")
    print("================================")
    print("ELEVENLABS QUOTA PROTECTION")
    print("================================")
    print(
        f"Characters required: {character_count}"
    )
    print(
        f"Maximum allowed: {MAX_CHARACTERS}"
    )
    print("================================")

    if character_count > MAX_CHARACTERS:

        print("")
        print(
            "ERROR: Script exceeds the "
            "ElevenLabs safety limit."
        )

        print(
            "Voice generation cancelled."
        )

        sys.exit(1)

    # Remove old file
    if os.path.isfile(
        OUTPUT_FILE
    ):

        os.remove(
            OUTPUT_FILE
        )

    # ======================================================
    # MULTI KEY FAILOVER
    # ======================================================

    for key_number, api_key in api_keys:

        print("")
        print("================================")
        print(
            f"TRYING ELEVENLABS API KEY {key_number}"
        )
        print("================================")

        try:

            client = ElevenLabs(
                api_key=api_key
            )

            print("")
            print(
                "Generating Laura female voice..."
            )

            audio = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                text=text,
                output_format="mp3_44100_128",
            )

            with open(
                OUTPUT_FILE,
                "wb"
            ) as f:

                for chunk in audio:

                    if chunk:
                        f.write(chunk)

            if not os.path.isfile(
                OUTPUT_FILE
            ):

                raise RuntimeError(
                    "voice.mp3 was not created."
                )

            file_size = os.path.getsize(
                OUTPUT_FILE
            )

            if file_size <= 0:

                raise RuntimeError(
                    "voice.mp3 is empty."
                )

            print("")
            print("================================")
            print("VOICE CREATED SUCCESSFULLY")
            print("================================")
            print(
                f"API Key used: {key_number}"
            )
            print(
                f"Voice: {VOICE_NAME}"
            )
            print(
                f"Words: {word_count}"
            )
            print(
                f"Characters: {character_count}"
            )
            print(
                f"Output: {OUTPUT_FILE}"
            )
            print(
                f"File size: {file_size} bytes"
            )
            print("================================")

            return

        except Exception as e:

            error = str(e).lower()

            print("")
            print("================================")
            print(
                f"ELEVENLABS KEY {key_number} ERROR"
            )
            print("================================")
            print(e)
            print("================================")

            quota_error = (
                "quota" in error
                or
                "quota_exceeded" in error
                or
                "credits" in error
                or
                "credit" in error
                or
                "rate limit" in error
                or
                "too many requests" in error
            )

            if quota_error:

                print(
                    f"API KEY {key_number} "
                    "HAS NO USABLE QUOTA."
                )

                print(
                    "Trying next API key..."
                )

                continue

            print(
                "Trying next API key..."
            )

            continue

    print("")
    print("================================")
    print("ALL ELEVENLABS KEYS FAILED")
    print("================================")
    print(
        "No voice.mp3 was created."
    )
    print(
        "Workflow stopped safely."
    )
    print("================================")

    sys.exit(1)


if __name__ == "__main__":
    main()
