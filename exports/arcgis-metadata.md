# ArcGIS Online Item Metadata

Copy-paste text for the Title, Summary, and Description fields when uploading layers to ArcGIS Online.

---

## Launch Sites

**Title:** Iranian Missile & Drone Launch Sites Across 4 True Promise Operations (55 Waves, 2024–2026)

**Summary:** OSINT-derived launch origin points for all 55 Iranian attack waves spanning True Promise 1 through True Promise 4. Covers ballistic missiles, cruise missiles, and Shahed-series drones launched from sites across western and central Iran between April 2024 and March 2026.

**Description:** Point layer representing the launch origins of 55 Iranian attack waves across four military operations: True Promise 1 (Apr 2024, 2 waves), True Promise 2 (Oct 2024, 2 waves), True Promise 3 (Jun 2025, 22 waves), and True Promise 4 (Feb–Mar 2026, 29 waves). Weapon systems include Emad, Ghadr, Kheibar Shekan, Fattah-1/2 hypersonic, Sejjil, Khorramshahr-4, Shahed-136/131/238, and Paveh cruise missiles. Each feature includes operation and wave identifiers, human-readable labels, ISO 8601 and epoch timestamps for time slider animation, weapon payload descriptions, munitions counts, interception rates, and casualty figures. The generic_location flag indicates whether coordinates represent an approximate provincial centroid or a specifically geolocated launch site. Source: OSINT dataset at github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data.

---

## Targets

**Title:** Israeli & US/Coalition Targets Struck in Iranian True Promise Operations (50 Geolocated Impact Sites, 2024–2026)

**Summary:** OSINT-derived target and impact points for Iranian attack waves across True Promise 1–4. Covers Israeli cities, IDF bases, US military installations in the Gulf, and naval assets in the Mediterranean and Arabian Sea.

**Description:** Point layer representing the target locations of 55 Iranian attack waves (50 with confirmed coordinates, 5 with null geometry where target location is unconfirmed). Targets span Israeli cities (Tel Aviv, Haifa, Jerusalem, Be'er Sheva, Nevatim, Ramat David), US/coalition military installations (Al Udeid, Al Dhafra, Camp Arifjan, Muwaffaq Salti, NSA Bahrain), and naval assets across the Gulf and Mediterranean. Munitions landed in 12 countries including Israel, Jordan, Iraq, Saudi Arabia, UAE, Kuwait, Bahrain, and Qatar. Each feature includes interception rates, casualty counts, damage assessments, and epoch timestamps for time slider animation. The generic_location flag distinguishes approximate city centroids from specifically geolocated impact sites. Source: OSINT dataset at github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data.

---

## Trajectories

**Title:** Launch-to-Target Trajectory Arcs for Iranian Strikes Across True Promise 1–4 (50 Attack Vectors, 2024–2026)

**Summary:** Straight-line arcs connecting Iranian launch sites to their targets in Israel and the Gulf, visualizing the geographic reach and escalation pattern across four operations and 50 confirmed attack vectors.

**Description:** LineString layer with 50 arcs connecting each attack wave's launch origin in Iran to its target location. These are great-circle approximations for visualization, not actual flight paths or ballistic trajectories. Arcs illustrate the geographic expansion from Israel-only targeting in True Promise 1–3 to multi-country targeting of US/coalition assets across the Gulf and Mediterranean in True Promise 4. Each feature carries enriched properties: operation labels, wave labels, popup summaries, epoch timestamps, weapon payloads, munitions counts, interception rates, and casualty data. Only waves with both confirmed launch and target coordinates are included (50 of 55). Source: OSINT dataset at github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data.

---

## Waves CSV

**Title:** All Iranian Attack Waves — Flat Table with Coordinates for ArcGIS Import (55 Waves, 32 Fields, 2024–2026)

**Summary:** Tabular export of all 55 Iranian attack waves with launch and target lat/lon columns, weapon data, interception performance, and casualty figures. Designed for drag-and-drop import into ArcGIS Online.

**Description:** Flat CSV containing 55 rows and 32 columns covering all Iranian attack waves from True Promise 1 through True Promise 4. Each row includes launch_lat/launch_lon and target_lat/target_lon columns for ArcGIS geocoding on import, along with operation labels, wave labels, popup summaries, epoch timestamps, weapon payloads, munitions counts, interception rates, casualty figures, and damage assessments. This is a fallback format for environments where GeoJSON import is unavailable — it produces point data only (no trajectory arcs). For full layer separation and trajectory visualization, use the companion GeoJSON files. Source: OSINT dataset at github.com/danielrosehill/Iran-Israel-War-2026-OSINT-Data.
