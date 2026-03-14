#!/usr/bin/env python3
"""
Export Iran-Israel War dataset to Neo4j graph database.

Graph model:
  Nodes:
    - War               (the conflict itself)
    - Round             (phases — neutral term; Iranian TP designations stored as properties)
    - Salvo             (individual attack incidents)
    - Side              ("Israel / Coalition", "Iran / Axis of Resistance")
    - Actor             (top-level forces: IDF, IRGC, Artesh, Hezbollah, US Navy, etc.)
    - Weapon            (Emad, Shahed-136, Ghadr, etc.)
    - DefenseSystem     (Arrow-3, Iron Dome, THAAD, etc.)
    - Target            (named locations — Nevatim, Tel Aviv, Camp Arifjan, etc.)
    - Country           (IL, US, IR, etc.)
    - Entity            (all 210 countries/multilaterals with reaction stances)
    - ReactionStance    (9 stance categories from neutral to active participant)

  Relationships:
    - (Round)-[:PHASE_OF]->(War)
    - (Salvo)-[:PART_OF]->(Round)
    - (Side)-[:BELLIGERENT_IN]->(War)
    - (Actor)-[:MEMBER_OF]->(Side)
    - (Actor)-[:SUBORDINATE_TO]->(Actor)     # IRGC-ASF → IRGC, IAF → IDF
    - (Actor)-[:BASED_IN]->(Country)
    - (Salvo)-[:LAUNCHED_BY]->(Actor)
    - (Salvo)-[:USED_WEAPON]->(Weapon)
    - (Salvo)-[:TARGETED]->(Target)
    - (Salvo)-[:INTERCEPTED_BY]->(DefenseSystem)
    - (Salvo)-[:COORDINATED_WITH]->(Salvo)
    - (Salvo)-[:LANDED_IN]->(Country)
    - (Entity)-[:REACTED_WITH]->(ReactionStance)  # per-round reaction

Usage:
    python build_neo4j.py [--clear]

Requires NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD environment variables.
"""

import json
import os
import sys
import argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env
env_path = os.path.join(REPO, '.env')
if os.path.isfile(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalization import Normalizer
from wave_enrichment import get_wave_uid, COUNTRY_NAMES

WAVE_FILES = [
    ('tp1', os.path.join(REPO, 'data', 'tp1-2024', 'waves.json')),
    ('tp2', os.path.join(REPO, 'data', 'tp2-2024', 'waves.json')),
    ('tp3', os.path.join(REPO, 'data', 'tp3-2025', 'waves.json')),
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'waves.json')),
]

REACTION_FILES = [
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'international_reactions.json')),
]

# Neutral round names — Iranian TP designations stored as properties, not primary labels
ROUND_META = {
    'tp1': {'round_number': 1, 'label': 'Round 1', 'iranian_designation': 'True Promise 1',
            'date_start': '2024-04-13', 'date_end': '2024-04-14'},
    'tp2': {'round_number': 2, 'label': 'Round 2', 'iranian_designation': 'True Promise 2',
            'date_start': '2024-10-01', 'date_end': '2024-10-01'},
    'tp3': {'round_number': 3, 'label': 'Round 3', 'iranian_designation': 'True Promise 3',
            'date_start': '2025-06-13', 'date_end': '2025-06-24'},
    'tp4': {'round_number': 4, 'label': 'Round 4', 'iranian_designation': 'True Promise 4',
            'date_start': '2026-02-28', 'date_end': None},
}

norm = Normalizer()


def _flatten(val):
    """Ensure a value is Neo4j-safe (no dicts/nested objects)."""
    if isinstance(val, dict):
        return json.dumps(val)
    return val


def connect():
    uri = os.environ.get('NEO4J_URI')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    pw = os.environ.get('NEO4J_PASSWORD')
    if not uri or not pw:
        print("ERROR: Set NEO4J_URI and NEO4J_PASSWORD (in .env or environment)")
        sys.exit(1)
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    driver.verify_connectivity()
    print(f"Connected to {uri}")
    return driver


def clear_database(session):
    session.run("MATCH (n) DETACH DELETE n")
    print("  Cleared all existing data")


def create_constraints(session):
    constraints = [
        ("War", "id"), ("Round", "id"), ("Salvo", "uid"), ("Side", "id"),
        ("Actor", "id"), ("Weapon", "id"), ("DefenseSystem", "id"),
        ("Target", "name"), ("Country", "code"), ("Entity", "code"),
        ("ReactionStance", "id"),
    ]
    for label, prop in constraints:
        try:
            session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE")
        except Exception:
            pass
    print("  Constraints created")


# ══════════════════════════════════════════════════════════════════════
# Phase 1: War, Sides, Rounds
# ══════════════════════════════════════════════════════════════════════

def load_war_and_sides(session):
    """Create the War node and the two Sides, linked by BELLIGERENT_IN."""
    session.run(
        "MERGE (w:War {id: 'iran_israel_war'}) "
        "SET w.name = 'Iran-Israel War', w.start_date = '2024-04-13'"
    )
    for side_id, side_name in [
        ('coalition', 'Israel / Coalition'),
        ('axis', 'Iran / Axis of Resistance'),
    ]:
        session.run(
            "MERGE (s:Side {id: $id}) SET s.name = $name",
            id=side_id, name=side_name
        )
        session.run(
            "MATCH (s:Side {id: $id}), (w:War {id: 'iran_israel_war'}) "
            "MERGE (s)-[:BELLIGERENT_IN]->(w)",
            id=side_id
        )
    print("  War + Sides created")


def load_rounds(session):
    """Create Round nodes (neutral naming) linked to the War."""
    for op_id, path in WAVE_FILES:
        meta = ROUND_META[op_id]
        # Also load incident_count from the JSON
        with open(path) as f:
            data_meta = json.load(f)['metadata']

        session.run(
            "MERGE (r:Round {id: $id}) "
            "SET r.round_number = $rn, r.label = $label, "
            "r.iranian_designation = $ird, r.iranian_designation_farsi = $irdf, "
            "r.date_start = $ds, r.date_end = $de, r.incident_count = $ic",
            id=op_id, rn=meta['round_number'], label=meta['label'],
            ird=meta['iranian_designation'],
            irdf=data_meta.get('operation_name_farsi'),
            ds=meta['date_start'], de=meta.get('date_end'),
            ic=data_meta.get('incident_count')
        )
        session.run(
            "MATCH (r:Round {id: $id}), (w:War {id: 'iran_israel_war'}) "
            "MERGE (r)-[:PHASE_OF]->(w)",
            id=op_id
        )
    print("  Rounds created")


# ══════════════════════════════════════════════════════════════════════
# Phase 2: Reference data — Countries, Actors, Weapons, Defense
# ══════════════════════════════════════════════════════════════════════

SIDE_MAPPING = {
    'Israel / Coalition': 'coalition',
    'Iran / Axis of Resistance': 'axis',
}


def load_countries(session):
    """Create Country nodes for all countries in COUNTRY_NAMES + key extras."""
    all_countries = dict(COUNTRY_NAMES)
    all_countries.update({
        'IR': 'Iran', 'LB': 'Lebanon', 'YE': 'Yemen',
        'US': 'United States', 'GB': 'United Kingdom',
        'FR': 'France', 'GR': 'Greece',
    })
    for code, name in all_countries.items():
        session.run("MERGE (c:Country {code: $code}) SET c.name = $name", code=code, name=name)
    print(f"  {len(all_countries)} countries loaded")


def load_actors(session):
    """Create Actor nodes from armed_forces reference with MEMBER_OF → Side and SUBORDINATE_TO hierarchy."""
    for entry in norm._forces:
        eid = entry.get('id')
        if not eid:
            continue

        session.run(
            "MERGE (a:Actor {id: $id}) "
            "SET a.name = $name, a.abbreviation = $abbr, a.country_code = $cc, "
            "a.side = $side, a.type = $type",
            id=eid, name=entry.get('name'), abbr=entry.get('abbreviation'),
            cc=entry.get('country_code'), side=entry.get('side'),
            type=entry.get('type')
        )

        # BASED_IN → Country
        cc = entry.get('country_code')
        if cc:
            session.run(
                "MATCH (a:Actor {id: $id}), (c:Country {code: $cc}) MERGE (a)-[:BASED_IN]->(c)",
                id=eid, cc=cc
            )

        # SUBORDINATE_TO → parent actor
        parent = entry.get('parent')
        if parent and parent in norm._force_by_id:
            session.run(
                "MATCH (child:Actor {id: $child}), (parent:Actor {id: $parent}) "
                "MERGE (child)-[:SUBORDINATE_TO]->(parent)",
                child=eid, parent=parent
            )

        # MEMBER_OF → Side (only for top-level actors without parents)
        if not parent:
            side_key = SIDE_MAPPING.get(entry.get('side'))
            if side_key:
                session.run(
                    "MATCH (a:Actor {id: $id}), (s:Side {id: $sid}) MERGE (a)-[:MEMBER_OF]->(s)",
                    id=eid, sid=side_key
                )

    print(f"  {len(norm._forces)} actors loaded")


def load_weapons(session):
    for entry in norm._weapons:
        eid = entry.get('id')
        if not eid:
            continue
        session.run(
            "MERGE (w:Weapon {id: $id}) "
            "SET w.name = $name, w.classification = $cls, w.propulsion = $prop, "
            "w.guidance = $guide, w.marv = $marv, w.range_km = $range",
            id=eid, name=entry.get('system_name'), cls=entry.get('classification'),
            prop=entry.get('propulsion'), guide=_flatten(entry.get('guidance')),
            marv=_flatten(entry.get('marv')), range=_flatten(entry.get('range_km'))
        )
    print(f"  {len(norm._weapons)} weapons loaded")


def load_defense_systems(session):
    for entry in norm._defense:
        eid = entry.get('id')
        if not eid:
            continue
        session.run(
            "MERGE (d:DefenseSystem {id: $id}) "
            "SET d.name = $name, d.classification = $cls, d.operator = $op, "
            "d.intercept_phase = $phase",
            id=eid, name=entry.get('system_name'), cls=entry.get('classification'),
            op=entry.get('operator'), phase=entry.get('intercept_phase')
        )
    print(f"  {len(norm._defense)} defense systems loaded")


# ══════════════════════════════════════════════════════════════════════
# Phase 3: Salvos + incident relationships
# ══════════════════════════════════════════════════════════════════════

def load_salvos(session):
    salvo_count = 0
    for op_id, path in WAVE_FILES:
        with open(path) as f:
            data = json.load(f)

        for w in data['incidents']:
            op = w.get('operation', op_id)
            wn = w['wave_number']
            uid = get_wave_uid(op, wn)
            timing = w.get('timing', {})
            weapons = w.get('weapons', {})
            munitions = w.get('munitions', {})
            impact = w.get('impact', {})
            interception = w.get('interception', {})

            session.run(
                "MERGE (s:Salvo {uid: $uid}) "
                "SET s.round = $op, s.salvo_number = $wn, "
                "s.codename_english = $ce, s.codename_farsi = $cf, "
                "s.description = $desc, "
                "s.launch_time_utc = $lt, s.launch_time_israel = $lti, "
                "s.conflict_day = $cd, "
                "s.payload = $payload, "
                "s.drones_used = $du, s.ballistic_missiles_used = $bmu, "
                "s.cruise_missiles_used = $cmu, "
                "s.estimated_munitions = $em, "
                "s.fatalities = $fat, s.injuries = $inj, "
                "s.damage = $dmg, "
                "s.intercept_rate = $ir, s.intercept_count = $ic",
                uid=uid, op=op, wn=wn,
                ce=w.get('wave_codename_english'), cf=w.get('wave_codename_farsi'),
                desc=w.get('description'),
                lt=timing.get('probable_launch_time'),
                lti=timing.get('launch_time_israel'),
                cd=timing.get('conflict_day'),
                payload=weapons.get('payload'),
                du=weapons.get('drones_used'), bmu=weapons.get('ballistic_missiles_used'),
                cmu=weapons.get('cruise_missiles_used'),
                em=munitions.get('estimated_munitions_count'),
                fat=impact.get('fatalities'), inj=impact.get('injuries'),
                dmg=impact.get('damage'),
                ir=interception.get('estimated_intercept_rate'),
                ic=interception.get('estimated_intercept_count'),
            )

            # PART_OF → Round
            session.run(
                "MATCH (s:Salvo {uid: $uid}), (r:Round {id: $op}) MERGE (s)-[:PART_OF]->(r)",
                uid=uid, op=op
            )

            # LAUNCHED_BY → Actor(s)
            af_list = w.get('attacking_force', [])
            if isinstance(af_list, dict):
                af_list = [af_list]
            for af in af_list:
                actor_raw = af.get('actor', '')
                actor_id = norm.normalize_actor(actor_raw)
                branch = norm.actor_branch(actor_raw)
                if actor_id:
                    session.run(
                        "MATCH (s:Salvo {uid: $uid}), (a:Actor {id: $aid}) "
                        "MERGE (s)-[r:LAUNCHED_BY]->(a) "
                        "SET r.subunit = $sub, r.branch = $branch",
                        uid=uid, aid=actor_id,
                        sub=af.get('subunit'), branch=branch
                    )

            # USED_WEAPON
            wt = weapons.get('types', {})
            for key, used in wt.items():
                if used and key.endswith('_used'):
                    weapon_id = norm.normalize_weapon(key[:-5])
                    if weapon_id:
                        session.run(
                            "MATCH (s:Salvo {uid: $uid}), (w:Weapon {id: $wid}) "
                            "MERGE (s)-[:USED_WEAPON]->(w)",
                            uid=uid, wid=weapon_id
                        )

            # INTERCEPTED_BY → DefenseSystem
            for sys_name in interception.get('interception_systems', []):
                sys_id = norm.normalize_defense(sys_name)
                if sys_id:
                    session.run(
                        "MATCH (s:Salvo {uid: $uid}), (d:DefenseSystem {id: $did}) "
                        "MERGE (s)-[:INTERCEPTED_BY]->(d)",
                        uid=uid, did=sys_id
                    )

            # LANDED_IN → Country
            for cc in w.get('targets', {}).get('landings_countries', []):
                session.run(
                    "MATCH (s:Salvo {uid: $uid}) "
                    "MERGE (c:Country {code: $cc}) "
                    "MERGE (s)-[:LANDED_IN]->(c)",
                    uid=uid, cc=cc
                )

            # TARGETED → Target locations
            for tl in w.get('targets', {}).get('target_locations', []):
                tname = tl.get('name')
                if tname:
                    session.run(
                        "MATCH (s:Salvo {uid: $uid}) "
                        "MERGE (t:Target {name: $name}) "
                        "ON CREATE SET t.type = $type "
                        "MERGE (s)-[r:TARGETED]->(t) "
                        "SET r.hit = $hit",
                        uid=uid, name=tname, type=tl.get('type', 'unknown'),
                        hit=tl.get('hit')
                    )

            salvo_count += 1

    print(f"  {salvo_count} salvos loaded")


# ══════════════════════════════════════════════════════════════════════
# Phase 4: International reactions
# ══════════════════════════════════════════════════════════════════════

def load_reaction_stances(session):
    """Load the 9 reaction stance categories."""
    path = os.path.join(REPO, 'data', 'reference', 'reaction_types.json')
    if not os.path.isfile(path):
        print("  No reaction_types.json found, skipping")
        return
    with open(path) as f:
        stances = json.load(f)
    for s in stances:
        session.run(
            "MERGE (rs:ReactionStance {id: $id}) "
            "SET rs.label = $label, rs.description = $desc, rs.spectrum_score = $score",
            id=s['id'], label=s.get('label'), desc=s.get('description'),
            score=s.get('spectrum_score')
        )
    print(f"  {len(stances)} reaction stances loaded")


def load_international_reactions(session):
    """Load entities and their reactions per round."""
    entity_count = 0
    reaction_count = 0

    for op_id, path in REACTION_FILES:
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            data = json.load(f)

        for rxn in data.get('reactions', []):
            code = rxn.get('iso_3166_1_alpha2')
            if not code:
                continue

            # Entity node (country or multilateral)
            session.run(
                "MERGE (e:Entity {code: $code}) "
                "SET e.name = $name, e.type = $type, "
                "e.eu_member_state = $eu, e.combatant = $comb",
                code=code, name=rxn.get('entity_name'),
                type=rxn.get('entity_type'),
                eu=rxn.get('eu_member_state', False),
                comb=rxn.get('combatant', False)
            )
            entity_count += 1

            # Also merge as Country if it's a state
            if rxn.get('entity_type') == 'state':
                session.run(
                    "MERGE (c:Country {code: $code}) SET c.name = $name",
                    code=code, name=rxn.get('entity_name')
                )

            # REACTED_WITH → ReactionStance (per round)
            stance = rxn.get('overall_stance')
            if stance:
                session.run(
                    "MATCH (e:Entity {code: $code}), (rs:ReactionStance {id: $sid}) "
                    "MERGE (e)-[r:REACTED_WITH]->(rs) "
                    "SET r.round = $round, r.notes = $notes",
                    code=code, sid=stance, round=op_id,
                    notes=rxn.get('notes')
                )
                reaction_count += 1

            # Statement relationships (head_of_state, foreign_ministry, etc.)
            for stmt_type in ('head_of_state_statement', 'head_of_government_statement',
                              'foreign_ministry_statement'):
                stmt = rxn.get(stmt_type, {})
                if stmt and stmt.get('made'):
                    session.run(
                        "MATCH (e:Entity {code: $code}), (rd:Round {id: $round}) "
                        "MERGE (e)-[r:ISSUED_STATEMENT]->(rd) "
                        "SET r.type = $stype, r.speaker = $speaker, "
                        "r.speaker_title = $title, r.summary = $summary, "
                        "r.category = $cat, r.date = $date",
                        code=code, round=op_id,
                        stype=stmt_type.replace('_statement', ''),
                        speaker=stmt.get('speaker'), title=stmt.get('speaker_title'),
                        summary=stmt.get('summary'), cat=stmt.get('category'),
                        date=stmt.get('date')
                    )

    print(f"  {entity_count} entities, {reaction_count} reactions loaded")


# ══════════════════════════════════════════════════════════════════════
# Phase 5: Coordination edges
# ══════════════════════════════════════════════════════════════════════

def create_coordination_edges(session):
    """COORDINATED_WITH between salvos by different actors ≤15 min apart."""
    from datetime import datetime
    result = session.run("""
        MATCH (s1:Salvo), (s2:Salvo)
        WHERE s1.round = s2.round AND s1.uid < s2.uid
          AND s1.launch_time_utc IS NOT NULL AND s2.launch_time_utc IS NOT NULL
        RETURN s1.uid AS uid1, s2.uid AS uid2,
               s1.launch_time_utc AS t1, s2.launch_time_utc AS t2
    """)

    coord_count = 0
    for record in result:
        try:
            t1 = datetime.fromisoformat(record['t1'].replace('Z', '+00:00'))
            t2 = datetime.fromisoformat(record['t2'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            continue
        if abs((t1 - t2).total_seconds()) / 60.0 > 15:
            continue
        r1 = session.run(
            "MATCH (s:Salvo {uid: $uid})-[:LAUNCHED_BY]->(a) RETURN a.id AS aid", uid=record['uid1']
        ).single()
        r2 = session.run(
            "MATCH (s:Salvo {uid: $uid})-[:LAUNCHED_BY]->(a) RETURN a.id AS aid", uid=record['uid2']
        ).single()
        if r1 and r2 and norm.actor_top_level(r1['aid'] or '') != norm.actor_top_level(r2['aid'] or ''):
            session.run(
                "MATCH (s1:Salvo {uid: $u1}), (s2:Salvo {uid: $u2}) "
                "MERGE (s1)-[:COORDINATED_WITH]->(s2)",
                u1=record['uid1'], u2=record['uid2']
            )
            coord_count += 1

    print(f"  {coord_count} coordination edges created")


# ══════════════════════════════════════════════════════════════════════
# Stats & Main
# ══════════════════════════════════════════════════════════════════════

def print_stats(session):
    result = session.run(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC"
    )
    print("\n=== Graph Statistics ===")
    total_nodes = 0
    for r in result:
        print(f"  {r['label']:20s} {r['cnt']:>4d} nodes")
        total_nodes += r['cnt']

    rel_result = session.run(
        "MATCH ()-[r]->() RETURN type(r) AS rel, count(r) AS cnt ORDER BY cnt DESC"
    )
    total_rels = 0
    for r in rel_result:
        print(f"  {r['rel']:20s} {r['cnt']:>4d} relationships")
        total_rels += r['cnt']

    print(f"\n  Total: {total_nodes} nodes, {total_rels} relationships")


def main():
    parser = argparse.ArgumentParser(description='Export dataset to Neo4j')
    parser.add_argument('--clear', action='store_true', help='Clear existing data first')
    args = parser.parse_args()

    driver = connect()

    with driver.session() as session:
        if args.clear:
            clear_database(session)

        print("Creating constraints...")
        create_constraints(session)

        print("Phase 1: War structure...")
        load_war_and_sides(session)
        load_rounds(session)

        print("Phase 2: Reference data...")
        load_countries(session)
        load_actors(session)
        load_weapons(session)
        load_defense_systems(session)

        print("Phase 3: Salvos...")
        load_salvos(session)

        print("Phase 4: International reactions...")
        load_reaction_stances(session)
        load_international_reactions(session)

        print("Phase 5: Coordination edges...")
        create_coordination_edges(session)

        print_stats(session)

    driver.close()
    print("\nDone.")


if __name__ == '__main__':
    main()
