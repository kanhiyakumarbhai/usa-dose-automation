import os
import sys
import re
import asyncio

from elevenlabs.client import ElevenLabs


VOICE_NAME = "Laura"
VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"
MODEL_ID = "eleven_multilingual_v2"

SCRIPT_FILE = "daily_script.txt"
OUTPUT_FILE = "voice.mp3"

MIN_WORDS = 40
MAX_WORDS = 55
MAX_CHARACTERS = 350

# Free fallback female US voice
EDGE_VOICE = "en-US-JennyNeural"


def get_api_keys():

    keys = []

    for number in range(1, 6):

        key = os.getenv(
            f"ELEVENLABS_API_KEY_{number}"
        )

        if key and key.strip():

            keys.append(
                (number, key.strip())
            )

    # Old secret name support
    if not keys:

        old_key = os.getenv(
            "ELEVENLABS_API_KEY"
        )

        if old_key and old_key.strip():

            keys.append(
                (1, old_key.strip())
            )

    return keys


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


def try_elevenlabs(api_keys, text):

    if not api_keys:

        print("")
        print("No ElevenLabs API keys available.")
        return False

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
            ) as file:

                for chunk in audio:

                    if chunk:
                        file.write(chunk)

            if not os.path.isfile(
                OUTPUT_FILE
            ):

                raise RuntimeError(
                    "voice.mp3 was not created."
                )

            size = os.path.getsize(
                OUTPUT_FILE
            )

            if size <= 0:

                raise RuntimeError(
                    "voice.mp3 is empty."
                )

            print("")
            print("================================")
            print("ELEVENLABS VOICE SUCCESS")
            print("================================")
            print(
                f"Voice: {VOICE_NAME}"
            )
            print(
                f"API Key: {key_number}"
            )
            print(
                f"Output: {OUTPUT_FILE}"
            )
            print(
                f"File size: {size} bytes"
            )
            print("================================")

            return True

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

            if (
                "quota" in error_text
                or "credits" in error_text
                or "credit" in error_text
                or "rate limit" in error_text
                or "too many requests" in error_text
            ):

                print(
                    f"API KEY {key_number} "
                    "HAS NO USABLE QUOTA."
                )

            elif (
                "permission" in error_text
                or "missing_permissions" in error_text
                or "unauthorized" in error_text
                or "text_to_speech" in error_text
            ):

                print(
                    f"API KEY {key_number} "
                    "DOES NOT HAVE TTS PERMISSION."
                )

            else:

                print(
                    f"API KEY {key_number} FAILED."
                )

            print(
                "Trying next ElevenLabs key..."
            )

    print("")
    print("================================")
    print("ELEVENLABS UNAVAILABLE")
    print("================================")
    print(
        "Switching to free female TTS."
    )
    print("================================")

    return False


async def generate_edge_voice_async(text):

    import edge_tts

    print("")
    print("================================")
    print("FREE FEMALE TTS FALLBACK")
    print("================================")
    print(
        f"Voice: {EDGE_VOICE}"
    )
    print(
        "Provider: Microsoft Edge TTS"
    )
    print("================================")

    communicate = edge_tts.Communicate(
        text=text,
        voice=EDGE_VOICE,
        rate="+0%",
        volume="+0%",
        pitch="+0Hz",
    )

    await communicate.save(
        OUTPUT_FILE
    )


def generate_edge_voice(text):

    try:

        asyncio.run(
            generate_edge_voice_async(
                text
            )
        )

    except Exception as error:

        print("")
        print("================================")
        print("FREE TTS ERROR")
        print("================================")
        print(error)
        print("================================")

        return False

    if not os.path.isfile(
        OUTPUT_FILE
    ):

        print(
            "ERROR: voice.mp3 was not created."
        )

        return False

    size = os.path.getsize(
        OUTPUT_FILE
    )

    if size <= 0:

        print(
            "ERROR: voice.mp3 is empty."
        )

        return False

    print("")
    print("================================")
    print("FREE FEMALE VOICE SUCCESS")
    print("================================")
    print(
        f"Voice: {EDGE_VOICE}"
    )
    print(
        f"Output: {OUTPUT_FILE}"
    )
    print(
        f"File size: {size} bytes"
    )
    print(
        "ElevenLabs credits used: 0"
    )
    print("================================")

    return True


def main():

    print("================================")
    print("USA DOSE SMART FEMALE VOICE")
    print("================================")
    print(
        f"Primary: {VOICE_NAME}"
    )
    print(
        f"Fallback: {EDGE_VOICE}"
    )
    print("================================")

    # ------------------------------------------------------
    # READ SCRIPT
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
    # SAFETY LIMITS
    # ------------------------------------------------------

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

    if character_count > MAX_CHARACTERS:

        print(
            "ERROR: Script exceeds "
            "350 character safety limit."
        )

        sys.exit(1)

    # ------------------------------------------------------
    # REMOVE OLD AUDIO
    # ------------------------------------------------------

    if os.path.isfile(
        OUTPUT_FILE
    ):

        os.remove(
            OUTPUT_FILE
        )

    # ------------------------------------------------------
    # ELEVENLABS
    # ------------------------------------------------------

    api_keys = get_api_keys()

    print("")
    print(
        f"ElevenLabs API keys available: "
        f"{len(api_keys)}"
    )

    if try_elevenlabs(
        api_keys,
        text
    ):

        print("")
        print(
            "Primary ElevenLabs voice completed."
        )

        return

    # ------------------------------------------------------
    # FREE FALLBACK
    # ------------------------------------------------------

    if generate_edge_voice(
        text
    ):

        print("")
        print("================================")
        print("VOICE GENERATION COMPLETE")
        print("================================")
        print(
            "Free female fallback succeeded."
        )
        print(
            "Video generation can continue."
        )
        print("================================")

        return

    # ------------------------------------------------------
    # EVERYTHING FAILED
    # ------------------------------------------------------

    print("")
    print("================================")
    print("ALL VOICE SYSTEMS FAILED")
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
