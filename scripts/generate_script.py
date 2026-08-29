import random
from datetime import datetime

topics = [
    "A surprising fact about New York City",
    "Why Americans drive on the right side of the road",
    "A strange law in the United States",
    "The most unusual place in America",
    "A surprising fact about the Statue of Liberty",
    "Why American houses often use wooden structures",
    "A little-known fact about Las Vegas",
    "The story behind the American flag",
    "A surprising fact about Yellowstone",
    "Something most people don't know about American roads"
]

topic = random.choice(topics)

script = f"""
HOOK:
Did you know this surprising fact about the USA? 🇺🇸

TOPIC:
{topic}

SCRIPT:
Here is something most people don't know about America.

{topic}.

This is one of those fascinating facts that makes the United States so interesting.

Follow USA Dose for more amazing USA facts and stories! 🇺🇸🔥
"""

print("TOPIC:")
print(topic)
print("\nSCRIPT:")
print(script)

with open("daily_script.txt", "w", encoding="utf-8") as f:
    f.write(f"USA DOSE DAILY SCRIPT\n\nTopic: {topic}\n\n{script}")

print("\nScript saved successfully!")
