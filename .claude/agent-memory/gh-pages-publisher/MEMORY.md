# GH Pages Publisher — Persistent Memory

## Site Architecture

- **Publish root:** `docs/` directory on `main` branch (GitHub Pages setting)
- **Pages:** index.html, map.html, timeline.html, data.html, about.html
- **Assets:** docs/css/style.css, docs/js/data.js, docs/js/map.js
- **Data copies:** docs/data/ contains tp3-waves.json, tp4-waves.json, israeli_targets.json, us_bases.json, launch_zones.json

## Libraries (CDN)

- Leaflet 1.9.4 (with integrity hash) — used on map.html
- CartoDB dark_all tiles for dark map aesthetic
- No Chart.js or D3 yet — charts deferred

## Data Loading Pattern

- `docs/js/data.js` provides shared utilities: `loadTP3Waves()`, `loadTP4Waves()`, `loadAllWaves()`, `loadIsraeliTargets()`, `loadUSBases()`, `loadLaunchZones()`
- All pages use relative paths from the `docs/` root (e.g., `data/tp3-waves.json`)
- `data.js` is loaded before `map.js` on the map page

## Key Data Facts

- TP3: 22 waves, Jun 13-24 2025, schema v1.1. Most wave munitions counts are null (incomplete)
- TP4: 19 waves, Feb 28 - Mar 5 2026, schema v2.1. Has `time_between_waves_minutes` field absent in TP3.
- Launch site coords: TP3 waves have lat/lon=null in launch_site; must resolve from description via launch_zones.json patterns
- TP4 wave 1 launch_site has lat: 34.31, lon: 47.07 (western Iran centroid)
- Color scheme: Iran/launch=red (#cc2936), Israeli targets=blue (#4a90d9), US bases=green (#2da44e), drones=amber (#f0a500)

## Map Details

- Wave markers use DivIcon with rotated square (diamond shape)
- Launch zone markers use dashed circle (low fill opacity) to indicate imprecision
- Jitter applied to wave markers (+/- 0.4 deg) to avoid stacking at same launch centroid
- `resolveLaunchCoords()` in map.js matches launch_site.description against launch_zones.json patterns

## GitHub Pages Config

- Serve from `docs/` folder on `main` branch
- No custom domain set yet
- All asset paths are relative — no absolute URLs used

## Known Data Quirks

- TP3 `timing` block lacks `time_between_waves_minutes` and `wave_duration_minutes` fields (TP4-only)
- Both operations use `estimated_intercept_rate` (float 0-1) not percentage
- `us_bases` in targets is array of {name, country_code} objects, not strings
- `intercepted_by.other` is an array of strings (e.g., ["France", "UAE"])
