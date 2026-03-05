# Iran-Israel War Data

OSINT dataset tracking Iranian missile/drone attack waves against Israel and US/coalition targets across multiple operations.

## Operations Covered

- **True Promise 3** (Jun 13–24, 2025) — "Twelve-Day War", 22 waves, ~1,600-1,800 munitions
- **True Promise 4** (Feb 28–ongoing, 2026) — 17+ waves, expanded to US/coalition targets in Gulf

## File Structure

```
data/
  tp3-2025/
    waves.json             # TP3 wave data (22 waves, partial detail)
  tp4-2026/
    waves.csv              # Original flat CSV (75+ columns)
    waves.json             # Canonical nested JSON (17 waves)
    waves.geojson          # GeoJSON export
    waves.kml              # KML export
    reference/
      us_bases.json        # US/coalition bases with aliases, coords
      us_naval_vessels.json # Tracked naval vessels
      iranian_weapons.json # Iranian missile + drone specs
      armed_forces.json    # Armed groups/forces in conflict
analysis/
  *.png                    # Generated visualizations
prompts/
  waves.md                 # Schema documentation / LLM extraction prompt
docs/
  data-dictionary.md       # Full field reference
```

Note: `scripts/` is git-ignored. Processing scripts are kept locally only — this repo shares findings, not methodology.

## JSON Structure

Both TP3 and TP4 use the same schema. Each wave is nested into: `timing`, `weapons` (with `types` + `categories`), `targets` (with `israeli_locations`, `us_bases`, `us_naval_vessels`), `launch_site`, `interception` (with `intercepted_by`), `munitions`, `impact`, `escalation`, `proxy`, `sources`.

## Conventions

- Booleans: native JSON `true`/`false`
- Nulls: `null` for unknown/missing
- Arrays: native JSON arrays for country codes, interception systems, sources
- Timestamps: ISO 8601 with timezone offset
- Coordinates: decimal degrees

## Python Environment

```bash
uv venv .venv
source .venv/bin/activate
uv pip install astral matplotlib pandas numpy seaborn
```
