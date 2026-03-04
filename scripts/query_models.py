#!/usr/bin/env python3
"""Query multiple OpenRouter models with web access for Operation True Promise 4 wave data."""

import os
import json
import httpx
import sys
from pathlib import Path
from datetime import datetime

API_KEY = os.environ.get("OPENROUTER_API_KEY", "REDACTED_OPENROUTER_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "waves.md"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

MODELS = [
    {
        "id": "perplexity/sonar-deep-research",
        "name": "perplexity-sonar",
        "note": "Real-time web search built-in",
    },
    {
        "id": "google/gemini-2.5-pro-preview-03-25",
        "name": "gemini-2.5-pro",
        "note": "Google search grounding",
    },
    {
        "id": "openai/gpt-4o-search-preview",
        "name": "gpt-4o-search",
        "note": "Bing search integration",
    },
    {
        "id": "x-ai/grok-3-beta",
        "name": "grok-3",
        "note": "X/Twitter real-time data access",
    },
    {
        "id": "google/gemini-3-flash-preview-20251217",
        "name": "gemini-3-flash",
        "note": "Gemini 3 Flash with Google search grounding",
    },
]

SYSTEM_MSG = (
    "You are a military/OSINT research assistant. You have access to real-time web information. "
    "Today's date is 2026-03-04. The user is requesting structured data about ongoing events. "
    "Return ONLY the CSV data requested — no commentary, no markdown fences, just the CSV with a header row. "
    "Use the exact column names specified. If data is unknown for a field, leave it empty. "
    "Be as accurate as possible — do not fabricate data. If you are unsure about a value, leave it blank rather than guessing."
)


def query_model(model: dict, prompt: str) -> str:
    """Send prompt to a model via OpenRouter and return the response text."""
    print(f"\n{'='*60}")
    print(f"Querying: {model['name']} ({model['id']})")
    print(f"Note: {model['note']}")
    print(f"{'='*60}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/danielrosehill/Iran-Israel-War-2026-Data",
        "X-Title": "Operation True Promise 4 Data Collection",
    }

    payload = {
        "model": model["id"],
        "messages": [
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 32000,
    }

    # Enable Google search grounding for Gemini models
    if "gemini" in model["id"]:
        payload["tools"] = [{"google_search": {}}]

    try:
        resp = httpx.post(BASE_URL, headers=headers, json=payload, timeout=300.0)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Save raw response
        raw_path = OUTPUT_DIR / f"{model['name']}_raw.json"
        with open(raw_path, "w") as f:
            json.dump(data, f, indent=2)

        # Save CSV output
        csv_path = OUTPUT_DIR / f"{model['name']}_waves.csv"
        with open(csv_path, "w") as f:
            f.write(content)

        print(f"Saved: {csv_path}")
        print(f"Response preview (first 500 chars):\n{content[:500]}")
        return content

    except Exception as e:
        print(f"ERROR with {model['name']}: {e}")
        if hasattr(e, "response"):
            print(f"Response body: {e.response.text[:500]}")
        return ""


def main():
    prompt = PROMPT_FILE.read_text()

    # Allow selecting a single model via CLI arg
    if len(sys.argv) > 1:
        model_filter = sys.argv[1]
        models = [m for m in MODELS if model_filter in m["name"] or model_filter in m["id"]]
        if not models:
            print(f"No model matching '{model_filter}'. Available: {[m['name'] for m in MODELS]}")
            sys.exit(1)
    else:
        models = MODELS

    results = {}
    for model in models:
        content = query_model(model, prompt)
        if content:
            results[model["name"]] = content

    print(f"\n{'='*60}")
    print(f"Done. {len(results)}/{len(models)} models returned data.")
    print(f"Outputs saved to: {OUTPUT_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
