import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY is not available.")
    raise SystemExit(1)

try:
    client = genai.Client(api_key=api_key)

    prompt = """
You are the professional script writer for a YouTube Shorts channel called USA Dose.

Create ONE original English YouTube Short about an interesting topic related to the United States.

Requirements:
- Target audience: USA viewers
- Length: 30 to 60 seconds
- Start with a strong curiosity hook
- Use natural American English
- Make it entertaining and informative
- Use only factual information
- Do not invent facts
- Avoid political persuasion
- End with a short call to action
- Do not use emojis
- Return ONLY the final script
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    script = response.text.strip()

    if not script:
        raise RuntimeError("Gemini returned an empty response.")

    print("AI GENERATED USA SHORT:")
    print(script)

    with open("daily_script.txt", "w", encoding="utf-8") as file:
        file.write(script)

    print("SUCCESS: Script saved to daily_script.txt")

except Exception as error:
    print("ERROR:", str(error))
    raise
