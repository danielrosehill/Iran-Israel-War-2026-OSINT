#!/usr/bin/env python3
"""
Backfill missing weapons detail across all incident data files.

Fills in:
1. Drone variant flags (shahed_136, shahed_238, shahed_131, shahed_107, shahed_129, mohajer_6)
2. Ballistic missile type flags (emad, ghadr, sejjil, kheibar_shekan, fattah)
3. Missile categories (bm_liquid_fueled, bm_solid_fueled, bm_marv_equipped, bm_hypersonic, bm_cluster_warhead)
4. Interception systems (when intercepted=true but systems list is empty)
5. Estimated intercept count (calculated from rate * munitions count)
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

WAVE_FILES = [
    DATA_DIR / "tp1-2024" / "waves.json",
    DATA_DIR / "tp2-2024" / "waves.json",
    DATA_DIR / "tp3-2025" / "waves.json",
    DATA_DIR / "tp4-2026" / "waves.json",
]

# Drone variant keywords for payload text matching
DRONE_KEYWORDS = {
    "shahed_136_used": [r"shahed[- ]?136", r"geran[- ]?2"],
    "shahed_238_used": [r"shahed[- ]?238", r"geran[- ]?3", r"jet[- ]?powered"],
    "shahed_131_used": [r"shahed[- ]?131", r"geran[- ]?1"],
    "shahed_107_used": [r"shahed[- ]?107"],
    "shahed_129_used": [r"shahed[- ]?129"],
    "mohajer_6_used": [r"mohajer[- ]?6", r"mohajer"],
}

# BM type keywords for payload text matching
BM_KEYWORDS = {
    "emad_used": [r"\bemad\b", r"\bimad\b"],
    "ghadr_used": [r"\bghadr\b", r"\bghadr[- ]?[shf]\b", r"\bqadr\b"],
    "sejjil_used": [r"\bsejjil\b", r"\bashura\b"],
    "kheibar_shekan_used": [r"\bkheibar[- ]?shekan\b", r"\bkhaibar[- ]?shekan\b", r"\bkheibar\b", r"\bkhaibar\b"],
    "fattah_used": [r"\bfattah\b"],
    "khorramshahr_4_used": [r"\bkhorramshahr\b"],
}

# Which BM types imply which categories
BM_CATEGORIES = {
    "emad_used": {"bm_liquid_fueled": True, "bm_solid_fueled": False, "bm_marv_equipped": True, "bm_hypersonic": False},
    "ghadr_used": {"bm_liquid_fueled": True, "bm_solid_fueled": False, "bm_marv_equipped": True, "bm_hypersonic": False},
    "sejjil_used": {"bm_liquid_fueled": False, "bm_solid_fueled": True, "bm_marv_equipped": False, "bm_hypersonic": False},
    "kheibar_shekan_used": {"bm_liquid_fueled": False, "bm_solid_fueled": True, "bm_marv_equipped": True, "bm_hypersonic": False},
    "fattah_used": {"bm_liquid_fueled": False, "bm_solid_fueled": True, "bm_marv_equipped": True, "bm_hypersonic": False},
    "khorramshahr_4_used": {"bm_liquid_fueled": True, "bm_solid_fueled": False, "bm_marv_equipped": True, "bm_hypersonic": False},
}

# Default interception systems by operation
DEFAULT_INTERCEPTION_SYSTEMS = {
    "tp1": ["Arrow-2", "Arrow-3", "Iron Dome", "David's Sling", "Patriot PAC-3", "Aegis BMD / SM-3"],
    "tp2": ["Arrow-2", "Arrow-3", "Iron Dome", "David's Sling"],
    "tp3": ["Arrow-2", "Arrow-3", "Iron Dome", "David's Sling", "THAAD", "Patriot PAC-3", "Aegis BMD / SM-3"],
    "tp4": ["Arrow-2", "Arrow-3", "Iron Dome", "David's Sling", "THAAD", "Patriot PAC-3", "Aegis BMD / SM-3"],
}

# Default BM types by operation when payload text is generic
DEFAULT_BM_TYPES = {
    "tp3": {"emad_used": True, "ghadr_used": True},
    "tp4": {"emad_used": True, "ghadr_used": True, "kheibar_shekan_used": True},
}

changes_log = []


def get_wave_id(wave):
    """Get the wave identifier (sequence or wave_number)."""
    return wave.get("sequence", wave.get("wave_number", 0))


def log_change(op, seq, field, old_val, new_val):
    changes_log.append({
        "operation": op,
        "wave": seq,
        "field": field,
        "old": old_val,
        "new": new_val,
    })


def match_payload(payload, patterns):
    """Check if any pattern matches the payload text (case-insensitive)."""
    for pat in patterns:
        if re.search(pat, payload, re.IGNORECASE):
            return True
    return False


def backfill_drone_variants(wave, op):
    """Fill null drone variant flags based on payload text and operation context."""
    weapons = wave["weapons"]
    if not weapons.get("drones_used"):
        return

    types = weapons.get("types", {})
    payload = weapons.get("payload", "")
    seq = get_wave_id(wave)

    # Drone flags to check
    drone_flags = ["shahed_136_used", "shahed_238_used", "shahed_131_used",
                   "shahed_107_used", "shahed_129_used", "mohajer_6_used"]

    for flag in drone_flags:
        if types.get(flag) is not None:
            continue  # Already set

        # Try to match from payload text
        if flag in DRONE_KEYWORDS and match_payload(payload, DRONE_KEYWORDS[flag]):
            log_change(op, seq, f"types.{flag}", None, True)
            types[flag] = True
            continue

        # Apply defaults based on operation context
        if flag == "shahed_136_used":
            # Shahed-136 is the most common drone; default to True if drones_used
            # but only if no specific drone is mentioned at all
            any_drone_set = any(types.get(f) is True for f in drone_flags if f != flag)
            if not any_drone_set:
                # Generic "drones" payload - default to shahed_136
                log_change(op, seq, f"types.{flag}", None, True)
                types[flag] = True
            else:
                # Other drones set but this one not mentioned
                log_change(op, seq, f"types.{flag}", None, False)
                types[flag] = False
        elif flag == "shahed_238_used":
            # Jet-powered variant, only in TP3 (late waves) and TP4
            if op in ("tp3", "tp4") and match_payload(payload, [r"jet", r"238", r"advanced.*drone"]):
                log_change(op, seq, f"types.{flag}", None, True)
                types[flag] = True
            else:
                log_change(op, seq, f"types.{flag}", None, False)
                types[flag] = False
        elif flag == "shahed_131_used":
            # Often used alongside 136; default to True if 136 is used in TP1/TP3/TP4
            if op in ("tp1", "tp3", "tp4") and types.get("shahed_136_used") is True:
                log_change(op, seq, f"types.{flag}", None, True)
                types[flag] = True
            else:
                log_change(op, seq, f"types.{flag}", None, False)
                types[flag] = False
        elif flag == "shahed_107_used":
            # Shahed-107 not typically used in these operations
            log_change(op, seq, f"types.{flag}", None, False)
            types[flag] = False
        elif flag == "shahed_129_used":
            # Shahed-129 not typically used in these operations
            log_change(op, seq, f"types.{flag}", None, False)
            types[flag] = False
        elif flag == "mohajer_6_used":
            # Mohajer-6 used in TP3 (some waves) and TP4 (some waves)
            if match_payload(payload, DRONE_KEYWORDS["mohajer_6_used"]):
                log_change(op, seq, f"types.{flag}", None, True)
                types[flag] = True
            else:
                log_change(op, seq, f"types.{flag}", None, False)
                types[flag] = False


def backfill_bm_types(wave, op):
    """Fill null BM type flags based on payload text and operation context."""
    weapons = wave["weapons"]
    if not weapons.get("ballistic_missiles_used"):
        return

    types = weapons.get("types", {})
    payload = weapons.get("payload", "")
    seq = get_wave_id(wave)

    bm_flags = ["emad_used", "ghadr_used", "sejjil_used", "kheibar_shekan_used", "fattah_used"]

    # First pass: extract from payload text
    text_matches = {}
    for flag in bm_flags:
        if types.get(flag) is not None:
            continue
        if flag in BM_KEYWORDS and match_payload(payload, BM_KEYWORDS[flag]):
            text_matches[flag] = True

    # Also check for Khorramshahr-4 in payload (maps to khorramshahr_4_used, not in standard flags)
    khorramshahr_in_payload = match_payload(payload, BM_KEYWORDS.get("khorramshahr_4_used", []))

    # Second pass: apply text matches, then defaults for remaining nulls
    for flag in bm_flags:
        if types.get(flag) is not None:
            continue

        if flag in text_matches:
            log_change(op, seq, f"types.{flag}", None, True)
            types[flag] = True
        else:
            # Check if this is specifically contradicted by payload
            # If payload names specific missiles and this isn't one of them, set False
            specific_missiles_named = any(
                match_payload(payload, BM_KEYWORDS.get(f, []))
                for f in bm_flags if f != flag
            ) or khorramshahr_in_payload

            if specific_missiles_named:
                # Specific missiles named but this one not mentioned - set False
                log_change(op, seq, f"types.{flag}", None, False)
                types[flag] = False
            else:
                # Generic "ballistic missiles" - apply operation defaults
                defaults = DEFAULT_BM_TYPES.get(op, {"emad_used": True, "ghadr_used": True})
                if flag in defaults:
                    log_change(op, seq, f"types.{flag}", None, defaults[flag])
                    types[flag] = defaults[flag]
                else:
                    log_change(op, seq, f"types.{flag}", None, False)
                    types[flag] = False


def backfill_categories(wave, op):
    """Fill null category flags based on which BM types are set."""
    weapons = wave["weapons"]
    if not weapons.get("ballistic_missiles_used"):
        return

    types = weapons.get("types", {})
    cats = weapons.get("categories", {})
    seq = get_wave_id(wave)
    payload = weapons.get("payload", "")

    # Derive categories from active BM types
    derived = {
        "bm_liquid_fueled": False,
        "bm_solid_fueled": False,
        "bm_marv_equipped": False,
        "bm_hypersonic": False,
    }

    for bm_flag, cat_map in BM_CATEGORIES.items():
        if types.get(bm_flag) is True:
            for cat_key, cat_val in cat_map.items():
                if cat_val:
                    derived[cat_key] = True

    # Check for Fattah-2 (true hypersonic with HGV)
    if match_payload(payload, [r"fattah[- ]?2", r"hypersonic glide"]):
        derived["bm_hypersonic"] = True

    # Apply derived values where null OR where a True should override a False
    # (e.g., if Ghadr is used, bm_marv_equipped must be True even if previously set False)
    for cat_key in ["bm_liquid_fueled", "bm_solid_fueled", "bm_marv_equipped", "bm_hypersonic"]:
        if cats.get(cat_key) is None:
            log_change(op, seq, f"categories.{cat_key}", None, derived[cat_key])
            cats[cat_key] = derived[cat_key]
        elif derived[cat_key] is True and cats[cat_key] is False:
            # Correct: a weapon type that implies this category is present
            log_change(op, seq, f"categories.{cat_key}", False, True)
            cats[cat_key] = True

    # Cluster warhead
    if cats.get("bm_cluster_warhead") is None:
        cluster = bool(match_payload(payload, [r"cluster", r"submunition"]))
        log_change(op, seq, "categories.bm_cluster_warhead", None, cluster)
        cats["bm_cluster_warhead"] = cluster


def backfill_interception_systems(wave, op):
    """Fill empty interception_systems when intercepted=True."""
    interception = wave.get("interception", {})
    if not interception.get("intercepted"):
        return

    systems = interception.get("interception_systems", [])
    seq = get_wave_id(wave)

    if not systems:
        default_systems = DEFAULT_INTERCEPTION_SYSTEMS.get(op, [])
        log_change(op, seq, "interception.interception_systems", [], default_systems)
        interception["interception_systems"] = default_systems


def backfill_intercept_count(wave, op):
    """Calculate estimated_intercept_count from rate * munitions count."""
    interception = wave.get("interception", {})
    munitions = wave.get("munitions", {})
    seq = get_wave_id(wave)

    if interception.get("estimated_intercept_count") is not None:
        return

    rate = interception.get("estimated_intercept_rate")
    mun_count = munitions.get("estimated_munitions_count")

    if rate is not None and mun_count is not None:
        count = round(rate * mun_count)
        log_change(op, seq, "interception.estimated_intercept_count", None, count)
        interception["estimated_intercept_count"] = count


def process_file(filepath):
    """Process a single incident file."""
    with open(filepath) as f:
        data = json.load(f)

    op = data["metadata"]["operation"]
    incidents = data["incidents"]

    for incident in incidents:
        backfill_drone_variants(incident, op)
        backfill_bm_types(incident, op)
        backfill_categories(incident, op)
        backfill_interception_systems(incident, op)
        backfill_intercept_count(incident, op)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return len(incidents)


def main():
    total_incidents = 0
    for fp in WAVE_FILES:
        if not fp.exists():
            print(f"SKIP: {fp} not found")
            continue
        count = process_file(fp)
        total_incidents += count
        print(f"Processed {fp.name}: {count} incidents")

    # Summary
    print(f"\n{'='*70}")
    print(f"BACKFILL SUMMARY")
    print(f"{'='*70}")
    print(f"Total incidents processed: {total_incidents}")
    print(f"Total fields updated:  {len(changes_log)}")

    # Group by operation
    by_op = {}
    for c in changes_log:
        op = c["operation"]
        if op not in by_op:
            by_op[op] = []
        by_op[op].append(c)

    for op in sorted(by_op.keys()):
        entries = by_op[op]
        print(f"\n--- {op.upper()} ({len(entries)} changes) ---")

        # Group by field category
        drone_changes = [e for e in entries if "shahed" in e["field"] or "mohajer" in e["field"]]
        bm_changes = [e for e in entries if any(k in e["field"] for k in ["emad", "ghadr", "sejjil", "kheibar", "fattah"])]
        cat_changes = [e for e in entries if "categories" in e["field"]]
        intercept_changes = [e for e in entries if "interception" in e["field"]]

        if drone_changes:
            set_true = sum(1 for c in drone_changes if c["new"] is True)
            set_false = sum(1 for c in drone_changes if c["new"] is False)
            print(f"  Drone variants:     {len(drone_changes)} fields ({set_true} set True, {set_false} set False)")
        if bm_changes:
            set_true = sum(1 for c in bm_changes if c["new"] is True)
            set_false = sum(1 for c in bm_changes if c["new"] is False)
            print(f"  BM types:           {len(bm_changes)} fields ({set_true} set True, {set_false} set False)")
        if cat_changes:
            set_true = sum(1 for c in cat_changes if c["new"] is True)
            set_false = sum(1 for c in cat_changes if c["new"] is False)
            print(f"  Categories:         {len(cat_changes)} fields ({set_true} set True, {set_false} set False)")
        if intercept_changes:
            systems = [c for c in intercept_changes if "systems" in c["field"]]
            counts = [c for c in intercept_changes if "count" in c["field"]]
            if systems:
                print(f"  Interception sys:   {len(systems)} waves backfilled")
            if counts:
                print(f"  Intercept counts:   {len(counts)} waves calculated")

    # Detail for non-False changes (the interesting ones)
    print(f"\n{'='*70}")
    print("DETAIL: Fields set to True or non-trivial values")
    print(f"{'='*70}")
    for c in changes_log:
        if c["new"] is not False:
            print(f"  {c['operation'].upper()} wave {c['wave']:>2}: {c['field']} = {c['new']}")


if __name__ == "__main__":
    main()
