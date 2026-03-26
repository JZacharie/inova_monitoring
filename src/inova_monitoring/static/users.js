/**
 * ══════════════════════════════════════════════════════
 * User Activity & Profiling — Page Module
 * Hexagonal approach: this script is loaded on-demand
 * and only runs its timers/animations when the page
 * has focus (Page Visibility API).
 * ══════════════════════════════════════════════════════
 */

(function UserActivityModule() {
    'use strict';

    // ── Ports (Data Adapters) ──────────────────────────────
    // Simulated data; in production these would call real APIs.

    const SessionTrendsPort = {
        _baseCurve: [20, 35, 28, 55, 42, 70, 58, 40, 65, 50, 30, 45, 60, 48, 72, 55, 38, 62, 50, 35],
        _baselineCurve: [30, 32, 30, 35, 33, 38, 36, 34, 37, 35, 33, 36, 38, 35, 40, 37, 34, 38, 36, 33],
        getData(period) {
            const jitter = () => Math.floor(Math.random() * 8) - 4;
            const scale = period === '30d' ? 1.4 : period === '7d' ? 1.1 : 1;
            return {
                active: this._baseCurve.map(v => Math.max(5, Math.round(v * scale + jitter()))),
                baseline: this._baselineCurve.map(v => Math.max(5, Math.round(v * scale + jitter()))),
            };
        }
    };

    const TopUsersPort = {
        _users: [
            { name: 'Marcus Vane', hours: 152 },
            { name: 'Elena Rossi', hours: 128 },
            { name: 'Chen Wei', hours: 114 },
            { name: 'Sarah Miller', hours: 98 },
            { name: 'Julian Drax', hours: 84 },
        ],
        getData() {
            return this._users.map(u => ({
                ...u,
                hours: u.hours + Math.floor(Math.random() * 4) - 1,
            }));
        }
    };

    const KPIPort = {
        getData() {
            return {
                peakSessions: 138 + Math.floor(Math.random() * 10),
                avgDuration: (3.8 + Math.random() * 0.8).toFixed(1),
                uniqueUsers: 82 + Math.floor(Math.random() * 8),
                alerts: Math.floor(Math.random() * 6),
            };
        }
    };

    const HeatmapPort = {
        _assets: ['MIX-01', 'FIL-04', 'PAC-12', 'LAB-02'],
        _shifts: ['Shift A', 'Shift B', 'Shift C'],
        getData() {
            return this._shifts.map(shift => ({
                shift,
                values: this._assets.map(() => Math.floor(Math.random() * 18)),
            }));
        }
    };

    const SessionLogPort = {
        _sessions: [
            { user: 'Marcus Vane', initials: 'MV', asset: 'MIX-01 High-Speed', login: '08:14:22', duration: '04h 12m', status: 'active' },
            { user: 'Elena Rossi', initials: 'ER', asset: 'FIL-04 Aseptic', login: '07:55:10', duration: '04h 31m', status: 'active' },
            { user: 'Chen Wei', initials: 'CW', asset: 'PAC-12 Primary', login: '08:02:45', duration: '03h 55m', status: 'active' },
            { user: 'Sarah Miller', initials: 'SM', asset: 'LAB-02 QC', login: '09:10:03', duration: '02h 48m', status: 'active' },
            { user: 'Julian Drax', initials: 'JD', asset: 'MIX-01 High-Speed', login: '10:30:18', duration: '01h 28m', status: 'idle' },
            { user: 'Anika Patel', initials: 'AP', asset: 'FIL-04 Aseptic', login: '11:42:55', duration: '00h 15m', status: 'idle' },
        ],
        getData() {
            return this._sessions;
        }
    };

    // ── Domain Logic (Use Cases) ──────────────────────────

    function buildSVGPath(values, width, height, padding) {
        const maxVal = Math.max(...values, 1);
        const stepX = (width - padding * 2) / (values.length - 1);
        let path = '';
        const points = values.map((v, i) => ({
            x: padding + i * stepX,
            y: padding + (1 - v / maxVal) * (height - padding * 2),
        }));

        // Smooth cubic bezier
        points.forEach((p, i) => {
            if (i === 0) {
                path += `M${p.x},${p.y}`;
            } else {
                const prev = points[i - 1];
                const cpx1 = prev.x + (p.x - prev.x) * 0.4;
                const cpx2 = p.x - (p.x - prev.x) * 0.4;
                path += ` C${cpx1},${prev.y} ${cpx2},${p.y} ${p.x},${p.y}`;
            }
        });
        return path;
    }

    function buildAreaPath(values, width, height, padding) {
        const linePath = buildSVGPath(values, width, height, padding);
        const maxVal = Math.max(...values, 1);
        const stepX = (width - padding * 2) / (values.length - 1);
        const lastX = padding + (values.length - 1) * stepX;
        return `${linePath} L${lastX},${height - padding} L${padding},${height - padding} Z`;
    }

    // ── Rendering Adapters (UI) ───────────────────────────

    let currentPeriod = '24h';

    function renderSessionTrends(period) {
        currentPeriod = period || currentPeriod;
        const data = SessionTrendsPort.getData(currentPeriod);
        const svg = document.getElementById('session-trends-svg');
        if (!svg) return;

        const w = 620, h = 260, pad = 20;
        const activePath = buildSVGPath(data.active, w, h, pad);
        const activeArea = buildAreaPath(data.active, w, h, pad);
        const baselinePath = buildSVGPath(data.baseline, w, h, pad);

        svg.innerHTML = `
            <defs>
                <linearGradient id="activeGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="var(--primary-light)" stop-opacity="0.25"/>
                    <stop offset="100%" stop-color="var(--primary-light)" stop-opacity="0"/>
                </linearGradient>
            </defs>
            <path d="${activeArea}" fill="url(#activeGrad)"/>
            <path d="${activePath}" fill="none" stroke="var(--primary-light)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="${baselinePath}" fill="none" stroke="var(--accent-green)" stroke-width="2" stroke-dasharray="6,5" stroke-linecap="round" opacity="0.7"/>
        `;

        // Update period buttons
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.period === currentPeriod);
        });
    }

    function renderTopUsers() {
        const users = TopUsersPort.getData();
        const container = document.getElementById('top-users-list');
        if (!container) return;

        const maxHours = Math.max(...users.map(u => u.hours));
        container.innerHTML = users.map(u => `
            <div class="leaderboard-item">
                <div class="leaderboard-name">${u.name.toUpperCase()}</div>
                <div class="leaderboard-value">${u.hours}H</div>
                <div class="leaderboard-bar-track">
                    <div class="leaderboard-bar-fill" style="width:${(u.hours / maxHours * 100).toFixed(0)}%"></div>
                </div>
            </div>
        `).join('');
    }

    function renderKPIs() {
        const data = KPIPort.getData();
        animateValue('kpi-peak', data.peakSessions);
        document.getElementById('kpi-duration').textContent = data.avgDuration + 'h';
        animateValue('kpi-users', data.uniqueUsers);
        const alertEl = document.getElementById('kpi-alerts');
        alertEl.textContent = String(data.alerts).padStart(2, '0');
        alertEl.style.color = data.alerts > 2 ? 'var(--accent-red)' : 'var(--accent-green)';
    }

    function renderHeatmap() {
        const data = HeatmapPort.getData();
        const grid = document.getElementById('heatmap-grid');
        if (!grid) return;

        const assets = HeatmapPort._assets;
        let html = '<div class="heatmap-header-row"><div class="heatmap-label"></div>';
        assets.forEach(a => { html += `<div class="heatmap-col-label">${a}</div>`; });
        html += '</div>';

        data.forEach(row => {
            html += `<div class="heatmap-row"><div class="heatmap-label">${row.shift}</div>`;
            row.values.forEach(v => {
                const opacity = Math.min(v / 16, 1);
                const showVal = v > 8;
                html += `<div class="heatmap-cell" style="background:rgba(139,92,246,${(0.15 + opacity * 0.7).toFixed(2)});">${showVal ? v : ''}</div>`;
            });
            html += '</div>';
        });

        grid.innerHTML = html;
    }

    function renderSessionLog() {
        const sessions = SessionLogPort.getData();
        const tbody = document.getElementById('session-log-body');
        if (!tbody) return;

        tbody.innerHTML = sessions.map(s => `
            <tr class="fade-in">
                <td>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div class="session-avatar">${s.initials}</div>
                        <span style="font-weight:600;">${s.user}</span>
                    </div>
                </td>
                <td>${s.asset}</td>
                <td><span class="login-time">${s.login}</span></td>
                <td>${s.duration}</td>
                <td><span class="status-badge status-${s.status}">${s.status === 'active' ? 'ACTIVE' : 'IDLE'}</span></td>
            </tr>
        `).join('');
    }

    // ── Utilities ─────────────────────────────────────────

    function animateValue(id, target) {
        const el = document.getElementById(id);
        if (!el) return;
        const start = parseInt(el.textContent) || 0;
        const range = target - start;
        if (range === 0) return;
        const startTime = performance.now();
        const duration = 600;

        function step(now) {
            const progress = Math.min((now - startTime) / duration, 1);
            el.textContent = Math.round(start + progress * range);
            if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    // ── Application Service (Orchestrator) ────────────────

    let refreshTimer = null;

    function renderAll() {
        renderSessionTrends();
        renderTopUsers();
        renderKPIs();
        renderHeatmap();
        renderSessionLog();
    }

    function startLiveRefresh() {
        if (refreshTimer) return;
        refreshTimer = setInterval(() => {
            renderSessionTrends();
            renderTopUsers();
            renderKPIs();
        }, 8000);
    }

    function stopLiveRefresh() {
        if (refreshTimer) {
            clearInterval(refreshTimer);
            refreshTimer = null;
        }
    }

    // ── Page Visibility Gate ───────────────────────────────
    // Only run timers/animations when the page is focused.

    function onVisibilityChange() {
        if (document.visibilityState === 'visible') {
            renderAll();
            startLiveRefresh();
        } else {
            stopLiveRefresh();
        }
    }

    document.addEventListener('visibilitychange', onVisibilityChange);

    // ── Boot ──────────────────────────────────────────────

    // Period selector buttons
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            renderSessionTrends(btn.dataset.period);
        });
    });

    // Initial render (only if page is visible)
    if (document.visibilityState === 'visible') {
        renderAll();
        startLiveRefresh();
    }

})();
