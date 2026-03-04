![Banner](docs/banner.png)

# Iran-Israel War 2026 — OSINT Dataset

Open-source intelligence dataset tracking **Operation True Promise 4** (عملیات وعده صادق ۴) — the Iranian missile and drone attack waves against Israel and US/coalition targets beginning February 28, 2026.

## Overview

This repository collects and structures publicly available information about the attack waves launched by Iran during the ongoing conflict. Data is cross-referenced across multiple sources and organized into a machine-readable format suitable for analysis and visualization.

- **18 attack waves** documented (Feb 28 – Mar 4, 2026)
- **75+ data fields** per wave covering timing, weapons, targets, interception, and escalation
- Canonical data format: nested JSON with CSV source
- Enrichment pipelines for solar/timezone data, temporal patterns, missile categorization, and US base targeting

## Dataset

The primary dataset is [`data/waves.json`](data/waves.json), containing structured records for each attack wave. Each wave includes:

| Category | Fields |
|----------|--------|
| **Timing** | UTC timestamps, local times (Israel/Iran), solar phase, conflict day, tempo between waves |
| **Weapons** | Payload descriptions, missile/drone types (Emad, Ghadr, Sejjil, Fattah, Shahed-136/238, etc.), fuel and warhead categories |
| **Targets** | Israeli locations, US/coalition bases, naval vessels |
| **Interception** | Systems used (Iron Dome, Arrow, David's Sling, THAAD, Aegis), interception rates |
| **Impact** | Casualties, infrastructure damage, military vs. civilian impact |
| **Escalation** | Escalation flags, proxy involvement, cumulative munitions tracking |

Reference data for US/coalition bases and naval vessels is in [`data/reference/`](data/reference/).

## Data Pipeline

```
LLM queries (multi-model) → CSV → csv_to_json.py → enrich_*.py → waves.json
```

1. Raw data collected via multi-model LLM queries with source grounding
2. CSV converted to nested JSON structure
3. Enrichment scripts add computed fields (solar phases, temporal patterns, missile categories, base matching)

## Repository Structure

```
data/
  waves.csv                # Original flat CSV (75+ columns)
  waves.json               # Canonical nested JSON
  reference/
    us_bases.json           # US/coalition bases with coordinates and aliases
    us_naval_vessels.json   # Tracked naval vessels
scripts/
  csv_to_json.py            # CSV → JSON conversion
  enrich_solar.py           # Solar/timezone enrichment
  enrich_tempo.py           # Temporal/escalation enrichment
  enrich_categories.py      # Missile categories + location targeting
  enrich_us_bases.py        # US base/vessel matching
  query_models.py           # Multi-model LLM data collection
  query_gemini_grounded.py  # Gemini with Google Search grounding
prompts/
  waves.md                  # Schema documentation / LLM extraction prompt
docs/
  data-dictionary.md        # Full field reference
```

## Potential Use Cases

- **Pattern analysis** — temporal patterns in attack waves, escalation dynamics
- **Geovisualization** — mapping launch sites, targets, and interception zones
- **Weapons tracking** — categorizing and tracking Iranian missile/drone inventory usage
- **Interception analysis** — comparing defense system performance across waves
- **Conflict timeline** — reconstructing the operational tempo of the campaign

## Getting Started

```bash
git clone https://github.com/danielrosehill/Iran-Israel-War-2026-Data.git
cd Iran-Israel-War-2026-Data

# Set up Python environment (optional, only needed for enrichment scripts)
uv venv .venv
source .venv/bin/activate
uv pip install astral  # Required only by enrich_solar.py

# Run enrichment pipeline
python scripts/csv_to_json.py
python scripts/enrich_solar.py
python scripts/enrich_tempo.py
python scripts/enrich_categories.py
python scripts/enrich_us_bases.py
```

## Data Conventions

- **Timestamps**: ISO 8601 with timezone offsets
- **Coordinates**: Decimal degrees
- **Booleans**: Native JSON `true`/`false`
- **Missing values**: `null`
- **Arrays**: Native JSON arrays for country codes, interception systems, sources

See [`docs/data-dictionary.md`](docs/data-dictionary.md) for the full field reference.

## Methodology

Data is gathered from publicly available sources including official military announcements, verified news reporting, and satellite imagery analysis. Information is cross-checked across multiple sources wherever possible. Iranian nomenclature (operation names, wave codenames) is preserved alongside English translations.

This is an independent open-source research project. All data should be treated as provisional and subject to revision as new information becomes available.

## License

This dataset is provided for research and educational purposes.

## Author

[Daniel Rosehill](https://github.com/danielrosehill)
