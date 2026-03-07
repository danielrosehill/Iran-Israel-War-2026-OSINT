Query BOTH Grok 4.1 and Perplexity Sonar via OpenRouter, then cross-reference their outputs to check for new attack waves or updated data for the Iran-Israel conflict dataset.

## Instructions

1. Read the current state of the database to determine the latest wave number, timestamp, and identify data gaps:

```bash
source .env && sqlite3 data/iran_israel_war.db "SELECT operation, wave_number, announced_utc, wave_codename_english, estimated_munitions_count, fatalities, injuries FROM waves ORDER BY announced_utc DESC LIMIT 15;"
```

2. Find waves with missing data:

```bash
source .env && sqlite3 data/iran_israel_war.db "SELECT operation, wave_number, announced_utc, wave_codename_english FROM waves WHERE estimated_munitions_count IS NULL ORDER BY announced_utc DESC;"
```

3. Build a detailed prompt including today's date, the latest wave data, and specific gaps. Then call BOTH models sequentially via OpenRouter (using `OPENROUTER_API_KEY` from `.env`):

**Grok 4.1 Fast:**
```python
payload = {
    "model": "x-ai/grok-4.1-fast",
    "messages": [{"role": "user", "content": "YOUR QUERY"}],
    "temperature": 0.2
}
```

**Perplexity Sonar:**
```python
payload = {
    "model": "perplexity/sonar",
    "messages": [{"role": "user", "content": "YOUR QUERY"}],
    "temperature": 0.2
}
```

Use the standard OpenRouter endpoint and auth pattern:
```python
import json, os, urllib.request

API_KEY = os.environ["OPENROUTER_API_KEY"]
url = "https://openrouter.ai/api/v1/chat/completions"

req = urllib.request.Request(url, data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json",
             "Authorization": f"Bearer {API_KEY}"}, method="POST")
with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.loads(resp.read())
    print(result["choices"][0]["message"]["content"])
```

4. **Cross-reference both outputs.** Compare Grok and Perplexity responses:
   - Data points confirmed by BOTH models are higher confidence
   - Data from only one model should be flagged as lower confidence
   - Contradictions between models should be noted explicitly

5. **Validate against existing data.** Do NOT overwrite curated records. Only incorporate data that:
   - Fills `null` gaps in existing records
   - Adds genuinely new waves not yet tracked
   - Is corroborated by at least one model with source citations
   - Does not contradict existing curated data

6. Present a consolidated report to the user:
   - **High confidence** (both models agree): new waves, gap fills
   - **Medium confidence** (one model only): potential updates needing verification
   - **Conflicts**: where models disagree with each other or with existing data
   - Recommended actions

Do NOT automatically modify the JSON files — present findings for user approval first.
