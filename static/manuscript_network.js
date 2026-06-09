// ═══════════════════════════════════════════════════════════════════════════
//  MANUSCRIPT NETWORKS
//  Traces, for a given NT letter, the ORBIS routes from its COMPOSITION city
//  and its RECIPIENT city out to every find-site where a manuscript of that
//  letter was discovered. Each route is the Fastest route (horse+river+sea)
//  and is drawn with the exact same styling as the route planner, so the
//  lines look identical to a planner query between the same two cities.
//  Reuses script.js globals: networkData, orbisNodeMap, buildCombinedGraph,
//  dijkstra, getPath, geoToCRS, edgeTypeMap, manuscripts, and the route
//  planner's SEL_ROAD_STYLE / SEL_SEA_STYLE / SEL_RIVER_STYLE constants.
// ═══════════════════════════════════════════════════════════════════════════

// ── LETTER CONFIG ─────────────────────────────────────────────────────────────
// compId / recId are ORBIS city ids; *Name are the readable labels shown in the UI.
const MN_LETTERS = [
  { book: 'Romans',          compId: 'corinthus',    compName: 'Corinth',
                             recId:  'roma',         recName:  'Rome' },
  { book: '1 Corinthians',   compId: 'ephesos',      compName: 'Ephesus',
                             recId:  'corinthus',    recName:  'Corinth' },
  { book: '2 Corinthians',   compId: 'thessalonica', compName: 'Macedonia (Thessalonica)',
                             recId:  'corinthus',    recName:  'Corinth' },
  { book: 'Galatians',       compId: 'ephesos',      compName: 'Ephesus',
                             recId:  'ancyra',       recName:  'Galatia (Ancyra)' },
  { book: 'Ephesians',       compId: 'roma',         compName: 'Rome',
                             recId:  'ephesos',      recName:  'Ephesus' },
  { book: 'Philippians',     compId: 'ephesos',      compName: 'Ephesus',
                             recId:  'philippi',     recName:  'Philippi' },
  { book: 'Colossians',      compId: 'ephesos',      compName: 'Ephesus',
                             recId:  'colossae',     recName:  'Colossae' },
  { book: '1 Thessalonians', compId: 'athenai',      compName: 'Athens',
                             recId:  'thessalonica', recName:  'Thessalonica' },
  { book: '2 Thessalonians', compId: 'corinthus',    compName: 'Corinth',
                             recId:  'thessalonica', recName:  'Thessalonica' },
  { book: '1 Timothy',       compId: 'thessalonica', compName: 'Macedonia',
                             recId:  'ephesos',      recName:  'Ephesus' },
  { book: '2 Timothy',       compId: 'roma',         compName: 'Rome',
                             recId:  'ephesos',      recName:  'Ephesus' },
  { book: 'Titus',           compId: 'roma',         compName: 'Rome',
                             recId:  'gortyna',      recName:  'Crete (Gortyna)' },
  { book: 'Philemon',        compId: 'ephesos',      compName: 'Ephesus',
                             recId:  'colossae',     recName:  'Colossae' },
];

// ── STATE ─────────────────────────────────────────────────────────────────────
let _mnLayer = null;   // L.layerGroup holding the route polylines + markers
// The currently displayed letter and its (user-adjustable) parameters.
//   { book, compId, recId, view }   view ∈ 'land' | 'fastest' | 'both'
let _mnState = null;

// Track the find-site density orbs the network switched on (reusing the
// Manuscripts browser's showBookOnMap/hideBookOnMap), so we can turn them off
// again without disturbing any book the user activated in the browser itself.
let _mnOrbBook      = null;
let _mnOrbWasActive = false;

// ── HELPERS ───────────────────────────────────────────────────────────────────

function _mnCoord(nodeId) {
    const n = orbisNodeMap[nodeId];
    return n ? geoToCRS(n.x, n.y) : null;
}

// The city object (with lat/lon/name) for an ORBIS city id.
function _mnCity(cityId) {
    return (orbisData?.cities || []).find(c => c.id === cityId) || null;
}
function _mnCityLatLng(cityId) {
    const c = _mnCity(cityId);
    return c ? geoToCRS(c.lon, c.lat) : null;
}
// Readable name for an ORBIS city id (falls back to the id if not yet loaded).
function _mnCityName(cityId) {
    const c = _mnCity(cityId);
    return c ? c.name : (cityId || '');
}

// Find-sites for a book, mapped to the NEAREST named city — so each route is
// an exact city-to-city query, identical to what the route planner would draw
// (e.g. an Oxyrhynchus find → routes to the city "Oxyrhynchus").
function _mnFindSites(book) {
    const cities = orbisData?.cities || [];
    const byCity = new Map();
    manuscripts.forEach(m => {
        if (!(m.books || []).includes(book)) return;
        if (m.lat == null || m.lon == null) return;
        let best = null, bd = Infinity;
        cities.forEach(c => {
            if (c.lat == null || c.lon == null) return;
            const d = (c.lat - m.lat) ** 2 + (c.lon - m.lon) ** 2;
            if (d < bd) { bd = d; best = c; }
        });
        if (!best) return;
        if (!byCity.has(best.id)) byCity.set(best.id, { cityId: best.id, name: best.name, count: 0 });
        byCity.get(best.id).count++;
    });
    return [...byCity.values()];
}

// Reproduce the route planner's runRoute() node-selection + graph exactly:
//   modes with 'sea'  → use the sea node (better coastal links)
//   modes without sea → use the land node
function _mnPlannerPath(fromCityId, toCityId, modes) {
    const useSea = modes.has('sea');
    const fromId = useSea
        ? (networkData.citySeaNodes?.[fromCityId] ?? networkData.cityNodes?.[fromCityId])
        : networkData.cityNodes?.[fromCityId];
    const toId = useSea
        ? (networkData.citySeaNodes?.[toCityId] ?? networkData.cityNodes?.[toCityId])
        : networkData.cityNodes?.[toCityId];
    if (fromId == null || toId == null) return null;
    const graph = buildCombinedGraph(modes);
    const { prev } = dijkstra(graph, fromId);
    return getPath(prev, fromId, toId);
}

// Draw a node path exactly the way the route planner's drawRoute() does:
// consecutive edges of the same type are batched into one polyline using the
// planner's own SEL_*_STYLE constants, with the junction node shared between
// adjacent segments so there is no gap. This guarantees the network lines are
// visually identical to a planner route between the same two cities.
function _mnDrawPath(path) {
    if (!path || path.length < 2) return;

    const styleOf = (a, b) => {
        const ty = edgeTypeMap[`${a}-${b}`];
        if (ty === 'river')                 return SEL_RIVER_STYLE;
        if (ty === 'coast' || ty === 'sea') return SEL_SEA_STYLE;
        return SEL_ROAD_STYLE;
    };

    const flush = (nodes, style) => {
        const coords = nodes.map(_mnCoord).filter(Boolean);
        if (coords.length > 1) {
            L.polyline(coords, { ...style, className: 'mn-route' }).addTo(_mnLayer);
        }
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

// Show the same red find-site density orbs the Manuscripts browser shows when
// a book is opened — to visualise where this letter's manuscripts were found.
// Records whether the book was already active so we don't switch off orbs the
// user turned on independently in the Manuscripts browser.
function _mnShowOrbs(book) {
    _mnHideOrbs();
    if (typeof showBookOnMap !== 'function') return;
    _mnOrbWasActive = (typeof activeMsBooks !== 'undefined') && activeMsBooks.has(book);
    _mnOrbBook = book;
    showBookOnMap(book);
}
function _mnHideOrbs() {
    if (_mnOrbBook && !_mnOrbWasActive && typeof hideBookOnMap === 'function') {
        hideBookOnMap(_mnOrbBook);
    }
    _mnOrbBook = null;
    _mnOrbWasActive = false;
}

function _mnOriginDot(cityId, kind, label) {
    const c = _mnCityLatLng(cityId);
    if (!c) return null;
    L.circleMarker(c, {
        radius: 6, color: '#1a1208', weight: 1.5,
        fillColor: kind === 'comp' ? '#e0b84e' : '#d4843e',  // comp gold, rec terracotta
        fillOpacity: 1, pane: 'orbPane',
    }).addTo(_mnLayer).bindTooltip(label, { direction: 'top', offset: [0, -6], className: 'city-tooltip' });
    return c;
}

// ── ACTIVATE / RENDER / CLEAR ───────────────────────────────────────────────
// Open a letter: seed the adjustable state from its default cities and draw.
function mnActivateLetter(cfg) {
    if (!networkData || !manuscripts.length) return;
    _mnState = { book: cfg.book, compId: cfg.compId, recId: cfg.recId, view: 'both' };
    _mnShowOrbs(cfg.book);   // red find-site density orbs, as in the Manuscripts browser
    _mnRender(true);
}

// Draw the current state onto the map. Re-run on any change (city or view).
//   fit = true  → frame the map to the routes (on open / city change)
//   fit = false → leave the current view (on a route-view toggle)
function _mnRender(fit) {
    if (!_mnState || !_mnLayer) return;
    _mnLayer.clearLayers();

    const { book, compId, recId, view } = _mnState;
    const sites    = _mnFindSites(book);
    const bounds   = [];
    const showLand = (view === 'land'    || view === 'both');
    const showFast = (view === 'fastest' || view === 'both');

    // For each origin (composition + recipient) → each find-site city, draw the
    // selected route(s), styled identically to the route planner. The foot/river
    // (land) route is drawn first so the fastest route sits on top where they overlap.
    const FAST = new Set(['horse', 'river', 'sea']);
    const FOOT = new Set(['foot', 'river']);
    [recId, compId].forEach(originId => {
        if (!originId) return;
        sites.forEach(s => {
            if (s.cityId === originId) return;  // no self-route
            if (showLand) { const pw = _mnPlannerPath(originId, s.cityId, FOOT); if (pw) _mnDrawPath(pw); }
            if (showFast) { const pf = _mnPlannerPath(originId, s.cityId, FAST); if (pf) _mnDrawPath(pf); }
        });
    });

    // Origin dots (composition + recipient) and find-site dots.
    const cc = compId ? _mnOriginDot(compId, 'comp', `Composition · ${_mnCityName(compId)}`) : null;
    const rc = recId  ? _mnOriginDot(recId,  'rec',  `Recipient · ${_mnCityName(recId)}`)   : null;
    if (cc) bounds.push(cc);
    if (rc) bounds.push(rc);
    sites.forEach(s => {
        const c = _mnCityLatLng(s.cityId);
        if (!c) return;
        bounds.push(c);
        L.circleMarker(c, {
            radius: 5, color: '#1a1208', weight: 1.5,
            fillColor: '#c0533a', fillOpacity: 0.95, pane: 'orbPane',
        }).addTo(_mnLayer).bindTooltip(
            `${s.name} — find-site of ${s.count} ${book} MS${s.count === 1 ? '' : 'S'}`,
            { direction: 'top', offset: [0, -6], className: 'city-tooltip' });
    });

    _mnLayer.addTo(map);
    if (fit && bounds.length > 1) {
        map.fitBounds(L.latLngBounds(bounds).pad(0.2), { maxZoom: 6 });
    }
}

function mnClearRoutes() {
    if (_mnLayer) _mnLayer.clearLayers();
    _mnHideOrbs();
    _mnState = null;
}

// Wire a typable city search box + dropdown (styled like the filters' book
// search). getSelectedId() returns the currently chosen id (to restore the
// label on blur); onSelect(id) is called when the user picks a city.
function _mnWireCityPicker(input, dropdown, getSelectedId, onSelect) {
    const renderList = (q) => {
        const cities = (orbisData?.cities || []).slice()
            .sort((a, b) => a.name.localeCompare(b.name));
        const ql   = (q || '').trim().toLowerCase();
        const hits = (ql
            ? cities.filter(c => c.name.toLowerCase().includes(ql) ||
                                 (c.modern || '').toLowerCase().includes(ql))
            : cities
        ).slice(0, 60);
        if (!hits.length) { dropdown.classList.remove('open'); dropdown.innerHTML = ''; return; }
        dropdown.innerHTML = hits.map(c =>
            `<div class="mn-city-option" data-id="${c.id}">` +
                `<span class="mn-city-opt-name">${c.name}</span>` +
                `<span class="mn-city-opt-modern">${c.modern || ''}</span>` +
            `</div>`
        ).join('');
        dropdown.classList.add('open');
        dropdown.querySelectorAll('.mn-city-option').forEach(opt => {
            // mousedown (not click) so it fires before the input's blur handler.
            opt.addEventListener('mousedown', e => {
                e.preventDefault();
                const id = opt.dataset.id;
                input.value = _mnCityName(id);
                dropdown.classList.remove('open');
                onSelect(id);
            });
        });
    };

    input.addEventListener('focus', () => renderList(input.value));
    input.addEventListener('input', () => renderList(input.value));
    input.addEventListener('keydown', e => {
        if (e.key === 'Escape') { dropdown.classList.remove('open'); input.blur(); }
        if (e.key === 'Enter') {
            const first = dropdown.querySelector('.mn-city-option');
            if (first) {
                const id = first.dataset.id;
                input.value = _mnCityName(id);
                dropdown.classList.remove('open');
                onSelect(id);
            }
        }
    });
    // On blur, close the list and restore the label to the active selection.
    input.addEventListener('blur', () => setTimeout(() => {
        dropdown.classList.remove('open');
        input.value = _mnCityName(getSelectedId());
    }, 120));
}

// ── SIDEBAR MENU ────────────────────────────────────────────────────────────
function mnBuildMenu() {
    const host = document.getElementById('social-networks-section');
    if (!host) return;

    // Route/marker layer (created once, here, where Leaflet `map` is ready).
    if (!_mnLayer) _mnLayer = L.layerGroup();

    const sec = document.createElement('div');
    sec.id = 'manuscript-networks-section';
    sec.innerHTML =
        `<div class="mn-section-header" id="mn-section-toggle">` +
            `<span class="mn-chevron">&#8250;</span>` +
            `<span class="mn-section-title">Manuscript Networks</span>` +
        `</div>` +
        `<div id="mn-section-body">` +
            `<div class="mn-group" id="mn-group-nt">` +
                `<div class="mn-group-header" id="mn-nt-toggle">` +
                    `<span class="mn-chevron2">&#8250;</span>` +
                    `<span class="mn-group-title">New Testament</span>` +
                `</div>` +
                `<div class="mn-group-body">` +
                    MN_LETTERS.map(c =>
                        `<div class="mn-letter" data-book="${c.book}">` +
                            `<button class="mn-letter-name"><span class="mn-letter-chev">&#9656;</span>${c.book}</button>` +
                            `<div class="mn-letter-detail">` +
                                `<div class="mn-field">` +
                                    `<div class="filter-date-label">Composition</div>` +
                                    `<div class="mn-city-wrap">` +
                                        `<input type="text" class="mn-city-input" data-role="comp" placeholder="Search city&hellip;" autocomplete="off" />` +
                                        `<div class="mn-city-dropdown"></div>` +
                                    `</div>` +
                                `</div>` +
                                `<div class="mn-field">` +
                                    `<div class="filter-date-label">Recipient</div>` +
                                    `<div class="mn-city-wrap">` +
                                        `<input type="text" class="mn-city-input" data-role="rec" placeholder="Search city&hellip;" autocomplete="off" />` +
                                        `<div class="mn-city-dropdown"></div>` +
                                    `</div>` +
                                `</div>` +
                                `<div class="mn-field">` +
                                    `<div class="filter-date-label">Route View</div>` +
                                    `<div class="mn-view-toggle">` +
                                        `<div class="mn-view-btn" data-view="land">Land</div>` +
                                        `<div class="mn-view-btn" data-view="fastest">Fastest</div>` +
                                        `<div class="mn-view-btn active" data-view="both">Both</div>` +
                                    `</div>` +
                                `</div>` +
                            `</div>` +
                        `</div>`
                    ).join('') +
                `</div>` +
            `</div>` +
        `</div>`;

    host.insertAdjacentElement('afterend', sec);

    // Section collapse
    document.getElementById('mn-section-toggle').addEventListener('click', () => {
        sec.classList.toggle('open');
    });
    // New Testament group collapse
    document.getElementById('mn-nt-toggle').addEventListener('click', () => {
        document.getElementById('mn-group-nt').classList.toggle('open');
    });
    // Letter activation (one at a time) + adjustable city pickers + route-view toggle
    sec.querySelectorAll('.mn-letter').forEach(el => {
        const cfg       = MN_LETTERS.find(c => c.book === el.dataset.book);
        const isActive  = () => _mnState && _mnState.book === cfg.book;
        const compInput = el.querySelector('.mn-city-input[data-role="comp"]');
        const recInput  = el.querySelector('.mn-city-input[data-role="rec"]');
        const compDd    = el.querySelector('.mn-city-wrap .mn-city-dropdown'); // first wrap = comp
        const recDd     = el.querySelectorAll('.mn-city-wrap .mn-city-dropdown')[1];
        const viewBtns  = el.querySelectorAll('.mn-view-btn');

        // Composition / Recipient searchable pickers — redraw + reframe on change.
        _mnWireCityPicker(compInput, compDd,
            () => _mnState?.compId,
            id => { if (isActive()) { _mnState.compId = id; _mnRender(true); } });
        _mnWireCityPicker(recInput, recDd,
            () => _mnState?.recId,
            id => { if (isActive()) { _mnState.recId = id; _mnRender(true); } });

        // Route-view toggle (Land / Fastest / Both) — redraw without reframing.
        viewBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (!isActive()) return;
                _mnState.view = btn.dataset.view;
                viewBtns.forEach(b => b.classList.toggle('active', b === btn));
                _mnRender(false);
            });
        });

        // Open / close the letter.
        el.querySelector('.mn-letter-name').addEventListener('click', () => {
            const wasOpen = el.classList.contains('open');
            sec.querySelectorAll('.mn-letter.open').forEach(o => o.classList.remove('open'));
            if (wasOpen) {
                mnClearRoutes();
            } else {
                el.classList.add('open');
                mnActivateLetter(cfg);                 // seeds _mnState (view = 'both')
                compInput.value = _mnCityName(cfg.compId);
                recInput.value  = _mnCityName(cfg.recId);
                viewBtns.forEach(b => b.classList.toggle('active', b.dataset.view === 'both'));
            }
        });
    });
}

// ── BOOTSTRAP ─────────────────────────────────────────────────────────────────
setTimeout(mnBuildMenu, 120);
