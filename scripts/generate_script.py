import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY secret is missing")

client = genai.Client(api_key=api_key)

prompt = """
You are the professional script writer for a YouTube Shorts channel called USA Dose.

Create ONE original English YouTube Short about an interesting topic related to the United States.

Requirements:
- Target audience: USA viewers
- Length: 30 to 60 seconds
- Start with a powerful curiosity hook
- Use natural American English
- Make it entertaining and informative
- Use factual information only
- Do not invent facts
- Avoid political persuasion
- End with a short call to action
- Do not use emojis
- Return ONLY the final script
"""

interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=prompt
)

script = interaction.output_text.strip()

if not script:
    raise RuntimeError("Gemini returned an empty response.")

print("AI GENERATED USA SHORT:")
print(script)

with open("daily_script.txt", "w", encoding="utf-8") as file:
    file.write(script)

print("SUCCESS: Script saved to daily_script.txt")
