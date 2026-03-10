#!/usr/bin/env python3
"""
Calculate elapsed minutes between consecutive incidents in each operation.

For each operation's waves.json, sorts incidents by timing.announced_utc,
then computes elapsed_minutes_since_last for each incident (first = null).
Also processes the combined data/waves.json if it exists.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean

REPO_ROOT = Path(__file__).resolve().parent.parent

OPERATION_FILES = [
    "data/tp1-2024/waves.json",
    "data/tp2-2024/waves.json",
    "data/tp3-2025/waves.json",
    "data/tp4-2026/waves.json",
]

COMBINED_FILE = "data/waves.json"


def parse_utc(ts: str | None) -> datetime | None:
    """Parse an ISO 8601 UTC timestamp, returning None on failure."""
    if not ts:
        return None
    try:
        # Handle Z suffix and +00:00
        ts_clean = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_clean)
    except (ValueError, TypeError):
        return None


def process_incidents(incidents: list) -> dict:
    """
    Sort incidents by announced_utc, compute elapsed_minutes_since_last.
    Returns stats dict with min/max/avg and pairs under 60 min.
    """
    # Build list of (parsed_time, index) for sorting
    timed = []
    for i, inc in enumerate(incidents):
        timing = inc.get("timing", {})
        ts = parse_utc(timing.get("announced_utc"))
        timed.append((ts, i))

    # Sort by timestamp; None timestamps go to the end
    timed.sort(key=lambda x: (x[0] is None, x[0] if x[0] else datetime.min))

    # Reorder incidents in place
    sorted_incidents = [incidents[idx] for _, idx in timed]
    incidents.clear()
    incidents.extend(sorted_incidents)

    elapsed_values = []
    rapid_pairs = []
    prev_time = None

    for inc in incidents:
        timing = inc.get("timing", {})
        cur_time = parse_utc(timing.get("announced_utc"))

        if prev_time is not None and cur_time is not None:
            delta = (cur_time - prev_time).total_seconds() / 60.0
            elapsed = round(delta, 1)
            timing["elapsed_minutes_since_last"] = elapsed
            elapsed_values.append(elapsed)
            if elapsed < 60:
                seq = inc.get("sequence", "?")
                rapid_pairs.append((seq, elapsed))
        else:
            timing["elapsed_minutes_since_last"] = None

        if cur_time is not None:
            prev_time = cur_time

    stats = {}
    if elapsed_values:
        stats["min"] = min(elapsed_values)
        stats["max"] = max(elapsed_values)
        stats["avg"] = round(mean(elapsed_values), 1)
        stats["count"] = len(elapsed_values)
        stats["rapid_pairs"] = rapid_pairs
    return stats


def process_file(filepath: Path, label: str) -> dict | None:
    """Process a single JSON file. Returns stats or None if file missing."""
    if not filepath.exists():
        print(f"  [{label}] File not found: {filepath}")
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    incidents = data.get("incidents")
    if incidents is None:
        print(f"  [{label}] No 'incidents' key found")
        return None

    stats = process_incidents(incidents)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return stats


def main():
    print("=" * 65)
    print("Elapsed Minutes Calculator — Iran-Israel OSINT Data")
    print("=" * 65)

    all_stats = {}

    # Process per-operation files
    for rel_path in OPERATION_FILES:
        fp = REPO_ROOT / rel_path
        label = rel_path.split("/")[1] if "/" in rel_path else rel_path
        print(f"\nProcessing {label} ...")
        stats = process_file(fp, label)
        if stats:
            all_stats[label] = stats

    # Process combined file
    combined_fp = REPO_ROOT / COMBINED_FILE
    if combined_fp.exists():
        print(f"\nProcessing combined waves.json ...")
        stats = process_file(combined_fp, "combined")
        if stats:
            all_stats["combined"] = stats

    # Print summary
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)

    for label, stats in all_stats.items():
        print(f"\n  {label}:")
        print(f"    Incidents with elapsed data: {stats['count']}")
        print(f"    Min elapsed: {stats['min']} min")
        print(f"    Max elapsed: {stats['max']} min")
        print(f"    Avg elapsed: {stats['avg']} min")

        if stats["rapid_pairs"]:
            print(f"    ** Rapid pairs (< 60 min):")
            for seq, elapsed in stats["rapid_pairs"]:
                print(f"       Incident #{seq}: {elapsed} min since previous")

    if not all_stats:
        print("\n  No data processed.")

    print()


if __name__ == "__main__":
    main()
