Query Gemini 3.1 Flash Lite with Google Search grounding to check for new attack waves or updated data for the Iran-Israel conflict dataset.

## Instructions

1. Read the current state of the database to determine the latest wave number, timestamp, and identify data gaps (missing munitions counts, casualties, codenames):

```bash
python3 -c "import json; waves=json.load(open('data/tp4-2026/waves.json'))['incidents']; [print(f'Wave {w[\"wave_number\"]}: {w.get(\"timing\",{}).get(\"announced_utc\",\"?\")} — {w.get(\"wave_codename_english\",\"\")}') for w in sorted(waves, key=lambda x: x.get('timing',{}).get('announced_utc',''), reverse=True)[:15]]"
```

2. Also find waves with missing `estimated_munitions_count`:

```bash
python3 -c "import json; waves=json.load(open('data/tp4-2026/waves.json'))['incidents']; [print(f'Wave {w[\"wave_number\"]}: {w.get(\"timing\",{}).get(\"announced_utc\",\"?\")} — {w.get(\"wave_codename_english\",\"\")}') for w in waves if not w.get('munitions',{}).get('estimated_munitions_count')]"
```

3. Call Gemini 3.1 Flash Lite with search grounding using `GOOGLE_API_KEY` from `.env` (also in `~/.bashrc`). Activate the project venv first (`source .venv/bin/activate`). Use this Python pattern:

```python
import os
from google import genai
from google.genai import types

os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents="YOUR QUERY HERE",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    ),
)

print(response.text)

# Print grounding sources
if response.candidates[0].grounding_metadata:
    gm = response.candidates[0].grounding_metadata
    if gm.grounding_chunks:
        print("\n=== Sources ===")
        for chunk in gm.grounding_chunks:
            if chunk.web:
                print(f"  {chunk.web.title} — {chunk.web.uri}")
```

4. Construct the prompt to include:
   - Today's date
   - The current latest wave number and timestamp
   - Specific data gaps (list waves missing munitions counts, casualties, codenames)
   - Ask for: new waves since last recorded, updated casualty/damage figures, interception data, new weapon systems observed
   - Request specific timestamps, numbers, and source citations

5. **Critically evaluate the response.** Cross-reference Gemini's claims against existing data. If it returns data that contradicts existing curated records (different codenames, timestamps, or munitions for waves already in the DB), flag these discrepancies and DO NOT overwrite existing data. Only incorporate data that:
   - Fills `null` gaps in existing records
   - Adds genuinely new waves not yet tracked
   - Comes with credible source attribution (check grounding metadata)

6. Present findings to the user with a clear summary of:
   - New waves found (if any)
   - Data gaps that can be filled
   - Discrepancies with existing data
   - Recommended updates
   - Grounding sources cited

Do NOT automatically modify the JSON files — present findings for user approval first.
