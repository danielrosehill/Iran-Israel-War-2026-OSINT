"""
Convert waves.csv to waves.json with nested structure.

Maps 75+ flat CSV columns into grouped JSON objects:
  timing, weapons (types + categories), targets (israeli_locations, us_bases,
  us_naval_vessels), launch_site, interception (intercepted_by), munitions,
  impact, escalation, proxy, sources

Conversions:
  - TRUE/FALSE → booleans
  - empty strings → null
  - comma-separated strings → arrays (where appropriate)
  - numeric strings → numbers
"""

import csv
import io
import json
from datetime import datetime
from pathlib import Path


def to_bool(val: str) -> bool | None:
    """Convert TRUE/FALSE string to boolean, empty to None."""
    v = val.strip().upper()
    if v == "TRUE":
        return True
    if v == "FALSE":
        return False
    return None


def to_int(val: str) -> int | None:
    v = val.strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def to_float(val: str) -> float | None:
    v = val.strip()
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def to_str(val: str) -> str | None:
    """Return stripped string or None if empty."""
    v = val.strip()
    return v if v else None


def to_list(val: str, sep: str = ",") -> list[str]:
    """Split comma-separated string into trimmed list, empty → []."""
    v = val.strip()
    if not v:
        return []
    return [item.strip() for item in v.split(sep) if item.strip()]


def convert_row(row: dict) -> dict:
    """Convert a flat CSV row dict into nested JSON structure."""
    wave = {
        "wave_number": to_int(row.get("wave_number", "")),
        "wave_codename_farsi": to_str(row.get("wave_codename_farsi", "")),
        "wave_codename_english": to_str(row.get("wave_codename_english", "")),

        "timing": {
            "announced_utc": to_str(row.get("announced_utc", "")),
            "announcement_source": to_str(row.get("announcement_source", "")),
            "announcement_x_url": to_str(row.get("announcement_x_url", "")),
            "probable_launch_time": to_str(row.get("probable_launch_time", "")),
            "launch_time_israel": to_str(row.get("launch_time_israel", "")),
            "launch_time_iran": to_str(row.get("launch_time_iran", "")),
            "solar_phase_launch_site": to_int(row.get("solar_phase_launch_site", "")),
            "solar_phase_target": to_int(row.get("solar_phase_target", "")),
            "conflict_day": to_int(row.get("conflict_day", "")),
            "hours_since_last_wave": to_float(row.get("hours_since_last_wave", "")),
            "time_between_waves_minutes": to_float(row.get("time_between_waves_minutes", "")),
            "wave_duration_minutes": to_float(row.get("wave_duration_minutes", "")),
        },

        "weapons": {
            "payload": to_str(row.get("payload", "")),
            "drones_used": to_bool(row.get("drones_used", "")),
            "ballistic_missiles_used": to_bool(row.get("ballistic_missiles_used", "")),
            "cruise_missiles_used": to_bool(row.get("cruise_missiles_used", "")),
            "types": {
                "emad_used": to_bool(row.get("emad_used", "")),
                "ghadr_used": to_bool(row.get("ghadr_used", "")),
                "sejjil_used": to_bool(row.get("sejjil_used", "")),
                "kheibar_shekan_used": to_bool(row.get("kheibar_shekan_used", "")),
                "fattah_used": to_bool(row.get("fattah_used", "")),
                "shahed_136_used": to_bool(row.get("shahed_136_used", "")),
                "shahed_238_used": to_bool(row.get("shahed_238_used", "")),
            },
            "categories": {
                "bm_liquid_fueled": to_bool(row.get("bm_liquid_fueled", "")),
                "bm_solid_fueled": to_bool(row.get("bm_solid_fueled", "")),
                "bm_marv_equipped": to_bool(row.get("bm_marv_equipped", "")),
                "bm_hypersonic": to_bool(row.get("bm_hypersonic", "")),
            },
        },

        "targets": {
            "israel_targeted": to_bool(row.get("israel_targeted", "")),
            "us_bases_targeted": to_bool(row.get("us_bases_targeted", "")),
            "targets": to_str(row.get("targets", "")),
            "landings_countries": to_list(row.get("landings_countries", "")),
            "israeli_locations": {
                "targeted_tel_aviv": to_bool(row.get("targeted_tel_aviv", "")),
                "targeted_jerusalem": to_bool(row.get("targeted_jerusalem", "")),
                "targeted_haifa": to_bool(row.get("targeted_haifa", "")),
                "targeted_negev_beersheba": to_bool(row.get("targeted_negev_beersheba", "")),
                "targeted_northern_periphery": to_bool(row.get("targeted_northern_periphery", "")),
                "targeted_eilat": to_bool(row.get("targeted_eilat", "")),
            },
            "us_bases": [],
            "us_naval_vessels": [],
            "target_coordinates": {
                "lat": to_float(row.get("target_lat", "")),
                "lon": to_float(row.get("target_lon", "")),
            },
        },

        "launch_site": {
            "description": to_str(row.get("launch_site_description", "")),
            "lat": to_float(row.get("launch_site_lat", "")),
            "lon": to_float(row.get("launch_site_lon", "")),
        },

        "interception": {
            "intercepted": to_bool(row.get("intercepted", "")),
            "interception_systems": to_list(row.get("interception_systems", "")),
            "intercepted_by": {
                "israel": to_bool(row.get("intercepted_by_israel", "")),
                "us": to_bool(row.get("intercepted_by_us", "")),
                "uk": to_bool(row.get("intercepted_by_uk", "")),
                "jordan": to_bool(row.get("intercepted_by_jordan", "")),
                "other": to_list(row.get("intercepted_by_other", "")),
            },
            "estimated_intercept_count": to_int(row.get("estimated_intercept_count", "")),
            "estimated_intercept_rate": to_float(row.get("estimated_intercept_rate", "")),
            "exoatmospheric_interception": to_bool(row.get("exoatmospheric_interception", "")),
            "endoatmospheric_interception": to_bool(row.get("endoatmospheric_interception", "")),
            "interception_report": to_str(row.get("interception_report", "")),
        },

        "munitions": {
            "estimated_munitions_count": to_int(row.get("estimated_munitions_count", "")),
            "munitions_targeting_israel": to_int(row.get("munitions_targeting_israel", "")),
            "munitions_targeting_us_bases": to_int(row.get("munitions_targeting_us_bases", "")),
            "cumulative_total": to_int(row.get("cumulative_munitions", "")),
        },

        "impact": {
            "damage": to_str(row.get("damage", "")),
            "fatalities": to_int(row.get("fatalities", "")),
            "injuries": to_int(row.get("injuries", "")),
            "civilian_casualties": to_int(row.get("civilian_casualties", "")),
            "military_casualties": to_int(row.get("military_casualties", "")),
            "sirens_activated": to_bool(row.get("sirens_activated", "")),
            "sirens_locations": to_str(row.get("sirens_locations", "")),
        },

        "escalation": {
            "new_country_targeted": to_bool(row.get("new_country_targeted", "")),
            "new_weapon_first_use": to_bool(row.get("new_weapon_first_use", "")),
        },

        "proxy": {
            "involvement": to_bool(row.get("proxy_involvement", "")),
            "description": to_str(row.get("proxy_description", "")),
        },

        "sources": {
            "idf_statement": to_str(row.get("idf_statement", "")),
            "urls": to_list(row.get("sources", "")),
        },

        "description": to_str(row.get("description", "")),
    }

    return wave


def main():
    data_dir = Path(__file__).parent.parent / "data"
    csv_path = data_dir / "waves.csv"
    json_path = data_dir / "waves.json"

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    waves = [convert_row(row) for row in rows]

    output = {
        "metadata": {
            "operation_name": "Operation True Promise 4",
            "operation_name_farsi": "عملیات وعده صادق ۴",
            "version": "2.0",
            "wave_count": len(waves),
            "date_range": {
                "start": "2026-02-28",
                "end": "2026-03-04",
            },
            "canonical_format": "json",
            "source_csv_columns": len(rows[0]) if rows else 0,
        },
        "waves": waves,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(waves)} waves from CSV to JSON")
    print(f"  Source columns: {output['metadata']['source_csv_columns']}")
    print(f"  Output: {json_path}")

    # Quick validation
    for w in waves:
        wn = w["wave_number"]
        assert wn is not None, "Missing wave_number"
        assert w["timing"]["probable_launch_time"] is not None, f"Wave {wn}: missing launch time"
    print("  Validation: all waves have wave_number and launch time")


if __name__ == "__main__":
    main()
