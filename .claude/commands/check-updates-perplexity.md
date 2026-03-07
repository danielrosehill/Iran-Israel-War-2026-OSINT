Query Perplexity Sonar via OpenRouter (with built-in web search and citations) to check for new attack waves or updated data for the Iran-Israel conflict dataset.

## Instructions

1. Read the current state of the database to determine the latest wave number, timestamp, and identify data gaps (missing munitions counts, casualties, codenames):

```bash
source .env && sqlite3 data/iran_israel_war.db "SELECT operation, wave_number, announced_utc, wave_codename_english, estimated_munitions_count, fatalities, injuries FROM waves ORDER BY announced_utc DESC LIMIT 15;"
```

2. Also find waves with missing `estimated_munitions_count`:

```bash
source .env && sqlite3 data/iran_israel_war.db "SELECT operation, wave_number, announced_utc, wave_codename_english FROM waves WHERE estimated_munitions_count IS NULL ORDER BY announced_utc DESC;"
```

3. Call Perplexity Sonar via OpenRouter using the `OPENROUTER_API_KEY` from `.env`. Use this Python pattern:

```python
import json, os, urllib.request

API_KEY = os.environ["OPENROUTER_API_KEY"]
url = "https://openrouter.ai/api/v1/chat/completions"

payload = {
    "model": "perplexity/sonar",
    "messages": [{"role": "user", "content": "YOUR QUERY HERE"}],
    "temperature": 0.2
}

req = urllib.request.Request(url, data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json",
             "Authorization": f"Bearer {API_KEY}"}, method="POST")
with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.loads(resp.read())
    print(result["choices"][0]["message"]["content"])
```

4. Construct the prompt to include:
   - Today's date
   - The current latest wave number and timestamp
   - Specific data gaps (list waves missing munitions counts, casualties, codenames)
   - Ask for: new waves since last recorded, updated casualty/damage figures, interception data, new weapon systems observed
   - Request specific timestamps, numbers, and source citations

5. **Critically evaluate the response.** Cross-reference Perplexity's claims against existing data. If it returns data that contradicts existing curated records (different codenames, timestamps, or munitions for waves already in the DB), flag these discrepancies and DO NOT overwrite existing data. Only incorporate data that:
   - Fills `null` gaps in existing records
   - Adds genuinely new waves not yet tracked
   - Comes with credible source attribution

6. Present findings to the user with a clear summary of:
   - New waves found (if any)
   - Data gaps that can be filled
   - Discrepancies with existing data
   - Recommended updates

Do NOT automatically modify the JSON files — present findings for user approval first.
