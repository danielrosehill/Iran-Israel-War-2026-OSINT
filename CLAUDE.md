# Iran-Israel War 2026 Data

OSINT dataset tracking Operation True Promise 4 — Iranian missile/drone attack waves against Israel and US/coalition targets (Feb 28 – ongoing, 2026).

## Data Pipeline

```
LLM query (CSV) → csv_to_json.py → enrich_*.py (JSON) → waves.json (canonical)
```

1. Raw data collected via multi-model LLM queries (`query_models.py`, `query_gemini_grounded.py`)
2. CSV converted to nested JSON: `python scripts/csv_to_json.py`
3. Enrichment scripts run on JSON (in order):
   - `enrich_solar.py` — local times, solar phase at launch/target
   - `enrich_tempo.py` — hours between waves, cumulative munitions, escalation flags
   - `enrich_categories.py` — missile category booleans, Israeli location targeting
   - `enrich_us_bases.py` — US base and naval vessel matching from reference data

## File Structure

```
data/
  waves.csv              # Original flat CSV (75+ columns, 17 rows)
  waves.json             # Canonical nested JSON format
  reference/
    us_bases.json        # 9 US/coalition bases with aliases, coords
    us_naval_vessels.json # Tracked naval vessels
    iranian_weapons.json # Specs for Iranian missiles + drones (Emad, Ghadr, Sejjil, Kheibar Shekan, Fattah-1/2, Shahed-136/238)
    armed_forces.json    # Armed groups/forces in conflict (IDF, IRGC, Artesh, USAF, USN, RAF, proxies, etc.)
scripts/
  csv_to_json.py         # One-time CSV → JSON conversion
  enrich_solar.py        # Solar/timezone enrichment (requires astral)
  enrich_tempo.py        # Temporal/escalation enrichment
  enrich_categories.py   # Missile categories + location targeting
  enrich_us_bases.py     # US base/vessel matching from reference
  query_models.py        # Multi-model LLM data collection
  query_gemini_grounded.py # Gemini with Google Search grounding
prompts/
  waves.md               # Schema documentation / LLM extraction prompt
docs/
  data-dictionary.md     # Full field reference
```

## JSON Structure

Each wave is nested into: `timing`, `weapons` (with `types` + `categories`), `targets` (with `israeli_locations`, `us_bases`, `us_naval_vessels`), `launch_site`, `interception` (with `intercepted_by`), `munitions`, `impact`, `escalation`, `proxy`, `sources`.

## Adding New Fields

1. Add the field to the appropriate nested object in `csv_to_json.py`
2. If enriched (computed), add logic to the relevant `enrich_*.py` script
3. Update `docs/data-dictionary.md` with path, type, description, example
4. Update `prompts/waves.md` if it's a primary (LLM-extracted) field

## Conventions

- Booleans: native JSON `true`/`false` (CSV used `TRUE`/`FALSE` strings)
- Nulls: `null` for unknown/missing (CSV used empty strings)
- Arrays: native JSON arrays for country codes, interception systems, sources
- Timestamps: ISO 8601 with timezone offset
- Coordinates: decimal degrees

## Python Environment

```bash
uv venv .venv
source .venv/bin/activate
uv pip install astral
```

Only `enrich_solar.py` requires the `astral` package. All other scripts use stdlib only.
