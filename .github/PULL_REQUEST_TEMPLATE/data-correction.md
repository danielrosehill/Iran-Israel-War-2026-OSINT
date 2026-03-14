---
name: Data Correction
about: Correct an error in existing dataset entries
title: 'fix: [brief description]'
labels: data-correction
---

## What is incorrect?

<!-- Identify the exact file, field, and current (wrong) value -->

- **File:** `data/tp_-____/waves.json` or `data/reference/_____.json`
- **Location:** Operation ___, Wave ___, field `_____`
- **Current value:**
- **Correct value:**

## Source(s) for correction

<!-- At least one OSINT source is required. More is better. -->

1.
2.

## Is this a disputed fact?

<!-- If Iran and Israel disagree on this data point, both claims should be recorded. -->

- [ ] No — this is a factual error (wrong coordinates, typo, wrong weapon name, etc.)
- [ ] Yes — this corrects a one-sided claim to include the other party's position
- [ ] Yes — this updates a claim based on new independent BDA/SATINT evidence

## If disputed, provide both sides

- **Iranian/IRGC claim:**
- **Israeli/IDF claim:**
- **Independent BDA (if available):**

## Build verification

- [ ] I ran `python3 scripts/build_neo4j.py --clear` and it completed without errors
- [ ] The correction does not break any existing data relationships

## Additional context

<!-- Any other relevant information about why this correction is needed -->
