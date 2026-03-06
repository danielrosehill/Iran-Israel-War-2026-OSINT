# Dataset Scope Statement

## What This Dataset Covers

This open-source dataset structures publicly available data on **Iranian missile and drone attack waves** against Israel and US/coalition targets, and the **defensive response** to those attacks.

Specifically, the dataset tracks:

- **Iranian attack waves** — timing, weapon systems used, launch sites, targets, munitions counts
- **Interception events** — which defense systems engaged, interception method, interceptor munitions used, phase of interception, intercepting force
- **Strike/impact events** — where munitions reached the ground, damage, casualties, coordinates
- **Competing claims** — what Iran/IRGC, Israel/IDF, and US/CENTCOM each claimed about specific events
- **Post-battle damage assessment (BDA)** — independent third-party assessments from satellite imagery (SATINT), ground reporting, and open-source analysis
- **Reference data** — Iranian weapon systems, coalition defense systems, interceptor munitions, armed forces, US bases, naval vessels

## What Is Out of Scope

- **Israeli and coalition offensive operations** — strikes on Iranian territory (e.g., Operation Epic Fury / Roaring Lion), IDF operations in Gaza/Lebanon, or other coalition military actions are **not tracked** in this dataset
- **Proxy group offensive operations** — Hezbollah, Houthi, or Iraqi militia attacks on Israel are not covered except where they are explicitly coordinated as part of an Iranian True Promise wave
- **Diplomatic, political, or economic dimensions** — sanctions, negotiations, domestic politics
- **Classified or non-public intelligence** — this dataset relies exclusively on open-source information (OSINT)

## Analytical Companion

For OSINT analysis, commentary, and visualizations built on this dataset, see the companion site repository:

- **Repo:** `danielrosehill/Iran-Israel-OSINT-Site` (private)
- **Live site:** `iranisrael.danielrosehill.com`

## Neutrality

This dataset aims to be factually neutral. Where Iran and Israel make contradictory claims about specific events, both claims are recorded verbatim alongside independent BDA assessments. The `outcome_status` field explicitly marks events as `confirmed`, `disputed`, or `unverified`. The dataset does not editorialize on whose claims are correct.
