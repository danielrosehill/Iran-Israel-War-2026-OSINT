---
name: New Data
about: Add new waves, events, BDA assessments, SATINT observations, or reference data
title: 'data: [brief description]'
labels: new-data
---

## What are you adding?

- [ ] New attack wave(s)
- [ ] New event(s) within an existing wave (interception/strike/impact)
- [ ] BDA / post-battle damage assessment
- [ ] SATINT observation (satellite imagery analysis)
- [ ] New or updated reference data (weapon system, defense system, interceptor munition, etc.)
- [ ] Cost estimate data
- [ ] Other: _______________

## Data summary

<!-- Brief description of what data is being added -->

**Operation:** TP__
**Wave(s):** ___
**Event count:** ___

## Source(s)

<!-- All new data must be sourced from OSINT. List all sources used. -->

1.
2.
3.

### Source quality

- [ ] Official government/military statement
- [ ] Satellite imagery (provider: _____________)
- [ ] Established news agency (AP, Reuters, AFP, etc.)
- [ ] OSINT analyst / think tank (name: _____________)
- [ ] Social media (supplementary only — not sole source)

## Competing claims

<!-- If this data involves events where parties disagree, have you recorded both sides? -->

- [ ] Not applicable — data is not disputed
- [ ] Yes — `iranian_claim`, `israeli_claim`, and/or `us_claim` fields are populated
- [ ] Yes — `outcome_status` is set to `disputed` where appropriate
- [ ] Yes — `event_type` is set to `impact` (not `strike`) for contested ground events

## Confidence assessment

<!-- What confidence level did you assign and why? -->

- Confidence level(s) used: `confirmed` / `probable` / `unconfirmed`
- Rationale:

## Schema compliance

- [ ] New data follows `data/schema/wave.schema.json`
- [ ] All required fields are populated (`event_type`, `location_name`, `wave_number`, etc.)
- [ ] Coordinates are in decimal degrees (WGS84)
- [ ] Timestamps are ISO 8601 with timezone offset
- [ ] Country codes are ISO 3166-1 alpha-2
- [ ] Booleans are native JSON `true`/`false` (not strings)
- [ ] Missing values use `null` (not empty strings)

## Build verification

- [ ] I ran `python3 scripts/build_db.py` and it completed without errors
- [ ] Row counts in the build summary look correct

## Additional context

<!-- Satellite imagery links, screenshots, maps, or any supporting material -->
