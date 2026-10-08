// tertius_badge.js — top-right "Tertius has translated N of M sources" badge.
// Data: GET /api/tertius (static/data/tertius_progress.json, committed by
// tertius.py with every push). Polls once a minute; hides itself on any error.
(function () {
    const badge = document.getElementById('tertius-badge');
    if (!badge) return;
    const fmt = n => Number(n || 0).toLocaleString('en-US');

    function ago(iso) {
        const t = Date.parse(iso);
        if (!t) return '';
        const m = Math.round((Date.now() - t) / 60000);
        if (m < 1) return 'just now';
        if (m < 60) return m + ' min ago';
        const h = Math.round(m / 60);
        if (h < 48) return h + ' h ago';
        return Math.round(h / 24) + ' days ago';
    }

    function render(d) {
        const done = d.translated || 0, total = d.total || 0;
        if (!total) { badge.hidden = true; return; }
        const finished = d.state === 'done' || done >= total;
        badge.querySelectorAll('.tb-n').forEach(el => { el.textContent = fmt(done); });
        badge.querySelectorAll('.tb-m').forEach(el => { el.textContent = fmt(total); });
        if (finished) {
            badge.querySelector('.tb-long').innerHTML =
                '<strong>Tertius</strong> has translated all <span class="tb-n">' +
                fmt(total) + '</span> sources &#x2713;';
        }
        badge.querySelector('.tb-bar span').style.width =
            (total ? Math.min(100, (done / total) * 100) : 0).toFixed(2) + '%';
        badge.classList.toggle('tb-working', d.state === 'translating');
        const pct = total ? ((done / total) * 100).toFixed(1) + '% complete' : '';
        const parts = [pct];
        if (d.state === 'translating' && d.current) parts.push('Currently working on ' + d.current);
        if (d.updated) parts.push('updated ' + ago(d.updated));
        badge.querySelector('.tb-detail').textContent = parts.filter(Boolean).join(' · ');
        badge.title = 'Tertius, our translating agent, works through every manuscript ' +
                      'and renders it line-by-line into English.';
        badge.hidden = false;
    }

    function poll() {
        fetch('/api/tertius', { cache: 'no-store' })
            .then(r => r.ok ? r.json() : Promise.reject(r.status))
            .then(render)
            .catch(() => { badge.hidden = true; });
    }

    badge.addEventListener('click', () => badge.classList.toggle('tb-open'));
    poll();
    setInterval(poll, 60000);
})();
