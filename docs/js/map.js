/**
 * map.js — Leaflet map initialization for the Iran-Israel War 2026 site
 */

// ---- Map setup ----
const map = L.map('map', {
  center: [30.0, 45.0],
  zoom: 5,
  zoomControl: true,
  attributionControl: true,
});

// Tile layer (CartoDB dark matter - good for military aesthetic)
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
  subdomains: 'abcd',
  maxZoom: 19,
}).addTo(map);

// ---- Layer groups ----
const layers = {
  launch:     L.layerGroup().addTo(map),
  'il-targets': L.layerGroup().addTo(map),
  'us-bases': L.layerGroup().addTo(map),
  'TP3':      L.layerGroup().addTo(map),
  'TP4':      L.layerGroup().addTo(map),
};

// Active layer state
const layerActive = {
  launch: true,
  'il-targets': true,
  'us-bases': true,
  TP3: true,
  TP4: true,
};

// ---- Marker builders ----
function circleMarkerOptions(color, radius = 9, opacity = 0.85) {
  return {
    radius,
    fillColor: color,
    color: color,
    weight: 2,
    opacity: 1,
    fillOpacity: opacity,
  };
}

function createLaunchMarker(zone) {
  const m = L.circleMarker([zone.lat, zone.lon], {
    ...circleMarkerOptions('#cc2936', 12, 0.3),
    color: '#cc2936',
    weight: 2,
    dashArray: '4 3',
  });
  m.bindPopup(`
    <div class="popup-title">${zone.label}</div>
    <div class="popup-type launch">IRGC LAUNCH ZONE</div>
    <div class="popup-row"><span>Type:</span> ${zone.type}</div>
    <div class="popup-row"><span>Precision:</span> ~${zone.precision_km} km radius</div>
    <div class="popup-row" style="margin-top:6px;font-style:italic;font-size:11px;color:#5a6a7e;">${zone.notes || ''}</div>
  `, { maxWidth: 260 });
  return m;
}

function createIsraeliTargetMarker(target) {
  const typeColors = {
    air_base: '#4a90d9',
    naval_base: '#7ab8f5',
    military_hq: '#e8661a',
    military_industrial: '#9b59b6',
    infrastructure: '#2da44e',
    military_comms: '#f0a500',
    city_area: '#4a90d9',
    region: '#4a90d9',
    military: '#cc2936',
  };
  const color = typeColors[target.type] || '#4a90d9';
  const m = L.circleMarker([target.lat, target.lon], circleMarkerOptions(color, 8, 0.75));
  m.bindPopup(`
    <div class="popup-title">${target.name}</div>
    <div class="popup-type il-target">ISRAELI TARGET — ${(target.type || '').replace(/_/g, ' ').toUpperCase()}</div>
    <div class="popup-row"><span>Region:</span> ${target.region || '—'}</div>
    <div class="popup-row"><span>Coordinates:</span> ${target.lat.toFixed(4)}, ${target.lon.toFixed(4)}</div>
  `, { maxWidth: 240 });
  return m;
}

function createUSBaseMarker(base) {
  const m = L.circleMarker([base.lat, base.lon], circleMarkerOptions('#2da44e', 8, 0.8));
  m.bindPopup(`
    <div class="popup-title">${base.name}</div>
    <div class="popup-type us-base">US/COALITION BASE</div>
    <div class="popup-row"><span>Country:</span> ${base.country_name || '—'} (${base.country_code || '—'})</div>
    <div class="popup-row"><span>Branch:</span> ${base.branch || '—'}</div>
    <div class="popup-row"><span>Coordinates:</span> ${base.lat.toFixed(4)}, ${base.lon.toFixed(4)}</div>
  `, { maxWidth: 240 });
  return m;
}

// Wave diamond marker (rotated square using DivIcon)
function createWaveMarker(wave, lat, lon) {
  const op = wave._operation;
  const color = op === 'TP3' ? '#e8661a' : '#cc2936';
  const icon = L.divIcon({
    html: `<div style="
      width: 12px; height: 12px;
      background: ${color};
      border: 2px solid rgba(255,255,255,0.4);
      transform: rotate(45deg);
      box-shadow: 0 0 6px ${color}88;
    "></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
    className: '',
  });

  const m = L.marker([lat, lon], { icon });
  const munitions = getMunitionsCount(wave);
  const targetSummary = getTargetSummary(wave);
  const weaponSummary = getWeaponSummary(wave);
  const launchDesc = wave.launch_site?.description || '—';
  const intercepted = wave.interception?.intercepted;

  m.bindPopup(`
    <div class="popup-title">${op} Wave ${wave.wave_number}</div>
    <div class="popup-type ${op === 'TP3' ? 'launch' : 'launch'}" style="color: ${color}">
      ${op === 'TP3' ? 'TRUE PROMISE 3' : 'TRUE PROMISE 4'} — DAY ${wave.timing?.conflict_day ?? '?'}
    </div>
    <div class="popup-row"><span>Launched:</span> ${formatDate(wave.timing?.probable_launch_time)}</div>
    <div class="popup-row"><span>Launch Site:</span> ${launchDesc}</div>
    <div class="popup-row"><span>Weapons:</span> ${weaponSummary}</div>
    <div class="popup-row"><span>Targets:</span> ${targetSummary}</div>
    <div class="popup-row"><span>Munitions Est.:</span> ${munitions !== null ? munitions : '—'}</div>
    <div class="popup-row"><span>Intercepted:</span> ${intercepted ? 'Yes' : intercepted === false ? 'No' : '—'}</div>
    ${wave.impact?.damage ? `<div class="popup-row" style="margin-top:6px;font-size:11px;color:#8899aa;">${wave.impact.damage.slice(0, 120)}${wave.impact.damage.length > 120 ? '…' : ''}</div>` : ''}
  `, { maxWidth: 280 });

  m.on('click', () => showWavePanel(wave));
  return m;
}

// ---- Wave panel ----
function showWavePanel(wave) {
  const panel = document.getElementById('wave-panel');
  const title = document.getElementById('wave-panel-title');
  const body = document.getElementById('wave-panel-body');

  const op = wave._operation;
  title.textContent = `${op} Wave ${wave.wave_number}`;

  const rows = [
    ['Operation', op === 'TP3' ? 'True Promise 3' : 'True Promise 4'],
    ['Wave #', wave.wave_number],
    ['Day', wave.timing?.conflict_day ?? '—'],
    ['Launch (UTC)', formatDate(wave.timing?.probable_launch_time)],
    ['Launch Site', wave.launch_site?.description || '—'],
    ['Weapons', getWeaponSummary(wave)],
    ['Targets', getTargetSummary(wave)],
    ['Munitions Est.', getMunitionsCount(wave) ?? '—'],
    ['Intercepted', wave.interception?.intercepted ? 'Yes' : wave.interception?.intercepted === false ? 'No' : '—'],
    ['Intercept Rate', wave.interception?.estimated_intercept_rate != null ? (wave.interception.estimated_intercept_rate * 100).toFixed(0) + '%' : '—'],
    ['Intercept Systems', (wave.interception?.interception_systems || []).join(', ') || '—'],
    ['Fatalities', wave.impact?.fatalities ?? '—'],
    ['Injuries', wave.impact?.injuries ?? '—'],
    ['Impact', wave.impact?.damage || '—'],
  ];

  body.innerHTML = rows.map(([k, v]) => `
    <div class="wave-detail-row">
      <span class="key">${k}</span>
      <span class="val">${v}</span>
    </div>
  `).join('');

  panel.classList.add('open');
}

function closeWavePanel() {
  document.getElementById('wave-panel').classList.remove('open');
}

// ---- Layer toggle ----
function toggleLayer(key) {
  layerActive[key] = !layerActive[key];
  const btn = document.getElementById(`btn-${key}`);
  if (layerActive[key]) {
    map.addLayer(layers[key]);
    btn.classList.add('active');
    btn.setAttribute('aria-pressed', 'true');
  } else {
    map.removeLayer(layers[key]);
    btn.classList.remove('active');
    btn.setAttribute('aria-pressed', 'false');
  }
}

function toggleOp(op) {
  layerActive[op] = !layerActive[op];
  const id = op === 'TP3' ? 'btn-tp3' : 'btn-tp4';
  const btn = document.getElementById(id);
  if (layerActive[op]) {
    map.addLayer(layers[op]);
    btn.classList.add('active');
    btn.setAttribute('aria-pressed', 'true');
  } else {
    map.removeLayer(layers[op]);
    btn.classList.remove('active');
    btn.setAttribute('aria-pressed', 'false');
  }
}

function fitBounds() {
  map.setView([30.0, 45.0], 5);
}

// ---- Main data load ----
async function initMap() {
  const loading = document.getElementById('map-loading');
  try {
    const [launchZones, israeliTargets, usBases, { tp3, tp4 }] = await Promise.all([
      loadLaunchZones(),
      loadIsraeliTargets(),
      loadUSBases(),
      loadAllWaves(),
    ]);

    // Launch zones
    launchZones.forEach(zone => {
      if (zone.lat && zone.lon) {
        createLaunchMarker(zone).addTo(layers['launch']);
      }
    });

    // Israeli targets
    israeliTargets.forEach(target => {
      if (target.lat && target.lon) {
        createIsraeliTargetMarker(target).addTo(layers['il-targets']);
      }
    });

    // US bases
    usBases.forEach(base => {
      if (base.lat && base.lon) {
        createUSBaseMarker(base).addTo(layers['us-bases']);
      }
    });

    // TP3 wave markers — use launch zone centroids by description matching
    const launchZoneMap = buildLaunchZoneIndex(launchZones);

    tp3.waves.forEach(wave => {
      const w = { ...wave, _operation: 'TP3' };
      const lat = wave.launch_site?.lat;
      const lon = wave.launch_site?.lon;
      const resolved = resolveLaunchCoords(wave.launch_site?.description, launchZoneMap);
      const rlat = lat ?? resolved?.lat;
      const rlon = lon ?? resolved?.lon;
      if (rlat && rlon) {
        // Slightly jitter to avoid stacking
        const jlat = rlat + (Math.random() - 0.5) * 0.4;
        const jlon = rlon + (Math.random() - 0.5) * 0.4;
        createWaveMarker(w, jlat, jlon).addTo(layers['TP3']);
      }
    });

    tp4.waves.forEach(wave => {
      const w = { ...wave, _operation: 'TP4' };
      const lat = wave.launch_site?.lat;
      const lon = wave.launch_site?.lon;
      const resolved = resolveLaunchCoords(wave.launch_site?.description, launchZoneMap);
      const rlat = lat ?? resolved?.lat;
      const rlon = lon ?? resolved?.lon;
      if (rlat && rlon) {
        const jlat = rlat + (Math.random() - 0.5) * 0.4;
        const jlon = rlon + (Math.random() - 0.5) * 0.4;
        createWaveMarker(w, jlat, jlon).addTo(layers['TP4']);
      }
    });

    loading.style.display = 'none';

  } catch (err) {
    loading.innerHTML = `<span style="color: var(--iran-red);">Error loading map data: ${err.message}</span>`;
    console.error('Map load error:', err);
  }
}

function buildLaunchZoneIndex(zones) {
  const index = [];
  zones.forEach(z => {
    (z.description_patterns || []).forEach(pat => {
      index.push({ pattern: pat.toLowerCase(), zone: z });
    });
  });
  return index;
}

function resolveLaunchCoords(description, index) {
  if (!description) return null;
  const desc = description.toLowerCase();
  // Exact pattern match first
  for (const entry of index) {
    if (desc.includes(entry.pattern)) return entry.zone;
  }
  // Fallback: western iran
  if (desc.includes('western')) return { lat: 34.31, lon: 47.07 };
  if (desc.includes('central')) return { lat: 33.50, lon: 52.00 };
  if (desc.includes('naval') || desc.includes('gulf')) return { lat: 26.50, lon: 53.00 };
  return { lat: 33.50, lon: 48.50 }; // generic IRGC fallback
}

// Boot
initMap();
