![Banner](docs/banner.png)

# Iran-Israel War — OSINT Dataset

Open-source intelligence dataset tracking Iranian missile and drone attack waves against Israel and US/coalition targets across multiple operations:

- **Operation True Promise 3** (Jun 13–24, 2025) — "Twelve-Day War", 22 waves
- **Operation True Promise 4** (Feb 28–ongoing, 2026) — 17+ waves, expanded to US/coalition targets across the Gulf and Mediterranean

> **Data Quality Disclaimer**: This dataset was assembled using a combination of AI-assisted research (multi-model LLM queries), news reporting, and publicly available OSINT sources. **It may contain inaccuracies, gaps, or errors.** Timestamps are approximate for many events. Munitions counts and casualty figures vary across sources and should be treated as estimates. Iranian state media claims (PressTV, Tasnim, IRGC statements) are preserved but often unverifiable. This data is provided for research and educational purposes only — always cross-reference against primary sources before drawing conclusions.

## Dataset

### True Promise 4 (2026)

Primary dataset: [`data/tp4-2026/waves.json`](data/tp4-2026/waves.json)

- **17 attack waves** documented (Feb 28 – Mar 4, 2026)
- **75+ data fields** per wave covering timing, weapons, targets, interception, and escalation
- Countries targeted: Israel, Kuwait, Bahrain, UAE, Qatar, Saudi Arabia, Iraq, Oman, Cyprus, Jordan
- Reference data for US/coalition bases and naval vessels in [`data/tp4-2026/reference/`](data/tp4-2026/reference/)

### True Promise 3 / Twelve-Day War (2025)

Dataset: [`data/tp3-2025/waves.json`](data/tp3-2025/waves.json)

- **22 attack waves** documented (Jun 13–24, 2025)
- Same JSON schema as TP4
- Countries targeted: Israel (only — TP3 did not target US/coalition bases)
- Data quality is lower than TP4; many waves have partial or missing detail

### Analysis

**Comparative report:** [`analysis/report.pdf`](analysis/report.pdf) — 15-page PDF analyzing attack pattern evolution between TP3 and TP4, including flight time breakdowns, weapon mix shifts, geographic expansion, and escalation trends. Generated 05/03/26 by Anthropic Claude Opus 4.6 — all facts require independent verification.

Visualizations in [`analysis/`](analysis/) covering timing patterns, weapon evolution, targeting geography, and operational tempo.

| Category | Fields |
|----------|--------|
| **Timing** | UTC timestamps, local times (Israel/Iran), solar phase, conflict day, tempo between waves |
| **Weapons** | Payload descriptions, missile/drone types (Emad, Ghadr, Sejjil, Fattah, Shahed-136/238, etc.), fuel and warhead categories |
| **Targets** | Israeli locations, US/coalition bases, naval vessels, country-level targeting |
| **Interception** | Systems used (Iron Dome, Arrow, David's Sling, THAAD, Aegis), interception rates |
| **Impact** | Casualties, infrastructure damage, military vs. civilian impact |
| **Escalation** | Escalation flags, proxy involvement, cumulative munitions tracking |

## Repository Structure

```
data/
  tp3-2025/
    waves.json               # TP3 wave data (22 waves, Jun 2025)
  tp4-2026/
    waves.csv                # Original flat CSV (75+ columns)
    waves.json               # Canonical nested JSON (17 waves)
    waves.geojson            # GeoJSON export
    waves.kml                # KML export
    reference/
      us_bases.json          # US/coalition bases with coordinates and aliases
      us_naval_vessels.json  # Tracked naval vessels
      iranian_weapons.json   # Iranian missile + drone specs
      armed_forces.json      # Armed groups/forces in conflict
analysis/
  report.typ                 # Typst source for comparative analysis
  report.pdf                 # 15-page TP3 vs TP4 comparative report (AI-generated)
  report_*.png               # Report-specific charts
  *.png                      # Generated visualizations
prompts/
  waves.md                   # Schema documentation / LLM extraction prompt
docs/
  data-dictionary.md         # Full field reference
```

## Potential Use Cases

- **Pattern analysis** — temporal patterns in attack waves, escalation dynamics
- **Geovisualization** — mapping launch sites, targets, and interception zones
- **Weapons tracking** — categorizing and tracking Iranian missile/drone inventory usage
- **Interception analysis** — comparing defense system performance across waves
- **Cross-operation comparison** — TP3 vs TP4 tactical evolution

## Data Conventions

- **Timestamps**: ISO 8601 with timezone offsets
- **Coordinates**: Decimal degrees
- **Booleans**: Native JSON `true`/`false`
- **Missing values**: `null`
- **Arrays**: Native JSON arrays for country codes, interception systems, sources
- **Country codes**: ISO 3166-1 alpha-2

See [`docs/data-dictionary.md`](docs/data-dictionary.md) for the full field reference.

## Methodology

Data is gathered from publicly available sources including official military announcements, verified news reporting, Wikipedia timelines, and satellite imagery analysis. AI tools (multi-model LLM queries with source grounding) are used to accelerate data collection and structuring. Information is cross-checked across multiple sources wherever possible. Iranian nomenclature (operation names, wave codenames) is preserved alongside English translations.

This is an independent open-source research project. All data should be treated as provisional and subject to revision as new information becomes available.

## License

This dataset is provided for research and educational purposes.

## Author

[Daniel Rosehill](https://github.com/danielrosehill)
