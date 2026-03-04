"""
Enrich waves.json with local times and solar phase data.

Reads/writes JSON paths:
  - timing.launch_time_israel
  - timing.launch_time_iran
  - timing.solar_phase_launch_site (integer 0-5)
  - timing.solar_phase_target (integer 0-5)
  - timing.conflict_day
  - launch_site.lat / launch_site.lon
  - targets.target_coordinates.lat / targets.target_coordinates.lon

Solar phase scale:
  0 = Night (sun below -18°)
  1 = Astronomical twilight (-18° to -12°)
  2 = Nautical twilight (-12° to -6°)
  3 = Civil twilight (-6° to 0°)
  4 = Low sun / golden hour (0° to 6°)
  5 = Full daylight (above 6°)
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from astral import sun


# Timezone definitions
TZ_ISRAEL = ZoneInfo("Asia/Jerusalem")
TZ_IRAN = ZoneInfo("Asia/Tehran")

# Default coordinates when wave has no specific lat/lon
DEFAULT_LAUNCH_LAT = 34.31  # Kermanshah region, western Iran
DEFAULT_LAUNCH_LON = 47.07
DEFAULT_TARGET_LAT = 32.09  # Tel Aviv area
DEFAULT_TARGET_LON = 34.78


def solar_elevation(dt_utc: datetime, lat: float, lon: float) -> float:
    """Calculate solar elevation angle in degrees for a given UTC time and location."""
    from astral import Observer
    obs = Observer(latitude=lat, longitude=lon, elevation=0)
    return sun.elevation(obs, dt_utc)


def elevation_to_phase(elevation_deg: float) -> int:
    """Convert solar elevation angle to phase integer 0-5."""
    if elevation_deg > 6:
        return 5  # Full daylight
    elif elevation_deg > 0:
        return 4  # Low sun / golden hour
    elif elevation_deg > -6:
        return 3  # Civil twilight
    elif elevation_deg > -12:
        return 2  # Nautical twilight
    elif elevation_deg > -18:
        return 1  # Astronomical twilight
    else:
        return 0  # Night


def enrich_wave(wave: dict) -> None:
    """Enrich a single wave with solar/timing data in place."""
    timing = wave.setdefault("timing", {})
    launch_str = timing.get("probable_launch_time")
    if not launch_str:
        return

    # Parse UTC time
    dt_utc = datetime.fromisoformat(launch_str.replace("Z", "+00:00"))

    # Local times
    dt_israel = dt_utc.astimezone(TZ_ISRAEL)
    dt_iran = dt_utc.astimezone(TZ_IRAN)
    timing["launch_time_israel"] = dt_israel.strftime("%Y-%m-%dT%H:%M:%S%z")
    timing["launch_time_iran"] = dt_iran.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Launch site coordinates
    ls = wave.get("launch_site", {})
    launch_lat = ls.get("lat") or DEFAULT_LAUNCH_LAT
    launch_lon = ls.get("lon") or DEFAULT_LAUNCH_LON
    elev = solar_elevation(dt_utc, launch_lat, launch_lon)
    timing["solar_phase_launch_site"] = elevation_to_phase(elev)

    # Conflict day (Day 1 = date of first launch in Israel local time)
    day1_date = datetime(2026, 2, 28, tzinfo=TZ_ISRAEL).date()
    israel_date = dt_israel.date()
    timing["conflict_day"] = (israel_date - day1_date).days + 1

    # Target coordinates
    tc = wave.get("targets", {}).get("target_coordinates", {})
    target_lat = tc.get("lat") or DEFAULT_TARGET_LAT
    target_lon = tc.get("lon") or DEFAULT_TARGET_LON
    elev = solar_elevation(dt_utc, target_lat, target_lon)
    timing["solar_phase_target"] = elevation_to_phase(elev)


def main():
    data_dir = Path(__file__).parent.parent / "data"
    json_path = data_dir / "waves.json"

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    for wave in data["waves"]:
        enrich_wave(wave)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"Enriched {len(data['waves'])} waves:")
    print(f"{'Wave':>4} | {'Israel Local':>22} | {'Iran Local':>22} | {'Phase(launch)':>13} | {'Phase(target)':>13}")
    print("-" * 85)
    for wave in data["waves"]:
        t = wave.get("timing", {})
        print(
            f"{wave['wave_number']:>4} | "
            f"{t.get('launch_time_israel', '') or '':>22} | "
            f"{t.get('launch_time_iran', '') or '':>22} | "
            f"{str(t.get('solar_phase_launch_site', '')):>13} | "
            f"{str(t.get('solar_phase_target', '')):>13}"
        )


if __name__ == "__main__":
    main()
