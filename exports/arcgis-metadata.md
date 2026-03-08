
## Disclaimer (include in all layer descriptions)

This dataset uses the Iranian operational designations "True Promise" (Hebrew: ועדה צדיקה, Farsi: وعده صادق) for standardisation and cross-referencing purposes only. Use of these terms carries no endorsement of Iranian military operations, strategic narratives, or political framing. This is an independent OSINT research dataset.

Most coordinates in this dataset are **approximate**. The majority of launch sites are placed at provincial or regional centroids rather than exact facility locations. Target coordinates are similarly approximate, typically representing city centres or known base locations rather than precise impact points. The `generic_location` flag (true/false) on each feature indicates whether coordinates are approximate centroids or specifically geolocated.

This dataset is a **point-in-time snapshot** and does not represent a complete record. The conflict referenced in this data is ongoing.

---

## Launch Sites

**Title:** Iranian Missile & Drone Launch Sites — True Promise Operations 1–4 (55 Waves Through 8 Mar 2026)

**Summary:** OSINT-derived approximate launch origin points for 55 Iranian attack waves through Wave 29 of True Promise 4 (data current as of 8 March 2026). Covers ballistic missiles, cruise missiles, and Shahed-series drones launched from sites across western and central Iran. Most coordinates are approximate provincial/regional centroids. The conflict is ongoing and this dataset does not represent a complete record.

**Description:** Point layer representing the approximate launch origins of 55 Iranian attack waves across four military operations: True Promise 1 (Apr 2024, 2 waves), True Promise 2 (Oct 2024, 2 waves), True Promise 3 (Jun 2025, 22 waves), and True Promise 4 (Feb–Mar 2026, 29 waves through Wave 29). True Promise 4 is ongoing — this layer reflects data available as of 8 March 2026 and will be updated as new waves occur. Weapon systems include Emad, Ghadr, Kheibar Shekan, Fattah-1/2 hypersonic, Sejjil, Khorramshahr-4, Shahed-136/131/238, and Paveh cruise missiles. IMPORTANT: The majority of launch site coordinates are approximate, placed at provincial or regional centroids rather than exact facility locations. The generic_location flag on each feature indicates whether coordinates are an approximate centroid (true) or specifically geolocated (false). Each feature includes operation and wave identifiers, human-readable labels, ISO 8601 and epoch timestamps for time slider animation, weapon payload descriptions, munitions counts, interception rates, and casualty figures. The "True Promise" operational designations are used for standardisation and cross-referencing only and carry no endorsement of Iranian military operations or narratives. Source: OSINT dataset at github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data.

---

## Targets

**Title:** Israeli & US/Coalition Targets — Iranian True Promise Operations 1–4 (50 Approximate Locations Through 8 Mar 2026)

**Summary:** OSINT-derived approximate target and impact points for Iranian attack waves through Wave 29 of True Promise 4 (data current as of 8 March 2026). Covers Israeli cities, IDF bases, US military installations in the Gulf, and naval assets. Most coordinates are approximate city/base centroids. The conflict is ongoing and this dataset does not represent a complete record.

**Description:** Point layer representing the approximate target locations of 55 Iranian attack waves (50 with coordinates, 5 with null geometry where target location is unconfirmed). This data covers through Wave 29 of True Promise 4 — the conflict is ongoing and additional waves may have occurred since this export. Targets span Israeli cities (Tel Aviv, Haifa, Jerusalem, Be'er Sheva, Nevatim, Ramat David), US/coalition military installations (Al Udeid, Al Dhafra, Camp Arifjan, Muwaffaq Salti, NSA Bahrain), and naval assets across the Gulf and Mediterranean. Munitions landed in 12 countries including Israel, Jordan, Iraq, Saudi Arabia, UAE, Kuwait, Bahrain, and Qatar. IMPORTANT: Most target coordinates are approximate, representing city centres or known base locations rather than precise impact points. The generic_location flag distinguishes approximate centroids (true) from specifically geolocated sites (false). Each feature includes interception rates, casualty counts, damage assessments, and epoch timestamps for time slider animation. The "True Promise" operational designations are used for standardisation and cross-referencing only and carry no endorsement of Iranian military operations or narratives. Source: OSINT dataset at github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data.

---

## Trajectories

**Title:** Launch-to-Target Trajectory Arcs — Iranian Strikes Across True Promise 1–4 (50 Approximate Vectors Through 8 Mar 2026)

**Summary:** Approximate straight-line arcs connecting Iranian launch sites to their targets in Israel and the Gulf through Wave 29 of True Promise 4 (data current as of 8 March 2026). These are visualisation approximations, not flight paths. Both endpoints use mostly approximate coordinates. The conflict is ongoing.

**Description:** LineString layer with 50 arcs connecting each attack wave's approximate launch origin in Iran to its approximate target location. These are straight-line approximations for visualisation purposes only — they do not represent actual flight paths, ballistic trajectories, or radar tracks. Both launch and target endpoints are predominantly approximate coordinates (provincial centroids and city centres), so arcs should be understood as general directional indicators rather than precise vectors. This data covers through Wave 29 of True Promise 4 — the conflict is ongoing. Arcs illustrate the geographic expansion from Israel-only targeting in True Promise 1–3 to multi-country targeting of US/coalition assets across the Gulf and Mediterranean in True Promise 4. Each feature carries enriched properties: operation labels, wave labels, popup summaries, epoch timestamps, weapon payloads, munitions counts, interception rates, and casualty data. Only waves with both launch and target coordinates are included (50 of 55). The "True Promise" operational designations are used for standardisation and cross-referencing only and carry no endorsement of Iranian military operations or narratives. Source: OSINT dataset at github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data.

---

## Waves CSV

**Title:** Iranian Attack Waves — Flat Table with Approximate Coordinates (55 Waves Through 8 Mar 2026, 32 Fields)

**Summary:** Tabular export of 55 Iranian attack waves through Wave 29 of True Promise 4 (data current as of 8 March 2026) with approximate launch and target lat/lon columns, weapon data, interception performance, and casualty figures. Designed for ArcGIS Online import. Most coordinates are approximate. The conflict is ongoing.

**Description:** Flat CSV containing 55 rows and 32 columns covering Iranian attack waves from True Promise 1 through Wave 29 of True Promise 4 (data as of 8 March 2026 — the conflict is ongoing and this does not represent a complete record). Each row includes launch_lat/launch_lon and target_lat/target_lon columns for ArcGIS geocoding on import, along with operation labels, wave labels, popup summaries, epoch timestamps, weapon payloads, munitions counts, interception rates, casualty figures, and damage assessments. IMPORTANT: Most coordinates are approximate, representing provincial centroids (launch sites) or city/base centres (targets) rather than precisely geolocated points. The generic_location flags indicate coordinate precision. This is a fallback format for environments where GeoJSON import is unavailable — it produces point data only (no trajectory arcs). For full layer separation and trajectory visualisation, use the companion GeoJSON files. The "True Promise" operational designations are used for standardisation and cross-referencing only and carry no endorsement of Iranian military operations or narratives. Source: OSINT dataset at github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data.
