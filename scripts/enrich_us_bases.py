"""
Enrich waves.json with US base and naval vessel targeting data.

Loads reference files (us_bases.json, us_naval_vessels.json), scans each wave's
targets, damage, and description text for name/alias matches, and populates:
  - targets.us_bases[] — matched base objects with name and country_code
  - targets.us_naval_vessels[] — matched vessel objects with name and type
"""

import json
from pathlib import Path


def load_reference(data_dir: Path) -> tuple[list[dict], list[dict]]:
    ref_dir = data_dir / "reference"
    with open(ref_dir / "us_bases.json", encoding="utf-8") as f:
        bases = json.load(f)
    with open(ref_dir / "us_naval_vessels.json", encoding="utf-8") as f:
        vessels = json.load(f)
    return bases, vessels


def match_bases(text: str, bases: list[dict]) -> list[dict]:
    """Find all US bases mentioned in text."""
    text_lower = text.lower()
    matched = []
    for base in bases:
        for alias in base.get("aliases", []):
            if alias.lower() in text_lower:
                matched.append({
                    "name": base["name"],
                    "country_code": base["country_code"],
                })
                break
    return matched


def match_vessels(text: str, vessels: list[dict]) -> list[dict]:
    """Find all naval vessels mentioned in text."""
    text_lower = text.lower()
    matched = []
    for vessel in vessels:
        for alias in vessel.get("aliases", []):
            if alias.lower() in text_lower:
                matched.append({
                    "name": vessel["name"],
                    "type": vessel["type"],
                })
                break
    return matched


def wave_text(wave: dict) -> str:
    """Combine all text fields for pattern matching."""
    parts = [
        wave.get("targets", {}).get("targets", "") or "",
        wave.get("impact", {}).get("damage", "") or "",
        wave.get("description", "") or "",
        wave.get("weapons", {}).get("payload", "") or "",
    ]
    return " | ".join(parts)


def main():
    data_dir = Path(__file__).parent.parent / "data"
    json_path = data_dir / "waves.json"

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    bases, vessels = load_reference(data_dir)

    for wave in data["waves"]:
        text = wave_text(wave)
        wave["targets"]["us_bases"] = match_bases(text, bases)
        wave["targets"]["us_naval_vessels"] = match_vessels(text, vessels)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"{'Wave':>4} | US Bases | Naval Vessels")
    print("-" * 50)
    for wave in data["waves"]:
        wn = wave["wave_number"]
        base_names = [b["name"] for b in wave["targets"]["us_bases"]]
        vessel_names = [v["name"] for v in wave["targets"]["us_naval_vessels"]]
        if base_names or vessel_names:
            print(f"{wn:>4} | {', '.join(base_names) or '-':40s} | {', '.join(vessel_names) or '-'}")


if __name__ == "__main__":
    main()
