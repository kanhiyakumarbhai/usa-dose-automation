import os
import subprocess
import sys

script_file = "daily_script.txt"
output_file = "voice.mp3"

if not os.path.exists(script_file):
    print("ERROR: daily_script.txt not found")
    sys.exit(1)

with open(script_file, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("ERROR: Script is empty")
    sys.exit(1)

# Free system TTS using espeak-ng
result = subprocess.run(
    [
        "espeak-ng",
        "-v", "en-us",
        "-s", "155",
        "-w", output_file,
        text
    ],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("TTS ERROR:")
    print(result.stderr)
    sys.exit(1)

if not os.path.exists(output_file):
    print("ERROR: Voice file was not created")
    sys.exit(1)

print("SUCCESS: AI voice created")
print(f"File: {output_file}")
