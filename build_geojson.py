#!/usr/bin/env python3
"""
Build GeoJSON FeatureCollection from all wave JSON data.

Produces two layers:
  - launch_sites: Point features at each wave's launch site
  - targets: Point features at each wave's target coordinates

Waves missing coordinates are included with null geometry.

Usage:
    python build_geojson.py [--output PATH]

Outputs (default):
    exports/waves_launch_sites.geojson
    exports/waves_targets.geojson
    exports/waves_combined.geojson   (both layers merged)
"""

import json
import os
import sys
import argparse
from datetime import datetime

REPO = os.path.dirname(os.path.abspath(__file__))

WAVE_FILES = [
    ('tp1', os.path.join(REPO, 'data', 'tp1-2024', 'waves.json')),
    ('tp2', os.path.join(REPO, 'data', 'tp2-2024', 'waves.json')),
    ('tp3', os.path.join(REPO, 'data', 'tp3-2025', 'waves.json')),
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'waves.json')),
]


def load_all_waves():
    """Load waves from all operation JSON files."""
    waves = []
    for op, path in WAVE_FILES:
        with open(path) as f:
            data = json.load(f)
        for w in data['waves']:
            w['_operation'] = op
            waves.append(w)
    return waves


def make_point(lat, lon):
    """Return a GeoJSON Point geometry, or None if coords are missing."""
    if lat is not None and lon is not None:
        return {"type": "Point", "coordinates": [lon, lat]}
    return None


def wave_properties(w):
    """Extract flat properties for a GeoJSON feature."""
    timing = w.get('timing', {})
    weapons = w.get('weapons', {})
    munitions = w.get('munitions', {})
    interception = w.get('interception', {})
    impact = w.get('impact', {})
    targets = w.get('targets', {})

    return {
        "operation": w.get('_operation'),
        "wave_number": w.get('wave_number'),
        "wave_id": f"{w.get('_operation')}_w{w.get('wave_number')}",
        "wave_codename_english": w.get('wave_codename_english'),
        "wave_codename_farsi": w.get('wave_codename_farsi'),
        "announced_utc": timing.get('announced_utc'),
        "probable_launch_time": timing.get('probable_launch_time'),
        "conflict_day": timing.get('conflict_day'),
        "payload": weapons.get('payload'),
        "drones_used": weapons.get('drones_used'),
        "ballistic_missiles_used": weapons.get('ballistic_missiles_used'),
        "cruise_missiles_used": weapons.get('cruise_missiles_used'),
        "estimated_munitions_count": munitions.get('estimated_munitions_count'),
        "munitions_targeting_israel": munitions.get('munitions_targeting_israel'),
        "munitions_targeting_us_bases": munitions.get('munitions_targeting_us_bases'),
        "interception_rate": interception.get('estimated_intercept_rate'),
        "intercepted_count": interception.get('estimated_intercept_count'),
        "israel_targeted": targets.get('israel_targeted'),
        "us_bases_targeted": targets.get('us_bases_targeted'),
        "landing_countries": targets.get('landings_countries'),
        "casualties_killed": impact.get('fatalities'),
        "casualties_wounded": impact.get('injuries'),
        "launch_site_description": w.get('launch_site', {}).get('description'),
    }


def build_features(waves):
    """Build launch-site and target feature lists."""
    launch_features = []
    target_features = []

    for w in waves:
        props = wave_properties(w)
        ls = w.get('launch_site', {})
        tc = w.get('targets', {}).get('target_coordinates', {})

        # Launch site feature
        launch_geom = make_point(ls.get('lat'), ls.get('lon'))
        launch_props = {
            **props,
            "layer": "launch_site",
            "generic_location": ls.get('generic_location'),
        }
        launch_features.append({
            "type": "Feature",
            "geometry": launch_geom,
            "properties": launch_props,
        })

        # Target feature
        target_geom = make_point(tc.get('lat'), tc.get('lon'))
        target_props = {
            **props,
            "layer": "target",
            "generic_location": tc.get('generic_location'),
        }
        target_features.append({
            "type": "Feature",
            "geometry": target_geom,
            "properties": target_props,
        })

    return launch_features, target_features


def feature_collection(features):
    return {
        "type": "FeatureCollection",
        "features": features,
    }


def main():
    parser = argparse.ArgumentParser(description='Build GeoJSON from wave data')
    parser.add_argument('--output-dir', default=os.path.join(REPO, 'exports'),
                        help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    waves = load_all_waves()
    launch_features, target_features = build_features(waves)

    # Write individual layers
    for name, features in [('waves_launch_sites', launch_features),
                           ('waves_targets', target_features)]:
        path = os.path.join(args.output_dir, f'{name}.geojson')
        with open(path, 'w') as f:
            json.dump(feature_collection(features), f, indent=2, ensure_ascii=False)
        geo_count = sum(1 for feat in features if feat['geometry'] is not None)
        print(f"  {path}: {len(features)} features ({geo_count} with coordinates)")

    # Write combined
    combined = launch_features + target_features
    path = os.path.join(args.output_dir, f'waves_combined.geojson')
    with open(path, 'w') as f:
        json.dump(feature_collection(combined), f, indent=2, ensure_ascii=False)
    print(f"  {path}: {len(combined)} features (combined)")

    print(f"\nDone — {len(waves)} waves across {len(WAVE_FILES)} operations.")


if __name__ == '__main__':
    main()
