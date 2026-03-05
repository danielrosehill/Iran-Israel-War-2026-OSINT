# SITREP Template — Iran-Israel OSINT

All SITREPs generated for this project must conform to this template. SITREPs are narrative intelligence documents, not just data tables. Each section should read as prose written in the third person, past tense, using precise language.

## Conventions

- **SITREP** is always fully capitalised
- All times in **UTC** with local times (Israel: Asia/Jerusalem, Iran: Asia/Tehran) in parentheses where relevant
- Date-Time Group (DTG) format: `DD HHMM(Z) MON YYYY` (e.g., `05 0530Z MAR 2026`)
- Coordinates in decimal degrees where referenced
- Weapon system names use canonical spellings (Emad, Ghadr, Sejjil, Kheibar Shekan, Fattah-1, Shahed-136, etc.)
- Unverified claims attributed to source (e.g., "IRGC claimed...", "IDF stated...")
- Numbers spelled out below 10 except for casualties, munitions counts, and technical data

## Template Structure

```
SITREP #{number} — {Date display}
DTG: {DD HHMM(Z) MON YYYY}
Period: {start DTG} to {end DTG}
Classification: UNCLASSIFIED // OSINT
Operation(s): {TP3 / TP4}

---

1. BLUF (Bottom Line Up Front)

A single paragraph (3-5 sentences) summarizing the most critical developments
of the reporting period. Lead with the highest-impact event. Include:
total waves, estimated total munitions, key targets hit, casualty summary,
and any escalatory developments.

---

2. SITUATION OVERVIEW

Narrative paragraph(s) providing context for the day's activity within the
broader operation. Reference the conflict day number, cumulative wave count,
and how today's activity compares to the operational tempo of preceding days.
Note any shifts in targeting doctrine, weapon mix, or geographic scope.

---

3. ENEMY FORCES — Attack Wave Activity

For each wave recorded during the period:

### Wave {N} — DTG: {DD HHMM(Z) MON YYYY}
  (Local: {HH:MM IST} Israel / {HH:MM IRST} Iran)

- **Weapon systems employed:** {List specific systems: Emad MRBM, Shahed-136, etc.}
- **Estimated munitions:** {count or "not confirmed"}
- **Launch origin:** {description, coordinates if known}
- **Target set:** {narrative description of intended targets}
- **Countries affected:** {ISO codes and names}
- **Proxy involvement:** {Yes/No — if yes, describe}

---

4. FRIENDLY FORCES — Interception & Defense

Narrative paragraph(s) describing coalition defensive response. For each wave:

- Which defense systems engaged (Arrow-2, Arrow-3, THAAD, Iron Dome, Patriot, Aegis SM-3, etc.)
- Which nations participated in interception (Israel, US, UK, Jordan, France, UAE, etc.)
- Estimated interception rate and count (if available)
- Exoatmospheric vs. endoatmospheric intercepts
- Any notable interception events (first combat use, failures, etc.)

---

5. CASUALTIES & DAMAGE ASSESSMENT

- **Fatalities:** {count} ({civilian/military breakdown if known})
- **Injuries:** {count}
- **Infrastructure damage:** Narrative description of confirmed damage to
  military installations, civilian infrastructure, critical facilities.
  Attribute damage reports to sources (satellite imagery, IDF statements,
  Iranian claims, media reports).

---

6. ESCALATION INDICATORS

Note any escalatory developments observed during the period:
- New countries targeted for the first time
- New weapon systems employed for the first time
- Shifts in targeting doctrine (civilian vs. military, Israeli vs. US/coalition)
- Proxy coordination changes
- Significant political/diplomatic developments

---

7. OUTLOOK & ASSESSMENT

1-2 paragraphs of forward-looking assessment based on observed patterns:
- Expected near-term operational tempo
- Potential target sets based on precedent
- Defense posture implications

---

CLASSIFICATION: UNCLASSIFIED // OSINT
PREPARED BY: AI (Claude) — NOT REVIEWED BY HUMAN ANALYST
GENERATED: {timestamp UTC}
DATA SOURCE: Iran-Israel War 2026 Data (github.com/danielrosehill/Iran-Israel-War-2026-Data)
```

## Notes for Generator

- If data for a section is unavailable, include the section header with "No confirmed data available for this reporting period." Do not omit sections.
- The SITREP should read as a coherent narrative document, not a collection of data fields. Connect facts with analytical prose.
- When multiple waves occur on the same day, the Situation Overview should describe the day's pattern (e.g., "Iran launched two waves in rapid succession, separated by three hours, suggesting a coordinated dual-salvo approach").
- Always note the cumulative wave count and where this day falls within the broader operation timeline.
