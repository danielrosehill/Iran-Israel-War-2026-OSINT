# About This Dataset

## Purpose

This dataset documents Iranian missile and drone attack waves against Israel and US/coalition targets across four military operations codenamed "True Promise" (وعده صادق) by Iran's Islamic Revolutionary Guard Corps (IRGC). It covers the period from April 2024 through March 2026, representing the first direct state-on-state military exchanges between Iran and Israel.

The dataset exists to provide structured, machine-readable records of each attack wave for research, analysis, and educational use. It is not affiliated with any government, military, or intelligence organisation. All data is derived from publicly available open-source intelligence (OSINT).

## What the Dataset Contains

The dataset has two main tables:

### 1. Attack Waves (53 rows, 87 columns)

Each row represents a single attack wave — a distinct salvo of missiles, drones, or both launched by Iran or its proxies toward Israeli or US/coalition targets. The 53 waves span four operations:

- **True Promise 1** (Apr 2024): 2 waves, ~320 munitions. Iran's first-ever direct strike on Israeli soil.
- **True Promise 2** (Oct 2024): 2 waves, ~200 munitions. Ballistic-missile-only strike; first combat use of the Fattah-1 hypersonic missile.
- **True Promise 3** (Jun 2025): 22 waves over 12 days, ~1,600–1,800 munitions. Sustained bombardment triggered by Israeli strikes on Iranian nuclear facilities.
- **True Promise 4** (Feb 2026–ongoing): 27 waves. First operation to target US/coalition bases directly, expanding the conflict across the Gulf and Mediterranean.

Each wave record captures:

**Timing fields** — UTC timestamps for announcement and estimated launch, local times in both Israel (IST) and Iran (IRST), solar illumination phase at launch site and target (a 0–5 scale from night to full daylight), conflict day number, and inter-wave tempo (hours and minutes since the previous wave). These fields support temporal pattern analysis and allow researchers to examine whether Iran favours night launches, dawn attacks, or varies timing tactically.

**Weapon system fields** — Boolean flags for each Iranian missile and drone type observed in the wave: Emad, Ghadr (liquid-fueled MRBMs), Sejjil, Kheibar Shekan (solid-fueled MRBMs), Fattah-1/2 (hypersonic), and Shahed-131/136/238 and Mohajer-6 (drones/UAVs). Categorical flags aggregate these into broader groups: liquid-fueled vs. solid-fueled ballistic missiles, MARV-equipped (maneuverable reentry vehicle), hypersonic-class, and cluster warhead carriers. A free-text `payload` field provides a human-readable description. For waves where cluster munitions were confirmed, a dedicated block records the carrier missile type, estimated submunition count, explosive weight per submunition, and dispersal radius.

**Target fields** — Whether Israel and/or US bases were targeted, free-text target descriptions, and boolean flags for six Israeli geographic zones (Tel Aviv, Jerusalem, Haifa, Negev/Beersheba, northern periphery, Eilat). For TP4 waves targeting US/coalition installations, named base and naval vessel lists are included. Target and launch site coordinates are provided in decimal degrees (WGS84) where available. A `landings_countries` field lists ISO 3166-1 alpha-2 codes for every country where munitions or debris landed — useful for tracking geographic escalation.

**Interception fields** — Whether the wave was intercepted, which defense systems engaged (Arrow-2, Arrow-3, David's Sling, Iron Dome, THAAD, Patriot PAC-3, Aegis SM-2/SM-3), which countries participated in the interception (Israel, US, UK, Jordan, others), estimated intercept count and rate, and whether interceptions occurred in the exoatmospheric or endoatmospheric phase. A free-text `interception_report` provides narrative detail.

**Impact fields** — Fatalities, injuries, civilian casualties, military casualties (all integers, null when unknown), and a free-text damage description.

**Escalation markers** — Boolean flags indicating whether the wave targeted a country not previously attacked in that operation (`new_country_targeted`) or introduced a weapon system not previously used (`new_weapon_first_use`). These are useful for identifying escalation thresholds.

**Proxy involvement** — Whether proxy forces (Hezbollah, Houthis, Iraqi Shia militias) participated, with a free-text description.

**Sources** — IDF statement summary, Iranian media claims (preserved as JSON), and a list of OSINT source URLs.

### 2. International Reactions (210 rows, 34 columns)

Each row represents one country's or multilateral organisation's official response to True Promise 4. The 210 entities include 193 sovereign states and 17 multilateral bodies (UN, EU, NATO, Arab League, African Union, ASEAN, etc.).

Each reaction record captures:

**Entity identification** — ISO 3166-1 alpha-2 country code (null for multilateral bodies), entity name, entity type (`state` or `multilateral`), EU membership status, and whether the entity is a combatant in the conflict.

**Overall stance** — A single categorical classification of the entity's position, drawn from nine values: `active_participant_coalition` (fighting alongside Israel/US), `active_participant_pro_iran` (fighting alongside Iran), `supports_israel`, `condemns_iran`, `calls_for_deescalation`, `neutral_acknowledgement`, `supports_iran`, `condemns_israel`, and `silent` (no public statement issued). The distribution is heavily weighted toward `silent` (68 entities), `calls_for_deescalation` (62), and `condemns_iran` (50).

**Official statements** — Three parallel blocks for head of state, head of government, and foreign ministry statements. Each block records whether a statement was made, the date, speaker name and title, a summary, the full or partial text, a source URL, and a tone category. An `additional_statements` field (JSON array) captures statements from other officials or bodies beyond these three channels.

**Notes** — Free-text contextual background on the entity's geopolitical position relative to the conflict.

## Data Quality and Limitations

This dataset was assembled using AI-assisted research (multi-model LLM queries with search grounding), news reporting, and publicly available OSINT sources. It has the following limitations:

- **Timestamps are approximate.** Exact launch times are rarely publicly confirmed; most are estimated from first detection reports, air raid sirens, or social media.
- **Munitions counts vary across sources.** Israeli military, Iranian state media, and independent analysts often report different numbers. Values here represent best estimates, not ground truth.
- **Casualty figures are incomplete.** Many waves have null values for fatalities and injuries, particularly in TP3 where wave-level attribution is difficult.
- **Iranian media claims are preserved but unverified.** They are included for analytical completeness, not as statements of fact.
- **Interception rates are contested.** Israeli/coalition claims of 85–99% interception are disputed by Iranian sources. The dataset records the values most commonly cited in Western reporting.
- **International reactions data is a snapshot.** Stances may evolve over time; the data reflects positions as of early March 2026.

Always cross-reference against primary sources before drawing conclusions.

## Suggested Use Cases

- **Temporal analysis** — Examine inter-wave timing, conflict tempo acceleration, and whether attack patterns correlate with time of day, solar conditions, or day of conflict.
- **Weapon system tracking** — Track the evolution of Iran's missile/drone arsenal across operations: the shift from liquid to solid fuel, the introduction of hypersonic and cluster munitions, and the changing drone-to-missile ratio.
- **Interception performance** — Compare defense system effectiveness across waves, operations, and engagement phases (exo vs. endoatmospheric). Analyse which systems are deployed against which threat types.
- **Geographic escalation** — Map the expansion of Iranian targeting from Israeli airbases (TP1) to cities (TP3) to US/coalition bases across 12 countries (TP4).
- **Geospatial visualisation** — Plot launch sites, target coordinates, and debris landing zones on maps. The coordinate fields and country code arrays support GIS analysis.
- **Cross-operation comparison** — Quantify how Iranian strike doctrine evolved from a single-night retaliatory strike (TP1) to a 12-day sustained bombardment (TP3) to a multi-theater campaign (TP4).
- **Diplomatic alignment analysis** — Use the international reactions table to map global diplomatic responses, identify voting blocs, correlate stance with EU membership or geographic region, and track which countries issued statements vs. stayed silent.
- **Escalation modelling** — Use the `new_country_targeted` and `new_weapon_first_use` flags alongside cumulative munitions totals to model escalation dynamics.
- **NLP and text analysis** — The free-text fields (damage descriptions, interception reports, Iranian media claims, diplomatic statement summaries) can support natural language processing tasks.

## Database and File Formats

The primary data store is a **SQLite database** at `data/iran_israel_war.db`. This is the recommended way to query the data — it contains all wave data, international reactions, reference tables (weapon specs, defense systems, armed forces, base locations, naval vessels), and junction tables for many-to-many relationships (landing countries, interception systems, US bases targeted, source URLs). Rebuild from source with `python3 scripts/build_db.py`.

Key tables:

| Table | Rows | Description |
|-------|-----:|-------------|
| `waves` | 53 | One row per attack wave — timing, weapons, targets, interception, impact, escalation |
| `international_reactions` | 210 | One row per country/org diplomatic response |
| `reaction_statements` | 630+ | Individual head-of-state, head-of-government, and foreign ministry statements |
| `wave_landing_countries` | 102+ | Countries where munitions landed, per wave |
| `wave_interception_systems` | 116+ | Defense systems used, per wave |
| `wave_us_bases_targeted` | 18+ | US/coalition bases targeted, per wave |
| `wave_events` | varies | Granular interception/strike/impact events within waves |
| `iranian_weapons` | 11 | Iranian missile and drone specifications |
| `defense_systems` | 8 | Coalition BMD and air defense system specifications |
| `entities` | 210 | Country/org reference with EU membership and combatant status |
| `reaction_types` | 9 | Stance classification reference with spectrum scores |

The SQLite database normalises many-to-many relationships that are flattened into comma-separated strings in the CSV/Parquet exports. For example, the `wave_interception_systems` junction table lets you query which defense systems were used in each wave without parsing strings.

Flattened exports are also available for platforms that don't support SQLite directly:

| Format | Files | Best For |
|--------|-------|----------|
| **Parquet** | `kaggle/waves.parquet`, `kaggle/international_reactions.parquet` | Python/pandas, Spark — compact, typed, fast |
| **CSV** | `kaggle/waves.csv`, `kaggle/international_reactions.csv` | Excel, R, any tabular tool |

The CSV and Parquet files are flattened exports of the SQLite data: many-to-many relationships (interception systems, landing countries, source URLs) are joined into comma-separated strings, and statement blocks are prefixed (`hos_`, `hog_`, `fm_`).

## Data Dictionary

A column-level reference for every field is in [`data/data_dictionary.csv`](../data/data_dictionary.csv) (CSV format) and [`docs/data-dictionary.md`](data-dictionary.md) (annotated Markdown with types and source annotations).
