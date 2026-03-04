#!/usr/bin/env python3
"""Query Gemini 3 Flash directly with Google Search grounding for Operation True Promise 4 wave data."""

import os
import json
import httpx
from pathlib import Path

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.0-flash"  # gemini 3 flash
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "waves.md"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_MSG = (
    "You are a military/OSINT research assistant. "
    "Today's date is 2026-03-04. The user is requesting structured data about ongoing events. "
    "Return ONLY the CSV data requested — no commentary, no markdown fences, just the CSV with a header row. "
    "Use the exact column names specified. If data is unknown for a field, leave it empty. "
    "Be as accurate as possible — do not fabricate data. If you are unsure about a value, leave it blank rather than guessing. "
    "You MUST use Google Search to find the latest information about each wave of Operation True Promise 4. "
    "Search for each wave individually. There are at least 17 announced waves as of March 4, 2026. "
    "Search for 'Operation True Promise 4 wave' and 'IRGC wave announcement' to find details."
)

prompt = PROMPT_FILE.read_text()

payload = {
    "system_instruction": {
        "parts": [{"text": SYSTEM_MSG}]
    },
    "contents": [
        {
            "role": "user",
            "parts": [{"text": prompt}]
        }
    ],
    "tools": [
        {"google_search": {}}
    ],
    "generationConfig": {
        "temperature": 0.1,
        "maxOutputTokens": 65536,
    }
}

print("Querying Gemini 3 Flash with Google Search grounding...")
resp = httpx.post(URL, json=payload, timeout=300.0)
resp.raise_for_status()
data = resp.json()

# Save raw response
raw_path = OUTPUT_DIR / "gemini-3-flash-grounded_raw.json"
with open(raw_path, "w") as f:
    json.dump(data, f, indent=2)

# Extract text content
try:
    parts = data["candidates"][0]["content"]["parts"]
    text = "".join(p.get("text", "") for p in parts)
except (KeyError, IndexError) as e:
    print(f"Error extracting content: {e}")
    print(json.dumps(data, indent=2)[:2000])
    exit(1)

# Save CSV
csv_path = OUTPUT_DIR / "gemini-3-flash-grounded_waves.csv"
with open(csv_path, "w") as f:
    f.write(text)

lines = text.strip().split("\n")
print(f"Saved: {csv_path}")
print(f"Rows: {len(lines) - 1} waves (plus header)")
print(f"Preview:\n{text[:500]}")
