# Data Visualizer Agent Memory

## Color Palette (established)
- TP3 / Iranian offensive: `#f97316` (orange)
- TP4 / Iranian offensive: `#ef4444` (red)
- Israeli / defensive: `#3b82f6` (blue)
- US / coalition: `#1e3a5f` (navy)
- Drones: `#a78bfa` (purple)
- Ballistic missiles: `#fb923c` (orange)
- Cruise missiles: `#38bdf8` (sky blue)
- Success / interception: `#22c55e` (green)
- Warning / impact: `#eab308` (yellow)

## Dark/Military Theme Constants
- Background: `#0d1117`, Panel: `#161b22`, Grid: `#21262d`
- Text: `#e6edf3`, Muted: `#8b949e`

## Data Quirks
- TP3 `munitions.estimated_munitions_count` is sparse (many nulls); fall back to wave count for cumulative charts
- TP4 has `timing.time_between_waves_minutes`; TP3 only has `timing.hours_since_last_wave`
- `solar_phase` 0=night, 1=dawn/dusk, 2=day
- Coordinates in TP3 launch sites are often null; TP4 has more coordinate data
- TP3: 22 waves over 12 days; TP4: 19 waves over ~6 days (as of 2026-03-05)

## Chart Generation
- Script: `scripts/generate_charts.py` (git-ignored per repo conventions)
- Output: `analysis/charts/` at 300 DPI PNG
- Always `source .venv/bin/activate` before running

## File Paths
- TP3 data: `data/tp3-2025/waves.json`
- TP4 data: `data/tp4-2026/waves.json`
- Charts: `analysis/charts/01_inter_wave_timing.png` through `10_hour_of_day.png`
