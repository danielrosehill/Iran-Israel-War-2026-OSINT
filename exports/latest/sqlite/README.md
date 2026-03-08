# SQLite Database

### `iran_israel_war.db`
Single queryable database combining all wave data, reference tables, and international reactions.

**18 tables**, ~400 KB. Rebuilt from source JSON via `build_db.py`.

Key tables:
- `operations` (4 rows) — TP1–TP4 metadata
- `waves` (55 rows, 76 columns) — all attack waves with full detail
- `wave_events` (19 rows) — granular strike/interception events with BDA
- `wave_landing_countries` — which countries each wave's munitions landed in
- `wave_interception_systems` — which defense systems intercepted each wave
- `wave_us_bases_targeted` — US/coalition bases targeted per wave
- `iranian_weapons` (12 rows) — weapon system reference data
- `defense_systems` (8 rows) — Israeli/coalition defense systems
- `interceptor_munitions` (11 rows) — interceptor missile types
- `us_bases` (13 rows) — US/coalition base locations with coordinates
- `international_reactions` (210 rows) — country/org responses to TP4
