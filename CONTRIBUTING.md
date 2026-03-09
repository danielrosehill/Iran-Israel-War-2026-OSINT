# Contributing to Iran-Israel War 2026 Data

Thank you for your interest in contributing to this open-source OSINT dataset. This document explains how to contribute new data, correct errors, and what standards we expect.

Please read [SCOPE.md](SCOPE.md) before contributing to understand what this dataset does and does not cover.

## Contribution Types

There are two predefined contribution paths, each with its own pull request template:

### 1. Data Correction

Use this when you have identified an error in the existing dataset — wrong coordinates, incorrect weapon attribution, inaccurate casualty figures, misattributed claims, etc.

- **PR template:** `data-correction`
- **Branch naming:** `fix/tp4-wave12-coordinates` or `fix/reference-emad-range`
- **Requirements:**
  - Identify the exact file(s) and field(s) that are wrong
  - Provide the corrected value(s)
  - Cite at least one OSINT source supporting the correction
  - If correcting a disputed fact, provide sources from multiple parties where possible

### 2. New Data

Use this when you are adding new information — new wave events, new BDA assessments, new SATINT observations, updated reference data, or new attack waves.

- **PR template:** `new-data`
- **Branch naming:** `data/tp4-wave21` or `data/bda-nevatim-satint`
- **Requirements:**
  - Follow the JSON schema in `data/schema/wave.schema.json`
  - Cite OSINT sources for all new data
  - Run `python3 scripts/build_db.py` and confirm it builds without errors
  - For new waves: populate all required fields (`wave_number`, `timing`, `weapons`, `targets`)
  - For new events: include `event_type`, `location_name`, `confidence`, and `outcome_status`

## Data Standards

### Sources and Attribution

- All data must be sourced from **open-source intelligence (OSINT)** only
- Provide URLs to source material wherever possible
- Acceptable sources include: official government/military statements, satellite imagery providers (Planet Labs, Maxar, Airbus), established news agencies (AP, Reuters, AFP), credible OSINT analysts, academic/think tank reports (CSIS, IISS, ISW)
- Social media (X/Twitter) posts are acceptable as supplementary sources but should not be the sole source for factual claims

### Neutrality and Competing Claims

This dataset does not take sides. When Iran and Israel (or any parties) make contradictory claims:

- Record **both claims verbatim** using `iranian_claim`, `israeli_claim`, and `us_claim` fields
- Set `outcome_status` to `disputed` when claims conflict
- Use `event_type: "impact"` (not `strike`) when the nature of a ground-level event is contested
- Include independent BDA where available to let the data speak for itself
- Do not editorialize in `damage_description` — describe what is observable, not whose narrative is correct

### Confidence Levels

Use these consistently:

| Level | Meaning |
|---|---|
| `confirmed` | Multiple independent sources agree; or verified by satellite imagery / official statements from both sides |
| `probable` | Single credible source, or multiple sources with minor discrepancies |
| `unconfirmed` | Single-source claim, social media only, or IRGC/IDF claim without independent corroboration |

### JSON Conventions

- **Booleans:** native JSON `true` / `false`
- **Missing/unknown:** `null` (never empty strings or `"unknown"`)
- **Arrays:** native JSON arrays, even for single items
- **Timestamps:** ISO 8601 with timezone offset (e.g. `2026-03-01T14:30:00Z`)
- **Coordinates:** decimal degrees (WGS84)
- **Country codes:** ISO 3166-1 alpha-2 (e.g. `IL`, `IR`, `US`)
- **UUIDs:** UUID v4 format; leave as `null` in contributions (auto-generated at build time)
- **Cost estimates:** use the `unit_cost_usd` object format with `estimate`, `range`, and `notes` fields

### File Structure

```
data/
  tp1-2024/waves.json       # Operation True Promise 1
  tp2-2024/waves.json       # Operation True Promise 2
  tp3-2025/waves.json       # Operation True Promise 3
  tp4-2026/waves.json       # Operation True Promise 4
  reference/
    iranian_weapons.json     # Iranian weapon systems with costs and navigation
    defense_systems.json     # Coalition defense systems/batteries
    interceptor_munitions.json  # Specific interceptor rounds with costs and specs
    armed_forces.json        # Military actors on both sides
    us_bases.json            # US/coalition bases in theater
    us_naval_vessels.json    # US Navy vessels involved
  schema/
    wave.schema.json         # JSON Schema for validation
```

## How to Contribute

1. **Fork** the repository
2. **Create a branch** using the naming conventions above
3. **Make your changes** following the data standards
4. **Run the build** to verify:
   ```bash
   python3 build_db.py
   ```
5. **Open a pull request** using the appropriate template:
   - Data correction: select the "Data Correction" template
   - New data: select the "New Data" template
6. **Fill in all template fields** — PRs missing required information (especially sources) will be asked to provide them before review

## What Not to Contribute

- Classified or non-public intelligence
- Israeli/coalition offensive operation data (see [SCOPE.md](SCOPE.md))
- Political commentary or editorialized descriptions
- Data without any OSINT sourcing
- Speculative or predictive analysis (this belongs in the companion site repo, not the data repo)

## Questions

Open a GitHub Issue with the `question` label if you're unsure about anything.
