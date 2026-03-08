#!/usr/bin/env python3
"""
Build ArcGIS StoryMap-optimized exports from wave data.

Produces:
  - arcgis_launch_sites.geojson — launch origins with display-friendly fields
  - arcgis_targets.geojson — target points with display-friendly fields
  - arcgis_trajectories.geojson — LineString arcs from launch → target
  - arcgis_waves.csv — flat CSV with lat/lon for ArcGIS Online CSV import

All files include: unique wave_uid for cross-layer joins, operation_label,
wave_label, narrative description, target type booleans, timestamp_epoch,
and icon_type fields optimized for ArcGIS pop-ups, symbology, filtering,
and time slider animation.

Usage:
    python build_arcgis.py [--output-dir PATH]
"""

import json
import os
import csv
import re
import argparse
from datetime import datetime

REPO = os.path.dirname(os.path.abspath(__file__))

WAVE_FILES = [
    ('tp1', os.path.join(REPO, 'data', 'tp1-2024', 'waves.json')),
    ('tp2', os.path.join(REPO, 'data', 'tp2-2024', 'waves.json')),
    ('tp3', os.path.join(REPO, 'data', 'tp3-2025', 'waves.json')),
    ('tp4', os.path.join(REPO, 'data', 'tp4-2026', 'waves.json')),
]

OPERATION_LABELS = {
    'tp1': 'True Promise 1 (Apr 2024)',
    'tp2': 'True Promise 2 (Oct 2024)',
    'tp3': 'True Promise 3 (Jun 2025)',
    'tp4': 'True Promise 4 (Feb–Mar 2026)',
}

OPERATION_SHORT = {
    'tp1': 'TP1',
    'tp2': 'TP2',
    'tp3': 'TP3',
    'tp4': 'TP4',
}

# ---------------------------------------------------------------------------
# Target-type classification keywords
# ---------------------------------------------------------------------------

IAF_BASE_KEYWORDS = [
    'nevatim', 'ramon', 'tel nof', 'hatzerim', 'ramat david', 'ovda',
    'israeli air force', 'iaf', 'air base', 'airbase',
]

US_BASE_KEYWORDS = [
    'al udeid', 'al-udeid', 'al dhafra', 'al-dhafra', 'camp arifjan',
    'ali al-salem', 'ali al salem', 'sheikh isa', 'harir', 'al minhad',
    'al-minhad', 'muwaffaq salti', 'al-azraq', 'camp udairi', 'camp buehring',
    'prince sultan', 'us base', 'us air base', 'american base', 'us military',
    'abdullah al-mubarak', 'abdullah mubarak', 'juffair', 'nsa bahrain',
]

NAVAL_BASE_KEYWORDS = [
    'naval base', 'naval yard', 'mina salman', 'mohammed al-ahmad',
    'naval facility', 'navy base', 'port jebel ali', 'naval port',
]

NAVAL_VESSEL_KEYWORDS = [
    'uss ', 'tanker', 'vessel', 'warship', 'navy marine',
    'ammunition ship', 'fuel support ship', 'naval asset',
]

GOV_C2_KEYWORDS = [
    'hakirya', 'ha-kirya', 'hakirya', 'ministry of war', 'ministry of defense',
    'defence ministry', 'defense ministry', 'general staff', 'c2',
    'command center', 'command centre', 'government complex',
    'netanyahu', 'mossad', 'unit 8200', 'glilot',
]

MIL_INDUSTRIAL_KEYWORDS = [
    'military-industrial', 'military industrial', 'rafael', 'semiconductor',
    'beit shams', 'ishtod', 'weapons', 'defense industry', 'defence industry',
    'military industry',
]

INTELLIGENCE_KEYWORDS = [
    'intelligence', 'cia', 'unit 8200', 'radar', 'satellite comms',
    'communications complex', 'cybersecurity', 'advanced technology',
]

CIVILIAN_INFRA_KEYWORDS = [
    'oil refinery', 'power plant', 'airport', 'ben gurion', 'data center',
    'data centre', 'aws', 'amazon', 'lng', 'aramco', 'fujairah oil',
    'hamad international', 'paphos airport', 'king khalid', 'pipeline',
]

CIVILIAN_AREA_KEYWORDS = [
    'residential', 'civilian', 'cities', 'bat yam', 'bnei brak',
    'crowne plaza', 'etihad towers', 'hotel', 'heart of',
]

DIPLOMATIC_KEYWORDS = [
    'embassy', 'consulate', 'diplomatic',
]

# ISO 3166-1 alpha-2 to readable country names (alphabetical by name)
COUNTRY_NAMES = {
    'AE': 'United Arab Emirates',
    'BH': 'Bahrain',
    'CY': 'Cyprus',
    'IL': 'Israel',
    'IO': 'British Indian Ocean Territory',
    'IQ': 'Iraq',
    'JO': 'Jordan',
    'KW': 'Kuwait',
    'OM': 'Oman',
    'PS': 'Palestine',
    'QA': 'Qatar',
    'SA': 'Saudi Arabia',
    'TR': 'Turkey',
}


def classify_target_types(w):
    """Classify target types from wave target description and structured fields."""
    targets = w.get('targets', {})
    desc = (targets.get('targets') or '').lower()
    us_bases = targets.get('us_bases') or []
    naval = targets.get('us_naval_vessels') or []

    # Also check us_bases structured field
    us_base_names = []
    for b in us_bases:
        if isinstance(b, dict):
            us_base_names.append((b.get('base_name', '') or '').lower())
            us_base_names.append((b.get('name', '') or '').lower())
        elif isinstance(b, str):
            us_base_names.append(b.lower())
    us_text = ' '.join(us_base_names)

    naval_names = []
    for v in naval:
        if isinstance(v, dict):
            naval_names.append((v.get('name', '') or '').lower())
        elif isinstance(v, str):
            naval_names.append(v.lower())
    naval_text = ' '.join(naval_names)

    combined = desc + ' ' + us_text + ' ' + naval_text

    def has_keyword(keywords, text=combined):
        return any(kw in text for kw in keywords)

    return {
        'target_iaf_base': has_keyword(IAF_BASE_KEYWORDS, desc),
        'target_us_base': has_keyword(US_BASE_KEYWORDS) or len(us_bases) > 0,
        'target_naval_base': has_keyword(NAVAL_BASE_KEYWORDS),
        'target_naval_vessel': has_keyword(NAVAL_VESSEL_KEYWORDS) or len(naval) > 0,
        'target_government_c2': has_keyword(GOV_C2_KEYWORDS, desc),
        'target_military_industrial': has_keyword(MIL_INDUSTRIAL_KEYWORDS, desc),
        'target_intelligence': has_keyword(INTELLIGENCE_KEYWORDS, desc),
        'target_civilian_infrastructure': has_keyword(CIVILIAN_INFRA_KEYWORDS, desc),
        'target_civilian_area': has_keyword(CIVILIAN_AREA_KEYWORDS, desc),
        'target_diplomatic': has_keyword(DIPLOMATIC_KEYWORDS),
    }


# ---------------------------------------------------------------------------
# Narrative descriptions for each wave
# ---------------------------------------------------------------------------

WAVE_NARRATIVES = {
    # --- TP1 ---
    'tp1_w1': (
        "The first wave of Iran's inaugural direct attack on Israel. Launched on the night of 13 April 2024, "
        "this wave comprised a large combined salvo of Shahed-136 drones, ballistic missiles, and cruise missiles "
        "targeting Nevatim Airbase and sites across the Negev desert and Israeli-occupied Golan Heights. "
        "The attack was widely telegraphed in advance, giving Israel, the US, UK, France, and Jordan time to "
        "coordinate a multilayered defensive response. The overwhelming majority of munitions were intercepted."
    ),
    'tp1_w2': (
        "The second and final wave of True Promise 1, continuing the bombardment of Nevatim Airbase and "
        "the Ramon Airbase area in the Negev. This wave followed the initial drone/missile salvo by several hours, "
        "with ballistic missiles arriving after the slower drones. Minor damage was reported at Nevatim. "
        "The combined two-wave attack involved approximately 320 munitions — the largest single aerial assault "
        "in the region's history at the time. Israel's multi-tier defense (Arrow, David's Sling, Iron Dome) "
        "achieved a near-total interception rate with coalition support."
    ),

    # --- TP2 ---
    'tp2_w1': (
        "True Promise 2 opened with a ballistic-missile-only salvo on 1 October 2024, a significant tactical "
        "shift from TP1's mixed drone/missile approach. Approximately 180–200 Emad and Ghadr ballistic missiles "
        "targeted Nevatim, Tel Nof, and Hatzerim airbases. The absence of slow-moving drones meant defenders "
        "had far less warning time. Some missiles penetrated Israeli defenses, impacting near Nevatim."
    ),
    'tp2_w2': (
        "The second wave of TP2 targeted the Mossad/Unit 8200 headquarters complex at Glilot north of Tel Aviv, "
        "marking the first Iranian strike aimed at Israeli intelligence infrastructure. Nevatim and Tel Nof "
        "airbases were also targeted again. Two fatalities were reported — the first confirmed deaths from "
        "a direct Iranian strike on Israel. The all-ballistic approach of TP2 demonstrated Iran's evolving "
        "understanding that fast-moving missiles were more effective at penetrating Israeli defenses than "
        "the mixed salvos of TP1."
    ),

    # --- TP3 ---
    'tp3_w1': (
        "The opening salvo of the Twelve-Day War. Launched on 13 June 2025, this wave targeted military "
        "centres and air bases across Israel with ballistic missiles. It marked the beginning of Iran's "
        "most sustained aerial campaign to date, which would continue for 22 waves over 12 days."
    ),
    'tp3_w2': (
        "The second wave shifted targeting to Haifa and the Galilee region in northern Israel, expanding "
        "the geographic scope beyond the southern airbases that dominated TP1 and TP2. Ballistic missiles "
        "were used alongside drone swarms for the first time in TP3."
    ),
    'tp3_w3': (
        "A significant wave that Iran claimed penetrated multiple Israeli defense layers and struck targets "
        "in the occupied territories. This represented an escalation in Iranian rhetoric about the "
        "effectiveness of their strikes."
    ),
    'tp3_w4': (
        "A multi-city bombardment targeting both Tel Aviv and Haifa simultaneously, forcing Israel to "
        "defend across a wide geographic front. This dual-axis approach became a hallmark of TP3's "
        "middle waves."
    ),
    'tp3_w5': (
        "This wave marked the first targeting of critical civilian infrastructure — specifically the Haifa "
        "oil refinery — alongside military targets. The expansion to economic infrastructure signalled "
        "an escalation in Iranian targeting doctrine."
    ),
    'tp3_w6': (
        "A wave targeting Israeli command and control centres in Haifa and Tel Aviv. Bat Yam, south of "
        "Tel Aviv, was struck — one of the first confirmed impacts in a densely populated residential area "
        "during TP3."
    ),
    'tp3_w7': (
        "Iran claimed this wave used enhanced intelligence-guided targeting against Tel Aviv and Haifa, "
        "suggesting improved battle damage assessment and target refinement from earlier waves. This "
        "indicated a feedback loop between Iranian ISR and strike planning."
    ),
    'tp3_w8': (
        "Targeting described as strategic and sensitive sites in Tel Aviv and Haifa, with specific focus "
        "on C2 (command and control) systems. The progressive focus on C2 nodes suggested an attempt "
        "to degrade Israeli coordination capabilities."
    ),
    'tp3_w9': (
        "A continuation wave maintaining pressure on Haifa and Tel Aviv. By this point in the campaign, "
        "the sustained tempo was testing Israeli air defense ammunition stocks and crew endurance."
    ),
    'tp3_w10': (
        "This wave specifically targeted Israeli airbases from which jets had launched strikes against "
        "Iran, marking a direct retaliatory link between Israeli offensive operations and Iranian "
        "target selection."
    ),
    'tp3_w11': (
        "A tactically significant wave that used Fattah hypersonic missiles to target and reportedly "
        "destroy Israeli air defense radar systems. Iran framed this as a SEAD (Suppression of Enemy "
        "Air Defenses) operation designed to clear the path for follow-on missile waves — a doctrinal "
        "first for Iranian forces."
    ),
    'tp3_w12': (
        "The first combat use of Iran's Sejjil two-stage solid-fuel ballistic missile against Tel Aviv. "
        "The Sejjil's longer range and faster flight time represented a qualitative escalation in "
        "the weapons employed. These ultra-heavy, long-range missiles were designed to stress "
        "Israel's upper-tier Arrow interceptors."
    ),
    'tp3_w13': (
        "A wave targeting military sites and military industrial facilities in the Haifa and Tel Aviv "
        "areas. The targeting of defense industry suggested an attempt to degrade Israel's capacity "
        "to sustain military operations and replenish interceptor stocks."
    ),
    'tp3_w14': (
        "Continued strikes on military and industrial facilities. The sustained nature of the campaign "
        "by this point — over a week of near-daily waves — was unprecedented in modern missile warfare."
    ),
    'tp3_w15': (
        "Iran announced this wave as a new phase of the campaign, suggesting a deliberate operational "
        "pause and reassessment before resuming strikes. Military targets remained the stated focus."
    ),
    'tp3_w16': (
        "A military-focused wave continuing the declared new phase. The cumulative effect of 16 waves "
        "was placing enormous strain on Israel's interceptor stockpiles, particularly Arrow-3 and "
        "David's Sling missiles."
    ),
    'tp3_w17': (
        "Strikes on military and strategic targets. The campaign had by this point settled into a "
        "pattern of daily waves designed to maintain continuous pressure rather than achieve a single "
        "decisive blow."
    ),
    'tp3_w18': (
        "One of the most significant waves of TP3, targeting 14 named strategic military sites including "
        "the Hadera power plant, Haifa oil refinery, Ovda airbase (home to cyber command), the Kiryat Gat "
        "semiconductor zone, and the Rafael advanced defense systems centre in Haifa. This wave demonstrated "
        "detailed Iranian intelligence on Israeli critical infrastructure."
    ),
    'tp3_w19': (
        "Described by Iran as a large combined operation against strategic targets. This wave involved "
        "both drone swarms and ballistic missiles in a coordinated strike designed to saturate defenses "
        "from multiple vectors simultaneously."
    ),
    'tp3_w20': (
        "A major escalation targeting Ben Gurion Airport (Israel's primary international airport), "
        "biological research centres, and C2 facilities. Striking the airport represented a direct "
        "threat to Israel's connectivity with the outside world and its ability to receive military "
        "resupply."
    ),
    'tp3_w21': (
        "Iran claimed new tactics for precision and destructiveness in this wave against military and "
        "strategic targets. The language suggested the introduction of updated guidance systems or "
        "warhead configurations refined based on lessons from earlier waves."
    ),
    'tp3_w22': (
        "The final wave of the Twelve-Day War, striking military and logistical centres in the last "
        "minutes before a US-brokered ceasefire took effect. The timing — launching right up to the "
        "ceasefire deadline — was a deliberate signal of Iranian resolve and willingness to continue. "
        "Over 22 waves, TP3 had launched an estimated 1,600–1,800 munitions at Israel."
    ),

    # --- TP4 ---
    'tp4_w1': (
        "The opening wave of True Promise 4 on 28 February 2026 marked a fundamental expansion of "
        "Iran's targeting doctrine. For the first time, US military facilities in the Persian Gulf were "
        "targeted alongside Israeli sites — including the USN Fifth Fleet headquarters in Bahrain, "
        "Port Jebel Ali in the UAE, and Duqm port in Oman. Nevatim Airbase and Tel Aviv were also hit. "
        "This wave shattered the geographic boundaries of the conflict."
    ),
    'tp4_w2': (
        "The second wave struck Tel Aviv and US bases in Iraq, confirming that the TP4 expansion to "
        "American targets was not a one-off escalation but a sustained new doctrine. The targeting of "
        "Iraq-based US forces opened a second geographic axis."
    ),
    'tp4_w3': (
        "A massive multi-axis wave targeting the Israeli naval base and warship dock in Haifa, Ramat David "
        "Air Base, the HaKirya military headquarters in Tel Aviv, and multiple US/coalition bases across "
        "Kuwait, Iraq, and Saudi Arabia. Notably, the French base Camp de la Paix in Abu Dhabi was also "
        "targeted — expanding the conflict to non-US coalition forces. Etihad Towers in Abu Dhabi and "
        "the Crowne Plaza Hotel in Manama were struck, raising civilian casualty concerns."
    ),
    'tp4_w4': (
        "Strikes on the Beit Shams and Ishtod military-industrial complexes in Israel alongside US bases "
        "in Kuwait and Iraq. The targeting of defense industrial facilities echoed TP3's attempts to "
        "degrade Israeli military production capacity."
    ),
    'tp4_w5': (
        "A maritime-focused wave targeting American vessels in the Indian Ocean and the Abdullah Mubarak "
        "naval base in Kuwait. Two missiles were reportedly fired towards British bases on Cyprus, though "
        "this was denied by the Cyprus Ministry of Defence. If confirmed, this would represent the first "
        "targeting of European territory."
    ),
    'tp4_w6': (
        "Strikes on Tel Nof Air Base, the HaKirya headquarters complex (IDF General Staff and Ministry "
        "of Defense) in Tel Aviv, and the Israeli Navy base and military naval yard in Haifa. This wave "
        "concentrated on high-value Israeli military command nodes."
    ),
    'tp4_w7': (
        "One of TP4's most geographically dispersed waves. Targets included US and British oil tankers "
        "in the Persian Gulf and Strait of Hormuz, multiple naval bases in Kuwait and Bahrain, the USS "
        "Abraham Lincoln carrier, Prince Sultan Airbase and King Khalid International Airport in Saudi Arabia, "
        "and an AWS data centre in the UAE. The targeting of cloud computing infrastructure was unprecedented."
    ),
    'tp4_w8': (
        "A continuation wave maintaining strikes on American and Israeli targets across regional US bases. "
        "The sustained tempo of TP4 — multiple waves per day — was designed to exhaust defensive systems "
        "and complicate coalition force protection."
    ),
    'tp4_w9': (
        "Multi-domain strikes on US naval assets, Israeli defense systems, and drone operations across "
        "multiple regions. RAF Akrotiri in Cyprus was struck — one drone hit the airfield and five were "
        "intercepted, causing minor damage. This confirmed the expansion of Iranian targeting to "
        "European-administered military facilities."
    ),
    'tp4_w10': (
        "A decapitation-focused wave targeting the Israeli government complex in Tel Aviv, military and "
        "security centres in Haifa, East Jerusalem, and reportedly Netanyahu's office in Tel Aviv. A Saudi "
        "Aramco facility was also targeted. The explicit targeting of political leadership marked a new "
        "threshold in Iranian escalation."
    ),
    'tp4_w11': (
        "The most geographically expansive wave of the entire conflict. Targets spanned US intelligence "
        "centres and military warehouses across the Gulf, an Israeli army communications complex in Be'er Sheva, "
        "over 20 sites in Tel Aviv, West Jerusalem, and the Galilee. Paphos Airport in Cyprus was evacuated, "
        "Akrotiri had sirens, Aramco's Ras Tanura refinery caught fire, Qatar LNG facilities were targeted, "
        "and the US-Jordanian embassy was evacuated. The wave demonstrated Iran's ability to threaten "
        "targets across an enormous geographic arc simultaneously."
    ),
    'tp4_w12': (
        "Strikes on Camp Arifjan in Kuwait, the Al Minhad command centre in the UAE, US naval facilities "
        "in Bahrain, and the fuel tanker Athens Nova in the Strait of Hormuz. Port Fujairah in the UAE, "
        "Dubai (hit by a ballistic missile), and targets in Iraqi Kurdistan including Sulaymaniyah and "
        "Erbil were also struck. The targeting of Dubai with a ballistic missile was a major escalation."
    ),
    'tp4_w13': (
        "A focused wave targeting the US Navy Marine base at Camp Arifjan and Ali Al-Salem Air Base, "
        "both in Kuwait. The concentration on Kuwait-based US forces suggested targeted pressure on a "
        "specific coalition partner."
    ),
    'tp4_w14': (
        "Strikes on Sheikh Isa Air Base in Bahrain and the US embassy in Riyadh, Saudi Arabia. Two drones "
        "struck the embassy compound causing a fire. The CIA headquarters in Riyadh was also reportedly hit "
        "by a drone. Saudi Arabia downed 9 drones. The targeting of diplomatic and intelligence facilities "
        "in a Gulf capital was a dramatic escalation."
    ),
    'tp4_w15': (
        "A wave targeting Al-Udeid Air Base in Qatar — the largest US base in the Middle East — alongside "
        "Israeli positions. The US Consulate in Al Seef, Dubai was struck by drones causing a fire. "
        "The Fujairah Oil Industry Zone in the UAE and Hamad International Airport in Qatar were also "
        "targeted. AWS cloud facilities in the UAE and Bahrain were hit, disrupting regional internet services."
    ),
    'tp4_w16': (
        "A massive wave striking the HaKirya complex (IDF General Staff and Ministry of War) in Tel Aviv, "
        "strategic infrastructure in Bnei Brak, and military targets in Beit Hakfa. Hundreds of drones "
        "were launched towards Kuwait, Iraq, Saudi Arabia, and the UAE. Greek F-16s intercepted Shahed "
        "drones near Cyprus, and Turkish air defences engaged missiles over Hatay province — drawing "
        "NATO allies into active defensive roles."
    ),
    'tp4_w17': (
        "Strikes on the Israeli Ministry of Defense building in Tel Aviv and Ben Gurion Airport. Iran "
        "claimed to have destroyed seven or more advanced US-supplied radar systems, potentially "
        "degrading Israel's early warning and tracking capabilities for subsequent waves."
    ),
    'tp4_w18': (
        "A wave in the ongoing TP4 campaign. Details of specific targeting for this wave are still being "
        "confirmed through OSINT sources."
    ),
    'tp4_w19': (
        "A wide-ranging wave targeting the Israeli Defense Ministry complex in Tel Aviv, Ben Gurion Airport, "
        "Jerusalem, and US military positions in Kuwait, Bahrain, and Qatar. The USS Abraham Lincoln carrier "
        "was targeted again, alongside an Amazon data centre in Bahrain. The repeated targeting of cloud "
        "infrastructure reflected a deliberate Iranian strategy to impose economic costs on Gulf states "
        "hosting Western digital infrastructure."
    ),
    'tp4_w20': (
        "A focused wave on Tel Aviv and surrounding central Israel. Sirens sounded across central Israel "
        "as this became the eighth Iranian attack since midnight — an unprecedented tempo of multiple "
        "waves within a single 24-hour period designed to exhaust air defense crews and deplete "
        "interceptor stocks."
    ),
    'tp4_w21': (
        "A combined strike on Tel Aviv using simultaneous drone swarms and Kheibar Shekan cluster munition "
        "missiles. This wave was specifically designed to saturate and overwhelm Israel's multi-layered "
        "air defences by forcing them to engage both slow drones and fast ballistic missiles simultaneously "
        "while cluster submunitions complicated terminal defense."
    ),
    'tp4_w22': (
        "A retaliatory wave explicitly linked to the Minab school strike in Iran. Targets included Tel Aviv, "
        "Ben Gurion Airport, Israeli Air Force military centres in Haifa, and US/Israeli positions across "
        "the Gulf including Al Udeid Air Base in Qatar and Al Dhafra Air Base in the UAE. The explicit "
        "framing as retaliation for a specific incident marked a shift in Iranian public messaging."
    ),
    'tp4_w23': (
        "A multi-country wave targeting four US bases in three countries: Sheikh Isa and NSA Bahrain/Juffair "
        "in Bahrain, Ali al-Salem in Kuwait, and al-Azraq (Muwaffaq Salti) in Jordan. In Israel, Be'er Sheva "
        "was targeted — specifically advanced technology centres, cybersecurity facilities, and military "
        "support centres. The focus on cyber/tech facilities in Be'er Sheva suggested targeting of "
        "Israel's 'Cyber Capital' cluster."
    ),
    'tp4_w24': (
        "A concentrated strike on Tel Aviv, described by Iran as targeting the heart of the occupied "
        "territories. At least three missile impacts were confirmed in Tel Aviv by Al Jazeera. The IRGC "
        "claimed strikes on strategic facilities. The high number of confirmed urban impacts indicated "
        "either improving Iranian accuracy or degraded Israeli interception capability."
    ),
    'tp4_w25': (
        "Strikes on joint US-Israeli military centres and logistical support at Al-Dhafra Air Base and "
        "Al-Minhad Air Base, both in the UAE. Iran claimed precision strikes on radar and satellite "
        "communications centres, suggesting continued SEAD operations to degrade coalition surveillance "
        "and early warning networks."
    ),
    'tp4_w26': (
        "Iran claimed targets from north to south of Israel were hit with precision. The Sdot Micha "
        "strategic military facility — believed to house Israel's nuclear-capable Jericho missile arsenal — "
        "was specifically targeted for its radar systems. Iran Army drones also struck Al-Minhad Air Base "
        "in the UAE and Camp Udairi in Kuwait, marking the regular Iranian Army's direct participation "
        "alongside the IRGC."
    ),
    'tp4_w27': (
        "Strikes on the Haifa oil refinery and US positions at Camp Udairi/Camp Buehring in Kuwait. "
        "Cluster warheads were confirmed over Israel, indicating the continued use of Kheibar Shekan "
        "or Khorramshahr-4 cluster munition variants designed to defeat terminal-phase interception "
        "by dispersing submunitions."
    ),
    'tp4_w28': (
        "Day 9 of True Promise 4. Strikes on Tel Aviv, Be'er Sheva, and Al-Azraq Air Base in Jordan. "
        "The continued targeting of Jordanian-based US assets placed pressure on Jordan's political "
        "position as a key US partner that had participated in defending Israel during TP1."
    ),
    'tp4_w29': (
        "Day 9 continued. Strikes on Tel Aviv, the Negev region, and an unspecified US airbase. "
        "As the 29th wave of TP4 and the 55th wave of the overall conflict, this wave represented "
        "a level of sustained Iranian aerial bombardment that had no precedent in modern warfare."
    ),
}


def load_all_waves():
    waves = []
    for op, path in WAVE_FILES:
        with open(path) as f:
            data = json.load(f)
        for w in data['waves']:
            w['_operation'] = op
            waves.append(w)
    return waves


def iso_to_epoch(iso_str):
    """Convert ISO 8601 timestamp to Unix epoch milliseconds (for ArcGIS time slider)."""
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str)
        return int(dt.timestamp() * 1000)
    except (ValueError, TypeError):
        return None


def build_wave_uid(w):
    """Build a globally unique wave identifier for cross-layer joins."""
    op = w.get('_operation', 'unknown')
    wn = w.get('wave_number', 0)
    return f"{op}_w{wn:02d}"


def build_wave_label(w):
    """Build a human-readable wave label for pop-ups."""
    op = OPERATION_SHORT.get(w.get('_operation'), w.get('_operation', ''))
    wn = w.get('wave_number', '?')
    codename = w.get('wave_codename_english')
    payload = w.get('weapons', {}).get('payload', '')

    if codename:
        return f"{op} Wave {wn} — {codename}"
    elif payload:
        short_payload = payload[:60] + ('...' if len(payload) > 60 else '')
        return f"{op} Wave {wn} — {short_payload}"
    else:
        return f"{op} Wave {wn}"


def build_popup_summary(w):
    """Build a compact HTML-friendly summary for ArcGIS pop-ups."""
    timing = w.get('timing', {})
    weapons = w.get('weapons', {})
    munitions = w.get('munitions', {})
    interception = w.get('interception', {})
    impact = w.get('impact', {})

    parts = []
    ts = timing.get('announced_utc') or timing.get('probable_launch_time')
    if ts:
        parts.append(f"Time: {ts}")

    payload = weapons.get('payload')
    if payload:
        parts.append(f"Payload: {payload}")

    count = munitions.get('estimated_munitions_count')
    if count:
        parts.append(f"Munitions: {count}")

    rate = interception.get('estimated_intercept_rate')
    if rate:
        parts.append(f"Intercept rate: {rate}")

    killed = impact.get('fatalities')
    wounded = impact.get('injuries')
    if killed or wounded:
        parts.append(f"Casualties: {killed or 0} killed, {wounded or 0} wounded")

    damage = impact.get('damage')
    if damage:
        short_damage = damage[:120] + ('...' if len(damage) > 120 else '')
        parts.append(f"Damage: {short_damage}")

    return ' | '.join(parts)


def get_narrative(wave_uid):
    """Get the narrative description for a wave, or a placeholder."""
    return WAVE_NARRATIVES.get(wave_uid, "Narrative pending — details being confirmed through OSINT sources.")


def arcgis_properties(w, icon_type):
    """Build ArcGIS-optimized properties."""
    timing = w.get('timing', {})
    weapons = w.get('weapons', {})
    munitions = w.get('munitions', {})
    interception = w.get('interception', {})
    impact = w.get('impact', {})
    targets = w.get('targets', {})
    ls = w.get('launch_site', {})
    tc = targets.get('target_coordinates', {})

    timestamp = timing.get('announced_utc') or timing.get('probable_launch_time')
    wave_uid = build_wave_uid(w)

    props = {
        # Unique identifier (for cross-layer joins)
        "wave_uid": wave_uid,

        # Display fields
        "operation": w.get('_operation'),
        "operation_label": OPERATION_LABELS.get(w.get('_operation'), w.get('_operation')),
        "operation_short": OPERATION_SHORT.get(w.get('_operation'), w.get('_operation')),
        "wave_number": w.get('wave_number'),
        "wave_label": build_wave_label(w),
        "narrative": get_narrative(wave_uid),
        "popup_summary": build_popup_summary(w),
        "icon_type": icon_type,

        # Time fields
        "timestamp_utc": timestamp,
        "timestamp_epoch": iso_to_epoch(timestamp),
        "conflict_day": timing.get('conflict_day'),

        # Weapons
        "payload": weapons.get('payload'),
        "drones_used": weapons.get('drones_used'),
        "ballistic_missiles_used": weapons.get('ballistic_missiles_used'),
        "cruise_missiles_used": weapons.get('cruise_missiles_used'),
        "estimated_munitions_count": munitions.get('estimated_munitions_count'),

        # Cluster munitions
        "cluster_munitions": bool(weapons.get('cluster_warhead') and (
            weapons['cluster_warhead'] is True or
            (isinstance(weapons['cluster_warhead'], dict) and
             weapons['cluster_warhead'].get('confirmed'))
        )),

        # Targeting
        "israel_targeted": targets.get('israel_targeted'),
        "us_bases_targeted": targets.get('us_bases_targeted'),
        "landing_countries_iso": ', '.join(sorted(targets.get('landings_countries', []) or [])),
        "landing_countries": ', '.join(
            sorted(COUNTRY_NAMES.get(c, c) for c in (targets.get('landings_countries', []) or []))
        ),
        "targets_description": targets.get('targets'),

        # Interception
        "interception_rate": interception.get('estimated_intercept_rate'),
        "intercepted_count": interception.get('estimated_intercept_count'),

        # Impact
        "fatalities": impact.get('fatalities'),
        "injuries": impact.get('injuries'),
        "damage": impact.get('damage'),

        # Location metadata
        "launch_site_description": ls.get('description'),
        "launch_lat": ls.get('lat'),
        "launch_lon": ls.get('lon'),
        "launch_generic": ls.get('generic_location'),
        "target_lat": tc.get('lat'),
        "target_lon": tc.get('lon'),
        "target_generic": tc.get('generic_location'),
    }

    # Target type booleans
    props.update(classify_target_types(w))

    return props


def make_point(lat, lon):
    if lat is not None and lon is not None:
        return {"type": "Point", "coordinates": [lon, lat]}
    return None


def make_line(lat1, lon1, lat2, lon2):
    if all(v is not None for v in [lat1, lon1, lat2, lon2]):
        return {"type": "LineString", "coordinates": [[lon1, lat1], [lon2, lat2]]}
    return None


def feature_collection(features):
    return {"type": "FeatureCollection", "features": features}


def main():
    parser = argparse.ArgumentParser(description='Build ArcGIS StoryMap exports')
    parser.add_argument('--output-dir', default=os.path.join(REPO, 'exports', 'latest'),
                        help='Output directory')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    waves = load_all_waves()

    launch_features = []
    target_features = []
    trajectory_features = []
    csv_rows = []

    for w in waves:
        ls = w.get('launch_site', {})
        tc = w.get('targets', {}).get('target_coordinates', {})

        launch_props = arcgis_properties(w, 'launch')
        target_props = arcgis_properties(w, 'target')

        # Launch site point
        launch_geom = make_point(ls.get('lat'), ls.get('lon'))
        launch_features.append({
            "type": "Feature",
            "geometry": launch_geom,
            "properties": launch_props,
        })

        # Target point
        target_geom = make_point(tc.get('lat'), tc.get('lon'))
        target_features.append({
            "type": "Feature",
            "geometry": target_geom,
            "properties": target_props,
        })

        # Trajectory line (launch → target)
        traj_geom = make_line(ls.get('lat'), ls.get('lon'),
                              tc.get('lat'), tc.get('lon'))
        if traj_geom:
            traj_props = arcgis_properties(w, 'trajectory')
            trajectory_features.append({
                "type": "Feature",
                "geometry": traj_geom,
                "properties": traj_props,
            })

        # CSV row
        csv_rows.append(launch_props)

    # Write GeoJSON layers
    outputs = [
        ('arcgis_launch_sites', launch_features),
        ('arcgis_targets', target_features),
        ('arcgis_trajectories', trajectory_features),
    ]
    for name, features in outputs:
        path = os.path.join(args.output_dir, f'{name}.geojson')
        with open(path, 'w') as f:
            json.dump(feature_collection(features), f, indent=2, ensure_ascii=False)
        geo_count = sum(1 for feat in features if feat['geometry'] is not None)
        print(f"  {path}: {len(features)} features ({geo_count} with geometry)")

    # Write CSV
    csv_path = os.path.join(args.output_dir, 'arcgis_waves.csv')
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"  {csv_path}: {len(csv_rows)} rows")

    print(f"\nDone — {len(waves)} waves, {len(trajectory_features)} trajectories.")


if __name__ == '__main__':
    main()
