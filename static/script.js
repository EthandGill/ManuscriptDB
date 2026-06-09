// ── MAP ───────────────────────────────────────────────────

const map = L.map('map', {
    crs: L.CRS.Simple,
    minZoom: 4,
    maxZoom: 7,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    zoomControl: true,
    inertia: true,
    maxBoundsViscosity: 1.0
});

L.tileLayer('/static/tiles/{z}/{x}/{y}.png', {
    tileSize: 256,
    minZoom: 1,
    maxZoom: 7,
    maxNativeZoom: 6,
    noWrap: true,
    keepBuffer: 2,
    updateWhenIdle: false
}).addTo(map);

const FULL_BOUNDS = L.latLngBounds([[-128, 0], [0, 256]]);
const TILE_BOUNDS = {
    5: L.latLngBounds([[-120,  96], [-72, 176]]),
    6: L.latLngBounds([[-120, 100], [-72, 176]]),
    7: L.latLngBounds([[-120, 100], [-72, 176]])
};

function applyBounds() {
    const z = map.getZoom();
    map.setMaxBounds(z >= 5 ? TILE_BOUNDS[Math.min(7, Math.round(z))] : FULL_BOUNDS);
}
map.on('zoomend', applyBounds);
map.setView([-96, 136], 4);
applyBounds();

// ── COORDINATE CONVERSION ─────────────────────────────────
// Tiles use standard Web Mercator (EPSG:3857) numbering.
// gorbit nodes: x = longitude, y = latitude

function geoToCRS(lon, lat) {
    const crs_lng = (lon + 180) / 360 * 256;
    const latRad  = lat * Math.PI / 180;
    const mercN   = Math.log(Math.tan(Math.PI / 4 + latRad / 2));
    const crs_lat = -(1 - mercN / Math.PI) * 128;
    return L.latLng(crs_lat, crs_lng);
}

// ── LAYER ORDER (bottom → top) ────────────────────────────
// networkLayer : permanent ORBIS road/sea network background
// routeLayer   : bright selected-route overlay
// cityLayer    : city dot markers (always on top)

const networkLayer     = L.layerGroup().addTo(map);
const routeLayer       = L.layerGroup().addTo(map);
const manuscriptLayer  = L.layerGroup().addTo(map);
const cityLayer        = L.layerGroup().addTo(map);  // always on top of manuscripts

// Pane for gradient orbs — sits at z-index 350, below the SVG overlay pane (400)
// that holds city circleMarkers, so orbs are always rendered behind city nodes.
map.createPane('orbPane');
map.getPane('orbPane').style.zIndex = '350';

// ── STATE ─────────────────────────────────────────────────

let orbisData    = null;   // {cities, routes}  — named cities + metadata
let networkData  = null;   // {nodes, edges, cityNodes}  — full ORBIS gorbit network
let orbisNodeMap = {};     // nodeId (int) → {id, x (lon), y (lat)}
let edgeTypeMap  = {};     // "s-t" → 'road'|'ferry'|'river'|'coast'|'sea'  (directed, for path colouring)
let orbisGraphs  = null;   // {foot, horse, sea}  — Dijkstra graphs on gorbit network

let fromCity   = null;
let toCity     = null;
let activeSlot = 'from';

// Multi-modal travel selection — any combination of modes may be active.
// Routes are computed by building a single combined graph from the selected modes.
const activeModes = new Set(['foot']);

// When true the panel shows the globally optimal (all-modes) route and
// auto-selects whichever modes that path actually uses.
// Resets to true on every new city-pair selection; turns off when the user
// manually toggles any mode button.
let fastestRouteActive = true;

const cityMarkers = {};

// ── MARKER STYLES ─────────────────────────────────────────

const S_DEFAULT = { radius: 3.5, fillColor: '#b8a888', color: '#0e0e0e', weight: 1,   fillOpacity: 0.9 };
const S_FROM    = { radius: 6,   fillColor: '#f0d070', color: '#fff',    weight: 1.5, fillOpacity: 1.0 };
const S_TO      = { radius: 6,   fillColor: '#d06848', color: '#fff',    weight: 1.5, fillOpacity: 1.0 };

// ── NETWORK LINE STYLES ───────────────────────────────────

const LAND_STYLE = {
    color: '#b0b0bc',
    weight: 1.1,
    opacity: 0.4,
    interactive: false
};

const SEA_STYLE = {
    color: '#1a3060',
    weight: 1.4,
    opacity: 0.6,
    dashArray: '5, 4',
    interactive: false
};

// ── SELECTED ROUTE STYLES ─────────────────────────────────

const SEL_ROAD_STYLE = {
    color: '#d4a840',
    weight: 3.5,
    opacity: 0.95
};

const SEL_SEA_STYLE = {
    color: '#4090c8',
    weight: 2.5,
    opacity: 0.9,
    dashArray: '9, 6'
};

const SEL_RIVER_STYLE = {
    color: '#a8d8f0',   // light baby blue — distinct from sea (#4090c8) and road gold
    weight: 2.5,
    opacity: 0.95,
    dashArray: '9, 6'   // same dot cadence as sea travel
};

// ── RENDER PERMANENT ORBIS NETWORK ────────────────────────
// Each edge is a real road segment / sea lane between ancient waypoints.

function renderOrbisNetworkLines(network) {
    network.edges.forEach(e => {
        const a = orbisNodeMap[e.s];
        const b = orbisNodeMap[e.t];
        if (!a || !b) return;
        L.polyline([geoToCRS(a.x, a.y), geoToCRS(b.x, b.y)],
            e.ty === 'c' ? SEA_STYLE : LAND_STYLE).addTo(networkLayer);
    });
}

// ── BUILD ORBIS ROUTING GRAPHS ────────────────────────────
//
// All weights come directly from the gorbit dataset (Stanford ORBIS model):
//
//   foot  — land only; gorbit road days ≈ 25 km/day (standard Roman pace)
//   horse — land only; road days × 0.5  ≈ 50 km/day (relay horse)
//   sea   — all edges; land legs at horse speed; sea legs at gorbit ship days
//
// River / ferry edges use gorbit days as-is for foot (boat speed unchanged);
// horse gets a slight speedup (× 0.6) for faster land approaches.

// ── BUILD ORBIS ROUTING GRAPHS ────────────────────────────
//
// The gorbit CSV (and our rebuilt JSON) stores fully DIRECTED edges: every
// road has both A→B and B→A entries; rivers have separate upstream and
// downstream entries with different travel times; coastal edges encode
// wind/current asymmetry. We therefore add each edge in ONE direction only
// — the direction it is stored — and never synthesise a reverse.
//
// Three graphs are built:
//
//   foot  — roads, ferries, rivers (directed Nile barges); ~25 km/day base
//   horse — roads and ferries only (horses don't ride boats); 2× road speed
//   sea   — all edges; road/ferry legs at horse speed to reach ports fast;
//            river legs at their stored speed; sea/coast at their speed
//
// Edge types in the JSON (mapped from full CSV type names):
//   'road'   — paved / unpaved Roman roads
//   'ferry'  — short river/estuary crossings
//   'river'  — directed Nile / Rhine / Rhône transport (up- or downstream)
//   'coast'  — coastal Mediterranean sailing (directed, wind-sensitive)
//   'sea'    — open-water overseas routes (directed)

function buildOrbisGraph(network) {
    const foot = {}, horse = {}, river = {}, sea = {};
    network.nodes.forEach(n => {
        foot[n.id] = []; horse[n.id] = []; river[n.id] = []; sea[n.id] = [];
    });

    network.edges.forEach(e => {
        const { s, t, d, ty } = e;

        if (ty === 'road') {
            // Roads: foot, horse, and sea (land legs to reach ports).
            // River graph deliberately excludes roads — the Nile cities are already
            // at river nodes, so no road approach is needed, and including roads
            // (even at horse speed) would let Dijkstra bypass the river entirely.
            foot[s].push({ to: t, w: d });
            horse[s].push({ to: t, w: d * 0.5 });
            sea[s].push({ to: t, w: d * 0.5 });   // road leg to reach a sea port

        } else if (ty === 'ferry') {
            // Ferries: all modes (river crossings are relevant for all travellers)
            foot[s].push({ to: t, w: d });
            horse[s].push({ to: t, w: d * 0.5 });
            river[s].push({ to: t, w: d * 0.5 });
            sea[s].push({ to: t, w: d * 0.5 });

        } else if (ty === 'river') {
            // Directed river transport (Nile, Rhine, Rhône…).
            // River and sea graphs use river edges; foot and horse do NOT —
            // they walk/ride along the bank road (injected above as road edges).
            // Keeping river out of foot/horse makes the two modes genuinely distinct.
            river[s].push({ to: t, w: d });        // primary river-mode edges
            sea[s].push({ to: t, w: d });

        } else {
            // 'coast' | 'sea' — maritime lanes: sea graph only, directed
            sea[s].push({ to: t, w: d, isSea: true });
        }
    });

    return { foot, horse, river, sea };
}

// Build a single combined routing graph from a Set of active mode names.
// The result can include any mix of road, river, and sea edges.
// Called fresh each time the user toggles a mode — Dijkstra then runs on
// this one graph, finding the optimal multi-modal path automatically.
function buildCombinedGraph(modes) {
    const graph = {};
    networkData.nodes.forEach(n => { graph[n.id] = []; });

    const hasLand  = modes.has('foot') || modes.has('horse');
    const roadW    = modes.has('horse') ? 0.5 : 1.0;  // horse 2× faster on roads
    const hasRiver = modes.has('river');
    const hasSea   = modes.has('sea');

    networkData.edges.forEach(e => {
        const { s, t, d, ty } = e;
        if ((ty === 'road' || ty === 'ferry') && hasLand) {
            graph[s].push({ to: t, w: d * roadW });
        } else if (ty === 'river' && hasRiver) {
            graph[s].push({ to: t, w: d });
        } else if ((ty === 'coast' || ty === 'sea') && hasSea) {
            graph[s].push({ to: t, w: d });
        }
    });

    return graph;
}

// ── SEA EDGE CHECK ────────────────────────────────────────

function orbisPathHasSea(path) {
    if (!path) return false;
    for (let i = 0; i < path.length - 1; i++) {
        const ty = edgeTypeMap[`${path[i]}-${path[i + 1]}`];
        if (ty === 'coast' || ty === 'sea') return true;
    }
    return false;
}

function orbisPathHasRiver(path) {
    if (!path) return false;
    for (let i = 0; i < path.length - 1; i++) {
        if (edgeTypeMap[`${path[i]}-${path[i + 1]}`] === 'river') return true;
    }
    return false;
}

// ── DIJKSTRA ──────────────────────────────────────────────

function dijkstra(graph, startId) {
    const dist = {}, prev = {};
    Object.keys(graph).forEach(id => { dist[id] = Infinity; });
    dist[startId] = 0;

    const pq = [{ cost: 0, id: startId }];

    while (pq.length) {
        pq.sort((a, b) => a.cost - b.cost);
        const { cost, id } = pq.shift();
        if (cost > dist[id]) continue;

        for (const { to, w } of (graph[id] || [])) {
            if (w == null || w === Infinity) continue;
            const alt = dist[id] + w;
            if (alt < dist[to]) {
                dist[to] = alt;
                prev[to] = id;
                pq.push({ cost: alt, id: to });
            }
        }
    }
    return { dist, prev };
}

function getPath(prev, startId, endId) {
    const path = [];
    let cur = endId;
    let guard = 0;
    while (cur !== undefined && String(cur) !== String(startId) && guard++ < 5000) {
        path.unshift(cur);
        cur = prev[cur];
    }
    if (String(cur) !== String(startId)) return null;
    path.unshift(startId);
    return path;
}

// ── CITY MARKERS ──────────────────────────────────────────

function renderCityMarkers(cities) {
    cities.forEach(city => {
        const pos = geoToCRS(city.lon, city.lat);
        const m   = L.circleMarker(pos, { ...S_DEFAULT });

        m.bindTooltip(city.name, {
            direction: 'top', offset: [0, -6], className: 'city-tooltip'
        });
        m.on('click', e => { L.DomEvent.stopPropagation(e); selectCity(city.id); });

        cityLayer.addLayer(m);
        cityMarkers[city.id] = m;
    });
}

// ── SLOT & SELECTION ──────────────────────────────────────

function setActiveSlot(slot) {
    activeSlot = slot;
    document.getElementById('slot-from').classList.toggle('active', slot === 'from');
    document.getElementById('slot-to').classList.toggle('active', slot === 'to');
}

function selectCity(id) {
    const city = orbisData.cities.find(c => c.id === id);
    if (!city) return;

    const pos = geoToCRS(city.lon, city.lat);
    if (!map.getBounds().contains(pos)) map.panTo(pos);

    if (routePlannerEnabled) {
        // ── Route planning mode: fill from/to slots ──────────
        if (activeSlot === 'from') {
            if (fromCity) cityMarkers[fromCity.id] && cityMarkers[fromCity.id].setStyle(S_DEFAULT);
            fromCity = city;
            cityMarkers[id] && cityMarkers[id].setStyle(S_FROM);
            updateSlotDisplay();
            setActiveSlot('to');
        } else {
            if (city.id === (fromCity && fromCity.id)) return;
            if (toCity) cityMarkers[toCity.id] && cityMarkers[toCity.id].setStyle(S_DEFAULT);
            toCity = city;
            cityMarkers[id] && cityMarkers[id].setStyle(S_TO);
            updateSlotDisplay();
            setActiveSlot('from');
            computeAndShow();
        }
        showMsAtCity(city);
    } else {
        // ── Manuscript-browse mode: replace previous city ────
        clearCityMs();
        showMsAtCity(city);
    }
}

function clearCityMs() {
    if (activeCityPopupObj) {
        map.closePopup(activeCityPopupObj);
        activeCityPopupObj = null;
    }
    cityActivatedMs.clear();
}

// ── CITY → MANUSCRIPT DISPLAY ─────────────────────────────

function showMsAtCity(city) {
    if (!city || !manuscripts.length) return;

    // Match manuscripts whose SNAP CITY is this city — same logic as renderManuscriptMarkers
    // so nearby cities (e.g. Coptos/Dishna 0.15° apart) don't bleed into each other.
    const nearby = manuscripts.filter(ms => {
        if (ms.lat == null || ms.lon == null) return false;
        const snap = findSnapCity(parseFloat(ms.lat), parseFloat(ms.lon));
        if (snap) {
            // Has a snap city: check it matches the clicked city dot
            return Math.abs(snap.lat - city.lat) < 0.001 && Math.abs(snap.lon - city.lon) < 0.001;
        }
        // No snap: tight raw proximity (manuscript has no nearby named city)
        return Math.abs(ms.lat - city.lat) < 0.1 && Math.abs(ms.lon - city.lon) < 0.1;
    });
    if (!nearby.length) return;

    nearby.forEach(ms => cityActivatedMs.add(ms.id));

    const listHtml = nearby.map(ms =>
        `<span class="city-ms-pill" data-ms-id="${ms.id}" title="${ms.name}">${ms.id}</span>`
    ).join('');
    const cityPopup = L.popup({ className: 'city-ms-popup', offset: [0, -8], closeButton: true, autoClose: true })
        .setLatLng(geoToCRS(city.lon, city.lat))
        .setContent(
            `<div class="city-ms-popup-title">${city.name}</div>` +
            `<div class="city-ms-popup-sub">${nearby.length} manuscript${nearby.length > 1 ? 's' : ''} found here</div>` +
            `<div class="city-ms-popup-pills">${listHtml}</div>`
        )
        .openOn(map);
    activeCityPopupObj = cityPopup;

    cityPopup.getElement()?.querySelectorAll('.city-ms-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const ms = manuscripts.find(m => m.id === pill.dataset.msId);
            const pair = msMarkers[ms?.id];
            if (pair?.popup) {
                map.closePopup(cityPopup);
                pair.popup.openOn(map);
            }
        });
    });
}

function clearRoute() {
    if (fromCity) cityMarkers[fromCity.id]?.setStyle(S_DEFAULT);
    if (toCity)   cityMarkers[toCity.id]?.setStyle(S_DEFAULT);
    fromCity = toCity = null;
    routeLayer.clearLayers();
    updateSlotDisplay();
    document.getElementById('route-result').style.display = 'none';
    document.getElementById('clear-btn').style.display    = 'none';
    setActiveSlot('from');
    // activeModes intentionally preserved so next route keeps the user's mode selection
}

// ── COMPUTE & DISPLAY ROUTE ───────────────────────────────

// Compute and draw the optimal route using the current activeModes selection.
// Builds a single combined graph and runs one Dijkstra pass.
function runRoute() {
    if (!fromCity || !toCity) return;

    // Sea nodes give better coastal connectivity for sea-mode routing;
    // land nodes are correct for road/river-only journeys.
    const hasSea = activeModes.has('sea');
    const fromId = hasSea
        ? (networkData.citySeaNodes?.[fromCity.id] ?? networkData.cityNodes[fromCity.id])
        : networkData.cityNodes[fromCity.id];
    const toId = hasSea
        ? (networkData.citySeaNodes?.[toCity.id] ?? networkData.cityNodes[toCity.id])
        : networkData.cityNodes[toCity.id];
    if (!fromId || !toId) return;

    const graph  = buildCombinedGraph(activeModes);
    const result = dijkstra(graph, fromId);
    const dist   = result.dist[toId];
    const path   = getPath(result.prev, fromId, toId);

    updateTravelDisplay(dist, path);
    routeLayer.clearLayers();
    if (path) drawRoute(path);

    fromCity && cityMarkers[fromCity.id]?.setStyle(S_FROM).bringToFront();
    toCity   && cityMarkers[toCity.id]?.setStyle(S_TO).bringToFront();
    if (fromCity && toCity) {
        map.fitBounds(
            L.latLngBounds([geoToCRS(fromCity.lon, fromCity.lat),
                            geoToCRS(toCity.lon,   toCity.lat)]).pad(0.3),
            { maxZoom: 6 }
        );
    }
}

// Compute the globally fastest route (horse + river + sea combined) and
// automatically select only the modes that path actually traverses.
// Road edges → Horse selected (horse always beats foot for speed).
// River edges → River selected.
// Coast/sea edges → Sea selected.
function computeFastestAndSetModes() {
    if (!fromCity || !toCity) return;

    // Use sea nodes so coastal connections are correct
    const fromId = networkData.citySeaNodes?.[fromCity.id] ?? networkData.cityNodes[fromCity.id];
    const toId   = networkData.citySeaNodes?.[toCity.id]   ?? networkData.cityNodes[toCity.id];
    if (!fromId || !toId) return;

    const allModes = new Set(['horse', 'river', 'sea']);
    const graph    = buildCombinedGraph(allModes);
    const result   = dijkstra(graph, fromId);
    const dist     = result.dist[toId];
    const path     = getPath(result.prev, fromId, toId);

    // Derive which modes the path actually uses
    activeModes.clear();
    if (path && path.length > 1) {
        for (let i = 0; i < path.length - 1; i++) {
            const ty = edgeTypeMap[`${path[i]}-${path[i + 1]}`];
            if (ty === 'road' || ty === 'ferry') activeModes.add('horse');
            else if (ty === 'river')             activeModes.add('river');
            else if (ty === 'coast' || ty === 'sea') activeModes.add('sea');
        }
    }
    if (activeModes.size === 0) activeModes.add('horse'); // fallback

    // Sync button highlights
    const box = document.getElementById('route-result');
    box?.querySelectorAll('.mode-btn').forEach(b =>
        b.classList.toggle('active', activeModes.has(b.dataset.mode))
    );

    routeLayer.clearLayers();
    if (path) drawRoute(path);
    updateTravelDisplay(dist, path);

    fromCity && cityMarkers[fromCity.id]?.setStyle(S_FROM).bringToFront();
    toCity   && cityMarkers[toCity.id]?.setStyle(S_TO).bringToFront();
    if (fromCity && toCity) {
        map.fitBounds(
            L.latLngBounds([geoToCRS(fromCity.lon, fromCity.lat),
                            geoToCRS(toCity.lon,   toCity.lat)]).pad(0.3),
            { maxZoom: 6 }
        );
    }
}

function computeAndShow() {
    if (!fromCity || !toCity) return;
    fastestRouteActive = true;  // each new city pair resets to Fastest Route
    showRoutePanel();
    document.getElementById('clear-btn').style.display = 'block';
}

// ── TRAVEL TIME FORMATTING ────────────────────────────────

function fmt(days) {
    if (days == null || days === Infinity || days > 9000) return null;
    if (days < 1) {
        const h = Math.round(days * 24);
        return h + (h === 1 ? ' hour' : ' hours');
    }
    const v = Math.round(days * 10) / 10;
    return v + (v === 1 ? ' day' : ' days');
}

// ── ROUTE PANEL ───────────────────────────────────────────

function showRoutePanel() {
    const box = document.getElementById('route-result');
    box.style.display = 'block';

    box.innerHTML = `
        <div class="result-header">
            <span class="result-from">${fromCity.name}</span>
            <span class="result-arrow">→</span>
            <span class="result-to">${toCity.name}</span>
        </div>

        <button class="fastest-route-btn${fastestRouteActive ? ' active' : ''}" id="fastest-route-btn">
            Fastest Route
        </button>

        <div class="mode-toggle-wrap">
            <div class="mode-btn" data-mode="foot">Foot</div>
            <div class="mode-btn" data-mode="horse">Horse</div>
            <div class="mode-btn" data-mode="river">River</div>
            <div class="mode-btn" data-mode="sea">Sea</div>
        </div>

        <div class="travel-result">
            <div class="travel-days"></div>
            <div class="travel-note"></div>
        </div>

        <div class="result-footnote">ORBIS Stanford · gorbit network · summer conditions</div>`;

    // Fastest Route button — recomputes globally optimal path and auto-selects modes
    const frBtn = document.getElementById('fastest-route-btn');
    frBtn?.addEventListener('click', () => {
        fastestRouteActive = true;
        frBtn.classList.add('active');
        computeFastestAndSetModes();
    });

    // Mode toggle buttons — manual selection deactivates Fastest Route
    box.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', activeModes.has(btn.dataset.mode));
        btn.addEventListener('click', () => {
            // Turn off Fastest Route when user manually adjusts modes
            fastestRouteActive = false;
            frBtn?.classList.remove('active');

            const mode = btn.dataset.mode;
            if (activeModes.has(mode) && activeModes.size > 1) {
                activeModes.delete(mode);
            } else {
                activeModes.add(mode);
            }
            box.querySelectorAll('.mode-btn').forEach(b =>
                b.classList.toggle('active', activeModes.has(b.dataset.mode))
            );
            runRoute();
        });
    });

    // Default: run fastest route on first display
    requestAnimationFrame(() => {
        if (fastestRouteActive) computeFastestAndSetModes();
        else runRoute();
    });
}

// Update the time readout for the current combined route result.
function updateTravelDisplay(dist, path) {
    const daysEl = document.querySelector('.travel-days');
    const noteEl = document.querySelector('.travel-note');
    if (!daysEl || !noteEl) return;

    const f = fmt(dist);
    if (!f) {
        // No route with the active modes
        const landOnly = !activeModes.has('river') && !activeModes.has('sea');
        daysEl.textContent = landOnly ? 'Access to waterways needed' : 'No route';
        daysEl.className   = 'travel-days no-route';
        noteEl.textContent = landOnly ? 'Try adding River or Sea mode' : '';
        return;
    }

    // Colour the time based on what the path actually uses
    const usesSea   = path && orbisPathHasSea(path);
    const usesRiver = path && orbisPathHasRiver(path);
    daysEl.textContent = f;
    daysEl.className   = 'travel-days'
        + (usesSea ? ' sea-time' : usesRiver ? ' river-time' : '');

    // Build mode label from active modes
    const labels = [];
    if (activeModes.has('foot'))  labels.push('Foot');
    if (activeModes.has('horse')) labels.push('Horse');
    if (activeModes.has('river')) labels.push('River');
    if (activeModes.has('sea'))   labels.push('Sea');
    noteEl.textContent = labels.join(' + ') + ' · ORBIS Stanford data';
}

// ── DRAW ROUTE ────────────────────────────────────────────

// Draw a multi-modal path with automatic colour per edge type:
//   road / ferry  → gold          (SEL_ROAD_STYLE)
//   river         → baby blue     (SEL_RIVER_STYLE)
//   coast / sea   → medium blue   (SEL_SEA_STYLE)
// Consecutive edges of the same type are batched into one polyline;
// the junction node is included in both polylines so there is no gap.
function drawRoute(path) {
    if (!path || path.length < 2) return;

    const getCoord = id => { const n = orbisNodeMap[id]; return n ? geoToCRS(n.x, n.y) : null; };

    const styleOf = (a, b) => {
        const ty = edgeTypeMap[`${a}-${b}`];
        if (ty === 'river')                 return SEL_RIVER_STYLE;
        if (ty === 'coast' || ty === 'sea') return SEL_SEA_STYLE;
        return SEL_ROAD_STYLE;
    };

    const flush = (nodes, style) => {
        const coords = nodes.map(getCoord).filter(Boolean);
        if (coords.length > 1) L.polyline(coords, style).addTo(routeLayer);
    };

    let curStyle = styleOf(path[0], path[1]);
    let segNodes = [path[0]];

    for (let i = 1; i < path.length; i++) {
        const es = styleOf(path[i - 1], path[i]);
        if (es !== curStyle) {
            flush(segNodes, curStyle);
            curStyle = es;
            segNodes = [path[i - 1], path[i]];  // junction node in both polylines
        } else {
            segNodes.push(path[i]);
        }
    }
    flush(segNodes, curStyle);
}

// ── SIDEBAR ───────────────────────────────────────────────

function updateSlotDisplay() {
    const fv = document.getElementById('from-value');
    const tv = document.getElementById('to-value');
    fv.textContent = fromCity ? fromCity.name : 'Select a city…';
    tv.textContent = toCity   ? toCity.name   : 'Select a city…';
    fv.classList.toggle('filled', !!fromCity);
    tv.classList.toggle('filled', !!toCity);
    const fs = document.getElementById('from-sub');
    const ts = document.getElementById('to-sub');
    if (fs) fs.textContent = fromCity ? fromCity.modern : '';
    if (ts) ts.textContent = toCity   ? toCity.modern   : '';
}

function renderSidebarList(cities, filter) {
    const q    = (filter || '').toLowerCase();
    const list = document.getElementById('locations-list');
    list.innerHTML = '';

    // Keep count badge in sync
    const countEl = document.getElementById('city-count');
    if (countEl) countEl.textContent = cities.length;

    const shown = q
        ? cities.filter(c => c.name.toLowerCase().includes(q) || c.modern.toLowerCase().includes(q))
        : cities;

    shown.forEach(city => {
        const isFrom = fromCity && fromCity.id === city.id;
        const isTo   = toCity   && toCity.id   === city.id;
        const el = document.createElement('div');
        el.className = 'city-item' + (isFrom ? ' is-from' : isTo ? ' is-to' : '');
        el.innerHTML =
            '<span class="city-dot"></span>' +
            '<span class="city-name">' + city.name + '</span>' +
            '<span class="city-modern">' + city.modern + '</span>';
        el.addEventListener('click', () => selectCity(city.id));
        list.appendChild(el);
    });

    if (shown.length === 0) {
        list.innerHTML = '<div class="city-empty">No cities match your search.</div>';
    }
}

// ── EVENTS ────────────────────────────────────────────────

document.getElementById('slot-from').addEventListener('click', () => setActiveSlot('from'));
document.getElementById('slot-to').addEventListener('click',   () => setActiveSlot('to'));
document.getElementById('clear-btn').addEventListener('click', clearRoute);

document.getElementById('search-input').addEventListener('input', function () {
    if (orbisData) renderSidebarList(orbisData.cities, this.value);
});

map.on('click', () => {
    document.getElementById('slot-from').classList.remove('active');
    document.getElementById('slot-to').classList.remove('active');
});

// ── REMAP ISOLATED CITY NODES ─────────────────────────────
// The gorbit network has gaps: some city-mapped nodes are either
// (a) sea-only (0 road edges) or (b) in a tiny disconnected road stub
//     (e.g. Corinthus ↔ one neighbor, not bridged to the main network).
//
// Strategy: BFS from Roma to find the main connected road component,
// then remap any city node that isn't in it to the nearest node that IS.
// True islands (Sicily, Rhodes, etc.) have no main-component node within
// MAX_DIST and stay sea-only, correctly showing "No route" for foot/horse.

function remapIsolatedCityNodes() {
    const MAX_DIST = 1.5; // degrees — don't remap if mainland is further than this

    // Build main road component via BFS from Roma
    const romaNodeId = networkData.cityNodes['roma'];
    if (!romaNodeId) return;

    const mainComp = new Set();
    const queue    = [romaNodeId];
    mainComp.add(romaNodeId);
    while (queue.length) {
        const cur = queue.shift();
        for (const { to } of (orbisGraphs.foot[cur] || [])) {
            if (!mainComp.has(to)) { mainComp.add(to); queue.push(to); }
        }
    }

    // Pre-build array of main-component nodes for distance search
    const mainNodes = [];
    mainComp.forEach(id => { const n = orbisNodeMap[id]; if (n) mainNodes.push(n); });

    // Remap any city not reachable from Roma by road
    Object.keys(networkData.cityNodes).forEach(cityId => {
        const nodeId = networkData.cityNodes[cityId];
        if (mainComp.has(nodeId)) return; // already in main road network

        const fromNode = orbisNodeMap[nodeId];
        if (!fromNode) return;

        let bestId = null, bestDist = Infinity;
        mainNodes.forEach(n => {
            const dx = n.x - fromNode.x, dy = n.y - fromNode.y;
            const d  = Math.sqrt(dx * dx + dy * dy);
            if (d < bestDist && d < MAX_DIST) { bestDist = d; bestId = n.id; }
        });

            if (bestId) networkData.cityNodes[cityId] = bestId;
        // If no main-comp node within MAX_DIST the city stays sea-only (correct for islands)
    });
}

// ── INIT ──────────────────────────────────────────────────

function initOrbis(data, network) {
    orbisData   = data;
    networkData = network;

    // ── INJECT NILE VALLEY + LEVANT-EGYPT ROAD EDGES ─────────────────────
    // The gorbit dataset has NO road edges along the Nile Valley south of
    // Memphis — all inter-city travel there is modelled as river transport.
    // To give foot/horse modes a genuine road route (distinct from the river),
    // we inject two sets of bidirectional road edges:
    //
    //  A. ORBIS NAMED ROUTES — authoritative foot-day values from orbis.json.
    //     These cover major city pairs (Memphis↔Oxyrhynchus, etc.) and the
    //     Levant–Egypt Via Maris (Jerusalem→Gaza→Pelusium).
    //
    //  B. NILE CHAIN — intermediate gorbit nodes (Aphroditopolis, Herakleopolis,
    //     Hermopolis Magna, Lykopolis, Coptos, etc.) that only have river edges.
    //     Distances calculated from gorbit coordinates and calibrated to the
    //     ORBIS Nile road speed (~46.8 km/day derived from the named routes).
    //
    // All edges use ty:'road' so foot/horse graphs pick them up and horse
    // automatically travels at 2× speed (d*0.5 in buildOrbisGraph).
    const ROAD_INJECT = [
        // ── A. ORBIS named routes (foot days exactly as published) ────────
        { s:50213, t:50181, d:1.5 },  // Hierosolyma ↔ Gaza
        { s:50181, t:50297, d:2.0 },  // Gaza ↔ Pelusium (Via Maris)
        { s:50297, t:50017, d:5.0 },  // Pelusium ↔ Alexandria
        { s:50017, t:50254, d:5.0 },  // Alexandria ↔ Memphis
        { s:50254, t:50288, d:4.0 },  // Memphis ↔ Oxyrhynchus
        { s:50288, t:50321, d:4.0 },  // Oxyrhynchus ↔ Ptolemais Hermeiou
        { s:50321, t:50150, d:4.0 },  // Ptolemais ↔ Diospolis Magna
        { s:50150, t:50373, d:4.0 },  // Diospolis ↔ Syene
        // ── B. Nile chain — intermediate gorbit nodes (~46.8 km/day road) ─
        { s:50254, t:50028, d:1.63 }, // Memphis ↔ Aphroditopolis
        { s:50028, t:50192, d:1.22 }, // Aphroditopolis ↔ Herakleopolis
        { s:50192, t:50288, d:1.42 }, // Herakleopolis ↔ Oxyrhynchus
        { s:50288, t:50194, d:2.49 }, // Oxyrhynchus ↔ Hermopolis Magna
        { s:50194, t:50244, d:1.93 }, // Hermopolis Magna ↔ Lykopolis
        { s:50244, t:50321, d:2.56 }, // Lykopolis ↔ Ptolemais
        { s:50321, t:50130, d:3.02 }, // Ptolemais ↔ Coptos
        { s:50130, t:50150, d:0.93 }, // Coptos ↔ Diospolis
        { s:50150, t:50674, d:1.14 }, // Diospolis ↔ Latopolis
        { s:50674, t:50660, d:1.22 }, // Latopolis ↔ Apollonopolis
        { s:50660, t:50284, d:1.42 }, // Apollonopolis ↔ Omboi
        { s:50284, t:50373, d:1.02 }, // Omboi ↔ Syene
        { s:50661, t:50254, d:2.22 }, // Krokodilopolis (Fayum) ↔ Memphis
    ];
    ROAD_INJECT.forEach(({ s, t, d }) => {
        network.edges.push({ s, t, d, ty: 'road' });
        network.edges.push({ s: t, t: s, d, ty: 'road' }); // bidirectional
    });

    // Build node lookup: integer ID → {id, x (lon), y (lat)}
    network.nodes.forEach(n => { orbisNodeMap[n.id] = n; });

    // Build directed edge-type map for O(1) sea-edge checks during path drawing.
    // Each gorbit edge is already stored in its correct direction in the data;
    // we do NOT add the reverse so coastal wind/current asymmetry is preserved.
    network.edges.forEach(e => {
        edgeTypeMap[`${e.s}-${e.t}`] = e.ty;
    });

    // Build all three routing graphs from gorbit network data
    orbisGraphs = buildOrbisGraph(network);

    // ── AUTO-ASSIGN GORBIT NODES FOR CUSTOM CITIES ───────────
    // Cities added for manuscript coverage (e.g. Lycopolis, Fayum, Dishna,
    // Nessana…) are not in the original ORBIS network and have no entry in
    // networkData.cityNodes. Without an entry the router can't reach them.
    //
    // Strategy: for every named city that has no node mapping yet, find the
    // nearest gorbit node that has at least one road edge, and wire it in.
    // The existing remapIsolatedCityNodes() pass below then fixes any that
    // ended up on disconnected stubs — so we get correct land routing for
    // free without hand-editing any data files.
    // Only consider nodes with at least one outgoing foot edge.
    // Every node is initialised to [] in buildOrbisGraph, so the full
    // key-set is all 677 nodes; filtering to non-empty gives only the
    // ~450 nodes that actually belong to a road/river network.
    // This prevents snapping to dead-end stub nodes (e.g. gorbit's
    // Raphia node which has 0 outgoing edges in the directed graph).
    const _roadNodeIds = new Set(
        Object.keys(orbisGraphs.foot)
              .filter(id => orbisGraphs.foot[id].length > 0)
              .map(Number)
    );
    data.cities.forEach(city => {
        if (networkData.cityNodes[city.id]) return; // already in ORBIS
        let bestId = null, bestDist = Infinity;
        network.nodes.forEach(n => {
            if (!_roadNodeIds.has(n.id)) return;          // skip non-road nodes
            const d = (n.x - city.lon) ** 2 + (n.y - city.lat) ** 2;
            if (d < bestDist) { bestDist = d; bestId = n.id; }
        });
        if (bestId != null) {
            networkData.cityNodes[city.id] = bestId;
        }
    });

    // Preserve original gorbit node mappings for sea routing — these nodes sit
    // at actual ancient ports with correct coastal connections (e.g. Corinthus
    // sits on the Gulf of Corinth with sea edges coming in from Patras).
    // Sea Dijkstra must use these; foot/horse use the remapped road nodes.
    // Copy AFTER auto-assign so custom cities also get sea-node entries.
    network.citySeaNodes = { ...network.cityNodes };

    // Remap isolated city nodes to road-connected alternatives for foot/horse
    remapIsolatedCityNodes(); // modifies networkData.cityNodes only

    // Render the full ancient road + sea-lane network as background
    renderOrbisNetworkLines(network);

    // City markers for our named sites
    renderCityMarkers(data.cities);
    renderSidebarList(data.cities, '');
    setActiveSlot('from');

    // City section collapse toggle
    const cityToggle = document.getElementById('city-section-toggle');
    if (cityToggle) {
        cityToggle.addEventListener('click', () => {
            document.getElementById('city-list-section').classList.toggle('open');
        });
    }

    // Manuscript browser (populated as manuscripts are added)
    renderManuscriptSection();

    // Epigraphy browser (populated as inscriptions are added)
    renderEpigraphySection();

    // Place manuscript rectangle markers on the map
    renderManuscriptMarkers();
}

// ── MANUSCRIPT DATA ───────────────────────────────────────
// Each manuscript will eventually have:
//   { id, name, genre, lat, lon, date, language, notes, ... }
// Genre values match MANUSCRIPT_GENRES[*].id below.

const MANUSCRIPT_GENRES = [
    { id: 'old-testament',  label: 'Old Testament',          icon: '◈' },
    { id: 'new-testament',  label: 'New Testament',          icon: '◈' },
    { id: 'early-church',   label: 'Early Church Epistles',  icon: '◈' },
    { id: 'apocrypha',      label: 'Apocrypha',              icon: '◈' },
    { id: 'receipts',       label: 'Receipts',               icon: '◇' },
    { id: 'contracts',      label: 'Contracts',              icon: '◇' },
    { id: 'letters',        label: 'Letters',                icon: '◇' },
];

// Shorthand helpers for the manuscript data strings below.
// n(str)  = nomen sacrum  → rendered with overline
// s(str)  = supplied text → bracketed, greyed (reconstructed lacuna)
// g(str)  = gap notation  → italic, dimmed
const _n = str => `<span class="nom-sac">${str}</span>`;
const _s = str => `<span class="ms-supplied">[${str}]</span>`;
const _g = str => `<span class="ms-gap">[ ${str} ]</span>`;

// Manuscripts are loaded from /api/manuscripts (see app.py).
// Each .txt file in /manuscripts/ becomes one entry here.
let manuscripts = [];

/* placeholder → HTML converter (mirrors app.py encoding) */
function decodeMsText(str) {
    str = str.replace(/__NOM__([^_]+)__END__/g, (_, w) => _n(w));
    str = str.replace(/__SUP__([^_]+)__END__/g, (_, w) => _s(w));
    return str;
}

function applyMsDecode(ms) {
    // Decode top-level greek array
    if (ms.greek) ms.greek.forEach(v => { if (v.text) v.text = decodeMsText(v.text); });
    // Decode per-book sections (multi-book manuscripts)
    if (ms.sections) {
        Object.values(ms.sections).forEach(sec => {
            if (sec.greek) sec.greek.forEach(v => { if (v.text) v.text = decodeMsText(v.text); });
        });
    }
    return ms;
}

/* ── LEGACY INLINE DATA (kept for fallback only) ── */
const _manuscriptsFallback = [
    {
        id:       'P1',
        name:     'Papyrus 1',
        label:    'P1',
        genre:    'new-testament',
        lat:       28.5383,   // Oxyrhynchus, Egypt  (P.Oxy. 2)
        lon:       30.6765,
        date:     'c. 250 CE',
        language: 'Greek (Koiné)',
        found:    'Oxyrhynchus, Egypt',
        held:     'University of Pennsylvania Museum (E 2746)',
        content:  'Matthew 1:1–9, 1:12–16, 1:18–20',

        // ── GREEK ─────────────────────────────────────────────────────────────
        // Diplomatic transcription from NTVMR (Uni. Münster, docID 10001).
        // Organised by MANUSCRIPT LINE, not by verse.
        // Overline = nomen sacrum; [brackets] = supplied lacuna;
        // em-dash (—) = word continues on next line; gap rows = lost lines.
        // Source: TEI XML with <lb/> line-break elements.
        greek: [
            // ── RECTO ────────────────────────────────────────────────────────
            { sep: 'folio', text: 'Recto' },
            { ref: 'r.1',  text: `βιβλος γενεσεως ${_n('ιυ')} ${_n('χυ')} ${_n('υυ')} δαυιδ ${_s('υιου')}` },
            { ref: 'r.2',  text: `αβρααμ` },
            { ref: 'r.3',  text: `αβρααμ εγεννησεν τον ${_s('ισαακ')}` },
            { ref: 'r.4',  text: `ισαακ δε εγεννησεν τον ιακωβ ${_s('ιακωβ')}` },
            { ref: 'r.5',  text: `δε εγεννησεν τον ιουδαν ${_s('και τους')}` },
            { ref: 'r.6',  text: `${_s('αδ')}ελφ${_s('ου')}ς αυτου` },
            { ref: 'r.7',  text: `ιουδ${_s('ας')} ${_s('δ')}ε εγε${_s('ννη')}—` },
            { ref: 'r.8',  text: `${_s('σεν')} τον φαρες και τον ζαρε εκ της θ${_s('α')}—` },
            { ref: 'r.9',  text: `${_s('μα')}ρ φαρες δε εγεννησεν τον ${_s('ε')}σρωμ` },
            { ref: 'r.10', text: `εσρωμ δε εγεννησεν τον ${_s('αρα')}μ ${_s('αραμ')}` },
            { ref: 'r.11', text: `δε εγεννησεν τον αμ${_s('μιν')}αδαβ ${_s('αμ')}—` },
            { ref: 'r.12', text: `${_s('μιν')}αδαβ δε εγεννησεν τον ναασσων` },
            { ref: 'r.13', text: `${_s('ν')}αασσων δε εγεννησεν τον σαλ${_s('μω')}ν` },
            { ref: 'r.14', text: `σαλμων δε εγεννησεν τον βοες ${_s('εκ')}` },
            { ref: 'r.15', text: `της ραχαβ βοες δε εγεννησεν τον ι—` },
            { ref: 'r.16', text: `ωβηδ εκ της ρ${_s('ο')}υθ ιωβηδ δε εγεν${_s('νη')}—` },
            { ref: 'r.17', text: `σεν τον ιε${_s('σσ')}αι ιεσσαι δε εγεννησεν` },
            { ref: 'r.18', text: `τον δ${_s('αυι')}δ τον βασιλεα ${_s('δαυι')}δ δε εγεν—` },
            { ref: 'r.19', text: `${_s('νη')}σεν τον σολομωνα ${_s('εκ')} της ουρειου σ${_s('ο')}—` },
            { ref: 'r.20', text: `λ${_s('ο')}μων δε εγεννησεν τον ${_s('ρ')}οβοαμ ροβο—` },
            { ref: 'r.21', text: `${_s('α')}μ δε εγεννησεν τον ${_s('αβ')}εια αβεια δε` },
            { ref: 'r.22', text: `εγεννησεν τον ασ${_s('α')}φ ${_s('ασα')}φ δε εγ${_s('εεν')}—` },
            { ref: 'r.23', text: `ν${_s('η')}σεν τον ιωσαφατ ${_s('ιωσα')}φατ δε εγεν—` },
            { ref: 'r.24', text: `ν${_s('η')}σεν τον ιωραμ ιω${_s('ρα')}μ δε εγεννησεν` },
            { ref: 'r.25', text: `τον ${_s('ο')}ζειαν οζειας δε εγεννησεν` },
            { sep: 'gap',   text: '≈ 7 lines — Matt 1:9b–11 not preserved' },
            // ── VERSO ────────────────────────────────────────────────────────
            { sep: 'folio', text: 'Verso' },
            { ref: 'v.1',  text: `${_s('μετα δε την με')}—` },
            { ref: 'v.2',  text: `${_s('τοικεσιαν βαβυλωνος ιεχονι')}ας εγεν—` },
            { ref: 'v.3',  text: `${_s('νησεν τον σαλαθιηλ σαλαθιηλ δε εγεν')}—` },
            { ref: 'v.4',  text: `${_s('νησεν τον ζοροβαβελ')} ${_s('ζοροβαβελ')} δε` },
            { sep: 'gap',   text: '≈ 3 lines — Matt 1:13 not preserved' },
            { ref: 'v.5',  text: `${_s('τον σα')}δωκ σαδωκ δε εγεννησεν τον` },
            { ref: 'v.6',  text: `${_s('αχειμ')} αχειμ δε εγεννησεν τον ελιουδ` },
            { ref: 'v.7',  text: `${_s('ελιουδ')} δε εγεννησεν τον ελεαζαρ ελε—` },
            { ref: 'v.8',  text: `${_s('α')}ζαρ δε εγεννησεν τον μαθθαν μαθθαν` },
            { ref: 'v.9',  text: `δε εγεννησεν τον ιακωβ ι${_s('α')}κωβ δε` },
            { ref: 'v.10', text: `${_s('εγ')}εννησεν τον ιωσηφ τον ανδρα ${_s('μα')}—` },
            { ref: 'v.11', text: `ριας εξ ης εγεννηθη ${_n('ις')} ο λεγομενος ${_n('χς')}` },
            { ref: 'v.12', text: `${_s('πα')}σαι ουν γενεαι απο αβρααμ εως` },
            { ref: 'v.13', text: `δαυιδ γενεαι ${_n('ιδ')} και απο ${_s('δαυιδ εως της')}` },
            { ref: 'v.14', text: `μετοικεσιας βαβυλωνος γε${_s('νεαι')} ${_n('ιδ')} ${_s('και')}` },
            { ref: 'v.15', text: `${_s('απο')} της μετοικεσιας βαβυλωνος εως` },
            { ref: 'v.16', text: `του ${_n('χυ')} γενεαι ${_n('ιδ')} του δε ${_n('ιυ')} ${_n('χυ')} η γενε—` },
            { ref: 'v.17', text: `σις ουτως ην ${_s('μν')}ηστευθεισης της μη—` },
            { ref: 'v.18', text: `τρος αυτου μαριας τω ${_s('ιω')}σηφ πριν η συν—` },
            { ref: 'v.19', text: `ελθειν αυτους ευρεθη εν γαστρι εχου—` },
            { ref: 'v.20', text: `σα εκ ${_n('πνς')} ${_s('αγιου')} ${_s('ιωσηφ δε ο')} ανηρ ${_s('αυ')}—` },
            { ref: 'v.21', text: `${_s('της δικαι')}ος ων ${_s('και μη θελων αυτην')}` },
            { ref: 'v.22', text: `${_s('δ')}ειγματισαι ${_s('εβουληθη λαθρα')}` },
            { ref: 'v.23', text: `${_s('α')}πολυσαι αυτην ${_s('ταυτα δε αυτου εν')}—` },
            { ref: 'v.24', text: `${_s('θυ')}μηθεντος ιδου ${_s('αγγελος')} ${_n('κυ')} ${_s('κατ')}—` },
            { ref: 'v.25', text: `${_s('ο')}ναρ εφανη αυτω λεγων ${_s('ιωσηφ')}` },
            { ref: 'v.26', text: `${_s('υιος δαυιδ μη')} φοβηθης ${_s('παρ')}αλαβειν` },
            { ref: 'v.27', text: `${_s('μα')}ριαν την γυναικα σου ${_s('το γαρ εν αυ')}—` },
            { ref: 'v.28', text: `${_s('τη')} γεννηθεν εκ ${_n('πνς')} ${_s('αγιου')}` },
        ],

        // ── TRANSLATION ───────────────────────────────────────────────────────
        // Translated from P1's actual readings (ζαρε, ουρειου, αβεια, ασαφ, etc.)
        // Bracketed text = supplied from reconstructed lacunae.
        translation: [
            { ref: '1:1',  text: 'The book of the genealogy of Jesus Christ, son of David, son of Abraham.' },
            { ref: '1:2',  text: 'Abraham begat Isaac, Isaac begat Jacob, Jacob begat Judah and his brothers,' },
            { ref: '1:3',  text: 'Judah begat Phares and Zare from Thamar, Phares begat Esrom, Esrom begat Aram,' },
            { ref: '1:4',  text: '[Aram] begat Aminadab, Aminadab begat Naason, Naason begat Salmon,' },
            { ref: '1:5',  text: 'Salmon begat Boes from Rachab, Boes begat Iobed from Routh, Iobed begat Jesse,' },
            { ref: '1:6',  text: 'Jesse begat David the king. David begat Solomon from the wife of Oureiou,' },
            { ref: '1:7',  text: 'Solomon begat Roboam, Roboam begat Abeia, Abeia begat Asaph,' },
            { ref: '1:8',  text: 'Asaph begat Iosaphat, Iosaphat begat Ioram, Ioram begat Ozeian,' },
            { ref: '1:9',  text: 'Ozeias begat — [≈ 7 lines — Matt 1:9b–11 not preserved]' },
            { ref: '1:12', text: '[After the deportation to Babylon, Iechonia]s begat [Salathiel, Salathiel begat Zoroba]bel,' },
            { ref: '1:13', text: '[Zorobabel] begat — [≈ 3 lines — Matt 1:13 not preserved]' },
            { ref: '1:14', text: '[Sadok,] Sadok begat Achim, Achim begat Elioud,' },
            { ref: '1:15', text: '[Elioud] begat Eleazar, Eleazar begat Maththan, Maththan begat Iakob,' },
            { ref: '1:16', text: 'Iakob begat Joseph the husband of Mary, from whom was born Jesus who is called Christ.' },
            { ref: '1:17', text: '[Al]l the generations from Abraham to David are 14, and from David to the deportation to Babylon 14, and from the deportation to Babylon to the Christ 14.' },
            { ref: '1:18', text: 'Now the birth of Jesus Christ was thus: when his mother Mary was betrothed to Joseph, before they came together she was found with child from the Holy Spirit.' },
            { ref: '1:19', text: '[Joseph her husband,] being just and [not wishing to expose her,] decided to divorce her secretly.' },
            { ref: '1:20', text: '[While he was pondering these things,] behold, an angel of the Lord appeared to him in a dream, saying: Joseph, son of David, do not be afraid to take Mary as your wife; for what was conceived in her is from the Holy Spirit.' },
        ],
    },
];

// ── EPIGRAPHY DATA ────────────────────────────────────────
// Each inscription will eventually have:
//   { id, name, genre, lat, lon, date, language, notes, ... }
// Genre values match EPIGRAPHY_GENRES[*].id below.

const EPIGRAPHY_GENRES = [
    { id: 'funerary',    label: 'Funerary',    icon: '◆' },
    { id: 'honourific',  label: 'Honourific',  icon: '◆' },
    { id: 'public',      label: 'Public',      icon: '◆' },
];

let epigraphy = [];  // populated when epigraphy data is added

// ── MANUSCRIPT SECTION ────────────────────────────────────

// NT books in canonical order — only those with manuscripts appear
const NT_BOOKS = [
    'Matthew','Mark','Luke','John','Acts',
    'Romans','1 Corinthians','2 Corinthians','Galatians','Ephesians',
    'Philippians','Colossians','1 Thessalonians','2 Thessalonians',
    '1 Timothy','2 Timothy','Titus','Philemon','Hebrews',
    'James','1 Peter','2 Peter','1 John','2 John','3 John',
    'Jude','Revelation'
];

// Source-filter book lists per genre. OT / EC / AP will be populated over time.
const OT_BOOKS = [];   // to be added
const EC_BOOKS = [];   // to be added
const AP_BOOKS = [];   // to be added

const SOURCE_GENRE_BOOKS = { OT: OT_BOOKS, NT: NT_BOOKS, EC: EC_BOOKS, AP: AP_BOOKS };
const SOURCE_GENRE_PLACEHOLDER = {
    OT: 'OT Book…',
    NT: 'NT Book…',
    EC: 'Early Church author…',
    AP: 'Apocryphal book…',
};

// Stored per-manuscript data, keyed by manuscript id
// Shape: { locKey, popup, lastOpenedBook }
const msMarkers = {};

// Per-location orb data, keyed by "lat,lon" string
// Shape: { orb, activeMs (Set), allMs, pos, onMap }
const locationOrbs = {};

// Per-popup open handlers, keyed by L.popup instance
const popupOpenHandlers = new Map();

// Track which book accordions are currently open (supports multi-book manuscripts)
const activeMsBooks = new Set();

// Date filter state — absolute years (negative = BCE, positive = CE)
const dateFilter = { active: false, minYear: null, maxYear: null };

// Pericope filter state
const pericopeFilter = { book: null, chapter: null, verseStart: null, verseEnd: null };

// Sidebar book element references — populated by renderManuscriptSection
// so that openBookInSidebar() can programmatically expand the right accordion row.
const bookElements = {};   // NT book name → { genreEl, bookEl }

// Route planner enabled state (OFF by default)
let routePlannerEnabled = false;

// ── WRITING STAND STATE ───────────────────────────────────
let wsCurrentMs      = null;   // manuscript currently loaded
let wsCurrentBook    = null;   // book currently shown
let wsFolioGroups    = null;   // folio groups for current book
let wsFolioIdx       = 0;      // currently displayed folio index

// Track manuscripts shown via city-click (so they can be cleared on next city click)
let cityActivatedMs  = new Set();
let activeCityPopupObj = null;

function _msBooks(ms) {
    // Early-church genre: group by author name (used as the map-visibility key)
    if (ms.genre === 'early-church') {
        return ms.author ? [ms.author] : ['Unknown'];
    }
    // Returns the list of books this manuscript belongs to.
    // Prefers the `books` array added by app.py; falls back to the raw `book` string.
    return (Array.isArray(ms.books) && ms.books.length > 0)
        ? ms.books
        : (ms.book ? [ms.book] : []);
}

// ── DATE FILTER HELPERS ───────────────────────────────────────

// Parse a manuscript date string into an absolute year range.
// Returns { min, max } where negative values are BCE, positive are CE.
// Returns null if the string cannot be parsed.
function parseManuscriptDateRange(str) {
    if (!str) return null;
    const s = str.trim();

    // "X–Y CE/BCE" or "c. X-Y CE/BCE"
    let m = s.match(/(\d{1,4})\s*[-–]\s*(\d{1,4})\s*(CE|AD|BCE|BC)\b/i);
    if (m) {
        const a = parseInt(m[1]), b = parseInt(m[2]);
        const era = m[3].toUpperCase();
        return (era === 'CE' || era === 'AD')
            ? { min: a, max: b }
            : { min: -b, max: -a };
    }

    // "X CE/BCE" (single year, e.g. "c. 200 CE")
    m = s.match(/\b(\d{1,4})\s*(CE|AD|BCE|BC)\b/i);
    if (m) {
        const yr   = parseInt(m[1]);
        const sign = (m[2].toUpperCase() === 'CE' || m[2].toUpperCase() === 'AD') ? 1 : -1;
        return { min: sign * yr, max: sign * yr };
    }

    // "Early / Mid / Late Nth century"
    m = s.match(/(early|mid|late)\s+(\d+)(st|nd|rd|th)\s+cent/i);
    if (m) {
        const base = (parseInt(m[2]) - 1) * 100;
        const mod  = m[1].toLowerCase();
        if (mod === 'early') return { min: base + 1,  max: base + 40 };
        if (mod === 'mid')   return { min: base + 35, max: base + 65 };
        if (mod === 'late')  return { min: base + 60, max: base + 99 };
    }

    // Plain "Nth century"
    m = s.match(/(\d+)(st|nd|rd|th)\s+cent/i);
    if (m) {
        const n = parseInt(m[1]);
        return { min: (n - 1) * 100 + 1, max: n * 100 };
    }

    return null;
}

// Returns true if the manuscript falls within the current date filter range.
// Manuscripts with unparseable dates always pass (unknown ≠ excluded).
function _msPassesDateFilter(ms) {
    if (!dateFilter.active) return true;
    const range = parseManuscriptDateRange(ms.date);
    if (!range) return true;  // undated: don't exclude
    const fMin = dateFilter.minYear != null ? dateFilter.minYear : -Infinity;
    const fMax = dateFilter.maxYear != null ? dateFilter.maxYear :  Infinity;
    // Ranges overlap when ms.min ≤ filterMax AND ms.max ≥ filterMin
    return range.min <= fMax && range.max >= fMin;
}

// ── PERICOPE FILTER ───────────────────────────────────────────

// Parse a content string (e.g. "John 3:16-18, 21; 4:1-5") into
// an array of { chapter, vStart, vEnd } spanning tuples.
// Cross-chapter ranges like "3:16-4:3" are expanded into:
//   { ch:3, 16-999 }  +  { ch:4, 1-3 }
function parseVerseRanges(contentStr) {
    const ranges = [];
    if (!contentStr) return ranges;

    // Strip trailing notes and ellipsis
    let s = contentStr.replace(/\s*\(partial\)/gi, '').replace(/\.\.\./g, '').trim();

    // Remove leading book name (handles "Matthew", "1 Corinthians", "1 John", etc.)
    s = s.replace(/^(?:\d+\s+)?[A-Za-z]+\s+/, '');

    // Split on semicolons; track current chapter within each group (comma-sep verses)
    const groups = s.split(';');
    for (const group of groups) {
        let curChapter = null;
        const parts = group.trim().split(',');
        for (const rawPart of parts) {
            const p = rawPart.trim();
            if (!p) continue;

            // Cross-chapter: "C1:V1-C2:V2"
            const cross = p.match(/^(\d+):(\d+)\s*[-–]\s*(\d+):(\d+)$/);
            if (cross) {
                const [, c1s, v1s, c2s, v2s] = cross;
                const c1 = +c1s, v1 = +v1s, c2 = +c2s, v2 = +v2s;
                curChapter = c2;
                ranges.push({ chapter: c1, vStart: v1, vEnd: 999 });
                for (let c = c1 + 1; c < c2; c++) ranges.push({ chapter: c, vStart: 1, vEnd: 999 });
                ranges.push({ chapter: c2, vStart: 1, vEnd: v2 });
                continue;
            }

            // Same-chapter verse (or verse range): "C:V" or "C:V-V"
            const chv = p.match(/^(\d+):(\d+)(?:\s*[-–]\s*(\d+))?$/);
            if (chv) {
                curChapter = +chv[1];
                ranges.push({ chapter: curChapter, vStart: +chv[2], vEnd: chv[3] ? +chv[3] : +chv[2] });
                continue;
            }

            // Continuation: just verse or verse range (uses previous chapter)
            if (curChapter !== null) {
                const v = p.match(/^(\d+)(?:\s*[-–]\s*(\d+))?$/);
                if (v) ranges.push({ chapter: curChapter, vStart: +v[1], vEnd: v[2] ? +v[2] : +v[1] });
            }
        }
    }
    return ranges;
}

// Returns true if this manuscript covers the pericope currently in pericopeFilter.
function _msPassesPericopeFilter(ms) {
    const { book, chapter, verseStart, verseEnd } = pericopeFilter;
    if (!book) return true;                              // no book selected → show all

    const msBooks = _msBooks(ms);
    if (!msBooks.includes(book)) return false;           // wrong book → hide

    if (!chapter) return true;                           // book-only filter → passes

    // Resolve the content string for this book
    let contentStr = null;
    if (ms.sections?.[book]) {
        contentStr = ms.sections[book].content || null;
    } else if (ms.content) {
        contentStr = ms.content;
    }
    if (!contentStr) return true;                        // no parseable content → don't exclude

    const ranges = parseVerseRanges(contentStr);
    if (!ranges.length) return true;                     // unrecognised format → don't exclude

    // Filter to the target chapter
    const inChapter = ranges.filter(r => r.chapter === chapter);
    if (!inChapter.length) return false;                 // chapter not in manuscript

    if (!verseStart && !verseEnd) return true;           // chapter-only → passes

    const qV1 = verseStart || 1;
    const qV2 = verseEnd   || 999;
    return inChapter.some(r => r.vStart <= qV2 && r.vEnd >= qV1);
}

// Combined check: manuscript must pass both date and pericope filters.
function _msPassesAllFilters(ms) {
    return _msPassesDateFilter(ms) && _msPassesPericopeFilter(ms);
}

// Show/hide the active-filter dot and button highlight.
// Called whenever either filter changes.
function syncFilterIndicator() {
    const anyActive = dateFilter.active
        || !!(pericopeFilter.book || pericopeFilter.chapter);
    const dot = document.getElementById('ms-filter-active-dot');
    const btn = document.getElementById('ms-filter-btn');
    if (dot) dot.style.display = anyActive ? 'inline-block' : 'none';
    if (btn) btn.classList.toggle('active', anyActive);
}

// Rebuild every orb's activeMs set from the current book filter + ALL active filters,
// then redraw all orbs. Call this whenever any filter changes.
function applyFilters() {
    Object.values(locationOrbs).forEach(loc => loc.activeMs.clear());
    activeMsBooks.forEach(book => {
        manuscripts.forEach(ms => {
            if (!_msBooks(ms).includes(book)) return;
            if (ms.lat == null || ms.lon == null) return;
            if (!_msPassesAllFilters(ms)) return;
            const pair = msMarkers[ms.id];
            if (!pair) return;
            const loc = locationOrbs[pair.locKey];
            if (loc) loc.activeMs.add(ms.id);
        });
    });
    Object.keys(locationOrbs).forEach(k => refreshLocationOrb(k));
}

// Programmatically open a book section in the sidebar accordion,
// activating its map markers (equivalent to the user clicking it).
function openBookInSidebar(book) {
    const refs = bookElements[book];
    if (!refs) return;
    // Open NT genre section if collapsed
    if (!refs.genreEl.classList.contains('open')) refs.genreEl.classList.add('open');
    // Open book row if collapsed
    if (!refs.bookEl.classList.contains('open')) {
        refs.bookEl.classList.add('open');
        showBookOnMap(book);
    }
    // Scroll the book row into view
    refs.bookEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showBookOnMap(book) {
    activeMsBooks.add(book);
    manuscripts.forEach(ms => {
        if (!_msBooks(ms).includes(book)) return;
        if (ms.lat == null || ms.lon == null) return;
        if (!_msPassesAllFilters(ms)) return;    // respect all active filters
        const pair = msMarkers[ms.id];
        if (!pair) return;
        pair.lastOpenedBook = book;
        const loc = locationOrbs[pair.locKey];
        if (loc) {
            loc.activeMs.add(ms.id);
            refreshLocationOrb(pair.locKey);
        }
    });
}

// Display label for a book — abbreviated where appropriate for compact tabs
const BOOK_ABBREV = {
    // Gospels / Acts
    'Matthew':          'Matt',
    // Mark, Luke, John, Acts are short enough already
    // Pauline corpus — all abbreviated for compact tabs on wide multi-book MSS like P46
    'Romans':           'Rom',
    '1 Corinthians':    '1 Cor',
    '2 Corinthians':    '2 Cor',
    'Galatians':        'Gal',
    'Ephesians':        'Eph',
    'Philippians':      'Phil',
    'Colossians':       'Col',
    '1 Thessalonians':  '1 Thes',
    '2 Thessalonians':  '2 Thes',
    '1 Timothy':        '1 Tim',
    '2 Timothy':        '2 Tim',
    'Philemon':         'Phlm',
    'Hebrews':          'Heb',
    // Catholic Epistles
    'James':            'Jas',
    '1 Peter':          '1 Pet',
    '2 Peter':          '2 Pet',
    'Revelation':       'Rev',
};
function bookLabel(book) { return BOOK_ABBREV[book] || book; }

// Scholarly adjectival forms used in the orb hover badge.
// Falls back to the plain book name if not listed.
const BOOK_ADJECTIVES = {
    'Matthew':          'Matthean',
    'Mark':             'Markan',
    'Luke':             'Lukan',
    'John':             'Johannine',
    'Acts':             'Acts',
    'Romans':           'Romans',
    '1 Corinthians':    '1 Corinthian',
    '2 Corinthians':    '2 Corinthian',
    'Galatians':        'Galatian',
    'Ephesians':        'Ephesian',
    'Philippians':      'Philippian',
    'Colossians':       'Colossian',
    '1 Thessalonians':  '1 Thessalonian',
    '2 Thessalonians':  '2 Thessalonian',
    'Hebrews':          'Hebrews',
    'James':            'James',
    '1 Peter':          '1 Petrine',
    '2 Peter':          '2 Petrine',
    '1 John':           '1 Johannine',
    '2 John':           '2 Johannine',
    '3 John':           '3 Johannine',
    'Jude':             'Jude',
    'Revelation':       'Revelation',
};

// Switch the visible book tab inside an already-open multi-book popup
function switchMsBook(popupEl, book) {
    popupEl.querySelectorAll('.ms-book-tab').forEach(t =>
        t.classList.toggle('active', t.dataset.book === book));
    popupEl.querySelectorAll('.ms-book-section').forEach(s =>
        s.classList.toggle('active', s.dataset.book === book));
}

function hideBookOnMap(book) {
    activeMsBooks.delete(book);
    manuscripts.forEach(ms => {
        const books = _msBooks(ms);
        if (!books.includes(book)) return;
        if (ms.lat == null || ms.lon == null) return;
        // Only remove from orb if none of this manuscript's books are still active
        if (books.some(b => activeMsBooks.has(b))) return;
        const pair = msMarkers[ms.id];
        if (!pair) return;
        const loc = locationOrbs[pair.locKey];
        if (loc) {
            loc.activeMs.delete(ms.id);
            refreshLocationOrb(pair.locKey);
        }
    });
}

// Composes the hover badge label for an orb.
// When a single NT book is active at this location, uses its scholarly adjective
// ("12 Matthean manuscripts active here"). When multiple books are open, falls
// back to a plain count ("12 manuscripts active here").
function orbBadgeText(loc) {
    const count = loc.activeMs.size;
    if (count === 0) return '';

    // Intersect the globally-open book accordions with the books represented
    // at this location — so P45 (multi-gospel) counted as "Matthean" when only
    // Matthew is open, rather than as five different books simultaneously.
    const localBooks = new Set();
    loc.allMs.forEach(ms => {
        if (!loc.activeMs.has(ms.id)) return;
        _msBooks(ms).forEach(b => { if (activeMsBooks.has(b)) localBooks.add(b); });
    });

    const noun = count === 1 ? 'manuscript' : 'manuscripts';
    if (localBooks.size === 1) {
        const adj = BOOK_ADJECTIVES[[...localBooks][0]] || [...localBooks][0];
        return `${count} ${adj} ${noun} active here`;
    }
    return `${count} ${noun} active here`;
}

// Returns a CSS radial-gradient string whose alpha channels scale with `intensity`
// (0–1). Using rgba() alpha instead of CSS opacity keeps child elements unaffected.
function orbGradient(intensity) {
    const a = (base) => +Math.min(1, intensity * base).toFixed(2);
    return `radial-gradient(circle at center,` +
        `rgba(160,0,0,${a(1.00)}) 0%,` +
        `rgba(200,0,0,${a(0.90)}) 20%,` +
        `rgba(210,0,0,${a(0.50)}) 58%,` +
        `rgba(220,0,0,0) 100%)`;
}

// Redraws (or hides) the orb for a given location based on its current activeMs count.
function refreshLocationOrb(locKey) {
    const loc = locationOrbs[locKey];
    if (!loc) return;
    const count = loc.activeMs.size;

    if (count === 0) {
        if (loc.onMap) {
            manuscriptLayer.removeLayer(loc.orb);
            loc.onMap = false;
        }
        return;
    }

    // Size grows with sqrt(count). Intensity controls the gradient's alpha values —
    // we intentionally avoid CSS 'opacity' on the parent div because it cascades
    // to children and would dim the .ms-orb-count button.
    const size      = Math.round(22 + 9 * Math.sqrt(Math.min(count, 55)));
    const intensity = 0.60 + 0.35 * Math.min(1, count / 20);   // 0.60 → 0.95
    const grad      = orbGradient(intensity);

    // Lightweight DOM update when only gradient or text changes (size unchanged);
    // full setIcon when size changes so Leaflet keeps the anchor centred.
    const iconEl = loc.orb.getElement?.();
    const circle = iconEl?.querySelector('.ms-orb-circle');
    const hoverLabel = `${count} MSS`;
    if (circle && circle.style.width === `${size * 2}px`) {
        circle.style.background = grad;
        const tip = circle.querySelector('.ms-orb-count');
        if (tip) tip.textContent = hoverLabel;
    } else {
        loc.orb.setIcon(L.divIcon({
            className: 'ms-orb-icon',
            iconSize:   [size * 2, size * 2],
            iconAnchor: [size, size],
            html: `<div class="ms-orb-circle" style="width:${size*2}px;height:${size*2}px;background:${grad}"><div class="ms-orb-count">${hoverLabel}</div></div>`,
        }));
    }

    if (!loc.onMap) {
        loc.orb.addTo(manuscriptLayer);
        loc.onMap = true;
    }
}

// Opens a city-style popup listing active manuscripts at a given location.
function showOrbPopup(locKey) {
    const loc = locationOrbs[locKey];
    if (!loc) return;
    const displayMs = loc.activeMs.size > 0
        ? loc.allMs.filter(m => loc.activeMs.has(m.id))
        : loc.allMs;
    // Use the stored snap city name (correct even when two cities are close together)
    const cityName = loc.snapCity?.name || 'This site';
    const listHtml = displayMs.map(ms =>
        `<span class="city-ms-pill" data-ms-id="${ms.id}" title="${ms.name}">${ms.id}</span>`
    ).join('');
    const orbPopup = L.popup({ className: 'city-ms-popup', offset: [0, -8], closeButton: true, autoClose: true })
        .setLatLng(loc.pos)
        .setContent(
            `<div class="city-ms-popup-title">${cityName}</div>` +
            `<div class="city-ms-popup-sub">${orbBadgeText(loc)}</div>` +
            `<div class="city-ms-popup-pills">${listHtml}</div>`
        )
        .openOn(map);
    activeCityPopupObj = orbPopup;
    orbPopup.getElement()?.querySelectorAll('.city-ms-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            const ms = manuscripts.find(m => m.id === pill.dataset.msId);
            const pair = msMarkers[ms?.id];
            if (pair?.popup) {
                map.closePopup(orbPopup);
                pair.popup.openOn(map);
            }
        });
    });
}

function renderManuscriptSection() {
    const container = document.getElementById('genre-list');
    if (!container) return;
    container.innerHTML = '';

    MANUSCRIPT_GENRES.forEach(genre => {
        const genreItems = manuscripts.filter(m => m.genre === genre.id);

        const el = document.createElement('div');
        el.className = 'genre-item';

        // ── New Testament: nested by book ──────────────────
        if (genre.id === 'new-testament') {
            // Group by book in canonical order (multi-book manuscripts appear under each)
            const bookMap = {};
            genreItems.forEach(m => {
                const books = (Array.isArray(m.books) && m.books.length > 0)
                    ? m.books : [(m.book || 'Unknown')];
                books.forEach(b => {
                    if (!bookMap[b]) bookMap[b] = [];
                    bookMap[b].push(m);
                });
            });

            const booksWithMs = NT_BOOKS.filter(b => bookMap[b]);

            const booksHtml = booksWithMs.length === 0
                ? `<div class="genre-empty">No manuscripts yet</div>`
                : booksWithMs.map(book => {
                    const items = bookMap[book];
                    return `
                    <div class="genre-item book-item" data-book="${book}">
                        <div class="genre-header book-header">
                            <span class="genre-chevron">›</span>
                            <span class="genre-name">${book}</span>
                            <span class="genre-count">${items.length}</span>
                        </div>
                        <div class="genre-body">
                            ${items.map(m => `
                            <div class="ms-item" data-id="${m.id}">
                                <span class="ms-item-name">${m.id} — ${m.name}</span>
                                <span class="ms-item-meta">${m.date || ''}</span>
                            </div>`).join('')}
                        </div>
                    </div>`;
                }).join('');

            el.innerHTML = `
                <div class="genre-header">
                    <span class="genre-chevron">›</span>
                    <span class="genre-icon">${genre.icon}</span>
                    <span class="genre-name">${genre.label}</span>
                    <span class="genre-count">${genreItems.length}</span>
                </div>
                <div class="genre-body">${booksHtml}</div>`;

            // Genre toggle
            el.querySelector('.genre-header').addEventListener('click', () => {
                el.classList.toggle('open');
            });

            // Book toggle — show/hide map markers
            el.querySelectorAll('.book-item').forEach(bookEl => {
                const book = bookEl.dataset.book;
                // Track for programmatic open (Source filter → sidebar sync)
                if (book) bookElements[book] = { genreEl: el, bookEl };
                bookEl.querySelector('.book-header').addEventListener('click', e => {
                    e.stopPropagation();
                    const wasOpen = bookEl.classList.contains('open');
                    bookEl.classList.toggle('open');
                    wasOpen ? hideBookOnMap(book) : showBookOnMap(book);
                    // Keep Source input in sync with active book
                    const src = document.getElementById('filter-book-input');
                    if (src) {
                        if (!wasOpen) {
                            // Just opened: fill Source if it's empty or the same book
                            if (!src.value || src.value === book) {
                                src.value = book;
                                pericopeFilter.book = book;
                                syncFilterIndicator();
                            }
                        } else if (src.value === book) {
                            // Closed this book: clear Source
                            src.value = '';
                            pericopeFilter.book = null;
                            syncFilterIndicator();
                        }
                    }
                });
            });

        // ── Early Church Epistles: nested by author ────────
        } else if (genre.id === 'early-church') {
            // Build author map preserving insertion order
            const authorMap = {};
            genreItems.forEach(m => {
                const author = m.author || 'Unknown';
                if (!authorMap[author]) authorMap[author] = [];
                authorMap[author].push(m);
            });

            const authorsHtml = Object.keys(authorMap).length === 0
                ? `<div class="genre-empty">No texts yet</div>`
                : Object.entries(authorMap).map(([author, items]) => `
                    <div class="genre-item book-item" data-author="${author}">
                        <div class="genre-header book-header">
                            <span class="genre-chevron">›</span>
                            <span class="genre-name">${author}</span>
                            <span class="genre-count">${items.length}</span>
                        </div>
                        <div class="genre-body">
                            ${items.map(m => `
                            <div class="ms-item" data-id="${m.id}">
                                <span class="ms-item-name">${m.label || m.id} — ${m.name}</span>
                                <span class="ms-item-meta">${m.date || ''}</span>
                            </div>`).join('')}
                        </div>
                    </div>`).join('');

            el.innerHTML = `
                <div class="genre-header">
                    <span class="genre-chevron">›</span>
                    <span class="genre-icon">${genre.icon}</span>
                    <span class="genre-name">${genre.label}</span>
                    <span class="genre-count">${genreItems.length}</span>
                </div>
                <div class="genre-body">${authorsHtml}</div>`;

            // Top-level genre toggle
            el.querySelector('.genre-header').addEventListener('click', () => {
                el.classList.toggle('open');
            });

            // Author toggle — show/hide map markers for that author's texts
            el.querySelectorAll('.book-item').forEach(authorEl => {
                const author = authorEl.dataset.author;
                authorEl.querySelector('.book-header').addEventListener('click', e => {
                    e.stopPropagation();
                    const wasOpen = authorEl.classList.contains('open');
                    authorEl.classList.toggle('open');
                    wasOpen ? hideBookOnMap(author) : showBookOnMap(author);
                });
            });

        // ── Other genres: flat list ────────────────────────
        } else {
            el.innerHTML = `
                <div class="genre-header">
                    <span class="genre-chevron">›</span>
                    <span class="genre-icon">${genre.icon}</span>
                    <span class="genre-name">${genre.label}</span>
                    <span class="genre-count">${genreItems.length}</span>
                </div>
                <div class="genre-body">
                    ${genreItems.length === 0
                        ? `<div class="genre-empty">No manuscripts yet</div>`
                        : genreItems.map(m => `
                            <div class="ms-item" data-id="${m.id}">
                                <span class="ms-item-name">${m.name}</span>
                                <span class="ms-item-meta">${m.date || ''}${m.language ? ' · ' + m.language : ''}</span>
                            </div>`).join('')}
                </div>`;

            el.querySelector('.genre-header').addEventListener('click', () => {
                el.classList.toggle('open');
            });
        }

        // Manuscript item click — pan to location and open popup
        el.querySelectorAll('.ms-item').forEach(row => {
            row.addEventListener('click', () => {
                const ms = manuscripts.find(m => m.id === row.dataset.id);
                if (ms && ms.lat != null && ms.lon != null) {
                    map.panTo(geoToCRS(parseFloat(ms.lon), parseFloat(ms.lat)));
                    const pair = msMarkers[ms.id];
                    if (pair) {
                        // Set book/author context so the popup opens on the right tab
                        const bookEl = row.closest('.book-item');
                        if (bookEl?.dataset.book)        pair.lastOpenedBook = bookEl.dataset.book;
                        else if (bookEl?.dataset.author) pair.lastOpenedBook = bookEl.dataset.author;
                        pair.popup.openOn(map);
                    }
                }
            });
        });

        container.appendChild(el);
    });
}

// ── MANUSCRIPT SEARCH ─────────────────────────────────────

function renderMsSearchResults(query) {
    const resultsEl = document.getElementById('ms-search-results');
    const genreList = document.getElementById('genre-list');
    if (!resultsEl || !genreList) return;

    const q = query.trim().toLowerCase();
    if (!q) {
        resultsEl.innerHTML = '';
        resultsEl.classList.remove('active');
        genreList.style.display = '';
        return;
    }

    genreList.style.display = 'none';
    resultsEl.classList.add('active');

    const matches = manuscripts.filter(ms => {
        const searchable = [
            ms.id, ms.name, ms.content, ms.date, ms.found, ms.held,
            ...(Array.isArray(ms.books) ? ms.books : [ms.book || ''])
        ].filter(Boolean).join(' ').toLowerCase();
        return searchable.includes(q);
    });

    if (matches.length === 0) {
        resultsEl.innerHTML = `<div class="ms-search-no-results">No manuscripts match "${query}"</div>`;
        return;
    }

    resultsEl.innerHTML = matches.map(ms => {
        const books = (Array.isArray(ms.books) && ms.books.length > 0)
            ? ms.books.join(' · ')
            : (ms.book || '');
        return `
        <div class="ms-search-result" data-id="${ms.id}">
            <div>
                <span class="ms-search-result-id">${ms.id}</span>
                <span class="ms-search-result-name">${ms.name}</span>
            </div>
            <div class="ms-search-result-meta">${books}${ms.date ? ' · ' + ms.date : ''}</div>
        </div>`;
    }).join('');

    resultsEl.querySelectorAll('.ms-search-result').forEach(row => {
        row.addEventListener('click', () => {
            const ms = manuscripts.find(m => m.id === row.dataset.id);
            if (!ms || ms.lat == null || ms.lon == null) return;
            map.panTo(geoToCRS(parseFloat(ms.lon), parseFloat(ms.lat)));
            const pair = msMarkers[ms.id];
            if (pair?.popup) pair.popup.openOn(map);
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const msSearchInput = document.getElementById('ms-search-input');
    if (msSearchInput) {
        msSearchInput.addEventListener('input', function () {
            renderMsSearchResults(this.value);
        });
    }

    // ── DATE FILTER PANEL ─────────────────────────────────────
    const filterBtn   = document.getElementById('ms-filter-btn');
    const filterPanel = document.getElementById('ms-filter-panel');
    const filterDot   = document.getElementById('ms-filter-active-dot');
    const startInput  = document.getElementById('filter-start-year');
    const endInput    = document.getElementById('filter-end-year');
    const filterClear = document.getElementById('ms-filter-clear');

    let startEra = 'CE', endEra = 'CE';

    function updateDateFilter() {
        const startVal = parseInt(startInput?.value) || null;
        const endVal   = parseInt(endInput?.value)   || null;
        dateFilter.minYear = startVal != null
            ? (startEra === 'BCE' ? -startVal : startVal)
            : null;
        dateFilter.maxYear = endVal != null
            ? (endEra === 'BCE' ? -endVal : endVal)
            : null;
        dateFilter.active  = (dateFilter.minYear !== null || dateFilter.maxYear !== null);
        syncFilterIndicator();
        applyFilters();
    }

    // Toggle panel open/closed; pre-fill Source if one NT book is already active
    if (filterBtn) {
        filterBtn.addEventListener('click', () => {
            filterPanel?.classList.toggle('open');
            if (filterPanel?.classList.contains('open')) {
                const srcInput = document.getElementById('filter-book-input');
                if (srcInput && !srcInput.value) {
                    const ntActive = [...activeMsBooks].filter(b => NT_BOOKS.includes(b));
                    if (ntActive.length === 1) {
                        srcInput.value = ntActive[0];
                        pericopeFilter.book = ntActive[0];
                        syncFilterIndicator();
                    }
                }
            }
        });
    }

    // Year inputs
    if (startInput) startInput.addEventListener('input', updateDateFilter);
    if (endInput)   endInput.addEventListener('input',   updateDateFilter);

    // BCE / CE era toggle buttons
    document.querySelectorAll('.filter-era-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const field = btn.dataset.field;
            const era   = btn.dataset.era;
            // Deactivate siblings, activate this one
            btn.closest('.filter-era-toggle')
               .querySelectorAll('.filter-era-btn')
               .forEach(b => b.classList.toggle('active', b.dataset.era === era));
            if (field === 'start') startEra = era;
            else                   endEra   = era;
            updateDateFilter();
        });
    });

    // Clear button — reset ALL filter inputs
    if (filterClear) {
        filterClear.addEventListener('click', () => {
            // Date range
            if (startInput) startInput.value = '';
            if (endInput)   endInput.value   = '';
            startEra = endEra = 'CE';
            document.querySelectorAll('.filter-era-btn').forEach(b =>
                b.classList.toggle('active', b.dataset.era === 'CE')
            );
            // Pericope
            const bkIn = document.getElementById('filter-book-input');
            const chIn = document.getElementById('filter-chapter');
            const vsIn = document.getElementById('filter-verse-start');
            const veIn = document.getElementById('filter-verse-end');
            const bkDd = document.getElementById('filter-book-dropdown');
            if (bkIn) bkIn.value = '';
            if (chIn) chIn.value = '';
            if (vsIn) vsIn.value = '';
            if (veIn) veIn.value = '';
            if (bkDd) bkDd.classList.remove('open');
            pericopeFilter.book = pericopeFilter.chapter =
                pericopeFilter.verseStart = pericopeFilter.verseEnd = null;
            updateDateFilter(); // resets date state + calls applyFilters + syncFilterIndicator
        });
    }

    // ── PERICOPE FILTER INPUTS ────────────────────────────────

    const bookInput     = document.getElementById('filter-book-input');
    const bookDropdown  = document.getElementById('filter-book-dropdown');
    const chapterInput  = document.getElementById('filter-chapter');
    const verseStartEl  = document.getElementById('filter-verse-start');
    const verseEndEl    = document.getElementById('filter-verse-end');

    // ── GENRE TABS (OT / NT / EC / AP) ───────────────────────
    let sourceGenre = 'NT';

    document.querySelectorAll('.filter-genre-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            sourceGenre = tab.dataset.genre;
            // Highlight active tab
            document.querySelectorAll('.filter-genre-tab')
                .forEach(t => t.classList.toggle('active', t.dataset.genre === sourceGenre));
            // Reset book selection + close dropdown
            if (bookInput) {
                bookInput.value = '';
                bookInput.placeholder = SOURCE_GENRE_PLACEHOLDER[sourceGenre] || 'Book…';
            }
            if (bookDropdown) bookDropdown.classList.remove('open');
            pericopeFilter.book = null;
            syncFilterIndicator();
            applyFilters();
        });
    });

    function updatePericopeFilter() {
        pericopeFilter.chapter    = parseInt(chapterInput?.value)  || null;
        pericopeFilter.verseStart = parseInt(verseStartEl?.value)  || null;
        pericopeFilter.verseEnd   = parseInt(verseEndEl?.value)    || null;
        syncFilterIndicator();
        applyFilters();
    }

    // Book autocomplete
    if (bookInput && bookDropdown) {
        bookInput.addEventListener('input', () => {
            const q = bookInput.value.trim().toLowerCase();
            if (!q) {
                bookDropdown.classList.remove('open');
                pericopeFilter.book = null;
                syncFilterIndicator();
                applyFilters();
                return;
            }
            const hits = (SOURCE_GENRE_BOOKS[sourceGenre] || []).filter(b =>
                b.toLowerCase().startsWith(q) || b.toLowerCase().includes(q)
            );
            if (!hits.length) { bookDropdown.classList.remove('open'); return; }
            bookDropdown.innerHTML = hits.map(b =>
                `<div class="filter-book-option" data-book="${b}">${b}</div>`
            ).join('');
            bookDropdown.classList.add('open');
            bookDropdown.querySelectorAll('.filter-book-option').forEach(opt => {
                opt.addEventListener('click', () => {
                    const book = opt.dataset.book;
                    bookInput.value = book;
                    bookDropdown.classList.remove('open');
                    pericopeFilter.book = book;
                    openBookInSidebar(book);
                    syncFilterIndicator();
                    applyFilters();
                });
            });
        });

        // Close dropdown on outside click
        document.addEventListener('click', e => {
            if (!bookInput.contains(e.target) && !bookDropdown.contains(e.target)) {
                bookDropdown.classList.remove('open');
            }
        });

        bookInput.addEventListener('keydown', e => {
            if (e.key === 'Escape') bookDropdown.classList.remove('open');
            // Enter picks the first result
            if (e.key === 'Enter') {
                const first = bookDropdown.querySelector('.filter-book-option');
                if (first) first.click();
            }
        });
    }

    // Chapter / verse inputs
    if (chapterInput) chapterInput.addEventListener('input', updatePericopeFilter);
    if (verseStartEl) verseStartEl.addEventListener('input', updatePericopeFilter);
    if (verseEndEl)   verseEndEl.addEventListener('input',   updatePericopeFilter);

    // Writing Stand close button
    const wsCloseBtn = document.getElementById('ws-close');
    if (wsCloseBtn) wsCloseBtn.addEventListener('click', closeWritingStand);

    // Dispatch popup-open wiring for manuscript standalone popups
    map.on('popupopen', e => {
        const handler = popupOpenHandlers.get(e.popup);
        if (handler) handler(e.popup.getElement());
    });

    const routeToggle = document.getElementById('route-planner-toggle');
    if (routeToggle) {
        routeToggle.addEventListener('change', function () {
            routePlannerEnabled = this.checked;
            document.getElementById('route-planner').classList.toggle('enabled', this.checked);
            // When disabling route planner, reset any active city highlights
            if (!this.checked) {
                if (fromCity) cityMarkers[fromCity.id] && cityMarkers[fromCity.id].setStyle(S_DEFAULT);
                if (toCity)   cityMarkers[toCity.id]   && cityMarkers[toCity.id].setStyle(S_DEFAULT);
                fromCity = toCity = null;
                routeLayer.clearLayers();
                updateSlotDisplay();
                document.getElementById('route-result').style.display = 'none';
            }
        });
    }
});

// ── EPIGRAPHY SECTION ─────────────────────────────────────

function renderEpigraphySection() {
    const container = document.getElementById('epigraphy-genre-list');
    if (!container) return;
    container.innerHTML = '';

    EPIGRAPHY_GENRES.forEach(genre => {
        const items = epigraphy.filter(e => e.genre === genre.id);

        const el = document.createElement('div');
        el.className = 'genre-item';
        el.innerHTML = `
            <div class="genre-header">
                <span class="genre-chevron">›</span>
                <span class="genre-icon">${genre.icon}</span>
                <span class="genre-name">${genre.label}</span>
                <span class="genre-count">${items.length}</span>
            </div>
            <div class="genre-body">
                ${items.length === 0
                    ? `<div class="genre-empty">No inscriptions yet</div>`
                    : items.map(e => `
                        <div class="ms-item" data-id="${e.id}">
                            <span class="ms-item-name">${e.name}</span>
                            <span class="ms-item-meta">${e.date || ''}${e.language ? ' · ' + e.language : ''}</span>
                        </div>`).join('')}
            </div>`;

        // Toggle open/closed on header click
        el.querySelector('.genre-header').addEventListener('click', () => {
            el.classList.toggle('open');
        });

        // Inscription item click — pan to location on map (wired up later)
        el.querySelectorAll('.ms-item').forEach(row => {
            row.addEventListener('click', () => {
                const insc = epigraphy.find(e => e.id === row.dataset.id);
                if (insc && insc.lat != null && insc.lon != null) {
                    map.panTo(geoToCRS(insc.lon, insc.lat));
                }
            });
        });

        container.appendChild(el);
    });
}

// ── MANUSCRIPT MAP MARKERS ───────────────────────────────

// Render an array of {ref, text} verse objects as popup HTML rows
function buildVerseHtml(verses) {
    if (!verses || verses.length === 0) return '<em class="ms-no-text">No text preserved</em>';
    return verses.map(v => {
        if (v.sep === 'folio') return `<div class="ms-folio-head">${v.text}</div>`;
        if (v.sep === 'gap')   return `<div class="ms-line-gap">[ ${v.text || 'gap'} ]</div>`;
        // data-ref lets scrollTranslationToVerse() locate this element by verse reference
        return `<div class="ms-verse" data-ref="${v.ref}"><span class="ms-verse-ref">${v.ref}</span><span class="ms-verse-text">${v.text}</span></div>`;
    }).join('');
}

// Group an array of greek-line entries into folio buckets for the dropdown navigator.
// Each {sep:'folio'} entry opens a new bucket; its text becomes the <option> label.
// Lines that precede the first folio separator land in an anonymous bucket.
function groupByFolio(lines) {
    if (!lines || lines.length === 0) return [];
    const groups = [];
    let cur = null;
    for (const entry of lines) {
        if (entry.sep === 'folio') {
            cur = { label: entry.text, lines: [] };
            groups.push(cur);
        } else {
            if (!cur) { cur = { label: '', lines: [] }; groups.push(cur); }
            cur.lines.push(entry);
        }
    }
    return groups;
}

// Scrolls a translation container to the verse that corresponds to a folio label.
// Folio labels look like "Folio 24 — John 4:45-50" or "Page 15 — Luke 3:1-14".
// We extract the first chapter:verse, then find the closest verse ≤ that reference.
function scrollTranslationToVerse(container, folioLabel) {
    if (!container || !folioLabel) return;

    // Pull first "chapter:verse" from the label (e.g. "4:45" from "John 4:45-50")
    const m = folioLabel.match(/(\d+):(\d+)/);
    if (!m) return;
    const chap    = m[1];
    const targetV = parseInt(m[2], 10);

    // Find the verse element at or just before the target in the same chapter
    let best = null;
    let bestV = -1;
    container.querySelectorAll('.ms-verse[data-ref]').forEach(el => {
        const rm = el.dataset.ref.match(/^(\d+):(\d+)/);
        if (!rm || rm[1] !== chap) return;
        const n = parseInt(rm[2], 10);
        if (n <= targetV && n > bestV) { bestV = n; best = el; }
    });

    if (best) {
        // Scroll within the container (getBoundingClientRect works regardless of
        // how deeply nested the element is or the container's position style)
        const cTop = container.getBoundingClientRect().top;
        const eTop = best.getBoundingClientRect().top;
        container.scrollTop += eTop - cTop - 6;   // 6 px breathing room at top
    }
}

// Build popup body for a single book section (Greek + translation).
// When the greek array has ≥5 FOLIO groups a dropdown navigator replaces the flat scroll,
// rendering only the selected folio's lines into the DOM at a time.
function buildSectionBody(label, greek, translation, bookName) {
    const folioGroups = groupByFolio(greek || []);
    const useFolioDropdown = folioGroups.length >= 5;

    let greekInner;
    if (useFolioDropdown) {
        const firstLabel = folioGroups[0]?.label || 'Folio 1';
        const opts = folioGroups.map((g, i) =>
            `<div class="ms-folio-option${i === 0 ? ' active' : ''}" data-index="${i}">${g.label || 'Folio ' + (i + 1)}</div>`
        ).join('');
        greekInner = `
            <div class="ms-folio-nav">
                <span class="ms-folio-label">Folio</span>
                <div class="ms-folio-dropdown">
                    <button class="ms-folio-trigger" type="button">
                        <span class="ms-folio-trigger-text">${firstLabel}</span>
                        <span class="ms-folio-arrow">▾</span>
                    </button>
                    <div class="ms-folio-panel">${opts}</div>
                </div>
            </div>
            <div class="ms-popup-text-scroll ms-popup-greek ms-folio-container">
                ${buildVerseHtml(folioGroups[0]?.lines || [])}
            </div>`;
    } else {
        greekInner = `<div class="ms-popup-text-scroll ms-popup-greek">
                ${buildVerseHtml(greek || [])}
            </div>`;
    }

    const transHtml = translation && translation.length > 0
        ? `<div class="ms-popup-text-section">
               <div class="ms-popup-field-label">English Translation</div>
               <div class="ms-popup-text-scroll ms-popup-english">
                   ${buildVerseHtml(translation)}
               </div>
           </div>`
        : '';
    return `
        <div class="ms-popup-text-section">
            <div class="ms-popup-field-label">
                Greek Text <span class="ms-popup-field-note">${label} reading</span>
            </div>
            ${greekInner}
        </div>
        ${transHtml}`;
}

// Find the closest city within 0.3° of a lat/lon point.
// Returns the city object or null. Used by both renderManuscriptMarkers
// and showMsAtCity so they agree on which city each manuscript belongs to.
function findSnapCity(lat, lon) {
    const cities = orbisData?.cities ?? [];
    const cands = cities.filter(c => Math.abs(c.lat - lat) < 0.3 && Math.abs(c.lon - lon) < 0.3);
    if (!cands.length) return null;
    return cands.sort((a, b) =>
        ((a.lat - lat) ** 2 + (a.lon - lon) ** 2) -
        ((b.lat - lat) ** 2 + (b.lon - lon) ** 2)
    )[0];
}

function renderManuscriptMarkers() {
    manuscriptLayer.clearLayers();
    Object.keys(locationOrbs).forEach(k => delete locationOrbs[k]);
    Object.keys(msMarkers).forEach(k => delete msMarkers[k]);
    popupOpenHandlers.clear();

    // ── 1. Group manuscripts by their SNAPPED CITY (not raw lat/lon) ──
    // This merges manuscripts from slightly different coordinates that all
    // belong to the same city (e.g. Bodmer Papyri spread across Dishna) into
    // ONE orb, and prevents nearby cities (Coptos vs Dishna, 0.15° apart)
    // from stealing each other's manuscripts.
    const locGroups = {};    // locKey → { snapCity, pos, msList }
    const msLocKey  = {};    // ms.id  → locKey

    manuscripts.forEach(ms => {
        if (ms.lat == null || ms.lon == null) return;
        const lat0 = parseFloat(ms.lat), lon0 = parseFloat(ms.lon);
        const snap = findSnapCity(lat0, lon0);

        // Key by the snapped city's coordinates (so all MSS at the same city merge).
        // Fall back to the raw manuscript coordinates when no city is within range.
        const locKey = snap
            ? `city:${snap.lat.toFixed(6)},${snap.lon.toFixed(6)}`
            : `raw:${lat0.toFixed(4)},${lon0.toFixed(4)}`;

        if (!locGroups[locKey]) {
            const pos = snap
                ? geoToCRS(snap.lon, snap.lat)
                : geoToCRS(lon0, lat0);
            locGroups[locKey] = { snap, pos, msList: [] };
        }
        locGroups[locKey].msList.push(ms);
        msLocKey[ms.id] = locKey;
    });

    // ── 2. Create one orb + count label per location ────────
    Object.entries(locGroups).forEach(([locKey, { snap, pos, msList }]) => {
        const ms0 = msList[0];
        const snapCity = snap;   // kept for showOrbPopup name lookup

        // Build a default gradient for the initial (hidden) state.
        // We use rgba() alpha channels rather than CSS opacity so that the
        // child .ms-orb-count button is never affected by the parent's transparency.
        const initGrad = orbGradient(0.60);

        // Circular orb with radial gradient — rendered in orbPane (z-index 350),
        // which sits below the SVG overlay (z-index 400) so city dots stay on top.
        // Circular orb with radial gradient — rendered in orbPane (z-index 350),
        // which sits below the SVG overlay (z-index 400) so city dots stay on top.
        // The count badge (.ms-orb-count) lives inside the circle div and
        // appears only on CSS :hover — no separate label marker needed.
        const orb = L.marker(pos, {
            icon: L.divIcon({
                className: 'ms-orb-icon',
                iconSize:   [56, 56],
                iconAnchor: [28, 28],
                html: `<div class="ms-orb-circle" style="width:56px;height:56px;background:${initGrad}"><div class="ms-orb-count">0 MSS</div></div>`,
            }),
            pane:        'orbPane',
            interactive:  true,
        });

        locationOrbs[locKey] = { orb, activeMs: new Set(), allMs: msList, pos, snapCity, onMap: false };

        // Clicking the orb → show pill popup for active manuscripts at this site
        orb.on('click', e => { L.DomEvent.stopPropagation(e); showOrbPopup(locKey); });
    });

    // ── 3. Build per-manuscript popup HTML + standalone L.popup ───
    manuscripts.forEach(ms => {
        if (ms.lat == null || ms.lon == null) return;

        // Use the city-snapped locKey computed in step 1
        const locKey  = msLocKey[ms.id];
        if (!locKey) return;
        // Popup anchors to the snapped city position (same as the orb)
        const loc     = locationOrbs[locKey];
        const cityPos = loc ? loc.pos : geoToCRS(parseFloat(ms.lon), parseFloat(ms.lat));
        const label   = ms.label || ms.id || '?';

        const msBooks     = _msBooks(ms);
        const isMultiBook = msBooks.length > 1 && ms.sections;

        let bodyHtml, versesLine;

        if (isMultiBook) {
            versesLine = ms.content || msBooks.join(' · ');
            const tabsHtml = msBooks.map((book, i) => {
                return `<div class="ms-book-tab${i === 0 ? ' active' : ''}" data-book="${book}"
                             onclick="switchMsBook(this.closest('.ms-popup'), '${book}')">
                             ${bookLabel(book)}
                         </div>`;
            }).join('');
            const sectionsHtml = msBooks.map((book, i) => {
                const sec = ms.sections[book] || {};
                const contentSummary = sec.content || '';
                return `<div class="ms-book-section${i === 0 ? ' active' : ''}" data-book="${book}">
                             ${contentSummary ? `<div class="ms-book-content-line">${contentSummary}</div>` : ''}
                             ${buildSectionBody(label, sec.greek || [], sec.translation || [], book)}
                         </div>`;
            }).join('');
            bodyHtml = `<div class="ms-book-tabs">${tabsHtml}</div>${sectionsHtml}`;
        } else {
            versesLine = ms.content || (msBooks[0] || '');
            bodyHtml   = buildSectionBody(label, ms.greek, ms.translation, msBooks[0]);
        }

        const popupHtml = `
            <div class="ms-popup">
                <button class="ms-ws-btn">Open Reading Stand</button>
                <div class="ms-popup-header">
                    <div class="ms-popup-id">${label}</div>
                    <div class="ms-popup-fullname">${ms.name}</div>
                    <div class="ms-popup-verses">${versesLine}</div>
                </div>
                ${bodyHtml}
                <div class="ms-popup-meta">
                    <div class="ms-popup-meta-item">
                        <div class="ms-popup-field-label">Date</div>
                        <div class="ms-popup-field-value">${ms.date || '—'}</div>
                    </div>
                    <div class="ms-popup-meta-item">
                        <div class="ms-popup-field-label">Language</div>
                        <div class="ms-popup-field-value">${ms.language || '—'}</div>
                    </div>
                </div>
            </div>`;

        // Pre-compute folio groups (≥5 folios → show dropdown)
        const folioGroupMap = {};
        msBooks.forEach(book => {
            const secGreek = isMultiBook ? (ms.sections?.[book]?.greek || []) : (ms.greek || []);
            const groups = groupByFolio(secGreek);
            if (groups.length >= 5) folioGroupMap[book] = groups;
        });

        // Standalone popup — not bound to any marker
        const msPopup = L.popup({ className: 'ms-popup-wrap', maxWidth: 360 })
            .setLatLng(cityPos)
            .setContent(popupHtml);

        msMarkers[ms.id] = { locKey, popup: msPopup, lastOpenedBook: null };

        // Register popup-open wiring (dispatched by map.on('popupopen') in DOMContentLoaded)
        popupOpenHandlers.set(msPopup, popupEl => {
            if (!popupEl) return;

            // Multi-book: activate the tab that last opened this manuscript
            if (isMultiBook) {
                const targetBook = msMarkers[ms.id]?.lastOpenedBook || msBooks[0];
                switchMsBook(popupEl, targetBook);
                // Scroll the active tab into view (essential when bar overflows like P46)
                const activeTabEl = popupEl.querySelector('.ms-book-tab.active');
                if (activeTabEl) activeTabEl.scrollIntoView({ inline: 'center', block: 'nearest' });
            }

            // Folio dropdown wiring
            Object.entries(folioGroupMap).forEach(([book, groups]) => {
                const scope = isMultiBook
                    ? popupEl.querySelector(`.ms-book-section[data-book="${book}"]`)
                    : popupEl;
                if (!scope) return;
                const dropdown = scope.querySelector('.ms-folio-dropdown');
                const box      = scope.querySelector('.ms-folio-container');
                if (!dropdown || !box) return;
                const trigger    = dropdown.querySelector('.ms-folio-trigger');
                const triggerTxt = dropdown.querySelector('.ms-folio-trigger-text');
                const panel      = dropdown.querySelector('.ms-folio-panel');

                trigger.addEventListener('click', e => {
                    e.stopPropagation();
                    dropdown.classList.toggle('open');
                });
                panel.querySelectorAll('.ms-folio-option').forEach(opt => {
                    opt.addEventListener('click', () => {
                        const idx = parseInt(opt.dataset.index, 10);
                        panel.querySelectorAll('.ms-folio-option').forEach(o => o.classList.remove('active'));
                        opt.classList.add('active');
                        triggerTxt.textContent = opt.textContent;
                        box.innerHTML = buildVerseHtml(groups[idx]?.lines || []);
                        dropdown.classList.remove('open');

                        // Realign the English translation to the selected folio's verse range
                        const transEl = scope.querySelector('.ms-popup-english');
                        scrollTranslationToVerse(transEl, groups[idx]?.label || '');
                    });
                });
                const popupContainer = scope.closest('.ms-popup') || scope;
                popupContainer.addEventListener('click', e => {
                    if (!dropdown.contains(e.target)) dropdown.classList.remove('open');
                });
            });

            // Writing Stand button
            const wsBtn = popupEl.querySelector('.ms-ws-btn');
            if (wsBtn) {
                wsBtn.addEventListener('click', () => {
                    const currentBook = isMultiBook
                        ? (popupEl.querySelector('.ms-book-tab.active')?.dataset.book || msBooks[0])
                        : (msBooks[0] || null);
                    openWritingStand(ms, currentBook);
                    msPopup.close();
                });
            }
        });
    });
}

// ── WRITING STAND ─────────────────────────────────────────

function openWritingStand(ms, book) {
    wsCurrentMs   = ms;
    wsCurrentBook = book || _msBooks(ms)[0];

    const stand = document.getElementById('writing-stand');
    stand.classList.add('open');

    // Header
    document.getElementById('ws-ms-id').textContent   = ms.label || ms.id || '';
    document.getElementById('ws-ms-name').textContent = ms.name  || '';

    // Metadata footer
    const metaEl = document.getElementById('ws-meta');
    metaEl.innerHTML = [
        ms.date     && `<div class="ws-meta-item"><div class="ws-meta-label">Date</div><div class="ws-meta-value">${ms.date}</div></div>`,
        ms.language && `<div class="ws-meta-item"><div class="ws-meta-label">Language</div><div class="ws-meta-value">${ms.language}</div></div>`,
        ms.found    && `<div class="ws-meta-item"><div class="ws-meta-label">Found</div><div class="ws-meta-value">${ms.found}</div></div>`,
        ms.held     && `<div class="ws-meta-item"><div class="ws-meta-label">Held</div><div class="ws-meta-value">${ms.held}</div></div>`,
    ].filter(Boolean).join('');

    // Book tabs (multi-book only)
    const msBooks    = _msBooks(ms);
    const isMultiBook = msBooks.length > 1 && ms.sections;
    const bookTabsEl = document.getElementById('ws-book-tabs');

    if (isMultiBook) {
        bookTabsEl.innerHTML = msBooks.map(b =>
            `<div class="ws-book-tab${b === wsCurrentBook ? ' active' : ''}" data-book="${b}">${bookLabel(b)}</div>`
        ).join('');
        bookTabsEl.classList.remove('ws-hidden');

        bookTabsEl.querySelectorAll('.ws-book-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                wsCurrentBook = tab.dataset.book;
                bookTabsEl.querySelectorAll('.ws-book-tab')
                          .forEach(t => t.classList.toggle('active', t.dataset.book === wsCurrentBook));
                populateWsContent();
            });
        });
    } else {
        bookTabsEl.classList.add('ws-hidden');
        bookTabsEl.innerHTML = '';
    }

    // Register outside-click listener once (closes folio dropdown)
    if (!stand._wsOutsideClickBound) {
        stand.addEventListener('click', e => {
            const dd = stand.querySelector('.ms-folio-dropdown');
            if (dd && !dd.contains(e.target)) dd.classList.remove('open');
        });
        stand._wsOutsideClickBound = true;
    }

    populateWsContent();
}

function populateWsContent() {
    if (!wsCurrentMs) return;

    const ms          = wsCurrentMs;
    const msBooks     = _msBooks(ms);
    const isMultiBook = msBooks.length > 1 && ms.sections;

    // Source greek + translation for the active book
    const greek = isMultiBook
        ? (ms.sections?.[wsCurrentBook]?.greek || [])
        : (ms.greek || []);
    const translation = isMultiBook
        ? (ms.sections?.[wsCurrentBook]?.translation || [])
        : (ms.translation || []);

    // Build folio groups
    wsFolioGroups = groupByFolio(greek);
    wsFolioIdx    = 0;

    // Folio navigator
    const folioBar = document.getElementById('ws-folio-bar');
    if (wsFolioGroups.length >= 5) {
        const firstLabel = wsFolioGroups[0]?.label || 'Folio 1';
        const opts = wsFolioGroups.map((g, i) =>
            `<div class="ms-folio-option${i === 0 ? ' active' : ''}" data-index="${i}">${g.label || 'Folio ' + (i + 1)}</div>`
        ).join('');
        folioBar.innerHTML = `
            <span class="ws-folio-label">Folio</span>
            <div class="ms-folio-dropdown">
                <button class="ms-folio-trigger" type="button">
                    <span class="ms-folio-trigger-text">${firstLabel}</span>
                    <span class="ms-folio-arrow">▾</span>
                </button>
                <div class="ms-folio-panel">${opts}</div>
            </div>`;
        folioBar.classList.remove('ws-hidden');

        const dropdown   = folioBar.querySelector('.ms-folio-dropdown');
        const trigger    = dropdown.querySelector('.ms-folio-trigger');
        const triggerTxt = dropdown.querySelector('.ms-folio-trigger-text');
        const panel      = dropdown.querySelector('.ms-folio-panel');

        trigger.addEventListener('click', e => {
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        panel.querySelectorAll('.ms-folio-option').forEach(opt => {
            opt.addEventListener('click', () => {
                const idx = parseInt(opt.dataset.index, 10);
                wsFolioIdx = idx;
                panel.querySelectorAll('.ms-folio-option').forEach(o => o.classList.remove('active'));
                opt.classList.add('active');
                triggerTxt.textContent = opt.textContent;
                dropdown.classList.remove('open');
                // Refresh the Greek column
                document.getElementById('ws-greek-scroll').innerHTML =
                    buildVerseHtml(wsFolioGroups[idx]?.lines || []);
                // Realign the English column to the selected folio's verse range
                scrollTranslationToVerse(
                    document.getElementById('ws-english-scroll'),
                    wsFolioGroups[idx]?.label || ''
                );
            });
        });
    } else {
        folioBar.classList.add('ws-hidden');
        folioBar.innerHTML = '<span class="ws-folio-label">Folio</span>';
    }

    // Greek column: first folio (or full text for small manuscripts)
    const greekLines = wsFolioGroups.length >= 5
        ? (wsFolioGroups[0]?.lines || [])
        : greek;
    document.getElementById('ws-greek-scroll').innerHTML = buildVerseHtml(greekLines);

    // English column: full translation (independently scrollable)
    const englishScroll = document.getElementById('ws-english-scroll');
    if (translation && translation.length > 0) {
        englishScroll.innerHTML = buildVerseHtml(translation);
    } else {
        englishScroll.innerHTML = '<em class="ms-no-text" style="color:#2a2a2a;font-style:italic;">No translation available</em>';
    }
}

function closeWritingStand() {
    document.getElementById('writing-stand').classList.remove('open');
    wsCurrentMs = wsCurrentBook = wsFolioGroups = null;
    wsFolioIdx  = 0;
}

// ── LOAD DATA ─────────────────────────────────────────────

// Fetch JSON with retry + backoff. The Flask dev server occasionally drops a
// response body (especially the large /api/manuscripts feed on the very first
// request after a restart), which makes r.json() throw. A couple of quick
// retries lets that transient failure self-heal instead of silently degrading
// the whole app to the inline fallback.
async function fetchJson(url, { retries = 3, delay = 250 } = {}) {
    for (let attempt = 0; ; attempt++) {
        try {
            const r = await fetch(url, { cache: 'no-store' });
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return await r.json();   // throws if the body was truncated
        } catch (err) {
            if (attempt >= retries) throw err;
            console.warn(`fetchJson(${url}) attempt ${attempt + 1} failed: ${err.message} — retrying`);
            await new Promise(res => setTimeout(res, delay * (attempt + 1)));
        }
    }
}

Promise.all([
    fetchJson('/static/data/orbis.json'),
    fetchJson('/static/data/orbis_network.json'),
    fetchJson('/api/manuscripts').catch(() => []),
    fetchJson('/static/data/custom_locations.json').catch(() => [])
])
.then(([data, network, msData, customLocs]) => {
    // Merge custom locations into orbis cities list
    if (customLocs && customLocs.length > 0) {
        data.cities = [...data.cities, ...customLocs];
    }
    // Populate manuscripts from API; fall back to inline data if empty
    if (msData && msData.length > 0) {
        manuscripts = msData.map(applyMsDecode);
    } else {
        manuscripts = _manuscriptsFallback;
    }
    initOrbis(data, network);
})
.catch(err => console.error('Failed to load data:', err));
