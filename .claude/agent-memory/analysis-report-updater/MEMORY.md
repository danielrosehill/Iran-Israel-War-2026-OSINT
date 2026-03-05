# Analysis Report Updater — Agent Memory

## Project Structure
- Canonical wave data: `data/tp3-2025/waves.json` and `data/tp4-2026/waves.json`
- Both files have top-level keys: `metadata` and `waves` (a list)
- Report source: `report/report.typ` (Typst); compiled to `report/report.pdf`
- Charts saved to `report/report_*.png` (10 charts total)
- Python venv at `.venv` (use `source .venv/bin/activate`)
- Chart generation script: `gen_charts.py` at repo root (created by this agent)
- Typst is available at `/usr/local/bin/typst`

## JSON Schema Conventions
- Weapon types live at `wave["weapons"]["types"]["emad_used"]` (bool or null)
- Weapon categories live at `wave["weapons"]["categories"]["bm_liquid_fueled"]`
- Top-level weapon booleans: `wave["weapons"]["drones_used"]`, `ballistic_missiles_used`, `cruise_missiles_used`
- Solar phase at `wave["timing"]["solar_phase_launch_site"]`: 0=Night, 1=Astro twilight, 2=Nautical, 3=Civil, 4=Low sun, 5=Daylight
- Inter-wave gap: `wave["timing"]["hours_since_last_wave"]` (null for first wave)
- Countries hit: `wave["targets"]["landings_countries"]` (list of ISO-2 codes)
- Israel targeted: `wave["targets"]["israel_targeted"]` (bool)
- US bases targeted: `wave["targets"]["us_bases_targeted"]` (bool)
- Proxy fields (houthi_involved etc.) are all null in current dataset — known gap

## Key Statistics (as of 2026-03-05)
- TP3: 22 waves, Jun 13–24 2025, Israel-only, ~1,600–1,800+ munitions estimated
- TP4: 19 waves (ongoing), Feb 28–Mar 5 2026, 12 countries
- Combined total: 41 waves

### TP3 Weapon Presence by Wave
- Emad: 20/22 (91%), Ghadr: 21/22 (95%) — both liquid-fueled MRBMs
- Shahed-136: 7/22 (32%), no cruise missiles
- Sejjil: 1/22 (W12), Fattah-1: 1/22 (W11), Kheibar Shekan: 2/22 (W20–21)

### TP4 Weapon Presence by Wave
- Shahed-136: 15/19 (79%), Emad: 2/19 (11%), Ghadr: 3/19 (16%)
- Drones: 16/19 (84%), BMs: 18/19 (95%), Cruise missiles: 3/19 (16%)
- Kheibar Shekan: 1/19 (W10), Khorramshahr-4: 1/19 (W19 — first combat use)

### Timing
- TP3 avg inter-wave: 10.5h (min 1.0h, max 23.0h)
- TP4 avg inter-wave: 5.4h (min 1.2h, max 14.0h)
- TP3 night (phase 0–1): 8/22; TP4 night: 8/19

### Targeting
- TP4 Israel targeted: 14/19 (74%); US bases: 16/19 (84%)
- TP4 countries: AE, BH, CY, IL, IO, IQ, JO, KW, OM, QA, SA, TR (12 total)

## Typst Formatting Patterns
- Footer uses "AI-GENERATED" disclaimer line
- Tables use `fill: (x, y) => if y == 0 { rgb(...).lighten(85%) }` for header rows
- Alternate row shading: `if calc.rem(y, 2) == 0 { rgb("#f8f8f8") }`
- Charts referenced as `image("report_NN_name.png", width: 100%)`
- Color palette: TP3=blue #2563EB, TP4=red #DC2626, accent=amber #F59E0B

## Data Quality Issues
- Wave 18 (TP4) has null timestamp — conflict day 5 confirmed, time unknown
- `houthi_involved` is null for all 41 waves — not wave-attributed
- TP3 solar phase shows 14/22 as Daylight — may be data entry artifact
- Munitions counts (launched/intercepted) are null for almost all waves
- `interception_rate_claimed` is null for all TP4 waves

## Chart Generation Notes
- Run `gen_charts.py` from repo root with `.venv` activated
- All charts saved at 300 DPI to `report/` with `report_` prefix
- Solar phase 0 = Night (not 5 — common mistake to flip the encoding)
