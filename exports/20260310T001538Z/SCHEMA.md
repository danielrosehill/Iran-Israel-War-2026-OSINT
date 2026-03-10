# Database Schema

Generated: 2026-03-10 00:15 UTC


## armed_forces (20 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `id` **PK** | TEXT | YES |  |
| 1 | `name` | TEXT | NO |  |
| 2 | `abbreviation` | TEXT | YES |  |
| 3 | `country_code` | TEXT | YES |  |
| 4 | `country_name` | TEXT | YES |  |
| 5 | `side` | TEXT | YES |  |
| 6 | `type` | TEXT | YES |  |
| 7 | `parent` | TEXT | YES |  |
| 8 | `notes` | TEXT | YES |  |

## armed_forces_aliases (48 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `force_id` **PK** | TEXT | NO |  |
| 1 | `alias` **PK** | TEXT | NO |  |

## defense_systems (8 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `id` **PK** | TEXT | YES |  |
| 1 | `system_name` | TEXT | NO |  |
| 2 | `operator` | TEXT | YES |  |
| 3 | `classification` | TEXT | YES |  |
| 4 | `intercept_phase` | TEXT | YES |  |
| 5 | `intercept_alt_min_km` | REAL | YES |  |
| 6 | `intercept_alt_max_km` | REAL | YES |  |
| 7 | `range_km` | REAL | YES |  |
| 8 | `kill_mechanism` | TEXT | YES |  |
| 9 | `developer` | TEXT | YES |  |
| 10 | `first_operational` | TEXT | YES |  |
| 11 | `first_combat_use` | TEXT | YES |  |
| 12 | `notes` | TEXT | YES |  |

## entities (210 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `iso_3166_1_alpha2` **PK** | TEXT | YES |  |
| 1 | `entity_name` | TEXT | NO |  |
| 2 | `entity_type` | TEXT | NO |  |
| 3 | `eu_member_state` | INTEGER | NO | 0 |
| 4 | `combatant` | INTEGER | NO | 0 |

## interceptor_munitions (11 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `id` **PK** | TEXT | YES |  |
| 1 | `name` | TEXT | NO |  |
| 2 | `parent_system` | TEXT | YES |  |
| 3 | `type` | TEXT | YES |  |
| 4 | `min_intercept_alt_km` | REAL | YES |  |
| 5 | `max_intercept_alt_km` | REAL | YES |  |
| 6 | `min_range_km` | REAL | YES |  |
| 7 | `max_range_km` | REAL | YES |  |
| 8 | `speed_mach` | REAL | YES |  |
| 9 | `length_m` | REAL | YES |  |
| 10 | `diameter_m` | REAL | YES |  |
| 11 | `weight_kg` | REAL | YES |  |
| 12 | `guidance` | TEXT | YES |  |
| 13 | `warhead_type` | TEXT | YES |  |
| 14 | `kill_mechanism` | TEXT | YES |  |
| 15 | `unit_cost_usd` | INTEGER | YES |  |
| 16 | `unit_cost_range` | TEXT | YES |  |
| 17 | `unit_cost_notes` | TEXT | YES |  |
| 18 | `developer` | TEXT | YES |  |
| 19 | `country` | TEXT | YES |  |
| 20 | `first_operational` | TEXT | YES |  |
| 21 | `first_combat_use` | TEXT | YES |  |
| 22 | `notes` | TEXT | YES |  |

## international_reactions (210 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `iso_3166_1_alpha2` **PK** | TEXT | NO |  |
| 1 | `operation` **PK** | TEXT | NO |  |
| 2 | `entity_name` | TEXT | NO |  |
| 3 | `entity_type` | TEXT | NO |  |
| 4 | `eu_member_state` | INTEGER | NO | 0 |
| 5 | `combatant` | INTEGER | NO | 0 |
| 6 | `overall_stance` | TEXT | YES |  |
| 7 | `notes` | TEXT | YES |  |

## iranian_weapons (12 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `id` **PK** | TEXT | YES |  |
| 1 | `system_name` | TEXT | NO |  |
| 2 | `type_key` | TEXT | YES |  |
| 3 | `classification` | TEXT | YES |  |
| 4 | `propulsion` | TEXT | YES |  |
| 5 | `stages` | INTEGER | YES |  |
| 6 | `range_km` | TEXT | YES |  |
| 7 | `warhead_kg` | REAL | YES |  |
| 8 | `launch_weight_kg` | REAL | YES |  |
| 9 | `length_m` | REAL | YES |  |
| 10 | `diameter_m` | REAL | YES |  |
| 11 | `guidance` | TEXT | YES |  |
| 12 | `cep_m` | TEXT | YES |  |
| 13 | `marv` | INTEGER | YES |  |
| 14 | `hypersonic` | TEXT | YES |  |
| 15 | `basing` | TEXT | YES |  |
| 16 | `first_combat_use` | TEXT | YES |  |
| 17 | `lineage` | TEXT | YES |  |
| 18 | `notes` | TEXT | YES |  |

## operations (4 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `operation` **PK** | TEXT | YES |  |
| 1 | `operation_name` | TEXT | YES |  |
| 2 | `operation_name_farsi` | TEXT | YES |  |
| 3 | `version` | TEXT | YES |  |
| 4 | `wave_count` | INTEGER | YES |  |
| 5 | `date_start` | TEXT | YES |  |
| 6 | `date_end` | TEXT | YES |  |
| 7 | `data_quality` | TEXT | YES |  |
| 8 | `conflict_name` | TEXT | YES |  |
| 9 | `total_ballistic_missiles` | TEXT | YES |  |
| 10 | `total_cruise_missiles` | TEXT | YES |  |
| 11 | `total_drones` | TEXT | YES |  |
| 12 | `total_munitions_estimate` | TEXT | YES |  |
| 13 | `interception_rate_claimed` | REAL | YES |  |
| 14 | `total_killed` | TEXT | YES |  |
| 15 | `total_wounded` | TEXT | YES |  |
| 16 | `trigger_event` | TEXT | YES |  |
| 17 | `historical_significance` | TEXT | YES |  |

## reaction_statements (630 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `id` **PK** | INTEGER | YES |  |
| 1 | `iso_3166_1_alpha2` | TEXT | NO |  |
| 2 | `operation` | TEXT | NO |  |
| 3 | `statement_type` | TEXT | NO |  |
| 4 | `made` | INTEGER | NO | 0 |
| 5 | `date` | TEXT | YES |  |
| 6 | `speaker` | TEXT | YES |  |
| 7 | `speaker_title` | TEXT | YES |  |
| 8 | `summary` | TEXT | YES |  |
| 9 | `statement_text` | TEXT | YES |  |
| 10 | `statement_url` | TEXT | YES |  |
| 11 | `category` | TEXT | YES |  |
| 12 | `source_type` | TEXT | YES |  |

## reaction_types (9 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `id` **PK** | TEXT | YES |  |
| 1 | `label` | TEXT | NO |  |
| 2 | `description` | TEXT | YES |  |
| 3 | `spectrum_score` | INTEGER | YES |  |

## sqlite_sequence (2 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `name` |  | YES |  |
| 1 | `seq` |  | YES |  |

## us_bases (13 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `name` **PK** | TEXT | YES |  |
| 1 | `country_code` | TEXT | YES |  |
| 2 | `country_name` | TEXT | YES |  |
| 3 | `branch` | TEXT | YES |  |
| 4 | `lat` | REAL | YES |  |
| 5 | `lon` | REAL | YES |  |

## us_naval_vessels (2 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `name` **PK** | TEXT | YES |  |
| 1 | `type` | TEXT | YES |  |
| 2 | `class` | TEXT | YES |  |
| 3 | `branch` | TEXT | YES |  |
| 4 | `fleet` | TEXT | YES |  |
| 5 | `notes` | TEXT | YES |  |

## wave_attacking_forces (79 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `operation` **PK** | TEXT | NO |  |
| 1 | `wave_number` **PK** | INTEGER | NO |  |
| 2 | `actor` **PK** | TEXT | NO |  |
| 3 | `subunit` | TEXT | YES |  |

## wave_events (19 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `uuid` **PK** | TEXT | YES |  |
| 1 | `operation` | TEXT | NO |  |
| 2 | `wave_number` | INTEGER | NO |  |
| 3 | `event_type` | TEXT | NO |  |
| 4 | `outcome_status` | TEXT | YES |  |
| 5 | `location_name` | TEXT | NO |  |
| 6 | `lat` | REAL | YES |  |
| 7 | `lon` | REAL | YES |  |
| 8 | `country_code` | TEXT | YES |  |
| 9 | `weapon_type` | TEXT | YES |  |
| 10 | `defense_system` | TEXT | YES |  |
| 11 | `interception_method` | TEXT | YES |  |
| 12 | `interceptor_munition` | TEXT | YES |  |
| 13 | `intercept_phase` | TEXT | YES |  |
| 14 | `intercepting_force` | TEXT | YES |  |
| 15 | `fatalities` | INTEGER | YES |  |
| 16 | `injuries` | INTEGER | YES |  |
| 17 | `damage_description` | TEXT | YES |  |
| 18 | `target_type` | TEXT | YES |  |
| 19 | `source_url` | TEXT | YES |  |
| 20 | `confidence` | TEXT | NO | 'probable' |
| 21 | `iranian_claim` | TEXT | YES |  |
| 22 | `israeli_claim` | TEXT | YES |  |
| 23 | `us_claim` | TEXT | YES |  |
| 24 | `bda_source_type` | TEXT | YES |  |
| 25 | `bda_source_name` | TEXT | YES |  |
| 26 | `bda_source_url` | TEXT | YES |  |
| 27 | `bda_assessment_date` | TEXT | YES |  |
| 28 | `bda_assessment` | TEXT | YES |  |
| 29 | `bda_damage_confirmed` | INTEGER | YES |  |
| 30 | `bda_impact_count` | INTEGER | YES |  |
| 31 | `satint_provider` | TEXT | YES |  |
| 32 | `satint_capture_date` | TEXT | YES |  |
| 33 | `satint_resolution_m` | REAL | YES |  |
| 34 | `satint_observations` | TEXT | YES |  |
| 35 | `satint_before_after` | INTEGER | YES |  |
| 36 | `satint_imagery_url` | TEXT | YES |  |
| 37 | `narrative` | TEXT | YES |  |
| 38 | `thumbnail` | TEXT | YES |  |
| 39 | `images_json` | TEXT | YES |  |

## wave_intercepted_by_other (4 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `operation` **PK** | TEXT | NO |  |
| 1 | `wave_number` **PK** | INTEGER | NO |  |
| 2 | `country` **PK** | TEXT | NO |  |

## wave_interception_systems (123 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `operation` **PK** | TEXT | NO |  |
| 1 | `wave_number` **PK** | INTEGER | NO |  |
| 2 | `system_name` **PK** | TEXT | NO |  |

## wave_landing_countries (131 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `operation` **PK** | TEXT | NO |  |
| 1 | `wave_number` **PK** | INTEGER | NO |  |
| 2 | `country_code` **PK** | TEXT | NO |  |

## wave_sources (61 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `operation` **PK** | TEXT | NO |  |
| 1 | `wave_number` **PK** | INTEGER | NO |  |
| 2 | `url` **PK** | TEXT | NO |  |

## wave_us_bases_targeted (27 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `operation` **PK** | TEXT | NO |  |
| 1 | `wave_number` **PK** | INTEGER | NO |  |
| 2 | `base_name` **PK** | TEXT | NO |  |
| 3 | `country_code` | TEXT | YES |  |

## wave_us_naval_vessels_targeted (5 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `operation` **PK** | TEXT | NO |  |
| 1 | `wave_number` **PK** | INTEGER | NO |  |
| 2 | `vessel_name` **PK** | TEXT | NO |  |
| 3 | `vessel_type` | TEXT | YES |  |

## waves (59 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `wave_uid` | TEXT | NO |  |
| 1 | `uuid` | TEXT | NO |  |
| 2 | `operation` **PK** | TEXT | NO |  |
| 3 | `wave_number` **PK** | INTEGER | NO |  |
| 4 | `narrative` | TEXT | YES |  |
| 5 | `wave_codename_farsi` | TEXT | YES |  |
| 6 | `wave_codename_english` | TEXT | YES |  |
| 7 | `description` | TEXT | YES |  |
| 8 | `announced_utc` | TEXT | YES |  |
| 9 | `announcement_source` | TEXT | YES |  |
| 10 | `announcement_x_url` | TEXT | YES |  |
| 11 | `probable_launch_time` | TEXT | YES |  |
| 12 | `launch_time_israel` | TEXT | YES |  |
| 13 | `launch_time_iran` | TEXT | YES |  |
| 14 | `solar_phase_launch_site` | INTEGER | YES |  |
| 15 | `solar_phase_target` | INTEGER | YES |  |
| 16 | `conflict_day` | INTEGER | YES |  |
| 17 | `hours_since_last_wave` | REAL | YES |  |
| 18 | `time_between_waves_min` | REAL | YES |  |
| 19 | `wave_duration_min` | REAL | YES |  |
| 20 | `payload` | TEXT | YES |  |
| 21 | `drones_used` | INTEGER | YES |  |
| 22 | `ballistic_missiles_used` | INTEGER | YES |  |
| 23 | `cruise_missiles_used` | INTEGER | YES |  |
| 24 | `emad_used` | INTEGER | YES |  |
| 25 | `ghadr_used` | INTEGER | YES |  |
| 26 | `sejjil_used` | INTEGER | YES |  |
| 27 | `kheibar_shekan_used` | INTEGER | YES |  |
| 28 | `fattah_used` | INTEGER | YES |  |
| 29 | `shahed_136_used` | INTEGER | YES |  |
| 30 | `shahed_238_used` | INTEGER | YES |  |
| 31 | `shahed_131_used` | INTEGER | YES |  |
| 32 | `shahed_107_used` | INTEGER | YES |  |
| 33 | `shahed_129_used` | INTEGER | YES |  |
| 34 | `mohajer_6_used` | INTEGER | YES |  |
| 35 | `shahab_3_used` | INTEGER | YES |  |
| 36 | `paveh_used` | INTEGER | YES |  |
| 37 | `bm_liquid_fueled` | INTEGER | YES |  |
| 38 | `bm_solid_fueled` | INTEGER | YES |  |
| 39 | `bm_marv_equipped` | INTEGER | YES |  |
| 40 | `bm_hypersonic` | INTEGER | YES |  |
| 41 | `cluster_munitions` | INTEGER | YES |  |
| 42 | `israel_targeted` | INTEGER | YES |  |
| 43 | `us_bases_targeted` | INTEGER | YES |  |
| 44 | `targets_description` | TEXT | YES |  |
| 45 | `targeted_tel_aviv` | INTEGER | YES |  |
| 46 | `targeted_jerusalem` | INTEGER | YES |  |
| 47 | `targeted_haifa` | INTEGER | YES |  |
| 48 | `targeted_negev_beersheba` | INTEGER | YES |  |
| 49 | `targeted_northern_periphery` | INTEGER | YES |  |
| 50 | `targeted_eilat` | INTEGER | YES |  |
| 51 | `target_lat` | REAL | YES |  |
| 52 | `target_lon` | REAL | YES |  |
| 53 | `target_generic_location` | INTEGER | YES |  |
| 54 | `landing_countries_names` | TEXT | YES |  |
| 55 | `target_iaf_base` | INTEGER | YES |  |
| 56 | `target_us_base` | INTEGER | YES |  |
| 57 | `target_naval_base` | INTEGER | YES |  |
| 58 | `target_naval_vessel` | INTEGER | YES |  |
| 59 | `target_government_c2` | INTEGER | YES |  |
| 60 | `target_military_industrial` | INTEGER | YES |  |
| 61 | `target_intelligence` | INTEGER | YES |  |
| 62 | `target_civilian_infrastructure` | INTEGER | YES |  |
| 63 | `target_civilian_area` | INTEGER | YES |  |
| 64 | `target_diplomatic` | INTEGER | YES |  |
| 65 | `attacking_force_actor` | TEXT | YES |  |
| 66 | `attacking_force_subunit` | TEXT | YES |  |
| 67 | `launch_site_description` | TEXT | YES |  |
| 68 | `launch_site_lat` | REAL | YES |  |
| 69 | `launch_site_lon` | REAL | YES |  |
| 70 | `launch_site_generic_location` | INTEGER | YES |  |
| 71 | `intercepted` | INTEGER | YES |  |
| 72 | `estimated_intercept_count` | INTEGER | YES |  |
| 73 | `estimated_intercept_rate` | REAL | YES |  |
| 74 | `exoatmospheric_interception` | INTEGER | YES |  |
| 75 | `endoatmospheric_interception` | INTEGER | YES |  |
| 76 | `interception_report` | TEXT | YES |  |
| 77 | `intercepted_by_israel` | INTEGER | YES |  |
| 78 | `intercepted_by_us` | INTEGER | YES |  |
| 79 | `intercepted_by_uk` | INTEGER | YES |  |
| 80 | `intercepted_by_jordan` | INTEGER | YES |  |
| 81 | `estimated_munitions_count` | INTEGER | YES |  |
| 82 | `munitions_targeting_israel` | INTEGER | YES |  |
| 83 | `munitions_targeting_us_bases` | INTEGER | YES |  |
| 84 | `cumulative_total` | INTEGER | YES |  |
| 85 | `damage` | TEXT | YES |  |
| 86 | `fatalities` | INTEGER | YES |  |
| 87 | `injuries` | INTEGER | YES |  |
| 88 | `civilian_casualties` | INTEGER | YES |  |
| 89 | `military_casualties` | INTEGER | YES |  |
| 90 | `new_country_targeted` | INTEGER | YES |  |
| 91 | `new_weapon_first_use` | INTEGER | YES |  |
| 92 | `proxy_involvement` | INTEGER | YES |  |
| 93 | `proxy_description` | TEXT | YES |  |
| 94 | `idf_statement` | TEXT | YES |  |

## x_post_snippets (54 rows)

| # | Column | Type | Nullable | Default |
|--:|--------|------|----------|---------|
| 0 | `id` **PK** | INTEGER | YES |  |
| 1 | `operation` | TEXT | NO |  |
| 2 | `wave_number` | INTEGER | NO |  |
| 3 | `source_type` | TEXT | NO | 'x_post' |
| 4 | `author` | TEXT | YES |  |
| 5 | `handle` | TEXT | YES |  |
| 6 | `post_date` | TEXT | YES |  |
| 7 | `text` | TEXT | NO |  |
| 8 | `image_file` | TEXT | YES |  |
