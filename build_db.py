#!/usr/bin/env python3
"""
Build SQLite database from all JSON data files.

Usage:
    python build_db.py

Outputs:
    data/iran_israel_war.db
"""

import json
import sqlite3
import os

REPO = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(REPO, 'data', 'iran_israel_war.db')

WAVE_FILES = [
    ('tp1', os.path.join(REPO, 'data', 'tp1-2024', 'waves.json')),
    ('tp2', os.path.join(REPO, 'data', 'tp2-2024', 'waves.json')),
    ('tp3', os.path.join(REPO, 'data', 'tp3-2025', 'waves.json')),
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'waves.json')),
]

REF_FILES = {
    'iranian_weapons': os.path.join(REPO, 'data', 'reference', 'iranian_weapons.json'),
    'defense_systems': os.path.join(REPO, 'data', 'reference', 'defense_systems.json'),
    'armed_forces': os.path.join(REPO, 'data', 'reference', 'armed_forces.json'),
    'us_bases': os.path.join(REPO, 'data', 'reference', 'us_bases.json'),
    'us_naval_vessels': os.path.join(REPO, 'data', 'reference', 'us_naval_vessels.json'),
}


def create_schema(cur):
    cur.executescript("""
    -- ══════════════════════════════════════════════════════════════
    -- Operations metadata
    -- ══════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS operations (
        operation         TEXT PRIMARY KEY,  -- tp1, tp2, tp3, tp4
        operation_name    TEXT,
        operation_name_farsi TEXT,
        version           TEXT,
        wave_count        INTEGER,
        date_start        TEXT,
        date_end          TEXT,
        data_quality      TEXT,
        conflict_name     TEXT,
        -- Aggregate stats (stored as-is from metadata)
        total_ballistic_missiles TEXT,
        total_cruise_missiles    TEXT,
        total_drones             TEXT,
        total_munitions_estimate TEXT,
        interception_rate_claimed REAL,
        total_killed             TEXT,
        total_wounded            TEXT,
        trigger_event            TEXT,
        historical_significance  TEXT
    );

    -- ══════════════════════════════════════════════════════════════
    -- Main waves table (one row per wave, flattened)
    -- ══════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS waves (
        -- Identity
        operation               TEXT NOT NULL,
        wave_number             INTEGER NOT NULL,
        wave_codename_farsi     TEXT,
        wave_codename_english   TEXT,
        description             TEXT,

        -- Timing
        announced_utc           TEXT,
        announcement_source     TEXT,
        announcement_x_url      TEXT,
        probable_launch_time    TEXT,
        launch_time_israel      TEXT,
        launch_time_iran        TEXT,
        solar_phase_launch_site INTEGER,
        solar_phase_target      INTEGER,
        conflict_day            INTEGER,
        hours_since_last_wave   REAL,
        time_between_waves_min  REAL,
        wave_duration_min       REAL,

        -- Weapons (booleans + payload text)
        payload                 TEXT,
        drones_used             INTEGER,  -- 0/1/NULL
        ballistic_missiles_used INTEGER,
        cruise_missiles_used    INTEGER,

        -- Weapon types (boolean flags)
        emad_used               INTEGER,
        ghadr_used              INTEGER,
        sejjil_used             INTEGER,
        kheibar_shekan_used     INTEGER,
        fattah_used             INTEGER,
        shahed_136_used         INTEGER,
        shahed_238_used         INTEGER,
        shahed_131_used         INTEGER,
        shahed_107_used         INTEGER,
        shahed_129_used         INTEGER,
        mohajer_6_used          INTEGER,
        shahab_3_used           INTEGER,
        paveh_used              INTEGER,

        -- Weapon categories
        bm_liquid_fueled        INTEGER,
        bm_solid_fueled         INTEGER,
        bm_marv_equipped        INTEGER,
        bm_hypersonic           INTEGER,

        -- Targets
        israel_targeted         INTEGER,
        us_bases_targeted       INTEGER,
        targets_description     TEXT,
        targeted_tel_aviv       INTEGER,
        targeted_jerusalem      INTEGER,
        targeted_haifa          INTEGER,
        targeted_negev_beersheba INTEGER,
        targeted_northern_periphery INTEGER,
        targeted_eilat          INTEGER,
        target_lat              REAL,
        target_lon              REAL,

        -- Launch site
        launch_site_description TEXT,
        launch_site_lat         REAL,
        launch_site_lon         REAL,

        -- Interception
        intercepted             INTEGER,
        estimated_intercept_count INTEGER,
        estimated_intercept_rate REAL,
        exoatmospheric_interception INTEGER,
        endoatmospheric_interception INTEGER,
        interception_report     TEXT,
        intercepted_by_israel   INTEGER,
        intercepted_by_us       INTEGER,
        intercepted_by_uk       INTEGER,
        intercepted_by_jordan   INTEGER,

        -- Munitions
        estimated_munitions_count INTEGER,
        munitions_targeting_israel INTEGER,
        munitions_targeting_us_bases INTEGER,
        cumulative_total        INTEGER,

        -- Impact
        damage                  TEXT,
        fatalities              INTEGER,
        injuries                INTEGER,
        civilian_casualties     INTEGER,
        military_casualties     INTEGER,

        -- Escalation
        new_country_targeted    INTEGER,
        new_weapon_first_use    INTEGER,

        -- Proxy
        proxy_involvement       INTEGER,
        proxy_description       TEXT,

        -- Sources
        idf_statement           TEXT,

        PRIMARY KEY (operation, wave_number),
        FOREIGN KEY (operation) REFERENCES operations(operation)
    );

    -- ══════════════════════════════════════════════════════════════
    -- Junction tables for many-to-many relationships
    -- ══════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS wave_landing_countries (
        operation       TEXT NOT NULL,
        wave_number     INTEGER NOT NULL,
        country_code    TEXT NOT NULL,
        PRIMARY KEY (operation, wave_number, country_code),
        FOREIGN KEY (operation, wave_number) REFERENCES waves(operation, wave_number)
    );

    CREATE TABLE IF NOT EXISTS wave_interception_systems (
        operation       TEXT NOT NULL,
        wave_number     INTEGER NOT NULL,
        system_name     TEXT NOT NULL,
        PRIMARY KEY (operation, wave_number, system_name),
        FOREIGN KEY (operation, wave_number) REFERENCES waves(operation, wave_number)
    );

    CREATE TABLE IF NOT EXISTS wave_intercepted_by_other (
        operation       TEXT NOT NULL,
        wave_number     INTEGER NOT NULL,
        country         TEXT NOT NULL,
        PRIMARY KEY (operation, wave_number, country),
        FOREIGN KEY (operation, wave_number) REFERENCES waves(operation, wave_number)
    );

    CREATE TABLE IF NOT EXISTS wave_us_bases_targeted (
        operation       TEXT NOT NULL,
        wave_number     INTEGER NOT NULL,
        base_name       TEXT NOT NULL,
        country_code    TEXT,
        PRIMARY KEY (operation, wave_number, base_name),
        FOREIGN KEY (operation, wave_number) REFERENCES waves(operation, wave_number)
    );

    CREATE TABLE IF NOT EXISTS wave_us_naval_vessels_targeted (
        operation       TEXT NOT NULL,
        wave_number     INTEGER NOT NULL,
        vessel_name     TEXT NOT NULL,
        vessel_type     TEXT,
        PRIMARY KEY (operation, wave_number, vessel_name),
        FOREIGN KEY (operation, wave_number) REFERENCES waves(operation, wave_number)
    );

    CREATE TABLE IF NOT EXISTS wave_sources (
        operation       TEXT NOT NULL,
        wave_number     INTEGER NOT NULL,
        url             TEXT NOT NULL,
        PRIMARY KEY (operation, wave_number, url),
        FOREIGN KEY (operation, wave_number) REFERENCES waves(operation, wave_number)
    );

    -- ══════════════════════════════════════════════════════════════
    -- Reference tables
    -- ══════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS iranian_weapons (
        id                  TEXT PRIMARY KEY,
        system_name         TEXT NOT NULL,
        type_key            TEXT,
        classification      TEXT,
        propulsion          TEXT,
        stages              INTEGER,
        range_km            TEXT,   -- can be int or object
        warhead_kg          REAL,
        launch_weight_kg    REAL,
        length_m            REAL,
        diameter_m          REAL,
        guidance            TEXT,
        cep_m               TEXT,
        marv                INTEGER,
        hypersonic          TEXT,   -- can be bool or object
        basing              TEXT,
        first_combat_use    TEXT,
        lineage             TEXT,
        notes               TEXT
    );

    CREATE TABLE IF NOT EXISTS defense_systems (
        id                  TEXT PRIMARY KEY,
        system_name         TEXT NOT NULL,
        operator            TEXT,
        classification      TEXT,
        intercept_phase     TEXT,
        intercept_alt_min_km REAL,
        intercept_alt_max_km REAL,
        range_km            REAL,
        kill_mechanism      TEXT,
        developer           TEXT,
        first_operational   TEXT,
        first_combat_use    TEXT,
        notes               TEXT
    );

    CREATE TABLE IF NOT EXISTS armed_forces (
        id              TEXT PRIMARY KEY,
        name            TEXT NOT NULL,
        abbreviation    TEXT,
        country_code    TEXT,
        country_name    TEXT,
        side            TEXT,
        type            TEXT,
        parent          TEXT,
        notes           TEXT
    );

    CREATE TABLE IF NOT EXISTS armed_forces_aliases (
        force_id    TEXT NOT NULL,
        alias       TEXT NOT NULL,
        PRIMARY KEY (force_id, alias),
        FOREIGN KEY (force_id) REFERENCES armed_forces(id)
    );

    CREATE TABLE IF NOT EXISTS us_bases (
        name            TEXT PRIMARY KEY,
        country_code    TEXT,
        country_name    TEXT,
        branch          TEXT,
        lat             REAL,
        lon             REAL
    );

    CREATE TABLE IF NOT EXISTS us_naval_vessels (
        name        TEXT PRIMARY KEY,
        type        TEXT,
        class       TEXT,
        branch      TEXT,
        fleet       TEXT,
        notes       TEXT
    );

    -- ══════════════════════════════════════════════════════════════
    -- X post snippets (OSINT social media sources)
    -- ══════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS x_post_snippets (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        operation       TEXT NOT NULL,
        wave_number     INTEGER NOT NULL,
        source_type     TEXT NOT NULL DEFAULT 'x_post',
        author          TEXT,
        handle          TEXT,
        post_date       TEXT,
        text            TEXT NOT NULL,
        image_file      TEXT,
        FOREIGN KEY (operation, wave_number) REFERENCES waves(operation, wave_number)
    );
    """)


def bool_to_int(val):
    if val is True:
        return 1
    if val is False:
        return 0
    return None


def load_operations(cur):
    for op_id, path in WAVE_FILES:
        with open(path) as f:
            data = json.load(f)
        meta = data['metadata']
        agg = meta.get('aggregate_stats', {})
        dr = meta.get('date_range', {})
        cur.execute("""
            INSERT OR REPLACE INTO operations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            meta.get('operation', op_id),
            meta.get('operation_name'),
            meta.get('operation_name_farsi'),
            meta.get('version'),
            meta.get('wave_count'),
            dr.get('start'),
            dr.get('end'),
            meta.get('data_quality'),
            meta.get('conflict_name'),
            str(agg.get('total_ballistic_missiles', '')) or None,
            str(agg.get('total_cruise_missiles', '')) or None,
            str(agg.get('total_drones', '')) or None,
            str(agg.get('total_munitions_estimate', '')) or None,
            agg.get('interception_rate_claimed') or agg.get('israeli_interception_rate_claimed'),
            str(agg.get('total_killed', '')) or None,
            str(agg.get('total_wounded', '')) or None,
            agg.get('trigger_event'),
            agg.get('historical_significance'),
        ))


def load_waves(cur):
    for op_id, path in WAVE_FILES:
        with open(path) as f:
            data = json.load(f)

        for w in data['waves']:
            op = w.get('operation', op_id)
            wn = w['wave_number']
            t = w.get('timing', {})
            wp = w.get('weapons', {})
            wt = wp.get('types', {})
            wc = wp.get('categories', {})
            tgt = w.get('targets', {})
            il = tgt.get('israeli_locations', {})
            tc = tgt.get('target_coordinates', {})
            ls = w.get('launch_site', {})
            icp = w.get('interception', {})
            ib = icp.get('intercepted_by', {})
            mun = w.get('munitions', {})
            imp = w.get('impact', {})
            esc = w.get('escalation', {})
            prx = w.get('proxy', {})
            src = w.get('sources', {})

            cur.execute("""
                INSERT OR REPLACE INTO waves VALUES (
                    ?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,
                    ?,?,?,?,?,
                    ?,?,
                    ?,?,
                    ?
                )
            """, (
                op, wn,
                w.get('wave_codename_farsi'),
                w.get('wave_codename_english'),
                w.get('description'),
                # timing
                t.get('announced_utc'),
                t.get('announcement_source'),
                t.get('announcement_x_url'),
                t.get('probable_launch_time'),
                t.get('launch_time_israel'),
                t.get('launch_time_iran'),
                t.get('solar_phase_launch_site'),
                t.get('solar_phase_target'),
                t.get('conflict_day'),
                t.get('hours_since_last_wave'),
                t.get('time_between_waves_minutes'),
                t.get('wave_duration_minutes'),
                # weapons
                wp.get('payload'),
                bool_to_int(wp.get('drones_used')),
                bool_to_int(wp.get('ballistic_missiles_used')),
                bool_to_int(wp.get('cruise_missiles_used')),
                # weapon types
                bool_to_int(wt.get('emad_used')),
                bool_to_int(wt.get('ghadr_used')),
                bool_to_int(wt.get('sejjil_used')),
                bool_to_int(wt.get('kheibar_shekan_used')),
                bool_to_int(wt.get('fattah_used')),
                bool_to_int(wt.get('shahed_136_used')),
                bool_to_int(wt.get('shahed_238_used')),
                bool_to_int(wt.get('shahed_131_used')),
                bool_to_int(wt.get('shahed_107_used')),
                bool_to_int(wt.get('shahed_129_used')),
                bool_to_int(wt.get('mohajer_6_used')),
                bool_to_int(wt.get('shahab_3_used')),
                bool_to_int(wt.get('paveh_used')),
                # categories
                bool_to_int(wc.get('bm_liquid_fueled')),
                bool_to_int(wc.get('bm_solid_fueled')),
                bool_to_int(wc.get('bm_marv_equipped')),
                bool_to_int(wc.get('bm_hypersonic')),
                # targets
                bool_to_int(tgt.get('israel_targeted')),
                bool_to_int(tgt.get('us_bases_targeted')),
                tgt.get('targets'),
                bool_to_int(il.get('targeted_tel_aviv')),
                bool_to_int(il.get('targeted_jerusalem')),
                bool_to_int(il.get('targeted_haifa')),
                bool_to_int(il.get('targeted_negev_beersheba')),
                bool_to_int(il.get('targeted_northern_periphery')),
                bool_to_int(il.get('targeted_eilat')),
                tc.get('lat'),
                tc.get('lon'),
                # launch site
                ls.get('description'),
                ls.get('lat'),
                ls.get('lon'),
                # interception
                bool_to_int(icp.get('intercepted')),
                icp.get('estimated_intercept_count'),
                icp.get('estimated_intercept_rate'),
                bool_to_int(icp.get('exoatmospheric_interception')),
                bool_to_int(icp.get('endoatmospheric_interception')),
                icp.get('interception_report'),
                bool_to_int(ib.get('israel')),
                bool_to_int(ib.get('us')),
                bool_to_int(ib.get('uk')),
                bool_to_int(ib.get('jordan')),
                # munitions
                mun.get('estimated_munitions_count'),
                mun.get('munitions_targeting_israel'),
                mun.get('munitions_targeting_us_bases'),
                mun.get('cumulative_total'),
                # impact
                imp.get('damage'),
                imp.get('fatalities'),
                imp.get('injuries'),
                imp.get('civilian_casualties'),
                imp.get('military_casualties'),
                # escalation
                bool_to_int(esc.get('new_country_targeted')),
                bool_to_int(esc.get('new_weapon_first_use')),
                # proxy
                bool_to_int(prx.get('involvement')),
                prx.get('description'),
                # sources
                src.get('idf_statement'),
            ))

            # Junction: landing countries
            for cc in tgt.get('landings_countries', []):
                cur.execute(
                    "INSERT OR IGNORE INTO wave_landing_countries VALUES (?,?,?)",
                    (op, wn, cc))

            # Junction: interception systems
            for sys in icp.get('interception_systems', []):
                cur.execute(
                    "INSERT OR IGNORE INTO wave_interception_systems VALUES (?,?,?)",
                    (op, wn, sys))

            # Junction: intercepted by other
            for other in ib.get('other', []):
                cur.execute(
                    "INSERT OR IGNORE INTO wave_intercepted_by_other VALUES (?,?,?)",
                    (op, wn, other))

            # Junction: US bases targeted
            for base in tgt.get('us_bases', []):
                cur.execute(
                    "INSERT OR IGNORE INTO wave_us_bases_targeted VALUES (?,?,?,?)",
                    (op, wn, base.get('name', ''), base.get('country_code')))

            # Junction: US naval vessels targeted
            for vessel in tgt.get('us_naval_vessels', []):
                cur.execute(
                    "INSERT OR IGNORE INTO wave_us_naval_vessels_targeted VALUES (?,?,?,?)",
                    (op, wn, vessel.get('name', ''), vessel.get('type')))

            # Junction: source URLs
            for url in src.get('urls', []):
                cur.execute(
                    "INSERT OR IGNORE INTO wave_sources VALUES (?,?,?)",
                    (op, wn, url))


def load_iranian_weapons(cur):
    with open(REF_FILES['iranian_weapons']) as f:
        weapons = json.load(f)
    for w in weapons:
        range_val = w.get('range_km')
        if isinstance(range_val, dict):
            range_val = json.dumps(range_val)
        hyp = w.get('hypersonic')
        if isinstance(hyp, dict):
            hyp = json.dumps(hyp)
        cep = w.get('CEP_m')
        if isinstance(cep, dict):
            cep = json.dumps(cep)
        cur.execute("""
            INSERT OR REPLACE INTO iranian_weapons VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            w['id'], w['system_name'], w.get('type_key'),
            w.get('classification'), w.get('propulsion'),
            w.get('stages'), str(range_val) if range_val else None,
            w.get('warhead_kg'), w.get('launch_weight_kg'),
            w.get('length_m'), w.get('diameter_m'),
            w.get('guidance') if isinstance(w.get('guidance'), str) else json.dumps(w.get('guidance')),
            str(cep) if cep else None,
            bool_to_int(w.get('marv')),
            str(hyp) if hyp else None,
            w.get('basing'),
            w.get('first_combat_use'),
            w.get('lineage'),
            '; '.join(w.get('key_features', [])) or None,
        ))


def load_defense_systems(cur):
    with open(REF_FILES['defense_systems']) as f:
        systems = json.load(f)
    for s in systems:
        alt = s.get('intercept_altitude_km', {})
        cur.execute("""
            INSERT OR REPLACE INTO defense_systems VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            s['id'], s['system_name'], s.get('operator'),
            s.get('classification'), s.get('intercept_phase'),
            alt.get('min') if isinstance(alt, dict) else None,
            alt.get('max') if isinstance(alt, dict) else None,
            s.get('range_km'), s.get('kill_mechanism'),
            s.get('developer'),
            str(s.get('first_operational', '')) or None,
            s.get('first_combat_use'),
            s.get('notes'),
        ))


def load_armed_forces(cur):
    with open(REF_FILES['armed_forces']) as f:
        forces = json.load(f)
    for af in forces:
        cur.execute("""
            INSERT OR REPLACE INTO armed_forces VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            af['id'], af['name'], af.get('abbreviation'),
            af.get('country_code'), af.get('country_name'),
            af.get('side'), af.get('type'),
            af.get('parent'), af.get('notes'),
        ))
        for alias in af.get('aliases', []):
            cur.execute(
                "INSERT OR IGNORE INTO armed_forces_aliases VALUES (?,?)",
                (af['id'], alias))


def load_us_bases(cur):
    with open(REF_FILES['us_bases']) as f:
        bases = json.load(f)
    for b in bases:
        cur.execute("""
            INSERT OR REPLACE INTO us_bases VALUES (?,?,?,?,?,?)
        """, (
            b['name'], b.get('country_code'), b.get('country_name'),
            b.get('branch'), b.get('lat'), b.get('lon'),
        ))


def load_us_naval_vessels(cur):
    with open(REF_FILES['us_naval_vessels']) as f:
        vessels = json.load(f)
    for v in vessels:
        cur.execute("""
            INSERT OR REPLACE INTO us_naval_vessels VALUES (?,?,?,?,?,?)
        """, (
            v['name'], v.get('type'), v.get('class'),
            v.get('branch'), v.get('fleet'), v.get('notes'),
        ))


SNIPPET_FILES = [
    os.path.join(REPO, 'data', 'tp4-2026', 'x_post_snippets.json'),
]


def load_x_post_snippets(cur):
    for path in SNIPPET_FILES:
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        for s in data.get('snippets', []):
            cur.execute("""
                INSERT INTO x_post_snippets
                    (operation, wave_number, source_type, author, handle, post_date, text, image_file)
                VALUES (?,?,?,?,?,?,?,?)
            """, (
                s['operation'], s['wave_number'], 'x_post',
                s.get('author'), s.get('handle'), s.get('date'),
                s['text'], s.get('image_file'),
            ))


def print_summary(cur):
    print("\n=== Database Summary ===")
    for table in ['operations', 'waves', 'wave_landing_countries',
                   'wave_interception_systems', 'wave_us_bases_targeted',
                   'wave_sources', 'iranian_weapons', 'defense_systems',
                   'armed_forces', 'us_bases', 'us_naval_vessels',
                   'x_post_snippets']:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cur.fetchone()[0]} rows")

    print("\n=== Per-Operation Stats ===")
    cur.execute("""
        SELECT
            operation,
            COUNT(*) as waves,
            SUM(CASE WHEN ballistic_missiles_used = 1 THEN 1 ELSE 0 END) as bm_waves,
            SUM(CASE WHEN drones_used = 1 THEN 1 ELSE 0 END) as drone_waves,
            SUM(CASE WHEN cruise_missiles_used = 1 THEN 1 ELSE 0 END) as cm_waves,
            SUM(COALESCE(estimated_munitions_count, 0)) as sum_known_munitions,
            SUM(COALESCE(fatalities, 0)) as sum_fatalities,
            SUM(COALESCE(injuries, 0)) as sum_injuries
        FROM waves
        GROUP BY operation
        ORDER BY operation
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} waves | BM:{row[2]} drone:{row[3]} CM:{row[4]} "
              f"| known_mun:{row[5]} | killed:{row[6]} injured:{row[7]}")

    print("\n=== Weapon System Usage Across All Operations ===")
    weapon_cols = [
        ('emad_used', 'Emad'), ('ghadr_used', 'Ghadr'),
        ('sejjil_used', 'Sejjil'), ('kheibar_shekan_used', 'Kheibar Shekan'),
        ('fattah_used', 'Fattah-1/2'), ('shahed_136_used', 'Shahed-136'),
        ('shahed_238_used', 'Shahed-238'), ('shahed_131_used', 'Shahed-131'),
        ('paveh_used', 'Paveh'),
    ]
    for col, name in weapon_cols:
        cur.execute(f"SELECT COUNT(*) FROM waves WHERE {col} = 1")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"  {name}: used in {count} waves")


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA foreign_keys=ON")

    print(f"Building {DB_PATH} ...")

    create_schema(cur)
    load_operations(cur)
    load_waves(cur)
    load_iranian_weapons(cur)
    load_defense_systems(cur)
    load_armed_forces(cur)
    load_us_bases(cur)
    load_us_naval_vessels(cur)
    load_x_post_snippets(cur)

    conn.commit()
    print_summary(cur)

    # Verify row counts
    cur.execute("SELECT COUNT(*) FROM waves")
    total_waves = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM operations")
    total_ops = cur.fetchone()[0]

    conn.close()

    size_kb = os.path.getsize(DB_PATH) / 1024
    print(f"\nDone. {total_ops} operations, {total_waves} waves. "
          f"Database size: {size_kb:.0f} KB")


if __name__ == '__main__':
    main()
