#!/usr/bin/env python3
"""
Build a timestamped export bundle for release.

Creates exports/<timestamp>/ with subfolders:
  json/     — Combined + per-operation JSON files
  sqlite/   — SQLite database
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
    sqlite_dir = os.path.join(export_dir, 'sqlite')
    geojson_dir = os.path.join(export_dir, 'geojson')
    arcgis_dir = os.path.join(export_dir, 'arcgis')
    for d in [json_dir, sqlite_dir, geojson_dir, arcgis_dir]:
        os.makedirs(d, exist_ok=True)

    print(f"Building export: {export_dir}\n")

    # 1. Combined JSON
    print("JSON:")
    build_combined_json(os.path.join(json_dir, 'waves_all.json'))

    # 2. Individual operation JSONs
    for op_id, path in WAVE_FILES:
        dest = os.path.join(json_dir, f'{op_id}_waves.json')
        shutil.copy2(path, dest)
        print(f"  {dest}")

    # 3. SQLite database
    print("\nSQLite:")
    db_src = os.path.join(REPO, 'data', 'iran_israel_war.db')
    if os.path.exists(db_src):
        db_dest = os.path.join(sqlite_dir, 'iran_israel_war.db')
        shutil.copy2(db_src, db_dest)
        size_kb = os.path.getsize(db_dest) / 1024
        print(f"  {db_dest} ({size_kb:.0f} KB)")
    else:
        print("  WARNING: database not found, run build_db.py first")

    # 4. GeoJSON
    print("\nGeoJSON:")
    result = subprocess.run(
        ['python3', os.path.join(REPO, 'build_geojson.py'),
         '--output-dir', geojson_dir],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")

    # 5. ArcGIS StoryMap exports
    print("ArcGIS:")
    result = subprocess.run(
        ['python3', os.path.join(REPO, 'build_arcgis.py'),
         '--output-dir', arcgis_dir],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")

    # 6. Auto-generate SQLite schema documentation
    print("\nSchema:")
    if os.path.exists(os.path.join(sqlite_dir, 'iran_israel_war.db')):
        import sqlite3
        conn = sqlite3.connect(os.path.join(sqlite_dir, 'iran_israel_war.db'))
        cur = conn.cursor()
        schema_lines = ["# Database Schema\n"]
        schema_lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM [{table}]")
            count = cur.fetchone()[0]
            schema_lines.append(f"\n## {table} ({count} rows)\n")
            cur.execute(f"PRAGMA table_info([{table}])")
            cols = cur.fetchall()
            schema_lines.append("| # | Column | Type | Nullable | Default |")
            schema_lines.append("|--:|--------|------|----------|---------|")
            for col in cols:
                cid, name, ctype, notnull, default, pk = col
                nullable = "NO" if notnull else "YES"
                default_str = str(default) if default is not None else ""
                pk_str = " **PK**" if pk else ""
                schema_lines.append(f"| {cid} | `{name}`{pk_str} | {ctype} | {nullable} | {default_str} |")
        conn.close()
        schema_path = os.path.join(export_dir, 'SCHEMA.md')
        with open(schema_path, 'w') as f:
            f.write('\n'.join(schema_lines) + '\n')
        print(f"  {schema_path} ({len(tables)} tables)")

    # 7. Copy JSON schema into export
    schema_src = os.path.join(REPO, 'data', 'schema', 'wave.schema.json')
    if os.path.exists(schema_src):
        shutil.copy2(schema_src, os.path.join(json_dir, 'wave.schema.json'))
        print(f"  Copied wave.schema.json to {json_dir}")

    # 8. Copy README files into subfolders
    readme_dir = os.path.join(REPO, 'exports', 'latest')
    for subdir in ['json', 'sqlite', 'geojson', 'arcgis']:
        readme_src = os.path.join(readme_dir, subdir, 'README.md')
        if os.path.exists(readme_src):
            shutil.copy2(readme_src, os.path.join(export_dir, subdir, 'README.md'))

    # 9. Write manifest
    manifest = {
        "timestamp": timestamp,
        "structure": {
            "json": "Combined and per-operation wave JSON files",
            "sqlite": "SQLite database with all tables and reference data",
            "geojson": "GeoJSON layers for GIS tools (QGIS, Mapbox, Leaflet, kepler.gl)",
            "arcgis": "ArcGIS Online / StoryMap optimized exports with enriched properties",
        },
        "files": collect_files(export_dir),
    }
    manifest_path = os.path.join(export_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # 10. Copy to latest/
    if os.path.exists(latest_dir):
        shutil.rmtree(latest_dir)
    shutil.copytree(export_dir, latest_dir)
    print(f"\nCopied to {latest_dir}")

    total_files = len(collect_files(export_dir))
    print(f"\nExport complete: {total_files} files in {export_dir}")
    return export_dir


if __name__ == '__main__':
    main()
