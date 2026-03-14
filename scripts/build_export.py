#!/usr/bin/env python3
"""
Build a timestamped export bundle for release.

Creates exports/<timestamp>/ with subfolders:
  json/     — Combined + per-operation JSON files
  geojson/  — GeoJSON layers (launch sites, targets, combined)
  arcgis/   — ArcGIS StoryMap-optimized exports (GeoJSON + CSV)

Also copies the latest export to exports/latest/ for stable URLs.

Usage:
    python build_export.py
"""

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WAVE_FILES = [
    ('tp1', os.path.join(REPO, 'data', 'tp1-2024', 'waves.json')),
    ('tp2', os.path.join(REPO, 'data', 'tp2-2024', 'waves.json')),
    ('tp3', os.path.join(REPO, 'data', 'tp3-2025', 'waves.json')),
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'waves.json')),
]


def build_combined_json(output_path):
    """Merge all operation incident files into a single JSON."""
    combined = {
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "operations": [],
    }
    total_incidents = 0
    for op_id, path in WAVE_FILES:
        with open(path) as f:
            data = json.load(f)
        combined["operations"].append(data)
        total_incidents += len(data["incidents"])

    combined["total_incidents"] = total_incidents

    with open(output_path, 'w') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"  {output_path} ({total_incidents} incidents)")


def collect_files(directory):
    """Recursively list all files relative to directory."""
    files = []
    for root, _, filenames in os.walk(directory):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(root, fn), directory)
            files.append(rel)
    return sorted(files)


def main():
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    export_dir = os.path.join(REPO, 'exports', timestamp)
    latest_dir = os.path.join(REPO, 'exports', 'latest')

    # Create subfolders
    json_dir = os.path.join(export_dir, 'json')
    geojson_dir = os.path.join(export_dir, 'geojson')
    arcgis_dir = os.path.join(export_dir, 'arcgis')
    for d in [json_dir, geojson_dir, arcgis_dir]:
        os.makedirs(d, exist_ok=True)

    print(f"Building export: {export_dir}\n")

    # 1. Combined JSON
    print("JSON:")
    build_combined_json(os.path.join(json_dir, 'incidents_all.json'))

    # 2. Individual operation JSONs
    for op_id, path in WAVE_FILES:
        dest = os.path.join(json_dir, f'{op_id}_incidents.json')
        shutil.copy2(path, dest)
        print(f"  {dest}")

    # 3. GeoJSON
    print("\nGeoJSON:")
    result = subprocess.run(
        ['python3', os.path.join(REPO, 'build_geojson.py'),
         '--output-dir', geojson_dir],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")

    # 4. ArcGIS StoryMap exports
    print("ArcGIS:")
    result = subprocess.run(
        ['python3', os.path.join(REPO, 'build_arcgis.py'),
         '--output-dir', arcgis_dir],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")

    # 5. Copy JSON schema into export
    schema_src = os.path.join(REPO, 'data', 'schema', 'wave.schema.json')
    if os.path.exists(schema_src):
        shutil.copy2(schema_src, os.path.join(json_dir, 'wave.schema.json'))
        print(f"  Copied wave.schema.json to {json_dir}")

    # 6. Copy README files into subfolders
    readme_dir = os.path.join(REPO, 'exports', 'latest')
    for subdir in ['json', 'geojson', 'arcgis']:
        readme_src = os.path.join(readme_dir, subdir, 'README.md')
        if os.path.exists(readme_src):
            shutil.copy2(readme_src, os.path.join(export_dir, subdir, 'README.md'))

    # 7. Write manifest
    manifest = {
        "timestamp": timestamp,
        "structure": {
            "json": "Combined and per-operation incident JSON files",
            "geojson": "GeoJSON layers for GIS tools (QGIS, Mapbox, Leaflet, kepler.gl)",
            "arcgis": "ArcGIS Online / StoryMap optimized exports with enriched properties",
        },
        "files": collect_files(export_dir),
    }
    manifest_path = os.path.join(export_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # 8. Copy to latest/
    if os.path.exists(latest_dir):
        shutil.rmtree(latest_dir)
    shutil.copytree(export_dir, latest_dir)
    print(f"\nCopied to {latest_dir}")

    total_files = len(collect_files(export_dir))
    print(f"\nExport complete: {total_files} files in {export_dir}")
    return export_dir


if __name__ == '__main__':
    main()
