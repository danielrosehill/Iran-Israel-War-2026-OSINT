#!/usr/bin/env python3
"""
Generate all 10 report charts for the TP3 vs TP4 comparative analysis.
Run from repo root with the .venv activated.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.gridspec as gridspec

# ── Load data ────────────────────────────────────────────────────────────────

with open('data/tp3-2025/waves.json') as f:
    tp3_data = json.load(f)

with open('data/tp4-2026/waves.json') as f:
    tp4_data = json.load(f)

tp3 = tp3_data['waves']
tp4 = tp4_data['waves']

N3 = len(tp3)   # 22
N4 = len(tp4)   # 19

# ── Style ─────────────────────────────────────────────────────────────────────

TP3_COLOR = '#2563EB'   # blue
TP4_COLOR = '#DC2626'   # red
ACCENT = '#F59E0B'      # amber

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

import os
from datetime import datetime

_today = datetime.now().strftime('%d%m')  # DDMM format, e.g. "0503" for Mar 5
OUT = f'report/{_today}/'

# ── Helper functions ──────────────────────────────────────────────────────────

def check_weapon_type(wave, key):
    return wave.get('weapons', {}).get('types', {}).get(key) is True

def check_weapon_bool(wave, key):
    return wave.get('weapons', {}).get(key) is True


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 1 – Weapon Mix per Wave
# ═══════════════════════════════════════════════════════════════════════════════

def chart01_weapon_mix():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

    def weapon_bars(ax, waves, title, color_bm, color_drone, color_cruise, n):
        xs = list(range(1, n + 1))
        bm   = [1 if check_weapon_bool(w, 'ballistic_missiles_used') else 0 for w in waves]
        dr   = [1 if check_weapon_bool(w, 'drones_used') else 0 for w in waves]
        cm   = [1 if check_weapon_bool(w, 'cruise_missiles_used') else 0 for w in waves]

        bottom_bm = np.zeros(n)
        bottom_dr = np.array(bm, dtype=float)
        bottom_cm = bottom_dr + np.array(dr, dtype=float)

        ax.bar(xs, bm, label='Ballistic Missiles', color=color_bm, alpha=0.85)
        ax.bar(xs, dr, bottom=bottom_dr, label='Drones', color=color_drone, alpha=0.85)
        ax.bar(xs, cm, bottom=bottom_cm, label='Cruise Missiles', color=color_cruise, alpha=0.85)

        ax.set_xticks(xs)
        ax.set_xticklabels(xs, fontsize=7)
        ax.set_xlabel('Wave Number')
        ax.set_ylabel('Categories Present')
        ax.set_yticks([0, 1, 2, 3])
        ax.set_ylim(0, 3.5)
        ax.set_title(title)
        ax.legend(fontsize=8, loc='upper right')

    weapon_bars(ax1, tp3, f'TP3 — Weapon Categories per Wave (n={N3})',
                TP3_COLOR, '#60A5FA', '#1D4ED8', N3)
    weapon_bars(ax2, tp4, f'TP4 — Weapon Categories per Wave (n={N4})',
                TP4_COLOR, '#FCA5A5', '#7C3AED', N4)

    fig.suptitle('Weapon Category Deployment by Wave', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT + 'report_01_weapon_mix.png')
    plt.close()
    print('Saved chart 01')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 2 – Inter-Wave Tempo
# ═══════════════════════════════════════════════════════════════════════════════

def chart02_tempo():
    tp3_intervals = [w.get('timing', {}).get('hours_since_last_wave')
                     for w in tp3[1:] if w.get('timing', {}).get('hours_since_last_wave') is not None]
    tp4_intervals = [w.get('timing', {}).get('hours_since_last_wave')
                     for w in tp4[1:] if w.get('timing', {}).get('hours_since_last_wave') is not None]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    xs3 = list(range(2, len(tp3_intervals) + 2))
    xs4 = list(range(2, len(tp4_intervals) + 2))

    ax1.bar(xs3, tp3_intervals, color=TP3_COLOR, alpha=0.8, label='TP3')
    ax1.axhline(np.mean(tp3_intervals), color=TP3_COLOR, linestyle='--', linewidth=1.5,
                label=f'Mean: {np.mean(tp3_intervals):.1f}h')
    ax1.set_xlabel('Wave Number')
    ax1.set_ylabel('Hours Since Previous Wave')
    ax1.set_title(f'TP3 Inter-Wave Intervals (mean={np.mean(tp3_intervals):.1f}h)')
    ax1.legend(fontsize=9)
    ax1.set_xticks(xs3)

    ax2.bar(xs4, tp4_intervals, color=TP4_COLOR, alpha=0.8, label='TP4')
    ax2.axhline(np.mean(tp4_intervals), color=TP4_COLOR, linestyle='--', linewidth=1.5,
                label=f'Mean: {np.mean(tp4_intervals):.1f}h')
    ax2.set_xlabel('Wave Number')
    ax2.set_ylabel('Hours Since Previous Wave')
    ax2.set_title(f'TP4 Inter-Wave Intervals (mean={np.mean(tp4_intervals):.1f}h)')
    ax2.legend(fontsize=9)
    ax2.set_xticks(xs4)

    fig.suptitle('Attack Tempo: Inter-Wave Intervals', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT + 'report_02_tempo.png')
    plt.close()
    print('Saved chart 02')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 3 – Cumulative Drone Integration Rate
# ═══════════════════════════════════════════════════════════════════════════════

def chart03_drone_ratio():
    fig, ax = plt.subplots(figsize=(10, 5))

    def cum_drone_rate(waves):
        rates = []
        count = 0
        for i, w in enumerate(waves):
            if check_weapon_bool(w, 'drones_used'):
                count += 1
            rates.append(count / (i + 1) * 100)
        return rates

    r3 = cum_drone_rate(tp3)
    r4 = cum_drone_rate(tp4)

    xs3 = list(range(1, N3 + 1))
    xs4 = list(range(1, N4 + 1))

    ax.plot(xs3, r3, color=TP3_COLOR, marker='o', markersize=4, linewidth=2, label=f'TP3 (final: {r3[-1]:.0f}%)')
    ax.plot(xs4, r4, color=TP4_COLOR, marker='s', markersize=4, linewidth=2, label=f'TP4 (final: {r4[-1]:.0f}%)')

    ax.axhline(50, color='#999', linestyle=':', linewidth=1)
    ax.set_xlabel('Wave Number')
    ax.set_ylabel('Cumulative Drone Wave Rate (%)')
    ax.set_title('Cumulative Drone Integration Rate — TP3 vs TP4', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 10))
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(OUT + 'report_03_drone_ratio.png')
    plt.close()
    print('Saved chart 03')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 4 – Target Geography
# ═══════════════════════════════════════════════════════════════════════════════

def chart04_target_geography():
    # Tally countries across TP4 waves
    country_count = {}
    for w in tp4:
        for c in w.get('targets', {}).get('landings_countries', []):
            country_count[c] = country_count.get(c, 0) + 1

    country_names = {
        'IL': 'Israel', 'IQ': 'Iraq', 'BH': 'Bahrain', 'AE': 'UAE',
        'QA': 'Qatar', 'JO': 'Jordan', 'OM': 'Oman', 'KW': 'Kuwait',
        'SA': 'Saudi Arabia', 'TR': 'Turkey', 'CY': 'Cyprus', 'IO': 'Diego Garcia (IO)'
    }

    sorted_countries = sorted(country_count.items(), key=lambda x: -x[1])
    labels = [country_names.get(c, c) for c, _ in sorted_countries]
    values = [v for _, v in sorted_countries]

    colors = [TP4_COLOR if c == 'IL' else
              '#7C3AED' if c in ['BH','AE','QA','KW','SA','OM'] else
              '#F59E0B' if c in ['IQ','JO','TR','CY','IO'] else
              '#6B7280'
              for c, _ in sorted_countries]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(range(len(labels)), values, color=colors, alpha=0.85, edgecolor='white')

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(val), ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha='right', fontsize=9)
    ax.set_ylabel('Number of Waves Targeted')
    ax.set_title('TP4 Target Countries — Waves Targeted (of 19 total)', fontsize=12, fontweight='bold')

    legend_patches = [
        mpatches.Patch(color=TP4_COLOR, label='Israel'),
        mpatches.Patch(color='#7C3AED', label='Gulf states'),
        mpatches.Patch(color=ACCENT, label='Other coalition/transit'),
    ]
    ax.legend(handles=legend_patches, fontsize=9)

    plt.tight_layout()
    plt.savefig(OUT + 'report_04_target_geography.png')
    plt.close()
    print('Saved chart 04')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 5 – Weapon System Heatmap
# ═══════════════════════════════════════════════════════════════════════════════

def chart05_weapon_heatmap():
    systems = [
        ('emad_used', 'Emad'),
        ('ghadr_used', 'Ghadr'),
        ('sejjil_used', 'Sejjil'),
        ('fattah_used', 'Fattah'),
        ('kheibar_shekan_used', 'Kheibar Shekan'),
        ('shahed_136_used', 'Shahed-136'),
        ('shahed_131_used', 'Shahed-131'),
        ('shahed_238_used', 'Shahed-238'),
    ]

    def build_matrix(waves, n):
        mat = np.zeros((len(systems), n))
        for j, w in enumerate(waves):
            types = w.get('weapons', {}).get('types', {})
            for i, (key, _) in enumerate(systems):
                val = types.get(key)
                if val is True:
                    mat[i, j] = 1.0
                elif val is None:
                    mat[i, j] = 0.3
                else:
                    mat[i, j] = 0.0
        return mat

    mat3 = build_matrix(tp3, N3)
    mat4 = build_matrix(tp4, N4)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))

    im1 = ax1.imshow(mat3, aspect='auto', cmap='Blues', vmin=0, vmax=1)
    ax1.set_xticks(range(N3))
    ax1.set_xticklabels(range(1, N3 + 1), fontsize=7)
    ax1.set_yticks(range(len(systems)))
    ax1.set_yticklabels([s[1] for s in systems], fontsize=9)
    ax1.set_title(f'TP3 Weapon Usage by Wave (n={N3})', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Wave Number')

    im2 = ax2.imshow(mat4, aspect='auto', cmap='Reds', vmin=0, vmax=1)
    ax2.set_xticks(range(N4))
    ax2.set_xticklabels(range(1, N4 + 1), fontsize=7)
    ax2.set_yticks(range(len(systems)))
    ax2.set_yticklabels([s[1] for s in systems], fontsize=9)
    ax2.set_title(f'TP4 Weapon Usage by Wave (n={N4})', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Wave Number')

    # Legend
    from matplotlib.patches import Patch
    legend_elems = [
        Patch(color='#1D4ED8', label='Confirmed used'),
        Patch(color='#BFDBFE', alpha=0.6, label='Unknown/null'),
        Patch(color='#F0F4FF', alpha=0.3, label='Not used'),
    ]
    fig.legend(handles=legend_elems, loc='lower center', ncol=3, fontsize=9, bbox_to_anchor=(0.5, -0.03))

    fig.suptitle('Weapon System Usage Heatmap', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUT + 'report_05_weapon_heatmap.png')
    plt.close()
    print('Saved chart 05')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 6 – Dual-Front Targeting (TP4)
# ═══════════════════════════════════════════════════════════════════════════════

def chart06_dual_front():
    il_targeted  = [1 if w.get('targets', {}).get('israel_targeted') is True else 0 for w in tp4]
    us_targeted  = [1 if w.get('targets', {}).get('us_bases_targeted') is True else 0 for w in tp4]

    xs = list(range(1, N4 + 1))

    fig, ax = plt.subplots(figsize=(12, 4))
    bar_width = 0.35
    bars1 = ax.bar([x - bar_width / 2 for x in xs], il_targeted, bar_width,
                   label='Israel targeted', color=TP3_COLOR, alpha=0.8)
    bars2 = ax.bar([x + bar_width / 2 for x in xs], us_targeted, bar_width,
                   label='US/coalition bases targeted', color=TP4_COLOR, alpha=0.8)

    ax.set_xticks(xs)
    ax.set_xticklabels(xs)
    ax.set_xlabel('TP4 Wave Number')
    ax.set_ylabel('Targeted (1=Yes, 0=No)')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['No', 'Yes'])
    ax.set_title(f'TP4 Dual-Front Targeting — Israel vs US/Coalition Bases per Wave\n'
                 f'(Israel: {sum(il_targeted)}/{N4} waves | US: {sum(us_targeted)}/{N4} waves)',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.4)

    plt.tight_layout()
    plt.savefig(OUT + 'report_06_dual_front.png')
    plt.close()
    print('Saved chart 06')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 7 – Ballistic Missile Flight Times
# ═══════════════════════════════════════════════════════════════════════════════

def chart07_flight_times():
    # Distance (km) from key launch sites to Tel Aviv (32.08N, 34.78E)
    # Using rounded values from OSINT / haversine estimates
    sites = ['Kermanshah\n(1,171 km)', 'Tabriz\n(1,242 km)', 'Isfahan\n(1,588 km)',
             'Shiraz\n(1,721 km)', 'Semnan\n(1,762 km)']
    distances = [1171, 1242, 1588, 1721, 1762]

    # Speed in km/s for each system (average ballistic trajectory)
    systems = {
        'Emad/Ghadr\n(Mach 10)': 3.0,
        'Kheibar Shekan\n(Mach 10)': 3.3,
        'Sejjil\n(Mach 14)': 4.0,
        'Fattah-1\n(Mach 13)': 3.8,
        'Fattah-2 HGV\n(Mach 15)': 4.5,
    }

    colors_sys = ['#2563EB', '#7C3AED', '#DC2626', '#F59E0B', '#111827']

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(sites))
    n_sys = len(systems)
    bar_w = 0.14

    for i, (sys_name, speed_kms) in enumerate(systems.items()):
        times = [d / speed_kms / 60 for d in distances]  # minutes
        offset = (i - n_sys / 2 + 0.5) * bar_w
        bars = ax.bar(x + offset, times, bar_w, label=sys_name, color=colors_sys[i], alpha=0.85)
        for bar, t in zip(bars, times):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                    f'{t:.1f}m', ha='center', va='bottom', fontsize=6.5, rotation=90)

    ax.set_xticks(x)
    ax.set_xticklabels(sites, fontsize=9)
    ax.set_ylabel('Estimated Flight Time (minutes)')
    ax.set_xlabel('Iranian Launch Site')
    ax.set_title('Estimated Ballistic Missile Flight Times to Tel Aviv\nby System and Launch Site',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=8, loc='upper left', ncol=2)
    ax.set_ylim(0, 14)

    plt.tight_layout()
    plt.savefig(OUT + 'report_07_flight_times.png')
    plt.close()
    print('Saved chart 07')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 8 – Night vs Day
# ═══════════════════════════════════════════════════════════════════════════════

def chart08_night_day():
    # 0=Night, 1=Astro twilight, 2=Nautical, 3=Civil, 4=Low sun, 5=Daylight
    phase_names = ['Night', 'Astro\nTwilight', 'Nautical\nTwilight', 'Civil\nTwilight', 'Low Sun', 'Daylight']
    phase_colors = ['#1e293b', '#334155', '#475569', '#94a3b8', '#fbbf24', '#fde68a']

    def phase_counts(waves, n_phases=6):
        counts = [0] * n_phases
        for w in waves:
            sp = w.get('timing', {}).get('solar_phase_launch_site')
            if sp is not None:
                counts[int(sp)] += 1
        return counts

    c3 = phase_counts(tp3)
    c4 = phase_counts(tp4)

    x = np.arange(len(phase_names))
    bar_w = 0.35

    fig, ax = plt.subplots(figsize=(11, 5))
    bars1 = ax.bar(x - bar_w / 2, c3, bar_w, label=f'TP3 (n={N3})', color=TP3_COLOR, alpha=0.8)
    bars2 = ax.bar(x + bar_w / 2, c4, bar_w, label=f'TP4 (n={N4})', color=TP4_COLOR, alpha=0.8)

    for bar in bars1:
        if bar.get_height() > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(int(bar.get_height())), ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        if bar.get_height() > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(int(bar.get_height())), ha='center', va='bottom', fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(phase_names, fontsize=9)
    ax.set_ylabel('Number of Waves')
    ax.set_xlabel('Solar Phase at Launch Site')
    ax.set_title('Launch Timing by Solar Phase — TP3 vs TP4', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)

    # Night bracket
    ax.axvspan(-0.5, 0.5, alpha=0.05, color='navy', label='_nolegend_')
    ax.text(0, max(c3[0], c4[0]) + 0.5, 'Night', ha='center', fontsize=8, color='navy')

    plt.tight_layout()
    plt.savefig(OUT + 'report_08_night_day.png')
    plt.close()
    print('Saved chart 08')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 9 – Escalation Staircase
# ═══════════════════════════════════════════════════════════════════════════════

def chart09_escalation():
    """Cumulative unique countries hit over waves."""

    def cum_countries(waves):
        seen = set()
        curve = []
        for w in waves:
            for c in w.get('targets', {}).get('landings_countries', []):
                seen.add(c)
            # TP3 only hits IL
            if not w.get('targets', {}).get('landings_countries'):
                seen.add('IL')  # TP3 default
            curve.append(len(seen))
        return curve

    def cum_countries_tp3(waves):
        # TP3 is Israel-only
        return [1] * len(waves)

    c3 = cum_countries_tp3(tp3)
    c4 = cum_countries(tp4)

    fig, ax = plt.subplots(figsize=(12, 5))
    xs3 = list(range(1, N3 + 1))
    xs4 = list(range(1, N4 + 1))

    ax.step(xs3, c3, color=TP3_COLOR, linewidth=2.5, where='post', label='TP3 countries')
    ax.step(xs4, c4, color=TP4_COLOR, linewidth=2.5, where='post', label='TP4 countries')

    ax.fill_between(xs3, c3, step='post', alpha=0.15, color=TP3_COLOR)
    ax.fill_between(xs4, c4, step='post', alpha=0.15, color=TP4_COLOR)

    ax.set_xlabel('Wave Number')
    ax.set_ylabel('Cumulative Unique Countries Targeted')
    ax.set_title('Escalation: Cumulative Countries Targeted — TP3 vs TP4', fontsize=12, fontweight='bold')
    ax.set_yticks(range(1, 14))
    ax.legend(fontsize=10)
    ax.set_xlim(1, max(N3, N4) + 0.5)

    # Annotate TP4 country milestones
    milestones = []
    seen = set()
    for i, w in enumerate(tp4):
        for c in w.get('targets', {}).get('landings_countries', []):
            if c not in seen:
                seen.add(c)
                milestones.append((i + 1, len(seen), c))

    country_names_short = {
        'IL': 'Israel', 'IQ': 'Iraq', 'BH': 'Bahrain', 'AE': 'UAE',
        'QA': 'Qatar', 'JO': 'Jordan', 'OM': 'Oman', 'KW': 'Kuwait',
        'SA': 'Saudi Arabia', 'TR': 'Turkey', 'CY': 'Cyprus', 'IO': 'Diego Garcia'
    }
    for wave_n, count, code in milestones[:8]:
        name = country_names_short.get(code, code)
        ax.annotate(f'+{name}', xy=(wave_n, count), xytext=(wave_n + 0.2, count + 0.2),
                    fontsize=7, color=TP4_COLOR, alpha=0.8)

    plt.tight_layout()
    plt.savefig(OUT + 'report_09_escalation.png')
    plt.close()
    print('Saved chart 09')


# ═══════════════════════════════════════════════════════════════════════════════
# CHART 10 – Schematic Attack Geography
# ═══════════════════════════════════════════════════════════════════════════════

def chart10_map():
    """Schematic map showing launch sites and target clusters (not geographically precise)."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor('#e8f4f8')
    ax.set_xlim(35, 67)
    ax.set_ylim(10, 44)
    ax.set_xlabel('Longitude (E)')
    ax.set_ylabel('Latitude (N)')
    ax.set_title('Schematic Attack Geography — TP3 & TP4\n(Approximate; not geographically precise)',
                 fontsize=12, fontweight='bold')

    # Iranian launch sites (triangles)
    launch_sites = {
        'Kermanshah': (47.1, 34.3),
        'Tabriz': (46.3, 38.1),
        'Isfahan': (51.7, 32.6),
        'Semnan': (53.4, 35.6),
        'Shiraz': (52.5, 29.6),
    }
    for name, (lon, lat) in launch_sites.items():
        ax.scatter(lon, lat, marker='^', s=120, color='#7C3AED', zorder=5, edgecolors='white', linewidth=0.8)
        ax.text(lon + 0.3, lat + 0.3, name, fontsize=7, color='#7C3AED')

    # TP3 targets (blue circles — Israel)
    tp3_targets = {
        'Tel Aviv': (34.8, 32.1),
        'Haifa': (35.0, 32.8),
        'Beersheba': (34.8, 31.3),
        'Nevatim AB': (35.0, 31.2),
        'Tel Nof AB': (34.8, 31.8),
    }
    for name, (lon, lat) in tp3_targets.items():
        ax.scatter(lon, lat, marker='o', s=80, color=TP3_COLOR, zorder=4,
                   edgecolors='white', linewidth=0.8, alpha=0.85)
    ax.scatter([], [], marker='o', s=80, color=TP3_COLOR, label='TP3 targets (Israel)')

    # TP4 additional targets (red squares)
    tp4_targets = {
        'Bahrain (5th Fleet)': (50.6, 26.2),
        'Al Udeid (Qatar)': (51.3, 25.1),
        'Al Dhafra (UAE)': (54.5, 24.3),
        'Al Asad (Iraq)': (42.4, 33.8),
        'Oman (Duqm)': (57.7, 19.7),
        'Kuwait bases': (47.9, 29.4),
        'Saudi Arabia': (44.0, 23.0),
        'Cyprus (Akrotiri)': (32.9, 34.6),
        'Diego Garcia': (72.4, -7.3),
    }
    for name, (lon, lat) in tp4_targets.items():
        if 10 <= lat <= 44 and 35 <= lon <= 67:
            ax.scatter(lon, lat, marker='s', s=80, color=TP4_COLOR, zorder=4,
                       edgecolors='white', linewidth=0.8, alpha=0.85)
            ax.text(lon + 0.3, lat + 0.3, name, fontsize=6.5, color=TP4_COLOR, alpha=0.9)
    ax.scatter([], [], marker='s', s=80, color=TP4_COLOR, label='TP4 new targets (US/coalition)')
    ax.scatter([], [], marker='^', s=120, color='#7C3AED', label='Iranian launch sites')

    # Grid lines
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.legend(loc='lower left', fontsize=9)

    # Label Iran region
    ax.text(53, 32, 'IRAN', fontsize=14, color='#999', alpha=0.4, fontweight='bold')
    ax.text(35, 31.5, 'ISRAEL', fontsize=8, color=TP3_COLOR, alpha=0.6, fontweight='bold')
    ax.text(50, 25, 'GULF\nREGION', fontsize=9, color=TP4_COLOR, alpha=0.4, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUT + 'report_10_map.png')
    plt.close()
    print('Saved chart 10')


# ── Run all ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.chdir('/home/daniel/repos/github/Iran-Israel-War-2026-Data')
    os.makedirs(OUT, exist_ok=True)

    chart01_weapon_mix()
    chart02_tempo()
    chart03_drone_ratio()
    chart04_target_geography()
    chart05_weapon_heatmap()
    chart06_dual_front()
    chart07_flight_times()
    chart08_night_day()
    chart09_escalation()
    chart10_map()

    print('\nAll 10 charts generated successfully.')
