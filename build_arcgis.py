#!/usr/bin/env python3
"""
Build ArcGIS StoryMap-optimized exports from wave data.

Produces:
  - arcgis_launch_sites.geojson — launch origins with display-friendly fields
  - arcgis_targets.geojson — target points with display-friendly fields
  - arcgis_trajectories.geojson — LineString arcs from launch → target
  - arcgis_waves.csv — flat CSV with lat/lon for ArcGIS Online CSV import

All files include operation_label, wave_label, timestamp_epoch, and icon_type
fields optimized for ArcGIS pop-ups, symbology, and time slider animation.

Usage:
    python build_arcgis.py [--output-dir PATH]
"""

import json
import os
import csv
import argparse
from datetime import datetime

REPO = os.path.dirname(os.path.abspath(__file__))

WAVE_FILES = [
    ('tp1', os.path.join(REPO, 'data', 'tp1-2024', 'waves.json')),
    ('tp2', os.path.join(REPO, 'data', 'tp2-2024', 'waves.json')),
    ('tp3', os.path.join(REPO, 'data', 'tp3-2025', 'waves.json')),
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'waves.json')),
]

OPERATION_LABELS = {
    'tp1': 'True Promise 1 (Apr 2024)',
    'tp2': 'True Promise 2 (Oct 2024)',
    'tp3': 'True Promise 3 (Jun 2025)',
    'tp4': 'True Promise 4 (Feb–Mar 2026)',
}

OPERATION_SHORT = {
    'tp1': 'TP1',
    'tp2': 'TP2',
    'tp3': 'TP3',
    'tp4': 'TP4',
}


def load_all_waves():
    waves = []
    for op, path in WAVE_FILES:
        with open(path) as f:
            data = json.load(f)
        for w in data['waves']:
            w['_operation'] = op
            waves.append(w)
    return waves


def iso_to_epoch(iso_str):
    """Convert ISO 8601 timestamp to Unix epoch milliseconds (for ArcGIS time slider)."""
    if not iso_str:
        return None
    try:
        # Handle timezone offsets
        dt = datetime.fromisoformat(iso_str)
        return int(dt.timestamp() * 1000)
    except (ValueError, TypeError):
        return None


def build_wave_label(w):
    """Build a human-readable wave label for pop-ups."""
    op = OPERATION_SHORT.get(w.get('_operation'), w.get('_operation', ''))
    wn = w.get('wave_number', '?')
    codename = w.get('wave_codename_english')
    payload = w.get('weapons', {}).get('payload', '')

    if codename:
        return f"{op} Wave {wn} — {codename}"
    elif payload:
        # Truncate long payloads
        short_payload = payload[:60] + ('...' if len(payload) > 60 else '')
        return f"{op} Wave {wn} — {short_payload}"
    else:
        return f"{op} Wave {wn}"


def build_popup_summary(w):
    """Build a compact HTML-friendly summary for ArcGIS pop-ups."""
    timing = w.get('timing', {})
    weapons = w.get('weapons', {})
    munitions = w.get('munitions', {})
    interception = w.get('interception', {})
    impact = w.get('impact', {})

    parts = []
    ts = timing.get('announced_utc') or timing.get('probable_launch_time')
    if ts:
        parts.append(f"Time: {ts}")

    payload = weapons.get('payload')
    if payload:
        parts.append(f"Payload: {payload}")

    count = munitions.get('estimated_munitions_count')
    if count:
        parts.append(f"Munitions: {count}")

    rate = interception.get('estimated_intercept_rate')
    if rate:
        parts.append(f"Intercept rate: {rate}")

    killed = impact.get('fatalities')
    wounded = impact.get('injuries')
    if killed or wounded:
        parts.append(f"Casualties: {killed or 0} killed, {wounded or 0} wounded")

    damage = impact.get('damage')
    if damage:
        short_damage = damage[:120] + ('...' if len(damage) > 120 else '')
        parts.append(f"Damage: {short_damage}")

    return ' | '.join(parts)


def arcgis_properties(w, icon_type):
    """Build ArcGIS-optimized properties."""
    timing = w.get('timing', {})
    weapons = w.get('weapons', {})
    munitions = w.get('munitions', {})
    interception = w.get('interception', {})
    impact = w.get('impact', {})
    targets = w.get('targets', {})
    ls = w.get('launch_site', {})
    tc = targets.get('target_coordinates', {})

    timestamp = timing.get('announced_utc') or timing.get('probable_launch_time')

    return {
        # Display fields
        "operation": w.get('_operation'),
        "operation_label": OPERATION_LABELS.get(w.get('_operation'), w.get('_operation')),
        "operation_short": OPERATION_SHORT.get(w.get('_operation'), w.get('_operation')),
        "wave_number": w.get('wave_number'),
        "wave_id": f"{w.get('_operation')}_w{w.get('wave_number')}",
        "wave_label": build_wave_label(w),
        "popup_summary": build_popup_summary(w),
        "icon_type": icon_type,

        # Time fields
        "timestamp_utc": timestamp,
        "timestamp_epoch": iso_to_epoch(timestamp),
        "conflict_day": timing.get('conflict_day'),

        # Weapons
        "payload": weapons.get('payload'),
        "drones_used": weapons.get('drones_used'),
        "ballistic_missiles_used": weapons.get('ballistic_missiles_used'),
        "cruise_missiles_used": weapons.get('cruise_missiles_used'),
        "estimated_munitions_count": munitions.get('estimated_munitions_count'),

        # Targeting
        "israel_targeted": targets.get('israel_targeted'),
        "us_bases_targeted": targets.get('us_bases_targeted'),
        "landing_countries": ', '.join(targets.get('landings_countries', []) or []),
        "targets_description": targets.get('targets'),

        # Interception
        "interception_rate": interception.get('estimated_intercept_rate'),
        "intercepted_count": interception.get('estimated_intercept_count'),

        # Impact
        "fatalities": impact.get('fatalities'),
        "injuries": impact.get('injuries'),
        "damage": impact.get('damage'),

        # Location metadata
        "launch_site_description": ls.get('description'),
        "launch_lat": ls.get('lat'),
        "launch_lon": ls.get('lon'),
        "launch_generic": ls.get('generic_location'),
        "target_lat": tc.get('lat'),
        "target_lon": tc.get('lon'),
        "target_generic": tc.get('generic_location'),
    }


def make_point(lat, lon):
    if lat is not None and lon is not None:
        return {"type": "Point", "coordinates": [lon, lat]}
    return None


def make_line(lat1, lon1, lat2, lon2):
    if all(v is not None for v in [lat1, lon1, lat2, lon2]):
        return {"type": "LineString", "coordinates": [[lon1, lat1], [lon2, lat2]]}
    return None


def feature_collection(features):
    return {"type": "FeatureCollection", "features": features}


def main():
    parser = argparse.ArgumentParser(description='Build ArcGIS StoryMap exports')
    parser.add_argument('--output-dir', default=os.path.join(REPO, 'exports', 'latest'),
                        help='Output directory')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    waves = load_all_waves()

    launch_features = []
    target_features = []
    trajectory_features = []
    csv_rows = []

    for w in waves:
        ls = w.get('launch_site', {})
        tc = w.get('targets', {}).get('target_coordinates', {})

        launch_props = arcgis_properties(w, 'launch')
        target_props = arcgis_properties(w, 'target')

        # Launch site point
        launch_geom = make_point(ls.get('lat'), ls.get('lon'))
        launch_features.append({
            "type": "Feature",
            "geometry": launch_geom,
            "properties": launch_props,
        })

        # Target point
        target_geom = make_point(tc.get('lat'), tc.get('lon'))
        target_features.append({
            "type": "Feature",
            "geometry": target_geom,
            "properties": target_props,
        })

        # Trajectory line (launch → target)
        traj_geom = make_line(ls.get('lat'), ls.get('lon'),
                              tc.get('lat'), tc.get('lon'))
        if traj_geom:
            traj_props = arcgis_properties(w, 'trajectory')
            trajectory_features.append({
                "type": "Feature",
                "geometry": traj_geom,
                "properties": traj_props,
            })

        # CSV row (target-centric with launch coords as columns)
        csv_rows.append(launch_props)

    # Write GeoJSON layers
    outputs = [
        ('arcgis_launch_sites', launch_features),
        ('arcgis_targets', target_features),
        ('arcgis_trajectories', trajectory_features),
    ]
    for name, features in outputs:
        path = os.path.join(args.output_dir, f'{name}.geojson')
        with open(path, 'w') as f:
            json.dump(feature_collection(features), f, indent=2, ensure_ascii=False)
        geo_count = sum(1 for feat in features if feat['geometry'] is not None)
        print(f"  {path}: {len(features)} features ({geo_count} with geometry)")

    # Write CSV
    csv_path = os.path.join(args.output_dir, 'arcgis_waves.csv')
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"  {csv_path}: {len(csv_rows)} rows")

    print(f"\nDone — {len(waves)} waves, {len(trajectory_features)} trajectories.")


if __name__ == '__main__':
    main()
