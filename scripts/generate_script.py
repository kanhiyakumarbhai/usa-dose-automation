import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY secret is missing")

client = genai.Client(api_key=api_key)

prompt = """
You are the script writer for a YouTube Shorts channel called USA Dose.

Create ONE original English YouTube Short about an interesting topic related to the United States.

Requirements:
- Target audience: people in the USA
- Length: 30 to 60 seconds
- Start with a powerful hook
- Use simple, natural American English
- Make it entertaining and informative
- Avoid political persuasion
- Avoid false or made-up facts
- End with a short call to action
- Do not use emojis inside the script
- Return ONLY the script, without explanations

Choose an interesting topic about USA facts, American history,
unusual places, culture, cities, inventions, traditions,
strange facts, or surprising everyday life.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=prompt
)

script = response.text.strip()

print("AI GENERATED USA SHORT:")
print(script)

with open("daily_script.txt", "w", encoding="utf-8") as f:
    f.write(script)

print("Script saved successfully!")
