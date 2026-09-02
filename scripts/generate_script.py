import os
import re
import sys
from datetime import datetime
from google import genai

# ============================================================
# USA DOSE - UNIVERSAL SHORTS SCRIPT GENERATOR
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY is missing.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.7-flash"

SCRIPT_FILE = "daily_script.txt"
TITLE_FILE = "video_title.txt"
HASHTAGS_FILE = "video_hashtags.txt"


# ============================================================
# PROMPT
# ============================================================

PROMPT = r"""
You are the senior content writer for a high-retention YouTube Shorts
channel called "USA Dose".

Your job is to create ONE completely original, factual, highly engaging
YouTube Short for a broad adult American audience roughly ages 18-70.

The video must feel like a human storyteller discovered something
interesting and is telling the viewer about it.

============================================================
CONTENT GOAL
============================================================

Create a topic that can attract viewers through curiosity.

Good topic categories include:

- strange places in America
- unusual American history
- mysterious events
- forgotten disasters
- abandoned places
- strange inventions
- surprising American businesses
- unusual laws or rules
- strange towns
- hidden locations
- incredible survival stories
- unusual people or events
- technology that changed America
- money/business stories
- engineering achievements
- things Americans commonly see but don't know the story behind
- little-known historical facts
- unexpected reasons behind familiar American things

Do NOT make every video about the same type of topic.

Rotate subjects naturally.

============================================================
FACTUAL ACCURACY
============================================================

This is extremely important.

Never invent:

- statistics
- quotes
- dates
- names
- locations
- scientific claims
- historical events
- laws
- deaths
- population numbers
- government information

If a detail is uncertain, leave it out.

Prefer well-established factual information.

Do not make a false statement just to make the story more exciting.

============================================================
HOOK
============================================================

The FIRST sentence must immediately create curiosity.

Do NOT begin with:

"Today we're going to..."
"Did you know..."
"Welcome back..."
"Here's an interesting fact..."
"In this video..."
"Have you ever wondered..."

Instead begin with a strong curiosity-driven statement or question.

Examples of the STYLE:

"There's a town in America that almost disappeared overnight."

"One of the strangest buildings in America was never meant to be used
the way you think."

"Thousands of people drive past this place without knowing what happened
there."

"America once built something so strange that people still talk about it."

Do not copy these examples.

Create a new hook for the chosen story.

============================================================
STORY STRUCTURE
============================================================

Use this structure:

1. HOOK
   Immediately create curiosity.

2. SETUP
   Give only enough information to make the viewer understand the story.

3. ESCALATION
   Introduce increasingly surprising details.

4. TWIST
   Somewhere around the middle, reveal a detail that changes how the
   viewer understands the story.

5. REVEAL
   Give the satisfying explanation or important fact.

6. FINAL CURIOSITY
   End with one memorable detail or thought.

7. NATURAL ENGAGEMENT
   Ask a simple question that encourages comments.

The viewer should feel:

"I need to know what happens next."

============================================================
RETENTION RULES
============================================================

Never reveal the entire answer in the first few seconds.

Keep information moving.

Every 2-4 seconds of narration should introduce either:

- a new fact
- a new question
- a visual opportunity
- a surprising detail
- a change in direction
- a consequence
- a piece of the mystery

Avoid long explanations.

Avoid filler.

Avoid repeating the same fact.

Avoid unnecessary adjectives.

Do not make the story sound like a school textbook.

============================================================
LANGUAGE
============================================================

Use simple, natural American English.

Short sentences.

Natural spoken language.

No complicated academic vocabulary unless absolutely necessary.

Write for listening, not reading.

The narration must sound natural when spoken by a female AI voice.

Do not use emojis.

Do not use stage directions.

Do not use:

[dramatic pause]
[show image]
[music]
(camera zooms)

Only write the words that should be spoken.

============================================================
LENGTH
============================================================

Target approximately 75-105 words.

The final spoken script should normally fit a YouTube Short of roughly
30-45 seconds depending on narration speed.

Do not make it unnecessarily long.

============================================================
ORIGINALITY
============================================================

Every video must feel different.

Do not repeatedly use:

"The reason is..."
"But here's the crazy part..."
"Believe it or not..."
"You won't believe..."
"Here's the twist..."

These phrases may occasionally appear naturally, but do not make them
a template.

Vary sentence structure and storytelling style.

============================================================
VISUAL THINKING
============================================================

Write stories that naturally allow stock footage or photographs.

Prefer stories where visuals can change frequently.

Examples:

- locations
- buildings
- roads
- cities
- maps
- old photographs
- machines
- people
- landscapes
- signs
- documents
- historical scenes

Do NOT write visual instructions inside the script.

============================================================
ENDING
============================================================

The final line should encourage a natural comment.

Examples of the TYPE of ending:

"Would you have gone inside?"

"Would you still visit this place?"

"Would you have believed the story?"

"What would you have done?"

Do not use the exact examples repeatedly.

============================================================
TITLE
============================================================

After the script, create ONE curiosity-driven YouTube Shorts title.

The title should:

- be short
- create curiosity
- accurately represent the story
- avoid fake clickbait
- avoid excessive punctuation

Do not put hashtags in the title.

============================================================
HASHTAGS
============================================================

Create 5-8 relevant hashtags.

Always include:

#USA
#Shorts

The remaining hashtags must relate to the actual story.

============================================================
OUTPUT FORMAT
============================================================

Return EXACTLY this format:

SCRIPT:
[spoken narration]

TITLE:
[title]

HASHTAGS:
[hashtags separated by spaces]

Do not add anything else.
"""


# ============================================================
# CLEAN RESPONSE
# ============================================================

def clean_text(text):
    text = text.strip()

    # Remove markdown code fences
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    # Remove accidental leading/trailing quotes
    text = text.strip().strip('"').strip("'")

    return text.strip()


# ============================================================
# PARSE AI RESPONSE
# ============================================================

def parse_response(text):

    text = clean_text(text)

    script_match = re.search(
        r"SCRIPT:\s*(.*?)(?=\n\s*TITLE:)",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    title_match = re.search(
        r"TITLE:\s*(.*?)(?=\n\s*HASHTAGS:)",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    hashtags_match = re.search(
        r"HASHTAGS:\s*(.*)$",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    if not script_match:
        raise ValueError("Could not find SCRIPT section.")

    if not title_match:
        raise ValueError("Could not find TITLE section.")

    if not hashtags_match:
        raise ValueError("Could not find HASHTAGS section.")

    script = clean_text(script_match.group(1))
    title = clean_text(title_match.group(1))
    hashtags = clean_text(hashtags_match.group(1))

    return script, title, hashtags


# ============================================================
# VALIDATION
# ============================================================

def validate_script(script, title, hashtags):

    words = len(script.split())

    print(f"Generated script words: {words}")

    if words < 55:
        print("WARNING: Script is shorter than expected.")

    if words > 125:
        print("WARNING: Script is longer than expected.")

    if len(title) < 5:
        raise ValueError("Generated title is too short.")

    if "#USA" not in hashtags:
        hashtags += " #USA"

    if "#Shorts" not in hashtags:
        hashtags += " #Shorts"

    return script, title, hashtags


# ============================================================
# GENERATE
# ============================================================

def generate_content():

    print("========================================")
    print("USA DOSE SMART SCRIPT GENERATOR")
    print("========================================")
    print(f"Model: {MODEL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("Generating original factual Short...")
    print()

    last_error = None

    # Try Gemini up to 3 times
    for attempt in range(1, 4):

        try:

            print("----------------------------------------")
            print(f"Gemini attempt {attempt}/3")
            print("----------------------------------------")

            response = client.models.generate_content(
                model=MODEL,
                contents=PROMPT
            )

            # Check for empty response
            if not response or not response.text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            raw_text = response.text.strip()

            if not raw_text:
                raise ValueError(
                    "Gemini returned empty text."
                )

            print("Gemini response received.")
            print()

            # Parse response
            script, title, hashtags = parse_response(
                raw_text
            )

            # Validate generated content
            script, title, hashtags = validate_script(
                script,
                title,
                hashtags
            )

            print("Gemini generation successful.")
            print()

            return script, title, hashtags

        except Exception as e:

            last_error = e

            print()
            print("Gemini attempt failed.")
            print(f"Error: {e}")
            print()

            # Retry if attempts remain
            if attempt < 3:

                import time

                wait_time = attempt * 10

                print(
                    f"Retrying Gemini in "
                    f"{wait_time} seconds..."
                )

                time.sleep(wait_time)

    # All attempts failed
    raise RuntimeError(
        "Gemini failed after 3 attempts. "
        f"Last error: {last_error}"
    )


# ============================================================
# SAVE FILES
# ============================================================

def save_files(script, title, hashtags):

    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(script)

    with open(TITLE_FILE, "w", encoding="utf-8") as f:
        f.write(title)

    with open(HASHTAGS_FILE, "w", encoding="utf-8") as f:
        f.write(hashtags)

    print()
    print("========================================")
    print("FILES CREATED SUCCESSFULLY")
    print("========================================")
    print(f"✓ {SCRIPT_FILE}")
    print(f"✓ {TITLE_FILE}")
    print(f"✓ {HASHTAGS_FILE}")
    print()
    print("TITLE:")
    print(title)
    print()
    print("HASHTAGS:")
    print(hashtags)
    print()
    print("SCRIPT:")
    print(script)
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        script, title, hashtags = generate_content()

        save_files(
            script,
            title,
            hashtags
        )

        print("USA Dose script generation completed successfully.")

    except Exception as e:

        print()
        print("========================================")
        print("SCRIPT GENERATION FAILED")
        print("========================================")
        print(str(e))
        print()

        sys.exit(1)


if __name__ == "__main__":
    main()
