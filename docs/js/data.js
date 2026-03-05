/**
 * data.js — Shared data loading utilities
 * Iran-Israel War 2026 Data — GitHub Pages site
 */

// ---- Data cache ----
const DataCache = {};

async function fetchJSON(path) {
  if (DataCache[path]) return DataCache[path];
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  const data = await res.json();
  DataCache[path] = data;
  return data;
}

// ---- Core loaders ----
async function loadTP3Waves() {
  const data = await fetchJSON('data/tp3-waves.json');
  return data;
}

async function loadTP4Waves() {
  const data = await fetchJSON('data/tp4-waves.json');
  return data;
}

async function loadIsraeliTargets() {
  return fetchJSON('data/israeli_targets.json');
}

async function loadUSBases() {
  return fetchJSON('data/us_bases.json');
}

async function loadLaunchZones() {
  return fetchJSON('data/launch_zones.json');
}

// ---- Combined wave loader ----
async function loadAllWaves() {
  const [tp3data, tp4data] = await Promise.all([loadTP3Waves(), loadTP4Waves()]);
  const tp3waves = (tp3data.waves || []).map(w => ({ ...w, _operation: 'TP3' }));
  const tp4waves = (tp4data.waves || []).map(w => ({ ...w, _operation: 'TP4' }));
  return {
    tp3: tp3data,
    tp4: tp4data,
    allWaves: [...tp3waves, ...tp4waves],
  };
}

// ---- Helpers ----
function formatDate(isoStr) {
  if (!isoStr) return '—';
  try {
    const d = new Date(isoStr);
    return d.toISOString().slice(0, 16).replace('T', ' ') + ' UTC';
  } catch { return isoStr; }
}

function formatDateShort(isoStr) {
  if (!isoStr) return '—';
  try {
    const d = new Date(isoStr);
    return d.toUTCString().slice(0, 17);
  } catch { return isoStr; }
}

function getMunitionsCount(wave) {
  const m = wave.munitions?.estimated_munitions_count;
  return (m !== null && m !== undefined) ? m : null;
}

function getWeaponPills(wave) {
  const pills = [];
  const w = wave.weapons || {};
  if (w.ballistic_missiles_used) pills.push({ label: 'BALLISTIC', cls: 'bm' });
  if (w.cruise_missiles_used) pills.push({ label: 'CRUISE', cls: 'cm' });
  if (w.drones_used) pills.push({ label: 'DRONE', cls: 'drone' });
  return pills;
}

function getWeaponSummary(wave) {
  const parts = [];
  const w = wave.weapons || {};
  if (w.ballistic_missiles_used) parts.push('Ballistic Missiles');
  if (w.cruise_missiles_used) parts.push('Cruise Missiles');
  if (w.drones_used) parts.push('Drones');
  return parts.join(', ') || '—';
}

function getTargetSummary(wave) {
  if (wave.targets?.targets) return wave.targets.targets;
  const parts = [];
  if (wave.targets?.israel_targeted) parts.push('Israel');
  if (wave.targets?.us_bases_targeted) parts.push('US Bases');
  return parts.join(', ') || '—';
}

function getInterceptionText(wave) {
  const i = wave.interception;
  if (!i) return '—';
  if (i.estimated_intercept_rate != null) return (i.estimated_intercept_rate * 100).toFixed(0) + '%';
  if (i.intercepted) return 'Yes';
  if (i.intercepted === false) return 'No';
  return '—';
}

function getConflictDay(wave) {
  return wave.timing?.conflict_day ?? '—';
}

// ---- Weapon colors for map/charts ----
const WEAPON_COLORS = {
  ballistic: '#cc2936',
  cruise: '#4a90d9',
  drone: '#f0a500',
  mixed: '#e8661a',
};

function getWaveWeaponColor(wave) {
  const w = wave.weapons || {};
  const hasBM = w.ballistic_missiles_used;
  const hasCM = w.cruise_missiles_used;
  const hasDrone = w.drones_used;
  const count = [hasBM, hasCM, hasDrone].filter(Boolean).length;
  if (count > 1) return WEAPON_COLORS.mixed;
  if (hasBM) return WEAPON_COLORS.ballistic;
  if (hasCM) return WEAPON_COLORS.cruise;
  if (hasDrone) return WEAPON_COLORS.drone;
  return '#888';
}

// ---- Nav active link ----
function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    const isIndex = href === 'index.html' || href === './index.html' || href === './' || href === '';
    const pathBase = path.split('/').pop() || 'index.html';
    if (href === pathBase || (isIndex && (pathBase === '' || pathBase === 'index.html'))) {
      a.classList.add('active');
    }
  });
}

// Run on load
document.addEventListener('DOMContentLoaded', setActiveNav);
