"""
Centralized normalization lookups for the Iran-Israel War dataset.

Loads reference JSON files and builds alias→canonical_id lookup tables for:
  - Armed forces / actors
  - Iranian weapons
  - Defense systems
  - Interceptor munitions

Usage:
    from normalization import Normalizer
    n = Normalizer()  # loads all reference data
    n.normalize_actor("IRGC Aerospace Force")  # → "irgc_asf"
    n.actor_country("irgc_asf")                # → "Iran"
    n.actor_top_level("IRGC Aerospace Force")  # → "Iran"
    n.normalize_weapon("Shahed-136")           # → "shahed_136"
    n.normalize_defense("Arrow-3")             # → "arrow_3"
    n.normalize_interceptor("Tamir")           # → "tamir"
"""

import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Reference file paths (primary + TP4-specific overrides)
_REF = os.path.join(REPO, 'data', 'reference')
_TP4_REF = os.path.join(REPO, 'data', 'tp4-2026', 'reference')


def _load_json(path):
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return []


def _build_lookup(entries, id_field='id', name_field='name'):
    """Build a case-insensitive alias→id lookup from a list of reference entries.

    Each entry should have an id_field, name_field, and optionally 'aliases' and
    'abbreviation' fields.  All are indexed for case-insensitive lookup.
    """
    lookup = {}
    for entry in entries:
        eid = entry.get(id_field)
        if not eid:
            continue
        # Index by id itself
        lookup[eid.lower()] = eid
        # Index by name
        name = entry.get(name_field) or entry.get('system_name')
        if name:
            lookup[name.lower()] = eid
        # Index by abbreviation
        abbr = entry.get('abbreviation')
        if abbr:
            lookup[abbr.lower()] = eid
        # Index by aliases
        for alias in entry.get('aliases', []):
            if alias:
                lookup[alias.lower()] = eid
        # Index by type_key (weapons)
        type_key = entry.get('type_key')
        if type_key:
            lookup[type_key.lower()] = eid
    return lookup


class Normalizer:
    """Centralized normalization engine backed by reference JSON files."""

    def __init__(self):
        # Armed forces
        self._forces = _load_json(os.path.join(_TP4_REF, 'armed_forces.json')) \
            or _load_json(os.path.join(_REF, 'armed_forces.json'))
        self._force_lookup = _build_lookup(self._forces)
        self._force_by_id = {e['id']: e for e in self._forces if 'id' in e}

        # Iranian weapons
        weapons_tp4 = _load_json(os.path.join(_TP4_REF, 'iranian_weapons.json'))
        weapons_base = _load_json(os.path.join(_REF, 'iranian_weapons.json'))
        # Merge: TP4 entries override base by id
        weapons_map = {e['id']: e for e in weapons_base if 'id' in e}
        for e in weapons_tp4:
            if 'id' in e:
                weapons_map[e['id']] = e
        self._weapons = list(weapons_map.values())
        self._weapon_lookup = _build_lookup(self._weapons, name_field='system_name')
        self._weapon_by_id = weapons_map

        # Defense systems
        self._defense = _load_json(os.path.join(_REF, 'defense_systems.json'))
        self._defense_lookup = _build_lookup(self._defense, name_field='system_name')
        self._defense_by_id = {e['id']: e for e in self._defense if 'id' in e}

        # Interceptor munitions
        self._interceptors = _load_json(os.path.join(_REF, 'interceptor_munitions.json'))
        self._interceptor_lookup = _build_lookup(self._interceptors)
        self._interceptor_by_id = {e['id']: e for e in self._interceptors if 'id' in e}

        # Add common aliases that may appear in wave data but aren't in reference
        _extra_force_aliases = {
            'iran': 'irgc',               # Generic "Iran" → treat as IRGC (primary strike force)
            'iranian army': 'artesh',      # Common name for Artesh
            'irgc aerospace': 'irgc_asf',
            'islamic resistance in iraq': 'islamic_resistance_iraq',
        }
        for alias, cid in _extra_force_aliases.items():
            if alias not in self._force_lookup and cid in self._force_by_id:
                self._force_lookup[alias] = cid

        # Precompute actor→top-level-country mapping by walking parent chains
        self._actor_country_cache = {}
        for entry in self._forces:
            eid = entry.get('id')
            if eid:
                self._actor_country_cache[eid] = self._resolve_country(eid)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_country(self, force_id):
        """Walk the parent chain to find the top-level country_name."""
        visited = set()
        current = force_id
        while current and current not in visited:
            visited.add(current)
            entry = self._force_by_id.get(current)
            if not entry:
                break
            country = entry.get('country_name')
            parent = entry.get('parent')
            if not parent:
                return country
            current = parent
        entry = self._force_by_id.get(force_id, {})
        return entry.get('country_name')

    # ------------------------------------------------------------------
    # Public API: normalize strings → canonical IDs
    # ------------------------------------------------------------------

    def normalize_actor(self, name):
        """Normalize an actor/force name to its canonical ID.

        Returns the canonical id (e.g. 'irgc_asf') or None if not found.
        """
        if not name:
            return None
        return self._force_lookup.get(name.lower())

    def normalize_weapon(self, name):
        """Normalize a weapon name to its canonical ID."""
        if not name:
            return None
        return self._weapon_lookup.get(name.lower())

    def normalize_defense(self, name):
        """Normalize a defense system name to its canonical ID."""
        if not name:
            return None
        return self._defense_lookup.get(name.lower())

    def normalize_interceptor(self, name):
        """Normalize an interceptor munition name to its canonical ID."""
        if not name:
            return None
        return self._interceptor_lookup.get(name.lower())

    def actor_branch(self, name):
        """Return the military branch for an actor — critically distinguishes IRGC vs Artesh.

        For Iranian forces, returns: 'irgc', 'artesh', or 'iran' (if generic/unknown).
        For non-Iranian actors, returns their canonical ID (e.g. 'hezbollah', 'houthis').

        This is analytically important for mapping dissent/fracture within Iran's
        military structure — Artesh involvement in strikes is a significant data point.
        """
        if not name:
            return None

        cid = name if name in self._force_by_id else self.normalize_actor(name)
        if not cid:
            # Try top-level actor names
            top = self.actor_top_level(name)
            if top == 'Iran':
                return 'iran'  # generic Iran, branch unknown
            return top.lower().replace(' ', '_') if top else None

        entry = self._force_by_id.get(cid, {})
        country = self._actor_country_cache.get(cid)

        if country != 'Iran':
            return cid  # non-Iranian → return their own ID

        # Walk up to find whether this is IRGC or Artesh branch
        visited = set()
        current = cid
        while current and current not in visited:
            visited.add(current)
            if current in ('irgc', 'artesh'):
                return current
            ent = self._force_by_id.get(current)
            if not ent:
                break
            current = ent.get('parent')

        return 'iran'  # Iranian but couldn't resolve to IRGC or Artesh

    # ------------------------------------------------------------------
    # Public API: resolve metadata from canonical IDs
    # ------------------------------------------------------------------

    def actor_country(self, id_or_name):
        """Return the top-level country name for a force (walking parent chain).

        Accepts either a canonical ID or a raw name (will normalize first).
        """
        cid = id_or_name if id_or_name in self._force_by_id else self.normalize_actor(id_or_name)
        if cid:
            return self._actor_country_cache.get(cid)
        return None

    def actor_top_level(self, name):
        """Map any actor/subunit name to a top-level state-level actor.

        This is the key function for salvo sequencing — it groups all Iranian
        subunits (IRGC, IRGC-ASF, Artesh, etc.) under 'Iran', while keeping
        non-state actors (Hezbollah, Ansar Allah) as their own top-level.

        Returns: 'Iran', 'Hezbollah', 'Ansar Allah (Houthis)', etc., or the
        original name if not found.
        """
        if not name:
            return 'Unknown'

        # Direct top-level actor names used in the attacking_force field
        TOP_LEVEL_ACTORS = {
            'iran': 'Iran',
            'hezbollah': 'Hezbollah',
            'ansar allah (houthis)': 'Ansar Allah (Houthis)',
            'islamic resistance in iraq': 'Islamic Resistance in Iraq',
        }
        match = TOP_LEVEL_ACTORS.get(name.lower())
        if match:
            return match

        # Try resolving through reference data
        country = self.actor_country(name)
        if country:
            return country

        return name

    def force_entry(self, id_or_name):
        """Return the full reference entry for a force."""
        cid = id_or_name if id_or_name in self._force_by_id else self.normalize_actor(id_or_name)
        return self._force_by_id.get(cid)

    def weapon_entry(self, id_or_name):
        """Return the full reference entry for a weapon."""
        cid = id_or_name if id_or_name in self._weapon_by_id else self.normalize_weapon(id_or_name)
        return self._weapon_by_id.get(cid)

    def defense_entry(self, id_or_name):
        """Return the full reference entry for a defense system."""
        cid = id_or_name if id_or_name in self._defense_by_id else self.normalize_defense(id_or_name)
        return self._defense_by_id.get(cid)

    def interceptor_entry(self, id_or_name):
        """Return the full reference entry for an interceptor munition."""
        cid = id_or_name if id_or_name in self._interceptor_by_id else self.normalize_interceptor(id_or_name)
        return self._interceptor_by_id.get(cid)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def stats(self):
        """Return a summary of loaded reference data."""
        return {
            'armed_forces': len(self._forces),
            'weapons': len(self._weapons),
            'defense_systems': len(self._defense),
            'interceptors': len(self._interceptors),
            'force_aliases': len(self._force_lookup),
            'weapon_aliases': len(self._weapon_lookup),
            'defense_aliases': len(self._defense_lookup),
            'interceptor_aliases': len(self._interceptor_lookup),
        }
