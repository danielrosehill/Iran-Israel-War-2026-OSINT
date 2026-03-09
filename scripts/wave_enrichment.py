"""
Shared wave enrichment logic used by build_arcgis.py, build_db.py, and build_kaggle.py.

Provides:
  - classify_target_types(wave) → dict of 10 target-type booleans
  - get_cluster_munitions(wave) → bool
  - countries_iso_to_names(iso_list) → str of readable country names
  - get_wave_uid(operation, wave_number) → str unique ID
  - WAVE_NARRATIVES → dict of wave_uid → narrative text
  - COUNTRY_NAMES → dict of ISO alpha-2 → readable name
"""

# ---------------------------------------------------------------------------
# Country code mapping (alphabetical by name)
# ---------------------------------------------------------------------------

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


def countries_iso_to_names(iso_list):
    """Convert a list of ISO country codes to sorted readable names string."""
    if not iso_list:
        return ''
    return ', '.join(sorted(COUNTRY_NAMES.get(c, c) for c in iso_list))


def get_wave_uid(operation, wave_number):
    """Build a globally unique wave identifier for cross-layer joins."""
    return f"{operation}_w{wave_number:02d}"


# ---------------------------------------------------------------------------
# Target-type classification keywords
# ---------------------------------------------------------------------------

_IAF_BASE = [
    'nevatim', 'ramon', 'tel nof', 'hatzerim', 'ramat david', 'ovda',
    'israeli air force', 'iaf', 'air base', 'airbase',
]

_US_BASE = [
    'al udeid', 'al-udeid', 'al dhafra', 'al-dhafra', 'camp arifjan',
    'ali al-salem', 'ali al salem', 'sheikh isa', 'harir', 'al minhad',
    'al-minhad', 'muwaffaq salti', 'al-azraq', 'camp udairi', 'camp buehring',
    'prince sultan', 'us base', 'us air base', 'american base', 'us military',
    'abdullah al-mubarak', 'abdullah mubarak', 'juffair', 'nsa bahrain',
]

_NAVAL_BASE = [
    'naval base', 'naval yard', 'mina salman', 'mohammed al-ahmad',
    'naval facility', 'navy base', 'port jebel ali', 'naval port',
]

_NAVAL_VESSEL = [
    'uss ', 'tanker', 'vessel', 'warship', 'navy marine',
    'ammunition ship', 'fuel support ship', 'naval asset',
]

_GOV_C2 = [
    'hakirya', 'ha-kirya', 'ministry of war', 'ministry of defense',
    'defence ministry', 'defense ministry', 'general staff', 'c2',
    'command center', 'command centre', 'government complex',
    'netanyahu', 'mossad', 'unit 8200', 'glilot',
]

_MIL_INDUSTRIAL = [
    'military-industrial', 'military industrial', 'rafael', 'semiconductor',
    'beit shams', 'ishtod', 'weapons', 'defense industry', 'defence industry',
    'military industry',
]

_INTELLIGENCE = [
    'intelligence', 'cia', 'unit 8200', 'radar', 'satellite comms',
    'communications complex', 'cybersecurity', 'advanced technology',
]

_CIVILIAN_INFRA = [
    'oil refinery', 'power plant', 'airport', 'ben gurion', 'data center',
    'data centre', 'aws', 'amazon', 'lng', 'aramco', 'fujairah oil',
    'hamad international', 'paphos airport', 'king khalid', 'pipeline',
]

_CIVILIAN_AREA = [
    'residential', 'civilian', 'cities', 'bat yam', 'bnei brak',
    'crowne plaza', 'etihad towers', 'hotel', 'heart of',
]

_DIPLOMATIC = [
    'embassy', 'consulate', 'diplomatic',
]


def classify_target_types(wave):
    """Classify target types from wave target description and structured fields."""
    targets = wave.get('targets', {})
    desc = (targets.get('targets') or '').lower()
    us_bases = targets.get('us_bases') or []
    naval = targets.get('us_naval_vessels') or []

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

    def has(keywords, text=combined):
        return any(kw in text for kw in keywords)

    return {
        'target_iaf_base': has(_IAF_BASE, desc),
        'target_us_base': has(_US_BASE) or len(us_bases) > 0,
        'target_naval_base': has(_NAVAL_BASE),
        'target_naval_vessel': has(_NAVAL_VESSEL) or len(naval) > 0,
        'target_government_c2': has(_GOV_C2, desc),
        'target_military_industrial': has(_MIL_INDUSTRIAL, desc),
        'target_intelligence': has(_INTELLIGENCE, desc),
        'target_civilian_infrastructure': has(_CIVILIAN_INFRA, desc),
        'target_civilian_area': has(_CIVILIAN_AREA, desc),
        'target_diplomatic': has(_DIPLOMATIC),
    }


def get_cluster_munitions(wave):
    """Return True if cluster munitions were confirmed for this wave."""
    cw = wave.get('weapons', {}).get('cluster_warhead')
    if cw is True:
        return True
    if isinstance(cw, dict) and cw.get('confirmed'):
        return True
    return False


# ---------------------------------------------------------------------------
# Narrative descriptions for each wave
# ---------------------------------------------------------------------------

WAVE_NARRATIVES = {
    # --- TP1 ---
    'tp1_w01': (
        "The first wave of Iran's inaugural direct attack on Israel. Launched on the night of 13 April 2024, "
        "this wave comprised a large combined salvo of Shahed-136 drones, ballistic missiles, and cruise missiles "
        "targeting Nevatim Airbase and sites across the Negev desert and Israeli-occupied Golan Heights. "
        "The attack was widely telegraphed in advance, giving Israel, the US, UK, France, and Jordan time to "
        "coordinate a multilayered defensive response. The overwhelming majority of munitions were intercepted."
    ),
    'tp1_w02': (
        "The second and final wave of True Promise 1, continuing the bombardment of Nevatim Airbase and "
        "the Ramon Airbase area in the Negev. This wave followed the initial drone/missile salvo by several hours, "
        "with ballistic missiles arriving after the slower drones. Minor damage was reported at Nevatim. "
        "The combined two-wave attack involved approximately 320 munitions — the largest single aerial assault "
        "in the region's history at the time. Israel's multi-tier defense (Arrow, David's Sling, Iron Dome) "
        "achieved a near-total interception rate with coalition support."
    ),

    # --- TP2 ---
    'tp2_w01': (
        "True Promise 2 opened with a ballistic-missile-only salvo on 1 October 2024, a significant tactical "
        "shift from TP1's mixed drone/missile approach. Approximately 180–200 Emad and Ghadr ballistic missiles "
        "targeted Nevatim, Tel Nof, and Hatzerim airbases. The absence of slow-moving drones meant defenders "
        "had far less warning time. Some missiles penetrated Israeli defenses, impacting near Nevatim."
    ),
    'tp2_w02': (
        "The second wave of TP2 targeted the Mossad/Unit 8200 headquarters complex at Glilot north of Tel Aviv, "
        "marking the first Iranian strike aimed at Israeli intelligence infrastructure. Nevatim and Tel Nof "
        "airbases were also targeted again. Two fatalities were reported — the first confirmed deaths from "
        "a direct Iranian strike on Israel. The all-ballistic approach of TP2 demonstrated Iran's evolving "
        "understanding that fast-moving missiles were more effective at penetrating Israeli defenses than "
        "the mixed salvos of TP1."
    ),

    # --- TP3 ---
    'tp3_w01': (
        "The opening salvo of the Twelve-Day War. Launched on 13 June 2025, this wave targeted military "
        "centres and air bases across Israel with ballistic missiles. It marked the beginning of Iran's "
        "most sustained aerial campaign to date, which would continue for 22 waves over 12 days."
    ),
    'tp3_w02': (
        "The second wave shifted targeting to Haifa and the Galilee region in northern Israel, expanding "
        "the geographic scope beyond the southern airbases that dominated TP1 and TP2. Ballistic missiles "
        "were used alongside drone swarms for the first time in TP3."
    ),
    'tp3_w03': (
        "A significant wave that Iran claimed penetrated multiple Israeli defense layers and struck targets "
        "in the occupied territories. This represented an escalation in Iranian rhetoric about the "
        "effectiveness of their strikes."
    ),
    'tp3_w04': (
        "A multi-city bombardment targeting both Tel Aviv and Haifa simultaneously, forcing Israel to "
        "defend across a wide geographic front. This dual-axis approach became a hallmark of TP3's "
        "middle waves."
    ),
    'tp3_w05': (
        "This wave marked the first targeting of critical civilian infrastructure — specifically the Haifa "
        "oil refinery — alongside military targets. The expansion to economic infrastructure signalled "
        "an escalation in Iranian targeting doctrine."
    ),
    'tp3_w06': (
        "A wave targeting Israeli command and control centres in Haifa and Tel Aviv. Bat Yam, south of "
        "Tel Aviv, was struck — one of the first confirmed impacts in a densely populated residential area "
        "during TP3."
    ),
    'tp3_w07': (
        "Iran claimed this wave used enhanced intelligence-guided targeting against Tel Aviv and Haifa, "
        "suggesting improved battle damage assessment and target refinement from earlier waves. This "
        "indicated a feedback loop between Iranian ISR and strike planning."
    ),
    'tp3_w08': (
        "Targeting described as strategic and sensitive sites in Tel Aviv and Haifa, with specific focus "
        "on C2 (command and control) systems. The progressive focus on C2 nodes suggested an attempt "
        "to degrade Israeli coordination capabilities."
    ),
    'tp3_w09': (
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
    'tp4_w01': (
        "The opening wave of True Promise 4 on 28 February 2026 marked a fundamental expansion of "
        "Iran's targeting doctrine. For the first time, US military facilities in the Persian Gulf were "
        "targeted alongside Israeli sites — including the USN Fifth Fleet headquarters in Bahrain, "
        "Port Jebel Ali in the UAE, and Duqm port in Oman. Nevatim Airbase and Tel Aviv were also hit. "
        "This wave shattered the geographic boundaries of the conflict."
    ),
    'tp4_w02': (
        "The second wave struck Tel Aviv and US bases in Iraq, confirming that the TP4 expansion to "
        "American targets was not a one-off escalation but a sustained new doctrine. The targeting of "
        "Iraq-based US forces opened a second geographic axis."
    ),
    'tp4_w03': (
        "A massive multi-axis wave targeting the Israeli naval base and warship dock in Haifa, Ramat David "
        "Air Base, the HaKirya military headquarters in Tel Aviv, and multiple US/coalition bases across "
        "Kuwait, Iraq, and Saudi Arabia. Notably, the French base Camp de la Paix in Abu Dhabi was also "
        "targeted — expanding the conflict to non-US coalition forces. Etihad Towers in Abu Dhabi and "
        "the Crowne Plaza Hotel in Manama were struck, raising civilian casualty concerns."
    ),
    'tp4_w04': (
        "Strikes on the Beit Shams and Ishtod military-industrial complexes in Israel alongside US bases "
        "in Kuwait and Iraq. The targeting of defense industrial facilities echoed TP3's attempts to "
        "degrade Israeli military production capacity."
    ),
    'tp4_w05': (
        "A maritime-focused wave targeting American vessels in the Indian Ocean and the Abdullah Mubarak "
        "naval base in Kuwait. Two missiles were reportedly fired towards British bases on Cyprus, though "
        "this was denied by the Cyprus Ministry of Defence. If confirmed, this would represent the first "
        "targeting of European territory."
    ),
    'tp4_w06': (
        "Strikes on Tel Nof Air Base, the HaKirya headquarters complex (IDF General Staff and Ministry "
        "of Defense) in Tel Aviv, and the Israeli Navy base and military naval yard in Haifa. This wave "
        "concentrated on high-value Israeli military command nodes."
    ),
    'tp4_w07': (
        "One of TP4's most geographically dispersed waves. Targets included US and British oil tankers "
        "in the Persian Gulf and Strait of Hormuz, multiple naval bases in Kuwait and Bahrain, the USS "
        "Abraham Lincoln carrier, Prince Sultan Airbase and King Khalid International Airport in Saudi Arabia, "
        "and an AWS data centre in the UAE. The targeting of cloud computing infrastructure was unprecedented."
    ),
    'tp4_w08': (
        "A continuation wave maintaining strikes on American and Israeli targets across regional US bases. "
        "The sustained tempo of TP4 — multiple waves per day — was designed to exhaust defensive systems "
        "and complicate coalition force protection."
    ),
    'tp4_w09': (
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
