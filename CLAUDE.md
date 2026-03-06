# Iran-Israel War Data

OSINT dataset tracking Iranian missile/drone attack waves against Israel and US/coalition targets across multiple operations.

## Operations Covered

- **True Promise 1** (Apr 13–14, 2024) — First direct Iranian attack on Israel, 2 waves, ~320 munitions
- **True Promise 2** (Oct 1, 2024) — Ballistic-missile-only strike, 2 waves, ~200 munitions
- **True Promise 3** (Jun 13–24, 2025) — "Twelve-Day War", 22 waves, ~1,600-1,800 munitions
- **True Promise 4** (Feb 28–ongoing, 2026) — 19+ waves, expanded to US/coalition targets in Gulf

## Data Access

### SQLite Database (preferred for queries)

`data/iran_israel_war.db` — single queryable database with all wave data, reference tables, and junction tables. Rebuild with `python3 build_db.py`.

Key tables: `operations` (4), `waves` (45 rows, 76 columns), `wave_landing_countries`, `wave_interception_systems`, `wave_us_bases_targeted`, `iranian_weapons`, `defense_systems`, `armed_forces`, `us_bases`, `us_naval_vessels`.

### JSON Source Files

```
data/
  iran_israel_war.db       # SQLite database (all data combined)
  tp1-2024/waves.json      # TP1 (2 waves, Apr 2024)
  tp2-2024/waves.json      # TP2 (2 waves, Oct 2024)
  tp3-2025/waves.json      # TP3 (22 waves, Jun 2025)
  tp4-2026/waves.json      # TP4 (19 waves, Feb-Mar 2026)
  tp4-2026/reference/      # TP4-specific reference (targets, bases, vessels, launch zones)
  reference/               # Shared reference data (weapons, defense systems, armed forces, bases)
  schema/wave.schema.json  # JSON Schema for validation
```

## Website Repository

The OSINT analysis site is in a separate repo:

- **Repo:** `~/repos/github/Iran-Israel-OSINT-Site/` (private, GitHub: `danielrosehill/Iran-Israel-OSINT-Site`)
- **Deployment:** Vercel at `promisedenied.com`
- **Data pipeline:** The site repo has `sync-data.sh` which pulls JSON from this repo's raw GitHub URLs

### Publishing Workflow

After validating and gathering new data in this repo:

1. Commit and push data changes to this repo
2. Run `cd ~/repos/github/Iran-Israel-OSINT-Site && bash sync-data.sh` to pull fresh data into the site
3. Commit and push the site repo — Vercel auto-deploys on push

This should be done automatically after any data update (new waves added, corrections applied, reference data changed).

## SITREP Format

All SITREPs must follow the template in `docs/sitrep-template.md`:
- **SITREP** is always fully capitalised
- All times in UTC with local times (Israel IST, Iran IRST) in parentheses
- DTG format: `DD HHMM(Z) MON YYYY`
- Sections: BLUF, Situation Overview, Enemy Forces (wave-by-wave), Friendly Forces (interception), Casualties & Damage, Escalation Indicators, Outlook
- SITREPs are narrative documents, not just data tables

## JSON Structure

All four operations (TP1–TP4) use the same schema. Each wave is nested into: `timing`, `weapons` (with `types` + `categories`), `targets` (with `israeli_locations`, `us_bases`, `us_naval_vessels`), `launch_site`, `interception` (with `intercepted_by`), `munitions`, `impact`, `escalation`, `proxy`, `sources`.

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
