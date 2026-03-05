# Iran-Israel War Data

OSINT dataset tracking Iranian missile/drone attack waves against Israel and US/coalition targets across multiple operations.

## Operations Covered

- **True Promise 3** (Jun 13–24, 2025) — "Twelve-Day War", 22 waves, ~1,600-1,800 munitions
- **True Promise 4** (Feb 28–ongoing, 2026) — 17+ waves, expanded to US/coalition targets in Gulf

## File Structure

```
data/
  tp3-2025/
    waves.json             # TP3 wave data (22 waves, Jun 2025)
  tp4-2026/
    waves.csv              # Original flat CSV (75+ columns)
    waves.json             # Canonical nested JSON (18 waves)
    waves.geojson          # GeoJSON export
    waves.kml              # KML export
    reference/
      israeli_targets.json # Israeli target sites with coords
      us_bases.json        # US/coalition bases (TP4-specific)
      us_naval_vessels.json # Tracked naval vessels (TP4-specific)
      launch_zones.json    # Iranian launch zone centroids
  reference/               # Shared reference data
    iranian_weapons.json   # Iranian missile + drone specs
    defense_systems.json   # Coalition BMD / air defense systems
    armed_forces.json      # Armed groups/forces in conflict
    us_bases.json          # US/coalition bases with aliases, coords
    us_naval_vessels.json  # Tracked naval vessels
  schema/
    wave.schema.json       # JSON Schema for validation
  waves.json               # Legacy root copy (prefer tp4-2026/)
  waves.csv                # Legacy root copy (prefer tp4-2026/)
report/
  report.pdf               # TP3 vs TP4 comparative analysis
  report.typ               # Typst source
  report_*.png             # Report charts
analysis/
  charts/                  # Standalone visualizations
prompts/
  waves.md                 # Schema documentation / LLM extraction prompt
docs/
  data-dictionary.md       # Full field reference
```

Note: `scripts/` is git-ignored. Processing scripts are kept locally only — this repo shares findings, not methodology. `data/waves.json` and `data/waves.csv` at root level are legacy copies — canonical files live in `tp3-2025/` and `tp4-2026/`.

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
