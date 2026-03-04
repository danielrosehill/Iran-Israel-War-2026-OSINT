"""
Enrich waves.json with ballistic missile categories and Israeli location targeting.

Reads/writes JSON paths:
  - weapons.categories.bm_liquid_fueled
  - weapons.categories.bm_solid_fueled
  - weapons.categories.bm_marv_equipped
  - weapons.categories.bm_hypersonic
  - targets.israeli_locations.targeted_tel_aviv
  - targets.israeli_locations.targeted_jerusalem
  - targets.israeli_locations.targeted_haifa
  - targets.israeli_locations.targeted_negev_beersheba
  - targets.israeli_locations.targeted_northern_periphery
  - targets.israeli_locations.targeted_eilat
"""

import json
from pathlib import Path


def text_match(text: str, patterns: list[str]) -> bool:
    """Case-insensitive check if any pattern appears in text."""
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in patterns)


def classify_wave(wave: dict) -> None:
    """Classify missile categories and location targeting in place."""
    weapons = wave.setdefault("weapons", {})
    types = weapons.get("types", {})
    categories = weapons.setdefault("categories", {})
    targets = wave.setdefault("targets", {})
    locations = targets.setdefault("israeli_locations", {})

    # --- Missile categories ---
    emad = types.get("emad_used") is True
    ghadr = types.get("ghadr_used") is True
    sejjil = types.get("sejjil_used") is True
    kheibar = types.get("kheibar_shekan_used") is True
    fattah = types.get("fattah_used") is True

    categories["bm_liquid_fueled"] = emad or ghadr
    categories["bm_solid_fueled"] = sejjil or kheibar or fattah
    categories["bm_marv_equipped"] = kheibar or fattah
    categories["bm_hypersonic"] = fattah

    # --- Israeli location targeting ---
    combined = " | ".join(filter(None, [
        targets.get("targets"),
        wave.get("impact", {}).get("damage"),
        wave.get("impact", {}).get("sirens_locations"),
        wave.get("description"),
    ]))

    israel_targeted = targets.get("israel_targeted") is True

    locations["targeted_tel_aviv"] = israel_targeted and text_match(
        combined, ["Tel Aviv", "HaKirya", "Bnei Brak", "Petah Tikva", "Tel Nof",
                    "Beit Shams", "Ishtod", "Beit Hakfa", "Central Israel"]
    )
    locations["targeted_jerusalem"] = israel_targeted and text_match(
        combined, ["Jerusalem", "East Jerusalem", "West Jerusalem"]
    )
    locations["targeted_haifa"] = israel_targeted and text_match(
        combined, ["Haifa"]
    )
    locations["targeted_negev_beersheba"] = israel_targeted and text_match(
        combined, ["Negev", "Beersheba", "Nevatim", "Southern Israel"]
    )
    locations["targeted_northern_periphery"] = israel_targeted and text_match(
        combined, ["Galilee", "Ramat David", "Northern Israel", "northern parts of occupied"]
    )
    locations["targeted_eilat"] = israel_targeted and text_match(
        combined, ["Eilat"]
    )


def main():
    data_dir = Path(__file__).parent.parent / "data"
    json_path = data_dir / "waves.json"

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    for wave in data["waves"]:
        classify_wave(wave)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"{'Wave':>4} | {'Liq':>3} | {'Sol':>3} | {'MaRV':>4} | {'Hyp':>3} | {'TLV':>3} | {'JLM':>3} | {'HFA':>3} | {'NGV':>3} | {'Nth':>3} | {'ELT':>3}")
    print("-" * 72)
    for wave in data["waves"]:
        c = wave.get("weapons", {}).get("categories", {})
        l = wave.get("targets", {}).get("israeli_locations", {})
        print(
            f"{wave['wave_number']:>4} | "
            f"{'Y' if c.get('bm_liquid_fueled') else '.':>3} | "
            f"{'Y' if c.get('bm_solid_fueled') else '.':>3} | "
            f"{'Y' if c.get('bm_marv_equipped') else '.':>4} | "
            f"{'Y' if c.get('bm_hypersonic') else '.':>3} | "
            f"{'Y' if l.get('targeted_tel_aviv') else '.':>3} | "
            f"{'Y' if l.get('targeted_jerusalem') else '.':>3} | "
            f"{'Y' if l.get('targeted_haifa') else '.':>3} | "
            f"{'Y' if l.get('targeted_negev_beersheba') else '.':>3} | "
            f"{'Y' if l.get('targeted_northern_periphery') else '.':>3} | "
            f"{'Y' if l.get('targeted_eilat') else '.':>3}"
        )


if __name__ == "__main__":
    main()
