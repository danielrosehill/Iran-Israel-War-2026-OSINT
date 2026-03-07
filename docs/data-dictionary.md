# Data Dictionary

This document covers both tables in the dataset: **waves** (attack wave records) and **international reactions** (diplomatic responses). See also [`about-dataset.md`](about-dataset.md) for a narrative description of the dataset and suggested use cases.

---

## Part 1: waves.json

Each entry in `waves[]` has the following structure. Fields marked **enriched** are computed by scripts; all others are **primary** (LLM-extracted or manually entered).

All four operations follow this schema: TP1 (`data/tp1-2024/waves.json`), TP2 (`data/tp2-2024/waves.json`), TP3 (`data/tp3-2025/waves.json`), and TP4 (`data/tp4-2026/waves.json`). See "TP3-specific extensions" below for additional weapon type fields in the TP3 dataset.

Validated against `data/schema/wave.schema.json`.

## Top-Level

| Path | Type | Description | Example | Source |
|------|------|-------------|---------|--------|
| `operation` | string | Operation identifier (`"tp1"`, `"tp2"`, `"tp3"`, or `"tp4"`) | `"tp4"` | primary |
| `wave_number` | int | Sequential wave identifier | `1` | primary |
| `wave_codename_farsi` | string\|null | Farsi codename from IRGC | `"وعده صادق ۴"` | primary |
| `wave_codename_english` | string\|null | English translation of codename | `"True Promise 4"` | primary |
| `description` | string\|null | Free-text summary of the wave | | primary |

## timing

| Path | Type | Description | Example | Source |
|------|------|-------------|---------|--------|
| `timing.announced_utc` | string\|null | UTC timestamp of public announcement | `"2026-02-28T18:30:00Z"` | primary |
| `timing.announcement_source` | string\|null | Who announced (e.g. "IRGC") | `"IRGC"` | primary |
| `timing.announcement_x_url` | string\|null | X/Twitter URL of announcement | | primary |
| `timing.probable_launch_time` | string\|null | Best UTC estimate of actual launch | `"2026-02-28T18:00:00Z"` | primary |
| `timing.launch_time_israel` | string\|null | Launch time in Asia/Jerusalem | `"2026-02-28T20:00:00+0200"` | enriched (solar) |
| `timing.launch_time_iran` | string\|null | Launch time in Asia/Tehran | `"2026-02-28T21:30:00+0330"` | enriched (solar) |
| `timing.solar_phase_launch_site` | int\|null | Daylight phase 0–5 at launch site | `0` | enriched (solar) |
| `timing.solar_phase_target` | int\|null | Daylight phase 0–5 at target | `0` | enriched (solar) |
| `timing.conflict_day` | int\|null | Day number (Day 1 = Feb 28 Israel time) | `1` | enriched (solar) |
| `timing.hours_since_last_wave` | float\|null | Hours since previous wave launch | `2.5` | enriched (tempo) |
| `timing.time_between_waves_minutes` | float\|null | Minutes since previous wave ended | | primary |
| `timing.wave_duration_minutes` | float\|null | Duration of wave in minutes | | primary |

## weapons

| Path | Type | Description | Example | Source |
|------|------|-------------|---------|--------|
| `weapons.payload` | string\|null | Free-text munitions description | `"Emad and Ghadr ballistic missiles"` | primary |
| `weapons.drones_used` | bool\|null | Drones/UAVs in payload | `true` | primary |
| `weapons.ballistic_missiles_used` | bool\|null | Ballistic missiles in payload | `true` | primary |
| `weapons.cruise_missiles_used` | bool\|null | Cruise missiles in payload | `false` | primary |

### weapons.types

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `weapons.types.emad_used` | bool\|null | Emad MRBM (liquid-fueled) | primary |
| `weapons.types.ghadr_used` | bool\|null | Ghadr MRBM (liquid-fueled) | primary |
| `weapons.types.sejjil_used` | bool\|null | Sejjil MRBM (solid-fueled) | primary |
| `weapons.types.kheibar_shekan_used` | bool\|null | Kheibar Shekan (MaRV, Mach 8) | primary |
| `weapons.types.fattah_used` | bool\|null | Fattah hypersonic missile | primary |
| `weapons.types.shahed_136_used` | bool\|null | Shahed-136 loitering munition | primary |
| `weapons.types.shahed_238_used` | bool\|null | Shahed-238 jet-powered drone | primary |

#### TP3-specific weapon types

These fields appear only in `data/tp3-2025/waves.json`:

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `weapons.types.shahed_131_used` | bool\|null | Shahed-131 loitering munition (lighter Shahed-136 variant) | primary |
| `weapons.types.shahed_107_used` | bool\|null | Shahed-107 UAV | primary |
| `weapons.types.shahed_129_used` | bool\|null | Shahed-129 UCAV | primary |
| `weapons.types.mohajer_6_used` | bool\|null | Mohajer-6 reconnaissance/strike UAV | primary |

### weapons.categories

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `weapons.categories.bm_liquid_fueled` | bool | Emad or Ghadr used | enriched (categories) |
| `weapons.categories.bm_solid_fueled` | bool | Sejjil, Kheibar Shekan, or Fattah | enriched (categories) |
| `weapons.categories.bm_marv_equipped` | bool | Kheibar Shekan or Fattah (MaRV) | enriched (categories) |
| `weapons.categories.bm_hypersonic` | bool | Fattah only | enriched (categories) |
| `weapons.categories.bm_cluster_warhead` | bool\|null | Warhead carried cluster submunitions. `true` = confirmed, `null` = not reported, `false` = ruled out | primary |

### weapons.cluster_warhead

Present (as object) when cluster warhead use is confirmed; `null` otherwise. Added 2026-03-05.

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `weapons.cluster_warhead.confirmed` | bool | Cluster warhead use confirmed by IDF/police/OSINT | primary |
| `weapons.cluster_warhead.carrier_missile` | string\|null | Missile type delivering the cluster warhead (e.g. Khorramshahr-4) | primary |
| `weapons.cluster_warhead.submunition_count` | int\|null | Estimated submunitions per warhead (~20 per IDF) | primary |
| `weapons.cluster_warhead.submunition_explosive_kg` | float\|null | Explosive weight per submunition in kg (~2.5 kg per IDF) | primary |
| `weapons.cluster_warhead.dispersal_radius_km` | float\|null | Estimated dispersal radius in km (~8 km per IDF) | primary |
| `weapons.cluster_warhead.dispersal_altitude_ft` | int\|null | Altitude at which warhead dispersed submunitions (feet) (~23,000 ft per TWZ) | primary |

## targets

| Path | Type | Description | Example | Source |
|------|------|-------------|---------|--------|
| `targets.israel_targeted` | bool\|null | Israel was a target | `true` | primary |
| `targets.us_bases_targeted` | bool\|null | US bases were targeted | `true` | primary |
| `targets.targets` | string\|null | Free-text target description | `"Nevatim airbase, Tel Aviv"` | primary |
| `targets.landings_countries` | string[] | ISO country codes where munitions landed | `["IL", "IQ"]` | primary |

### targets.israeli_locations

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `targets.israeli_locations.targeted_tel_aviv` | bool | Tel Aviv metro (incl. HaKirya, Bnei Brak, Petah Tikva) | enriched (categories) |
| `targets.israeli_locations.targeted_jerusalem` | bool | Jerusalem / East Jerusalem | enriched (categories) |
| `targets.israeli_locations.targeted_haifa` | bool | Haifa area | enriched (categories) |
| `targets.israeli_locations.targeted_negev_beersheba` | bool | Negev / Beersheba / Nevatim | enriched (categories) |
| `targets.israeli_locations.targeted_northern_periphery` | bool | Galilee / Ramat David / northern Israel | enriched (categories) |
| `targets.israeli_locations.targeted_eilat` | bool | Eilat | enriched (categories) |

### targets.us_bases

Array of matched US/coalition bases. Each entry:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Canonical base name |
| `country_code` | string | ISO country code |

Source: enriched (us_bases), matched against `data/reference/us_bases.json`

### targets.us_naval_vessels

Array of matched naval vessels. Each entry:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Vessel name |
| `type` | string | Vessel type |

Source: enriched (us_bases), matched against `data/reference/us_naval_vessels.json`

### targets.target_coordinates

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `targets.target_coordinates.lat` | float\|null | Primary target latitude | primary |
| `targets.target_coordinates.lon` | float\|null | Primary target longitude | primary |

## launch_site

| Path | Type | Description | Example | Source |
|------|------|-------------|---------|--------|
| `launch_site.description` | string\|null | Launch site description | `"Western Iran"` | primary |
| `launch_site.lat` | float\|null | Launch site latitude | `34.31` | primary |
| `launch_site.lon` | float\|null | Launch site longitude | `47.07` | primary |

## interception

| Path | Type | Description | Example | Source |
|------|------|-------------|---------|--------|
| `interception.intercepted` | bool\|null | Any munitions intercepted | `true` | primary |
| `interception.interception_systems` | string[] | Systems used | `["Arrow-2", "THAAD"]` | primary |
| `interception.estimated_intercept_count` | int\|null | Number intercepted | | primary |
| `interception.estimated_intercept_rate` | float\|null | Success rate (%) | | primary |
| `interception.exoatmospheric_interception` | bool\|null | Outside atmosphere (Arrow-3, SM-3) | `true` | primary |
| `interception.endoatmospheric_interception` | bool\|null | Inside atmosphere (Patriot, Iron Dome) | `true` | primary |
| `interception.interception_report` | string\|null | Narrative of interception effort | | primary |

### interception.intercepted_by

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `interception.intercepted_by.israel` | bool\|null | Israeli defenses engaged | primary |
| `interception.intercepted_by.us` | bool\|null | US forces engaged | primary |
| `interception.intercepted_by.uk` | bool\|null | UK forces engaged | primary |
| `interception.intercepted_by.jordan` | bool\|null | Jordanian forces engaged | primary |
| `interception.intercepted_by.other` | string[] | Other countries (e.g. France, UAE) | primary |

## munitions

| Path | Type | Description | Example | Source |
|------|------|-------------|---------|--------|
| `munitions.estimated_munitions_count` | int\|null | Total munitions this wave | `230` | primary |
| `munitions.munitions_targeting_israel` | int\|null | Munitions aimed at Israel | `230` | primary |
| `munitions.munitions_targeting_us_bases` | int\|null | Munitions aimed at US bases | `0` | primary |
| `munitions.cumulative_total` | int\|null | Running total across all waves | `35` | enriched (tempo) |

## impact

| Path | Type | Description | Example | Source |
|------|------|-------------|---------|--------|
| `impact.damage` | string\|null | Reported damage description | | primary |
| `impact.fatalities` | int\|null | Confirmed fatalities | `1` | primary |
| `impact.injuries` | int\|null | Confirmed injuries | `21` | primary |
| `impact.civilian_casualties` | int\|null | Civilian fatalities subset | | primary |
| `impact.military_casualties` | int\|null | Military fatalities subset | | primary |

## escalation

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `escalation.new_country_targeted` | bool | First appearance of a country code | enriched (tempo) |
| `escalation.new_weapon_first_use` | bool | First use of a weapon type | enriched (tempo) |

## proxy

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `proxy.involvement` | bool\|null | Proxy forces participated | primary |
| `proxy.description` | string\|null | Which proxies and their role | primary |

## sources

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `sources.idf_statement` | string\|null | IDF statement summary | primary |
| `sources.urls` | string[] | Source URLs | primary |

## reactions

Official statements and reactions from key parties, with links to source material.

| Path | Type | Description | Source |
|------|------|-------------|--------|
| `reactions.idf.statement` | string\|null | IDF spokesperson statement summary | primary |
| `reactions.idf.url` | string\|null | Link to IDF statement | primary |
| `reactions.us_government.statement` | string\|null | US government reaction summary | primary |
| `reactions.us_government.url` | string\|null | Link to US government statement | primary |
| `reactions.centcom.statement` | string\|null | CENTCOM statement summary | primary |
| `reactions.centcom.url` | string\|null | Link to CENTCOM statement | primary |

---

## Reference Data

### `data/reference/iranian_weapons.json`

Array of Iranian weapon system specs. Each entry includes `id`, `system_name`, `type_key` (matches `weapons.types.*_used`), `classification`, `propulsion`, `range_km`, `warhead_kg`, `guidance`, `marv`, `hypersonic`, `categories`, `first_combat_use`, and `sources`.

### `data/reference/defense_systems.json`

Array of air defense / BMD systems used by coalition forces. Each entry includes `id`, `system_name`, `operator`, `classification`, `intercept_phase` (exoatmospheric/endoatmospheric), `intercept_altitude_km`, `range_km`, `kill_mechanism`, `targets`, and `sources`. Systems covered: Arrow-2, Arrow-3, David's Sling, Iron Dome, THAAD, Patriot PAC-3, Aegis SM-3, Aegis SM-2.

### `data/reference/us_bases.json`

Array of US/coalition military bases in the region. Each entry: `name`, `aliases`, `country_code`, `country_name`, `branch`, `lat`, `lon`.

### `data/reference/us_naval_vessels.json`

Array of naval vessels relevant to the conflict. Each entry: `name`, `aliases`, `type`, `class`, `branch`, `fleet`.

### `data/reference/armed_forces.json`

Array of armed forces and non-state groups. Each entry: `id`, `name`, `abbreviation`, `aliases`, `country_code`, `side`, `type`, `parent`, `notes`.

### `data/tp4-2026/reference/israeli_targets.json`

Array of Israeli target sites. Each entry: `name`, `aliases`, `type`, `region`, `lat`, `lon`.

### `data/tp4-2026/reference/launch_zones.json`

Array of Iranian launch zones with approximate centroids. Each entry: `id`, `description_patterns`, `label`, `type`, `lat`, `lon`, `precision_km`.

## Validation

JSON Schema: `data/schema/wave.schema.json` — validates both TP3 and TP4 wave files.

---

## Schema Changelog

Track schema evolution as new fields are added or modified.

| Date | Field(s) Added/Changed | Reason |
|------|----------------------|--------|
| 2026-03-05 | `weapons.categories.bm_cluster_warhead` (bool\|null) | Track confirmed cluster warhead use per wave |
| 2026-03-05 | `weapons.cluster_warhead` (object\|null) | Structured cluster munition details: carrier missile, submunition count, explosive weight, dispersal radius, dispersal altitude |
| 2026-03-08 | `international_reactions.json` (new file) | 210 country/org diplomatic reactions to TP4 with statement-level detail |

---

## Part 2: international_reactions.json

Source file: `data/tp4-2026/international_reactions.json`

Each entry in `reactions[]` represents one country's or multilateral organisation's official response to an operation. Currently covers TP4 only (210 entities: 193 states, 17 multilateral bodies).

### Top-Level Metadata

| Path | Type | Description |
|------|------|-------------|
| `metadata.operation` | string | Operation identifier (`"tp4"`) |
| `metadata.operation_name` | string | Full operation name |
| `metadata.entity_count` | int | Number of entities in the reactions array |
| `metadata.last_updated` | string | ISO 8601 date of last update |

### Reaction Entity

| Path | Type | Description | Example |
|------|------|-------------|---------|
| `iso_3166_1_alpha2` | string\|null | ISO 3166-1 alpha-2 country code; null for multilateral bodies | `"US"` |
| `entity_name` | string | Country or organisation name | `"United States"` |
| `entity_type` | string | `"state"` or `"multilateral"` | `"state"` |
| `eu_member_state` | bool | Whether entity is an EU member state | `false` |
| `combatant` | bool | Whether entity is an active combatant | `true` |
| `overall_stance` | string | Categorical stance classification (see values below) | `"active_participant_coalition"` |
| `notes` | string\|null | Free-text contextual background | |

#### overall_stance Values

| Value | Count | Description |
|-------|------:|-------------|
| `silent` | 68 | No public statement issued |
| `calls_for_deescalation` | 62 | Called for restraint, ceasefire, or diplomatic resolution |
| `condemns_iran` | 50 | Condemned Iranian aggression or the attacks specifically |
| `condemns_israel` | 10 | Condemned Israeli actions that triggered the conflict |
| `supports_iran` | 7 | Expressed support or solidarity with Iran |
| `neutral_acknowledgement` | 5 | Acknowledged the situation without taking a clear side |
| `supports_israel` | 4 | Expressed support or solidarity with Israel |
| `active_participant_coalition` | 3 | Actively participating militarily alongside Israel/US |
| `active_participant_pro_iran` | 1 | Actively participating militarily alongside Iran |

### Statement Blocks

Three parallel blocks share the same structure: `head_of_state_statement`, `head_of_government_statement`, and `foreign_ministry_statement`.

| Path (prefix: `{block}.`) | Type | Description |
|----------------------------|------|-------------|
| `made` | bool | Whether a statement was issued |
| `date` | string\|null | ISO 8601 date of the statement |
| `speaker` | string\|null | Name of the speaker |
| `speaker_title` | string\|null | Title (e.g. "President", "Foreign Minister") |
| `summary` | string\|null | Brief summary of the statement |
| `statement_text` | string\|null | Full or partial text |
| `statement_url` | string\|null | Source URL |
| `category` | string\|null | Tone category (e.g. "condemnation", "support", "concern") |

### Additional Statements

| Path | Type | Description |
|------|------|-------------|
| `additional_statements` | array | Array of additional statements beyond the three standard channels |

Each entry in the array follows the same structure as the statement blocks above (speaker, title, summary, text, url, category).

### Flattened Export Columns

In the CSV/Parquet exports (`international_reactions.csv` / `.parquet`), the nested statement blocks are flattened with prefixes:

- `hos_` — head of state fields (e.g. `hos_statement_made`, `hos_speaker`, `hos_summary`)
- `hog_` — head of government fields
- `fm_` — foreign ministry fields
- `additional_statements_count` — integer count
- `additional_statements_json` — JSON string of the full array
