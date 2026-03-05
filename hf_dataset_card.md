---
license: cc-by-4.0
task_categories:
  - tabular-classification
  - tabular-regression
tags:
  - OSINT
  - military
  - geopolitics
  - Iran
  - Israel
  - missiles
  - conflict-data
  - time-series
language:
  - en
size_categories:
  - n<1K
pretty_name: Iran-Israel War 2026 OSINT Dataset
---

# Iran-Israel War — OSINT Dataset

Open-source intelligence dataset tracking Iranian missile and drone attack waves against Israel and US/coalition targets across four operations in the "True Promise" series (2024–2026).

## Dataset Description

46 attack waves across four Iranian military operations, each with 87 structured fields covering timing, weapons systems, targets, interception performance, casualties, and escalation indicators.

| Operation | Date | Waves | Munitions | Targets |
|-----------|------|------:|----------:|---------|
| True Promise 1 | Apr 13–14, 2024 | 2 | ~320 | Israel (airbases) |
| True Promise 2 | Oct 1, 2024 | 2 | ~200 | Israel (airbases, intel HQ) |
| True Promise 3 | Jun 13–24, 2025 | 22 | ~1,600–1,800 | Israel (cities, bases, infrastructure) |
| True Promise 4 | Feb 28–ongoing, 2026 | 20 | TBD | Israel, US/coalition bases across Gulf & Med |

## Data Fields (87 columns)

| Category | Fields |
|----------|--------|
| **Identity** | `operation`, `wave_number`, `wave_codename_farsi`, `wave_codename_english` |
| **Timing** | `announced_utc`, `probable_launch_time`, `launch_time_israel`, `launch_time_iran`, `conflict_day`, `hours_since_last_wave`, `time_between_waves_minutes` |
| **Weapons** | `payload`, `drones_used`, `ballistic_missiles_used`, `cruise_missiles_used`, per-system booleans (`emad_used`, `ghadr_used`, `kheibar_shekan_used`, `fattah_used`, `shahed_136_used`, etc.), fuel/warhead categories |
| **Cluster Warheads** | `cluster_warhead_confirmed`, `cluster_carrier_missile`, `cluster_submunition_count`, `cluster_dispersal_radius_km` |
| **Targets** | `israel_targeted`, `us_bases_targeted`, `targets` (text), `landings_countries`, per-city booleans, US base/vessel lists, coordinates |
| **Interception** | `intercepted`, `interception_systems`, per-country interception flags, intercept counts/rates, exo/endoatmospheric phase |
| **Impact** | `damage` (text), `fatalities`, `injuries`, `civilian_casualties`, `military_casualties` |
| **Escalation** | `new_country_targeted`, `new_weapon_first_use` |
| **Sources** | `idf_statement`, `iranian_media_claims`, `source_urls` |

## Files

- `waves.parquet` — All 46 waves, 87 columns (recommended)
- `waves.csv` — Same data in CSV format

## Usage

```python
from datasets import load_dataset
ds = load_dataset("danielrosehill/Iran-Israel-War-2026")

# Or with pandas
import pandas as pd
df = pd.read_parquet("hf://datasets/danielrosehill/Iran-Israel-War-2026/waves.parquet")

# Fatalities by operation
df.groupby("operation")["fatalities"].sum()

# Weapon systems used per operation
weapon_cols = [c for c in df.columns if c.endswith("_used")]
df.groupby("operation")[weapon_cols].sum()
```

## Data Quality

This dataset was assembled using AI-assisted research, news reporting, and publicly available OSINT sources. **It may contain inaccuracies, gaps, or errors.** Timestamps are approximate for many events. Munitions counts and casualty figures vary across sources and should be treated as estimates. Iranian state media claims are preserved but often unverifiable.

Always cross-reference against primary sources before drawing conclusions.

## Source Repository

**GitHub**: [danielrosehill/Iran-Israel-War-2026-OSINT-Data](https://github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data)

The GitHub repo contains the full nested JSON source files, SQLite database, GeoJSON/KML exports, reference data (weapon specs, defense systems, base locations), and JSON Schema for validation.

**Kaggle**: [danielrosehill/iran-israel-war-2026](https://www.kaggle.com/datasets/danielrosehill/iran-israel-war-2026)

**Interactive Map & Dashboard**: [iranisrael26.danielrosehill.com](https://iranisrael26.danielrosehill.com)

## License

CC-BY-4.0 — provided for research and educational purposes.

## Author

[Daniel Rosehill](https://github.com/danielrosehill)
