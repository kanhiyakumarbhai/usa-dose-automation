```python
import os
import sys
import re

from elevenlabs.client import ElevenLabs


# ==========================================================
# USA DOSE - ELEVENLABS MULTI-KEY FAILOVER
# ==========================================================

VOICE_NAME = "Laura"
VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"

MODEL_ID = "eleven_multilingual_v2"

SCRIPT_FILE = "daily_script.txt"
OUTPUT_FILE = "voice.mp3"

# ==========================================================
# QUOTA PROTECTION
# ==========================================================

MAX_CHARACTERS = 350
MIN_WORDS = 40
MAX_WORDS = 60


# ==========================================================
# ELEVENLABS API KEYS
# ==========================================================
# GitHub Secrets:
#
# ELEVENLABS_API_KEY_1
# ELEVENLABS_API_KEY_2
# ELEVENLABS_API_KEY_3
#
# Add more keys if needed:
# ELEVENLABS_API_KEY_4
# ELEVENLABS_API_KEY_5
# ==========================================================

def get_api_keys():

    keys = []

    for i in range(1, 11):

        key = os.getenv(
            f"ELEVENLABS_API_KEY_{i}"
        )

        if key:
            key = key.strip()

            if key:
                keys.append(
                    (i, key)
                )

    # Backward compatibility:
    # If only ELEVENLABS_API_KEY exists,
    # use it as the first key.

    if not keys:

        old_key = os.getenv(
            "ELEVENLABS_API_KEY"
        )

        if old_key:
            old_key = old_key.strip()

            if old_key:
                keys.append(
                    (1, old_key)
                )

    return keys


# ==========================================================
# CLEAN SCRIPT
# ==========================================================

def clean_text(text):

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
    # GET API KEYS
    # ------------------------------------------------------

    api_keys = get_api_keys()

    if not api_keys:

        print("")
        print("ELEVENLABS ERROR")
        print("")
        print(
            "No ElevenLabs API keys found."
        )
        print("")
        print(
            "Add these GitHub Secrets:"
        )
        print(
            "ELEVENLABS_API_KEY"
        )
        print(
            "ELEVENLABS_API_KEY_2"
        )
        print(
            "ELEVENLABS_API_KEY_3"
        )

        sys.exit(1)

    print("")
    print(
        f"API keys available: {len(api_keys)}"
    )

    # ------------------------------------------------------
    # CHECK SCRIPT FILE
    # ------------------------------------------------------

    if not os.path.isfile(
        SCRIPT_FILE
    ):

        print("")
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

        print("")
        print(
            "ERROR: daily_script.txt is empty."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # CLEAN SCRIPT
    # ------------------------------------------------------

    text = clean_text(
        text
    )

    # ------------------------------------------------------
    # CHECK FOR FORBIDDEN WORDS
    # ------------------------------------------------------

    forbidden_words = [
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

    lower_text = text.lower()

    for phrase in forbidden_words:

        if phrase in lower_text:

            print("")
            print(
                "ERROR: Forbidden production text found."
            )

            print(
                f"Found: {phrase}"
            )

            print("")
            print(
                "Voice generation cancelled."
            )

            sys.exit(1)

    # ------------------------------------------------------
    # WORD COUNT
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

        print("")
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
            "ERROR: Script exceeds the "
            "ElevenLabs character safety limit."
        )

        print("")
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
    # REMOVE OLD VOICE FILE
    # ------------------------------------------------------

    if os.path.isfile(
        OUTPUT_FILE
    ):

        try:

            os.remove(
                OUTPUT_FILE
            )

        except Exception as e:

            print(
                "ERROR removing old voice.mp3:"
            )

            print(e)

            sys.exit(1)

    # ------------------------------------------------------
    # TRY API KEYS ONE BY ONE
    # ------------------------------------------------------

    success = False

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
                "Generating natural female narration..."
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
            ) as f:

                for chunk in audio:

                    if chunk:

                        f.write(chunk)

            # --------------------------------------------------
            # VERIFY AUDIO
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

            success = True

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
                "Failover: ACTIVE"
            )
            print("================================")

            break

        except Exception as e:

            error_text = str(
                e
            ).lower()

            print("")
            print("================================")
            print(
                f"ELEVENLABS KEY {key_number} ERROR"
            )
            print("================================")
            print(e)
            print("================================")

            # --------------------------------------------------
            # DETECT QUOTA ERRORS
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
                "exceeds your quota" in error_text
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

                if key_number != api_keys[-1][0]:

                    print(
                        "Switching to next API key..."
                    )

                    continue

                else:

                    print(
                        "No more API keys available."
                    )

                    continue

            # --------------------------------------------------
            # INVALID KEY
            # --------------------------------------------------

            invalid_key = (
                "401" in error_text
                or
                "invalid api key" in error_text
                or
                "invalid_api_key" in error_text
                or
                "unauthorized" in error_text
            )

            if invalid_key:

                print("")
                print(
                    f"API KEY {key_number} "
                    "IS INVALID."
                )

                print(
                    "Trying next available key..."
                )

                continue

            # --------------------------------------------------
            # TEMPORARY SERVER ERROR
            # --------------------------------------------------

            temporary_error = (
                "500" in error_text
                or
                "502" in error_text
                or
                "503" in error_text
                or
                "504" in error_text
                or
                "timeout" in error_text
                or
                "temporarily unavailable"
                in error_text
            )

            if temporary_error:

                print("")
                print(
                    "Temporary ElevenLabs error."
                )

                print(
                    "Trying next API key..."
                )

                continue

            # --------------------------------------------------
            # UNKNOWN ERROR
            # --------------------------------------------------

            print("")
            print(
                "Unknown ElevenLabs error."
            )

            print(
                "Trying next API key..."
            )

            continue

    # ------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------

    if not success:

        print("")
        print("================================")
        print("ALL ELEVENLABS KEYS FAILED")
        print("================================")
        print("")
        print(
            "No voice.mp3 was successfully created."
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
```
