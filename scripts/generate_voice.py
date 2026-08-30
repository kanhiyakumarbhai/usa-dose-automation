import os
import sys
import re

from elevenlabs.client import ElevenLabs


# ==========================================================
# USA DOSE - LAURA FEMALE VOICE
# MULTI API KEY FAILOVER
# ==========================================================

VOICE_NAME = "Laura"
VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"
MODEL_ID = "eleven_multilingual_v2"

SCRIPT_FILE = "daily_script.txt"
OUTPUT_FILE = "voice.mp3"

MIN_WORDS = 40
MAX_WORDS = 55
MAX_CHARACTERS = 350


# ==========================================================
# GET ELEVENLABS KEYS
# ==========================================================

def get_api_keys():

    keys = []

    for number in range(1, 6):

        key = os.getenv(
            f"ELEVENLABS_API_KEY_{number}"
        )

        if key and key.strip():

            keys.append(
                (
                    number,
                    key.strip()
                )
            )

    # Old secret support
    if not keys:

        old_key = os.getenv(
            "ELEVENLABS_API_KEY"
        )

        if old_key and old_key.strip():

            keys.append(
                (
                    1,
                    old_key.strip()
                )
            )

    return keys


# ==========================================================
# CLEAN SCRIPT
# ==========================================================

def clean_script(text):

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


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("================================")
    print("USA DOSE FEMALE VOICE")
    print("================================")
    print(f"Voice: {VOICE_NAME}")
    print(f"Voice ID: {VOICE_ID}")
    print(f"Model: {MODEL_ID}")
    print("================================")

    # ------------------------------------------------------
    # API KEYS
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # SCRIPT FILE
    # ------------------------------------------------------

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
    ) as file:

        text = file.read().strip()

    if not text:

        print(
            "ERROR: daily_script.txt is empty."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # CLEAN
    # ------------------------------------------------------

    text = clean_script(
        text
    )

    # ------------------------------------------------------
    # SCRIPT CHECK
    # ------------------------------------------------------

    word_count = len(
        text.split()
    )

    character_count = len(
        text
    )

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

    # ------------------------------------------------------
    # WORD LIMIT
    # ------------------------------------------------------

    if word_count < MIN_WORDS:

        print("")
        print(
            "ERROR: Script is too short."
        )

        print(
            f"Minimum words: {MIN_WORDS}"
        )

        sys.exit(1)

    if word_count > MAX_WORDS:

        print("")
        print(
            "ERROR: Script is too long."
        )

        print(
            f"Maximum words: {MAX_WORDS}"
        )

        print(
            "Voice generation cancelled."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # CHARACTER LIMIT
    # ------------------------------------------------------

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
            "ERROR: Script exceeds 350 characters."
        )

        print(
            "Voice generation cancelled."
        )

        print(
            "No ElevenLabs request was sent."
        )

        sys.exit(1)

    print("")
    print(
        "Quota check: PASSED"
    )

    # ------------------------------------------------------
    # REMOVE OLD AUDIO
    # ------------------------------------------------------

    if os.path.isfile(
        OUTPUT_FILE
    ):

        try:

            os.remove(
                OUTPUT_FILE
            )

        except Exception as error:

            print(
                "ERROR removing old voice.mp3:"
            )

            print(error)

            sys.exit(1)

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

            # --------------------------------------------------
            # SAVE AUDIO
            # --------------------------------------------------

            with open(
                OUTPUT_FILE,
                "wb"
            ) as file:

                for chunk in audio:

                    if chunk:

                        file.write(
                            chunk
                        )

            # --------------------------------------------------
            # VERIFY
            # --------------------------------------------------

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

            # --------------------------------------------------
            # SUCCESS
            # --------------------------------------------------

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
                "Gender: Female"
            )
            print(
                "Accent: American"
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
            print(
                "Multi-key failover: ACTIVE"
            )
            print("================================")

            return

        except Exception as error:

            error_text = str(
                error
            ).lower()

            print("")
            print("================================")
            print(
                f"ELEVENLABS KEY {key_number} ERROR"
            )
            print("================================")
            print(error)
            print("================================")

            # --------------------------------------------------
            # QUOTA ERROR
            # --------------------------------------------------

            quota_error = (

                "quota" in error_text

                or

                "quota_exceeded" in error_text

                or

                "credits" in error_text

                or

                "credit" in error_text

                or

                "rate limit" in error_text

                or

                "too many requests" in error_text
            )

            if quota_error:

                print("")
                print(
                    f"API KEY {key_number} "
                    "HAS NO USABLE QUOTA."
                )

                print(
                    "Trying next API key..."
                )

                continue

            # --------------------------------------------------
            # INVALID KEY
            # --------------------------------------------------

            print("")
            print(
                f"API KEY {key_number} "
                "FAILED."
            )

            print(
                "Trying next API key..."
            )

            continue

    # ======================================================
    # ALL KEYS FAILED
    # ======================================================

    print("")
    print("================================")
    print("ALL ELEVENLABS KEYS FAILED")
    print("================================")
    print("")
    print(
        "No voice.mp3 was created."
    )
    print("")
    print(
        "Workflow stopped safely."
    )
    print(
        "Video generation should not continue."
    )
    print("================================")

    sys.exit(1)


if __name__ == "__main__":

    main()
