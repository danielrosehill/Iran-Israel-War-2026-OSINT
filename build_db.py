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
import uuid

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
    'interceptor_munitions': os.path.join(REPO, 'data', 'reference', 'interceptor_munitions.json'),
    'armed_forces': os.path.join(REPO, 'data', 'reference', 'armed_forces.json'),
    'us_bases': os.path.join(REPO, 'data', 'reference', 'us_bases.json'),
    'us_naval_vessels': os.path.join(REPO, 'data', 'reference', 'us_naval_vessels.json'),
    'entities': os.path.join(REPO, 'data', 'reference', 'entities.json'),
    'reaction_types': os.path.join(REPO, 'data', 'reference', 'reaction_types.json'),
}

REACTION_FILES = [
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'international_reactions.json')),
]


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
        uuid                    TEXT NOT NULL UNIQUE,
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
    -- Granular interception and strike events within each wave
    -- ══════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS wave_events (
        uuid                TEXT PRIMARY KEY,
        operation           TEXT NOT NULL,
        wave_number         INTEGER NOT NULL,
        event_type          TEXT NOT NULL CHECK (event_type IN ('interception', 'strike', 'impact')),
        outcome_status      TEXT CHECK (outcome_status IN ('confirmed', 'disputed', 'unverified', NULL)),
        location_name       TEXT NOT NULL,
        lat                 REAL,
        lon                 REAL,
        country_code        TEXT,
        weapon_type         TEXT,
        defense_system      TEXT,
        interception_method TEXT CHECK (interception_method IN ('surface_to_air_missile', 'air_to_air_missile', 'air_to_air_gun', 'directed_energy', 'electronic_warfare', NULL)),
        interceptor_munition TEXT,
        intercept_phase     TEXT CHECK (intercept_phase IN ('exoatmospheric', 'endoatmospheric', NULL)),
        intercepting_force  TEXT,
        fatalities          INTEGER,
        injuries            INTEGER,
        damage_description  TEXT,
        target_type         TEXT CHECK (target_type IN ('military', 'civilian', 'dual_use', 'infrastructure', NULL)),
        source_url          TEXT,
        confidence          TEXT NOT NULL DEFAULT 'probable' CHECK (confidence IN ('confirmed', 'probable', 'unconfirmed')),
        -- Competing claims
        iranian_claim       TEXT,
        israeli_claim        TEXT,
        us_claim            TEXT,
        -- Post-battle damage assessment
        bda_source_type     TEXT CHECK (bda_source_type IN ('satellite_imagery', 'ground_photo', 'video', 'media_report', 'government_report', 'multiple', NULL)),
        bda_source_name     TEXT,
        bda_source_url      TEXT,
        bda_assessment_date TEXT,
        bda_assessment      TEXT,
        bda_damage_confirmed INTEGER,  -- 0/1/NULL
        bda_impact_count    INTEGER,
        -- SATINT observations (nested within BDA)
        satint_provider     TEXT,
        satint_capture_date TEXT,
        satint_resolution_m REAL,
        satint_observations TEXT,
        satint_before_after INTEGER,  -- 0/1/NULL
        satint_imagery_url  TEXT,
        -- Media and narrative
        narrative           TEXT,
        thumbnail           TEXT,
        images_json         TEXT,  -- JSON array of image objects
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

    CREATE TABLE IF NOT EXISTS interceptor_munitions (
        id                  TEXT PRIMARY KEY,
        name                TEXT NOT NULL,
        parent_system       TEXT,
        type                TEXT,
        min_intercept_alt_km REAL,
        max_intercept_alt_km REAL,
        min_range_km        REAL,
        max_range_km        REAL,
        speed_mach          REAL,
        length_m            REAL,
        diameter_m          REAL,
        weight_kg           REAL,
        guidance            TEXT,
        warhead_type        TEXT,
        kill_mechanism      TEXT,
        unit_cost_usd       INTEGER,
        unit_cost_range     TEXT,
        unit_cost_notes     TEXT,
        developer           TEXT,
        country             TEXT,
        first_operational   TEXT,
        first_combat_use    TEXT,
        notes               TEXT,
        FOREIGN KEY (parent_system) REFERENCES defense_systems(id)
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
    -- Entities (countries + multilaterals)
    -- ══════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS entities (
        iso_3166_1_alpha2   TEXT PRIMARY KEY,
        entity_name         TEXT NOT NULL,
        entity_type         TEXT NOT NULL CHECK (entity_type IN ('state', 'multilateral')),
        eu_member_state     INTEGER NOT NULL DEFAULT 0,
        combatant           INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS reaction_types (
        id                  TEXT PRIMARY KEY,
        label               TEXT NOT NULL,
        description         TEXT,
        spectrum_score      INTEGER  -- -3 to +3, NULL for silent
    );

    -- ══════════════════════════════════════════════════════════════
    -- International reactions (per entity per operation)
    -- ══════════════════════════════════════════════════════════════
    CREATE TABLE IF NOT EXISTS international_reactions (
        iso_3166_1_alpha2   TEXT NOT NULL,
        operation           TEXT NOT NULL,
        entity_name         TEXT NOT NULL,
        entity_type         TEXT NOT NULL,
        eu_member_state     INTEGER NOT NULL DEFAULT 0,
        combatant           INTEGER NOT NULL DEFAULT 0,
        overall_stance      TEXT,
        notes               TEXT,
        PRIMARY KEY (iso_3166_1_alpha2, operation),
        FOREIGN KEY (iso_3166_1_alpha2) REFERENCES entities(iso_3166_1_alpha2),
        FOREIGN KEY (overall_stance) REFERENCES reaction_types(id)
    );

    CREATE TABLE IF NOT EXISTS reaction_statements (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        iso_3166_1_alpha2   TEXT NOT NULL,
        operation           TEXT NOT NULL,
        statement_type      TEXT NOT NULL CHECK (statement_type IN (
            'head_of_state', 'head_of_government', 'foreign_ministry', 'additional'
        )),
        made                INTEGER NOT NULL DEFAULT 0,
        date                TEXT,
        speaker             TEXT,
        speaker_title       TEXT,
        summary             TEXT,
        statement_text      TEXT,
        statement_url       TEXT,
        category            TEXT,
        source_type         TEXT,  -- for additional statements only
        FOREIGN KEY (iso_3166_1_alpha2, operation)
            REFERENCES international_reactions(iso_3166_1_alpha2, operation),
        FOREIGN KEY (category) REFERENCES reaction_types(id)
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


def get_uuid(obj):
    """Return existing UUID from JSON or generate a deterministic one."""
    return obj.get('uuid') or str(uuid.uuid4())


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
                    ?,?,?,?,?,?,
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
                get_uuid(w),
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

            # Events: granular interception and strike records
            for evt in w.get('events', []):
                bda = evt.get('bda') or {}
                satint = bda.get('satint') or {}
                cur.execute("""
                    INSERT INTO wave_events
                        (uuid, operation, wave_number, event_type, outcome_status,
                         location_name,
                         lat, lon, country_code, weapon_type,
                         defense_system, interception_method, interceptor_munition,
                         intercept_phase, intercepting_force,
                         fatalities, injuries, damage_description,
                         target_type, source_url, confidence,
                         iranian_claim, israeli_claim, us_claim,
                         bda_source_type, bda_source_name, bda_source_url,
                         bda_assessment_date, bda_assessment,
                         bda_damage_confirmed, bda_impact_count,
                         satint_provider, satint_capture_date,
                         satint_resolution_m, satint_observations,
                         satint_before_after, satint_imagery_url,
                         narrative, thumbnail, images_json)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    get_uuid(evt),
                    op, wn,
                    evt['event_type'],
                    evt.get('outcome_status'),
                    evt['location_name'],
                    evt.get('lat'),
                    evt.get('lon'),
                    evt.get('country_code'),
                    evt.get('weapon_type'),
                    evt.get('defense_system'),
                    evt.get('interception_method'),
                    evt.get('interceptor_munition'),
                    evt.get('intercept_phase'),
                    evt.get('intercepting_force'),
                    evt.get('fatalities'),
                    evt.get('injuries'),
                    evt.get('damage_description'),
                    evt.get('target_type'),
                    evt.get('source_url'),
                    evt.get('confidence', 'probable'),
                    evt.get('iranian_claim'),
                    evt.get('israeli_claim'),
                    evt.get('us_claim'),
                    bda.get('source_type'),
                    bda.get('source_name'),
                    bda.get('source_url'),
                    bda.get('assessment_date'),
                    bda.get('assessment'),
                    bool_to_int(bda.get('damage_confirmed')),
                    bda.get('impact_count'),
                    # SATINT
                    satint.get('imagery_provider'),
                    satint.get('capture_date'),
                    satint.get('resolution_m'),
                    satint.get('observations'),
                    bool_to_int(satint.get('before_after_available')),
                    satint.get('imagery_url'),
                    # Media and narrative
                    evt.get('narrative'),
                    evt.get('thumbnail'),
                    json.dumps(evt['images']) if evt.get('images') else None,
                ))


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


def load_interceptor_munitions(cur):
    with open(REF_FILES['interceptor_munitions']) as f:
        munitions = json.load(f)
    for m in munitions:
        cost = m.get('unit_cost_usd', {})
        if isinstance(cost, dict):
            cost_est = cost.get('estimate')
            cost_range = cost.get('range')
            cost_notes = cost.get('notes')
        else:
            cost_est = cost
            cost_range = None
            cost_notes = None
        cur.execute("""
            INSERT OR REPLACE INTO interceptor_munitions VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            m['id'], m['name'], m.get('parent_system'),
            m.get('type'),
            m.get('min_intercept_alt_km'), m.get('max_intercept_alt_km'),
            m.get('min_range_km'), m.get('max_range_km'),
            m.get('speed_mach'),
            m.get('length_m'), m.get('diameter_m'), m.get('weight_kg'),
            m.get('guidance'), m.get('warhead_type'), m.get('kill_mechanism'),
            cost_est, cost_range, cost_notes,
            m.get('developer'), m.get('country'),
            str(m.get('first_operational', '')) or None,
            m.get('first_combat_use'),
            m.get('notes'),
        ))


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


def load_entities(cur):
    with open(REF_FILES['entities']) as f:
        entities = json.load(f)
    for e in entities:
        cur.execute("""
            INSERT OR REPLACE INTO entities VALUES (?,?,?,?,?)
        """, (
            e['alpha2'], e['name'], e['type'],
            1 if e.get('eu_member_state') else 0,
            1 if e.get('combatant') else 0,
        ))


def load_reaction_types(cur):
    with open(REF_FILES['reaction_types']) as f:
        types = json.load(f)
    for rt in types:
        cur.execute("""
            INSERT OR REPLACE INTO reaction_types VALUES (?,?,?,?)
        """, (rt['id'], rt['label'], rt.get('description'), rt.get('spectrum_score')))


def load_international_reactions(cur):
    for op_id, path in REACTION_FILES:
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        operation = data['metadata'].get('operation', op_id)
        for r in data['reactions']:
            cur.execute("""
                INSERT OR REPLACE INTO international_reactions VALUES (?,?,?,?,?,?,?,?)
            """, (
                r['iso_3166_1_alpha2'], operation,
                r['entity_name'], r['entity_type'],
                1 if r.get('eu_member_state') else 0,
                1 if r.get('combatant') else 0,
                r.get('overall_stance'),
                r.get('notes'),
            ))
            # Statement types to load
            for stype, key in [
                ('head_of_state', 'head_of_state_statement'),
                ('head_of_government', 'head_of_government_statement'),
                ('foreign_ministry', 'foreign_ministry_statement'),
            ]:
                stmt = r.get(key)
                if not stmt:
                    continue
                cur.execute("""
                    INSERT INTO reaction_statements
                        (iso_3166_1_alpha2, operation, statement_type, made,
                         date, speaker, speaker_title, summary,
                         statement_text, statement_url, category, source_type)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    r['iso_3166_1_alpha2'], operation, stype,
                    1 if stmt.get('made') else 0,
                    stmt.get('date'), stmt.get('speaker'),
                    stmt.get('speaker_title'), stmt.get('summary'),
                    stmt.get('statement_text'), stmt.get('statement_url'),
                    stmt.get('category'), None,
                ))
            # Additional statements
            for stmt in r.get('additional_statements', []):
                cur.execute("""
                    INSERT INTO reaction_statements
                        (iso_3166_1_alpha2, operation, statement_type, made,
                         date, speaker, speaker_title, summary,
                         statement_text, statement_url, category, source_type)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    r['iso_3166_1_alpha2'], operation, 'additional',
                    1 if stmt.get('made') else 0,
                    stmt.get('date'), stmt.get('speaker'),
                    stmt.get('speaker_title'), stmt.get('summary'),
                    stmt.get('statement_text'), stmt.get('statement_url'),
                    stmt.get('category'), stmt.get('source_type'),
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
    for table in ['operations', 'waves', 'wave_events',
                   'wave_landing_countries',
                   'wave_interception_systems', 'wave_us_bases_targeted',
                   'wave_sources', 'iranian_weapons', 'defense_systems',
                   'interceptor_munitions',
                   'armed_forces', 'us_bases', 'us_naval_vessels',
                   'entities', 'reaction_types',
                   'international_reactions', 'reaction_statements',
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
    load_interceptor_munitions(cur)
    load_armed_forces(cur)
    load_us_bases(cur)
    load_us_naval_vessels(cur)
    load_entities(cur)
    load_reaction_types(cur)
    load_international_reactions(cur)
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
