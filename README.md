![Banner](images/banner-sm.png)

# Iran-Israel War — OSINT Dataset

Open-source intelligence dataset tracking Iranian missile and drone attack waves against Israel and US/coalition targets across four rounds of escalation — Iran's first-ever direct military strikes on Israeli territory.

> **Data Quality Disclaimer**: This dataset was assembled using a combination of AI-assisted research (multi-model LLM queries), news reporting, and publicly available OSINT sources. **It may contain inaccuracies, gaps, or errors.** Timestamps are approximate for many events. Munitions counts and casualty figures vary across sources and should be treated as estimates. Iranian state media claims (PressTV, Tasnim, IRGC statements) are preserved but often unverifiable. This data is provided for research and educational purposes only — always cross-reference against primary sources before drawing conclusions.

**[Interactive Map & Dashboard](https://promisedenied.com)** | **[Kaggle Dataset](https://www.kaggle.com/datasets/danielrosehill/iran-israel-war-2026)** | **[Hugging Face Dataset](https://huggingface.co/datasets/danielrosehill/Iran-Israel-War-2026)**

---

## Rounds Overview

| Round | Iranian Designation | Date | Waves | Est. Munitions | Targets |
|:-----:|---------------------|------|------:|---------------:|---------|
| **4** | True Promise 4 | Feb 28–ongoing, 2026 | 29+ | TBD | Israel, US/coalition bases across 12 countries |
| **3** | True Promise 3 | Jun 13–24, 2025 | 22 | ~1,600–1,800 | Israel (cities, bases, infrastructure) |
| **2** | True Promise 2 | Oct 1, 2024 | 2 | ~200 | Israel (airbases, intelligence HQ) |
| **1** | True Promise 1 | Apr 13–14, 2024 | 2 | ~320 | Israel (airbases) |

---

## What's In The Dataset

Each wave record includes:

| Category | Fields |
|----------|--------|
| **Identity** | Wave UID, UUID, attacking force (actor + subunit) |
| **Timing** | UTC timestamps, local times (Israel/Iran), solar phase, conflict day, inter-wave tempo |
| **Weapons** | Payload descriptions, missile/drone type flags, fuel/warhead categories, cluster munition details |
| **Targets** | Israeli locations, US/coalition bases, naval vessels, country-level targeting, critical infrastructure flags |
| **Interception** | Systems used, interception rates, exo/endo atmospheric phase, intercepting forces |
| **Impact** | Casualties (military/civilian), infrastructure damage |
| **Escalation** | New country/weapon flags, proxy involvement |

Full field reference: [`docs/data-dictionary.md`](docs/data-dictionary.md) | Schema: [`data/schema/wave.schema.json`](data/schema/wave.schema.json)

---

## Data Access

### Neo4j Graph Database

The dataset is available as a **property graph** on [Neo4j Aura](https://neo4j.com/cloud/aura-free/), modelling the war as a network of relationships between actors, weapons, targets, defense systems, and international reactions. Graph queries enable relationship-driven analysis — e.g. "which defense systems intercepted Fattah missiles?" or "all salvos where Artesh participated" — that are cumbersome in flat/relational formats.

**Graph model**: War → Round → Salvo, with Side/Actor hierarchy (Israel/Coalition vs Iran/Axis of Resistance), weapons, defense systems, targets, and 210 entity international reactions. Uses neutral "Round" terminology; Iranian operational designations stored as properties.

Rebuild: `python3 scripts/build_neo4j.py --clear`

### JSON Source Files

| File | Content |
|------|---------|
| [`data/tp4-2026/waves.json`](data/tp4-2026/waves.json) | Round 4 — 29 waves (Feb–Mar 2026) |
| [`data/tp3-2025/waves.json`](data/tp3-2025/waves.json) | Round 3 — 22 waves (Jun 2025) |
| [`data/tp2-2024/waves.json`](data/tp2-2024/waves.json) | Round 2 — 2 waves (Oct 2024) |
| [`data/tp1-2024/waves.json`](data/tp1-2024/waves.json) | Round 1 — 2 waves (Apr 2024) |

### Reference Data

| File | Description |
|------|-------------|
| [`data/reference/iranian_weapons.json`](data/reference/iranian_weapons.json) | Iranian missile + drone specs |
| [`data/reference/defense_systems.json`](data/reference/defense_systems.json) | Coalition BMD / air defense specs |
| [`data/reference/armed_forces.json`](data/reference/armed_forces.json) | Armed forces and non-state groups |
| [`data/reference/us_bases.json`](data/reference/us_bases.json) | US/coalition military bases with coordinates |
| [`data/reference/us_naval_vessels.json`](data/reference/us_naval_vessels.json) | Tracked naval vessels |

---

## Repository Structure

```
data/
  tp1-2024/waves.json        # Round 1 (2 waves)
  tp2-2024/waves.json        # Round 2 (2 waves)
  tp3-2025/waves.json        # Round 3 (22 waves)
  tp4-2026/waves.json        # Round 4 (29 waves)
  tp4-2026/reference/        # Round 4 targets, bases, vessels, launch zones
  reference/                 # Shared reference data
  schema/wave.schema.json    # JSON Schema for validation
scripts/
  build_neo4j.py             # Rebuild Neo4j graph database (primary DB)
  build_kaggle.py            # Build Kaggle CSV/Parquet exports
  build_export.py            # Build timestamped export bundles
  build_geojson.py           # Build GeoJSON exports
  build_arcgis.py            # Build ArcGIS-compatible exports
  normalization.py           # Centralized lookup tables (actors, weapons, defense)
  sync_platforms.py          # Sync to Kaggle + Hugging Face
  upload_kaggle.py           # Upload to Kaggle
  wave_enrichment.py         # Shared wave enrichment utilities
docs/
  data-dictionary.md         # Full field reference
  hf_dataset_card.md         # Hugging Face dataset card
```

## Data Conventions

- **Timestamps**: ISO 8601 with timezone offsets
- **Coordinates**: Decimal degrees
- **Booleans**: Native JSON `true`/`false`
- **Missing values**: `null`
- **Country codes**: ISO 3166-1 alpha-2

## Terms of Use

This dataset is provided **as-is without warranty**. Users assume all risk. It **may not** be used to glorify terrorism, incite violence, serve as propaganda, or dehumanise victims. Iranian operational names and weapon designations are used solely for analytical standardisation — not endorsement. Intended for academic research, journalism, defence analysis, and education. See [`TERMS_OF_USE.md`](TERMS_OF_USE.md) for full terms.

## Citation

```bibtex
@misc{daniel_rosehill_grok_4_1_fast_google_gemini_3_1_2026,
    title={Iran Israel War 2026},
    url={https://www.kaggle.com/dsv/15085716},
    DOI={10.34740/KAGGLE/DSV/15085716},
    publisher={Kaggle},
    author={Daniel Rosehill and Grok 4.1 Fast and Google Gemini 3.1},
    year={2026}
}
```

## License

This dataset is provided for research and educational purposes.

## Author

[Daniel Rosehill](https://github.com/danielrosehill)

---

> **Disclaimer**: The use of Iranian operational designations ("True Promise 1–4") in this dataset is for identification and reference purposes only. Their inclusion does not constitute endorsement, legitimisation, or glorification of any military operation, armed group, or state actor. This dataset documents events as reported in open sources for research and educational use. See [Terms of Use](TERMS_OF_USE.md) for full details.
