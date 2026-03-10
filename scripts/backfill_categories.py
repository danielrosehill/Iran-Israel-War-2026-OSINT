#!/usr/bin/env python3
"""Backfill weapons.categories from weapons.types in all wave JSON files."""

import json
import os

DATA_DIR = "/home/daniel/repos/github/Iran-Israel-War-2026-Data/data"

WAVE_FILES = [
    "tp1-2024/waves.json",
    "tp2-2024/waves.json",
    "tp3-2025/waves.json",
    "tp4-2026/waves.json",
]

# Mapping: category -> list of type keys that trigger it
LIQUID_FUELED = ["emad_used", "ghadr_used", "shahab_1_used", "shahab_2_used", "shahab_3_used"]
SOLID_FUELED = ["sejjil_used", "kheibar_shekan_used", "fattah_used", "fateh_110_used", "fateh_313_used", "zolfaghar_used"]
MARV_EQUIPPED = ["emad_used", "fattah_used"]
HYPERSONIC = ["fattah_used"]


def any_true(types: dict, keys: list) -> bool | None:
    """Return True if any key is True, False if none are True, None if all are None/missing."""
    found_false = False
    for k in keys:
        v = types.get(k)
        if v is True:
            return True
        if v is False:
            found_false = True
    return False if found_false else None


def derive_categories(wave: dict) -> dict | None:
    """Derive categories from types. Returns new categories dict or None if no weapons block."""
    weapons = wave.get("weapons")
    if not weapons:
        return None

    types = weapons.get("types", {})
    bm_used = weapons.get("ballistic_missiles_used")
    old_cats = weapons.get("categories", {})

    # If ballistic_missiles_used is False/null, categories should be null
    if not bm_used:
        return {
            "bm_liquid_fueled": None,
            "bm_solid_fueled": None,
            "bm_marv_equipped": None,
            "bm_hypersonic": None,
            "bm_cluster_warhead": old_cats.get("bm_cluster_warhead") if old_cats else None,
        }

    # ballistic_missiles_used is True - derive from types
    liquid = any_true(types, LIQUID_FUELED)
    solid = any_true(types, SOLID_FUELED)
    marv = any_true(types, MARV_EQUIPPED)
    hyper = any_true(types, HYPERSONIC)

    # For each: True if matching type is True, False if bm_used but no matching types True
    # (any_true already handles this - True if any match, False if at least one key exists as False)
    # But we want: if bm_used is True, set to False (not None) when no types match
    # So override None -> False when bm_used is True
    def resolve(val):
        return False if val is None else val

    return {
        "bm_liquid_fueled": resolve(liquid),
        "bm_solid_fueled": resolve(solid),
        "bm_marv_equipped": resolve(marv),
        "bm_hypersonic": resolve(hyper),
        "bm_cluster_warhead": old_cats.get("bm_cluster_warhead") if old_cats else None,
    }


def main():
    total_waves = 0
    total_changed = 0

    for rel_path in WAVE_FILES:
        fpath = os.path.join(DATA_DIR, rel_path)
        with open(fpath, "r") as f:
            data = json.load(f)

        waves = data.get("waves", [])
        file_changes = 0

        for wave in waves:
            total_waves += 1
            new_cats = derive_categories(wave)
            if new_cats is None:
                continue

            weapons = wave["weapons"]
            old_cats = weapons.get("categories", {})

            # Check if anything changed
            if old_cats != new_cats:
                op = wave.get("operation", "?")
                seq = wave.get("sequence", "?")
                print(f"  {op} wave {seq}:")
                for k in new_cats:
                    old_v = old_cats.get(k) if old_cats else None
                    new_v = new_cats[k]
                    if old_v != new_v:
                        print(f"    {k}: {old_v} -> {new_v}")
                weapons["categories"] = new_cats
                file_changes += 1
                total_changed += 1

        if file_changes > 0:
            with open(fpath, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"[{rel_path}] Updated {file_changes} wave(s)")
        else:
            print(f"[{rel_path}] No changes needed")

    print(f"\nSummary: {total_changed} waves changed out of {total_waves} total")


if __name__ == "__main__":
    main()
