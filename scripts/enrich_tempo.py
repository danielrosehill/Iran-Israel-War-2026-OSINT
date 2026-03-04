"""
Enrich waves.json with tempo and escalation analysis.

Reads/writes JSON paths:
  - timing.hours_since_last_wave
  - munitions.cumulative_total
  - escalation.new_country_targeted
  - escalation.new_weapon_first_use
"""

import json
from datetime import datetime
from pathlib import Path


WEAPON_KEYS = [
    "emad_used", "ghadr_used", "sejjil_used", "kheibar_shekan_used",
    "fattah_used", "shahed_136_used", "shahed_238_used",
]


def main():
    data_dir = Path(__file__).parent.parent / "data"
    json_path = data_dir / "waves.json"

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    prev_launch_utc = None
    cumulative = 0
    seen_countries: set[str] = set()
    seen_weapons: set[str] = set()

    for wave in data["waves"]:
        timing = wave.setdefault("timing", {})
        munitions = wave.setdefault("munitions", {})
        escalation = wave.setdefault("escalation", {})
        weapons = wave.get("weapons", {})
        targets = wave.get("targets", {})

        # --- hours_since_last_wave ---
        launch_str = timing.get("probable_launch_time")
        if launch_str:
            dt = datetime.fromisoformat(launch_str.replace("Z", "+00:00"))
            if prev_launch_utc is not None:
                delta = dt - prev_launch_utc
                hours = delta.total_seconds() / 3600
                timing["hours_since_last_wave"] = round(hours, 1)
            else:
                timing["hours_since_last_wave"] = None
            prev_launch_utc = dt
        else:
            timing["hours_since_last_wave"] = None

        # --- cumulative_total ---
        count = munitions.get("estimated_munitions_count")
        if count is not None:
            cumulative += count
        munitions["cumulative_total"] = cumulative if cumulative > 0 else None

        # --- new_country_targeted ---
        countries = set(targets.get("landings_countries", []))
        new_countries = countries - seen_countries
        escalation["new_country_targeted"] = bool(new_countries)
        seen_countries |= countries

        # --- new_weapon_first_use ---
        types = weapons.get("types", {})
        current_weapons = {k for k in WEAPON_KEYS if types.get(k) is True}
        # Also check top-level cruise_missiles_used
        if weapons.get("cruise_missiles_used") is True:
            current_weapons.add("cruise_missiles_used")
        new_weapons = current_weapons - seen_weapons
        escalation["new_weapon_first_use"] = bool(new_weapons)
        seen_weapons |= current_weapons

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"{'Wave':>4} | {'Hrs':>5} | {'Cumul':>6} | {'NewCtry':>7} | {'NewWpn':>6}")
    print("-" * 42)
    for wave in data["waves"]:
        t = wave.get("timing", {})
        m = wave.get("munitions", {})
        e = wave.get("escalation", {})
        hrs = t.get("hours_since_last_wave")
        cum = m.get("cumulative_total")
        print(
            f"{wave['wave_number']:>4} | "
            f"{hrs if hrs is not None else '':>5} | "
            f"{cum if cum is not None else '':>6} | "
            f"{'Y' if e.get('new_country_targeted') else '.':>7} | "
            f"{'Y' if e.get('new_weapon_first_use') else '.':>6}"
        )


if __name__ == "__main__":
    main()
