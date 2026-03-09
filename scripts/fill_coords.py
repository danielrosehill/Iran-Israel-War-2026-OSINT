#!/usr/bin/env python3
"""
Fill missing launch_site and target_coordinates from reference data.

Sets generic_location=true for all auto-filled coordinates.
Sets generic_location=false for existing specific coordinates.

Usage:
    python scripts/fill_coords.py          # dry-run (prints changes)
    python scripts/fill_coords.py --apply  # writes changes to JSON files
"""

import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WAVE_FILES = [
    os.path.join(REPO, 'data', 'tp1-2024', 'waves.json'),
    os.path.join(REPO, 'data', 'tp2-2024', 'waves.json'),
    os.path.join(REPO, 'data', 'tp3-2025', 'waves.json'),
    os.path.join(REPO, 'data', 'tp4-2026', 'waves.json'),
]

# ── Load reference data ──────────────────────────────────────────────

def load_launch_zones():
    path = os.path.join(REPO, 'data', 'tp4-2026', 'reference', 'launch_zones.json')
    with open(path) as f:
        return json.load(f)

def load_us_bases():
    path = os.path.join(REPO, 'data', 'reference', 'us_bases.json')
    with open(path) as f:
        bases = json.load(f)
    lookup = {}
    for b in bases:
        lookup[b['name'].lower()] = b
        for alias in b.get('aliases', []):
            lookup[alias.lower()] = b
    return lookup

def load_israeli_targets():
    path = os.path.join(REPO, 'data', 'tp4-2026', 'reference', 'israeli_targets.json')
    with open(path) as f:
        return json.load(f)


# ── City centroids for israeli_locations booleans ────────────────────

ISRAELI_CITY_COORDS = {
    'targeted_tel_aviv':           (32.07, 34.77),
    'targeted_jerusalem':          (31.78, 35.22),
    'targeted_haifa':              (32.82, 35.00),
    'targeted_negev_beersheba':    (31.25, 34.79),
    'targeted_northern_periphery': (32.85, 35.50),
    'targeted_eilat':              (29.56, 34.95),
}


# ── Matching logic ───────────────────────────────────────────────────

def match_launch_zone(description, zones):
    """Match a launch_site description to a launch zone, returning (lat, lon) or None."""
    if not description or description == 'None':
        return None, None, None

    desc_lower = description.lower()

    # Try exact pattern match first
    for zone in zones:
        for pattern in zone.get('description_patterns', []):
            if pattern.lower() in desc_lower:
                return zone['lat'], zone['lon'], zone['id']

    # Check for partial keywords
    if 'naval' in desc_lower or 'irgc naval' in desc_lower:
        for zone in zones:
            if zone['id'] == 'persian_gulf_naval':
                return zone['lat'], zone['lon'], zone['id']

    if 'irgc' in desc_lower:
        for zone in zones:
            if zone['id'] == 'irgc_positions':
                return zone['lat'], zone['lon'], zone['id']

    return None, None, None


def compute_target_centroid(wave):
    """Compute a representative target coordinate from israeli_locations + us_bases."""
    targets = wave.get('targets', {})
    il = targets.get('israeli_locations', {})
    us_bases_list = targets.get('us_bases', [])

    points = []

    # Collect Israeli city coords for targeted locations
    for key, coords in ISRAELI_CITY_COORDS.items():
        val = il.get(key)
        if val is True:
            points.append(coords)

    # We don't mix US base coords into the centroid — they're in different countries.
    # For waves targeting only US bases, use the first base's coords.
    if not points and us_bases_list:
        # Try to resolve base name from reference
        return None  # handled separately

    if not points:
        return None

    # Compute centroid
    avg_lat = sum(p[0] for p in points) / len(points)
    avg_lon = sum(p[1] for p in points) / len(points)
    return (round(avg_lat, 4), round(avg_lon, 4))


def resolve_us_base_target(wave, us_bases_lookup):
    """For waves targeting only US bases (no Israeli locations), pick first base coords."""
    targets = wave.get('targets', {})
    us_bases_list = targets.get('us_bases', [])
    for base in us_bases_list:
        name = base.get('name', base.get('base_name', ''))
        key = name.lower()
        ref = us_bases_lookup.get(key)
        if ref and ref.get('lat') is not None:
            return (ref['lat'], ref['lon'])
    return None


# ── Main ─────────────────────────────────────────────────────────────

def process_file(path, zones, us_bases_lookup, apply=False):
    with open(path) as f:
        data = json.load(f)

    changes = 0
    op = data['metadata'].get('operation', os.path.basename(os.path.dirname(path)))

    for w in data['waves']:
        wn = w['wave_number']
        ls = w.setdefault('launch_site', {})
        tc = w.setdefault('targets', {}).setdefault('target_coordinates', {})

        # ── Mark existing coords as specific (not generic) ──
        if ls.get('lat') is not None and 'generic_location' not in ls:
            ls['generic_location'] = False
            changes += 1
            print(f"  {op} w{wn:>2} launch: marked existing coords as specific")

        if tc.get('lat') is not None and 'generic_location' not in tc:
            tc['generic_location'] = False
            changes += 1
            print(f"  {op} w{wn:>2} target: marked existing coords as specific")

        # ── Fill missing launch coords ──
        if ls.get('lat') is None:
            desc = ls.get('description', '')
            lat, lon, zone_id = match_launch_zone(desc, zones)
            if lat is None:
                # Fallback: IRGC Aerospace Force or unknown → irgc_positions
                for zone in zones:
                    if zone['id'] == 'irgc_positions':
                        lat, lon, zone_id = zone['lat'], zone['lon'], zone['id']
                        break
            if lat is not None:
                ls['lat'] = lat
                ls['lon'] = lon
                ls['generic_location'] = True
                changes += 1
                print(f"  {op} w{wn:>2} launch: filled from zone '{zone_id}' → ({lat}, {lon})")

        # ── Fill missing target coords ──
        if tc.get('lat') is None:
            centroid = compute_target_centroid(w)
            if centroid:
                tc['lat'] = centroid[0]
                tc['lon'] = centroid[1]
                tc['generic_location'] = True
                changes += 1
                print(f"  {op} w{wn:>2} target: filled from israeli_locations centroid → ({centroid[0]}, {centroid[1]})")
            else:
                # Try US base coords
                base_coords = resolve_us_base_target(w, us_bases_lookup)
                if base_coords:
                    tc['lat'] = base_coords[0]
                    tc['lon'] = base_coords[1]
                    tc['generic_location'] = True
                    changes += 1
                    print(f"  {op} w{wn:>2} target: filled from US base coords → ({base_coords[0]}, {base_coords[1]})")

    if apply and changes > 0:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f"  >> Wrote {path}")

    return changes


def main():
    apply = '--apply' in sys.argv
    if not apply:
        print("DRY RUN — pass --apply to write changes\n")

    zones = load_launch_zones()
    us_bases_lookup = load_us_bases()

    total = 0
    for path in WAVE_FILES:
        print(f"\n{os.path.relpath(path, REPO)}:")
        total += process_file(path, zones, us_bases_lookup, apply=apply)

    print(f"\nTotal changes: {total}")
    if not apply:
        print("(dry run — no files modified)")


if __name__ == '__main__':
    main()
