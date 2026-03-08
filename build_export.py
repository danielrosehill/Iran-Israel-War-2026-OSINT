#!/usr/bin/env python3
"""
Build a timestamped export bundle for release.

Creates exports/<timestamp>/ containing:
  - waves_all.json         Combined JSON of all waves across all operations
  - iran_israel_war.db     SQLite database (copied from data/)
  - waves_launch_sites.geojson
  - waves_targets.geojson
  - waves_combined.geojson

Also copies the latest export to exports/latest/ for stable URLs.

Usage:
    python build_export.py
"""

import json
import os
import shutil
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.abspath(__file__))

WAVE_FILES = [
    ('tp1', os.path.join(REPO, 'data', 'tp1-2024', 'waves.json')),
    ('tp2', os.path.join(REPO, 'data', 'tp2-2024', 'waves.json')),
    ('tp3', os.path.join(REPO, 'data', 'tp3-2025', 'waves.json')),
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'waves.json')),
]


def build_combined_json(output_path):
    """Merge all operation wave files into a single JSON."""
    combined = {
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "operations": [],
    }
    total_waves = 0
    for op_id, path in WAVE_FILES:
        with open(path) as f:
            data = json.load(f)
        combined["operations"].append(data)
        total_waves += len(data["waves"])

    combined["total_waves"] = total_waves

    with open(output_path, 'w') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"  {output_path} ({total_waves} waves)")


def main():
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    export_dir = os.path.join(REPO, 'exports', timestamp)
    latest_dir = os.path.join(REPO, 'exports', 'latest')
    os.makedirs(export_dir, exist_ok=True)

    print(f"Building export: {export_dir}\n")

    # 1. Combined JSON
    print("Combined JSON:")
    build_combined_json(os.path.join(export_dir, 'waves_all.json'))

    # 2. Individual operation JSONs
    print("\nOperation JSONs:")
    for op_id, path in WAVE_FILES:
        dest = os.path.join(export_dir, f'{op_id}_waves.json')
        shutil.copy2(path, dest)
        print(f"  {dest}")

    # 3. SQLite database
    print("\nSQLite database:")
    db_src = os.path.join(REPO, 'data', 'iran_israel_war.db')
    if os.path.exists(db_src):
        db_dest = os.path.join(export_dir, 'iran_israel_war.db')
        shutil.copy2(db_src, db_dest)
        size_kb = os.path.getsize(db_dest) / 1024
        print(f"  {db_dest} ({size_kb:.0f} KB)")
    else:
        print("  WARNING: database not found, run build_db.py first")

    # 4. GeoJSON
    print("\nGeoJSON:")
    import subprocess
    result = subprocess.run(
        ['python3', os.path.join(REPO, 'build_geojson.py'),
         '--output-dir', export_dir],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")

    # 5. Copy to latest/
    if os.path.exists(latest_dir):
        shutil.rmtree(latest_dir)
    shutil.copytree(export_dir, latest_dir)
    print(f"\nCopied to {latest_dir}")

    # 6. Write manifest
    manifest = {
        "timestamp": timestamp,
        "export_dir": export_dir,
        "files": sorted(os.listdir(export_dir)),
    }
    manifest_path = os.path.join(export_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    # Also in latest
    shutil.copy2(manifest_path, os.path.join(latest_dir, 'manifest.json'))

    print(f"\nExport complete: {len(os.listdir(export_dir))} files in {export_dir}")
    return export_dir


if __name__ == '__main__':
    main()
