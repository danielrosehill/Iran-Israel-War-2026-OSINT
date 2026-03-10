#!/usr/bin/env python3
"""
Backfill target_hit and target_locations into wave JSON files.

Logic for target_hit (overall):
  - intercept_rate >= 0.99 AND no fatalities/injuries AND no damage mentions → false
  - intercept_rate < 0.80 → true
  - intercept_rate 0.80-0.99 → "partial"
  - fatalities or injuries > 0 → true (overrides intercept rate)
  - damage description mentions hits/damage/struck → true
  - intercepted == false → true
  - If none of the above can determine → null

Per-target hit:
  - If overall intercept_rate >= 0.99 and no casualties → all Israeli targets hit=false
  - If impact/damage mentions specific locations → those hit=true
  - US bases: derive from damage_reported if available
  - Default null if unclear
"""

import json
import re
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WAVE_FILES = [
    "data/tp1-2024/waves.json",
    "data/tp2-2024/waves.json",
    "data/tp3-2025/waves.json",
    "data/tp4-2026/waves.json",
]

LOCATION_MAP = {
    "targeted_tel_aviv": "Tel Aviv",
    "targeted_jerusalem": "Jerusalem",
    "targeted_haifa": "Haifa",
    "targeted_negev_beersheba": "Nevatim / Negev",
    "targeted_northern_periphery": "Northern Israel",
    "targeted_eilat": "Eilat",
}

# Keywords in damage text that indicate targets were hit
HIT_KEYWORDS = re.compile(
    r"struck|hit|impact|damage[ds]?|killed|destroyed|fire|shut down|penetrat|crater|fragment|submunition|engulfed",
    re.IGNORECASE,
)

# Patterns that negate damage (e.g., "No damage reported")
NO_DAMAGE_PATTERN = re.compile(
    r"no damage|all.*intercept|fully intercept|no.+report",
    re.IGNORECASE,
)


def determine_overall_target_hit(wave):
    """Determine overall target_hit status for a wave."""
    interception = wave.get("interception", {}) or {}
    impact = wave.get("impact", {}) or {}

    intercept_rate = interception.get("estimated_intercept_rate")
    intercepted = interception.get("intercepted")
    fatalities = impact.get("fatalities")
    injuries = impact.get("injuries")
    damage = impact.get("damage") or ""
    damage_desc = impact.get("damage_description") or ""
    combined_damage = f"{damage} {damage_desc}"

    has_casualties = (fatalities is not None and fatalities > 0) or (
        injuries is not None and injuries > 0
    )
    has_damage_text = bool(HIT_KEYWORDS.search(combined_damage))
    negated_damage = bool(NO_DAMAGE_PATTERN.search(combined_damage))
    # If negation present, discount the damage text
    if negated_damage:
        has_damage_text = False

    # If not intercepted at all, targets were hit
    if intercepted is False:
        return True

    # Intercept rate >= 0.99 with no casualties = fully defended
    if intercept_rate is not None and intercept_rate >= 0.99 and not has_casualties and not has_damage_text:
        return False

    # Casualties override everything
    if has_casualties:
        return True

    # Damage descriptions mentioning hits
    if has_damage_text:
        return True

    # Intercept rate logic (for rates < 0.99)
    if intercept_rate is not None:
        if intercept_rate >= 0.99:
            # Already handled above but with damage_text; if we're here, damage text is true
            return "partial"
        elif intercept_rate < 0.80:
            return True
        else:
            return "partial"

    # Events: check for strike events with damage
    events = wave.get("events", []) or []
    for evt in events:
        if evt.get("event_type") in ("strike", "impact"):
            evt_dmg = evt.get("damage_description") or ""
            if HIT_KEYWORDS.search(evt_dmg):
                return True

    # Also check the targets text description for clues
    targets = wave.get("targets", {}) or {}
    targets_desc = targets.get("targets") or ""
    if HIT_KEYWORDS.search(targets_desc):
        return True

    return None


def determine_per_target_hit(wave, overall_hit):
    """Build target_locations array with per-target hit status."""
    targets = wave.get("targets", {}) or {}
    impact = wave.get("impact", {}) or {}
    interception = wave.get("interception", {}) or {}
    events = wave.get("events", []) or []

    intercept_rate = interception.get("estimated_intercept_rate")
    damage = (impact.get("damage") or "") + " " + (impact.get("damage_description") or "")

    # Collect event damage text for location matching
    event_damage_texts = []
    for evt in events:
        if evt.get("event_type") in ("strike", "impact"):
            loc = evt.get("location_name") or ""
            dmg = evt.get("damage_description") or ""
            event_damage_texts.append(f"{loc} {dmg}")
    all_damage_text = f"{damage} {' '.join(event_damage_texts)}"

    target_locations = []

    # Israeli locations
    israeli_locs = targets.get("israeli_locations", {}) or {}
    for flag_key, display_name in LOCATION_MAP.items():
        if israeli_locs.get(flag_key) is True:
            hit = _determine_israeli_location_hit(
                display_name, overall_hit, intercept_rate, all_damage_text, impact
            )
            target_locations.append(
                {"name": display_name, "type": "israeli", "hit": hit}
            )

    # US bases
    us_bases = targets.get("us_bases", []) or []
    for base in us_bases:
        # Handle both formats: {name: ...} and {base_name: ...}
        base_name = base.get("base_name") or base.get("name") or "Unknown US Base"
        damage_reported = base.get("damage_reported")
        country = base.get("country_code") or base.get("country")

        if damage_reported is True:
            hit = True
        elif damage_reported is False:
            hit = False
        elif damage_reported is None:
            # Try to infer from damage text
            # Normalize the base name for matching
            base_name_lower = base_name.lower()
            name_parts = [p for p in re.split(r"[\s/\-]+", base_name_lower) if len(p) > 3]
            if any(part in all_damage_text.lower() for part in name_parts):
                if HIT_KEYWORDS.search(all_damage_text):
                    hit = True
                else:
                    hit = None
            else:
                hit = None
        else:
            hit = None

        entry = {"name": base_name, "type": "us_base", "hit": hit}
        if country:
            entry["country"] = country
        target_locations.append(entry)

    return target_locations


def _determine_israeli_location_hit(name, overall_hit, intercept_rate, all_damage_text, impact):
    """Determine hit status for a specific Israeli location."""
    # If overall intercept_rate >= 0.99 and no casualties, all targets false
    fatalities = impact.get("fatalities")
    injuries = impact.get("injuries")
    has_casualties = (fatalities is not None and fatalities > 0) or (
        injuries is not None and injuries > 0
    )

    negated = bool(NO_DAMAGE_PATTERN.search(all_damage_text))

    if intercept_rate is not None and intercept_rate >= 0.99 and not has_casualties:
        return False

    # Check if this specific location is mentioned in damage text
    name_lower = name.lower()
    damage_lower = all_damage_text.lower()

    # Location-specific keywords to search for
    search_terms = {
        "Tel Aviv": ["tel aviv", "tel nof", "hakirya", "glilot", "ben gurion", "bat yam",
                      "bnei brak", "ramat gan", "givatayim", "holon", "yehud", "or yehuda",
                      "petah tikva", "rishon", "central israel"],
        "Jerusalem": ["jerusalem"],
        "Haifa": ["haifa", "bazan", "refinery haifa"],
        "Nevatim / Negev": ["nevatim", "negev", "beersheba", "beer sheva", "ramon", "ovda",
                             "sdot micha", "hatzerim", "dimona", "arad"],
        "Northern Israel": ["northern israel", "galilee", "kiryat shmona", "upper galilee",
                             "golan", "hadera", "northern periphery"],
        "Eilat": ["eilat"],
    }

    terms = search_terms.get(name, [name_lower])
    location_mentioned_in_damage = any(t in damage_lower for t in terms)

    if location_mentioned_in_damage and HIT_KEYWORDS.search(all_damage_text):
        return True

    # If overall hit is true but we can't confirm this specific location
    if overall_hit is True:
        # If location is mentioned in damage text at all, likely hit
        if location_mentioned_in_damage:
            return True
        return None

    if overall_hit == "partial":
        if location_mentioned_in_damage:
            return True
        return None

    if overall_hit is False:
        return False

    return None


def process_file(filepath):
    """Process a single waves.json file."""
    with open(filepath) as f:
        data = json.load(f)

    op = data.get("metadata", {}).get("operation", filepath)
    waves = data.get("waves", [])
    stats = {"total": len(waves), "true": 0, "false": 0, "partial": 0, "null": 0}

    for wave in waves:
        overall_hit = determine_overall_target_hit(wave)
        target_locations = determine_per_target_hit(wave, overall_hit)

        # Insert into targets object
        targets = wave.get("targets", {})
        targets["target_hit"] = overall_hit
        targets["target_locations"] = target_locations

        # Count
        if overall_hit is True:
            stats["true"] += 1
        elif overall_hit is False:
            stats["false"] += 1
        elif overall_hit == "partial":
            stats["partial"] += 1
        else:
            stats["null"] += 1

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return op, stats, waves


def main():
    print("=" * 60)
    print("Backfilling target_hit into wave JSON files")
    print("=" * 60)

    total_waves = 0
    total_locations = 0

    for rel_path in WAVE_FILES:
        filepath = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(filepath):
            print(f"\n  SKIP: {rel_path} (not found)")
            continue

        op, stats, waves = process_file(filepath)
        total_waves += stats["total"]

        wave_locs = sum(
            len(w.get("targets", {}).get("target_locations", []))
            for w in waves
        )
        total_locations += wave_locs

        print(f"\n  {op} ({rel_path})")
        print(f"    Waves: {stats['total']}")
        print(
            f"    target_hit: true={stats['true']}, false={stats['false']}, "
            f"partial={stats['partial']}, null={stats['null']}"
        )
        print(f"    target_locations entries added: {wave_locs}")

    print(f"\n{'=' * 60}")
    print(f"Total waves processed: {total_waves}")
    print(f"Total target_locations entries: {total_locations}")
    print("Done.")


if __name__ == "__main__":
    main()
