/**
 * ══════════════════════════════════════════════════════
 * Logs Page Module
 * Hexagonal approach: this script is loaded on-demand
 * and runs a live log stream simulation only when focused.
 * ══════════════════════════════════════════════════════
 */

(function LogsModule() {
    'use strict';

    // ── Ports (Data Adapters) ──────────────────────────────
    
    // Initial static logs matching the picture
    const LogsPort = {
        _initial: [
            { ts: '2023-10-24 14:22:01.452', level: 'ERR', container: 'pasx-app-1', msg: 'Database connection timeout: pool exhausted after 30000ms. Retrying...' },
            { ts: '2023-10-24 14:22:00.912', level: 'WRN', container: 'pasx-api-1', msg: 'High memory usage detected: 89% utilized in container worker-node-4. Threshold: 85%.' },
            { ts: '2023-10-24 14:21:58.231', level: 'INF', container: 'pasx-app-1', msg: 'Health check passed for dependency redis-cache-cluster. Latency: 4ms.' },
            { ts: '2023-10-24 14:21:57.998', level: 'DBG', container: 'pasx-proxy', msg: 'Incoming GET request from 10.42.0.1 - User-Agent: kube-probe/1.24' },
            { ts: '2023-10-24 14:21:56.102', level: 'INF', container: 'pasx-app-1', msg: "Batch 'B-2904' state updated to 'IN_PROGRESS'. Equipment: RE-881 active." },
            { ts: '2023-10-24 14:21:55.452', level: 'ERR', container: 'pasx-api-1', msg: "504 Gateway Timeout: Upstream service 'weighing-engine' did not respond in time." },
            { ts: '2023-10-24 14:21:54.001', level: 'INF', container: 'pasx-auth', msg: "User 'j.doe@sanofi.com' successfully authenticated via LDAP provider." },
            { ts: '2023-10-24 14:21:53.882', level: 'WRN', container: 'pasx-app-2', msg: "Slow query detected: SELECT * FROM audit_logs WHERE timestamp > ... took 850ms." },
            { ts: '2023-10-24 14:21:52.551', level: 'INF', container: 'pasx-app-1', msg: "Syncing 42 records from external ERP system. Status: Started." },
            { ts: '2023-10-24 14:21:50.003', level: 'ERR', container: 'pasx-api-1', msg: "Critical exception: Unhandled promise rejection at main.js:241. 'null is not an object'." }
        ],
        _simulatedMessages: [
            { level: 'INF', container: 'pasx-app-1', msg: 'Processing transaction TX-9921...' },
            { level: 'DBG', container: 'pasx-proxy', msg: 'Router forwarded request to /api/v1/metrics' },
            { level: 'INF', container: 'pasx-auth', msg: 'OAuth token refreshed for session x-21.' },
            { level: 'WRN', container: 'pasx-api-1', msg: 'Latency anomaly detected on endpoint /orders' },
            { level: 'ERR', container: 'pasx-app-2', msg: 'Failed to write to audit stream. Retrying in 5s...' },
            { level: 'INF', container: 'redis', msg: 'Background saving started by pid 102' }
        ],
        
        getInitial() {
            return this._initial;
        },
        
        generateNewLog() {
            const template = this._simulatedMessages[Math.floor(Math.random() * this._simulatedMessages.length)];
            const d = new Date();
            const ts = d.toISOString().replace('T', ' ').substring(0, 23); // format YYYY-MM-DD HH:MM:SS.mmm
            return {
                ts,
                level: template.level,
                container: template.container,
                msg: template.msg + (Math.random() > 0.5 ? ' [ctx: ' + Math.floor(Math.random()*1000) + ']' : '')
            };
        }
    };

    const StatsPort = {
        getData() {
            return {
                totalLogs: "45,234",
                info: "42,890",
                warning: "156",
                error: "23",
                rate: 15,
                lines: "1,247",
                topSources: [
                    { name: "pasx-app-1", sub: "Main application server", count: 8 },
                    { name: "pasx-api-1", sub: "External API Gateway", count: 7 }
                ]
            };
        }
    };

    // ── Application State ─────────────────────────────────
    let isPaused = false;
    let autoScroll = true;
    let currentLogs = [];
    let logStreamTimer = null;

    // ── UI Adapters ───────────────────────────────────────

    function getLevelBadge(level) {
        if (level === 'ERR') return '<span class="log-badge log-err">ERR</span>';
        if (level === 'WRN') return '<span class="log-badge log-wrn">WRN</span>';
        if (level === 'INF') return '<span class="log-badge log-inf">INF</span>';
        if (level === 'DBG') return '<span class="log-badge log-dbg">DBG</span>';
        return `<span class="log-badge">${level}</span>`;
    }

    function renderLogRow(log, prepended = false) {
        const tbody = document.getElementById('log-table-body');
        if (!tbody) return;
        
        const tr = document.createElement('tr');
        if(prepended && !isPaused) tr.classList.add('fade-in-highlight');
        
        tr.innerHTML = `
            <td class="log-ts">${log.ts}</td>
            <td>${getLevelBadge(log.level)}</td>
            <td class="log-container-name">${log.container}</td>
            <td class="log-msg" title="${log.msg}">${log.msg}</td>
        `;
        
        if (prepended) {
            tbody.insertBefore(tr, tbody.firstChild);
            // keep max 50 rows
            if (tbody.children.length > 50) {
                tbody.removeChild(tbody.lastChild);
            }
        } else {
            tbody.appendChild(tr);
        }
    }

    function loadInitialLogs() {
        const tbody = document.getElementById('log-table-body');
        if (!tbody) return;
        tbody.innerHTML = '';
        currentLogs = LogsPort.getInitial();
        currentLogs.forEach(log => renderLogRow(log, false));
    }

    function renderStats() {
        const data = StatsPort.getData();
        document.getElementById('total-logs-count').textContent = data.totalLogs + " Total Logs";
        document.getElementById('stat-info').innerHTML = `<span class="dot-inf"></span> Info: ${data.info}`;
        document.getElementById('stat-wrn').innerHTML = `Warning: ${data.warning}`;
        document.getElementById('stat-err').innerHTML = `<span class="dot-err"></span> Error: ${data.error}`;
        
        document.getElementById('live-rate').textContent = data.rate + " logs/sec";
        document.getElementById('live-lines').textContent = data.lines;

        const sourcesDiv = document.getElementById('top-sources');
        if (sourcesDiv) {
            sourcesDiv.innerHTML = data.topSources.map(s => `
                <div class="source-card">
                    <div class="source-info">
                        <div class="source-name">${s.name}</div>
                        <div class="source-sub">${s.sub}</div>
                    </div>
                    <div class="source-count">${s.count}</div>
                </div>
            `).join('');
        }
    }

    // ── Application Service ───────────────────────────────

    function triggerNewLog() {
        if (isPaused) return;

        // Slight jitter to rate
        const currentRate = 12 + Math.floor(Math.random() * 8);
        document.getElementById('live-rate').textContent = currentRate + " logs/sec";
        
        let currentLines = parseInt(document.getElementById('live-lines').textContent.replace(',', ''));
        currentLines++;
        document.getElementById('live-lines').textContent = currentLines.toLocaleString();

        const newLog = LogsPort.generateNewLog();
        renderLogRow(newLog, true);
    }

    function startLogStream() {
        if (logStreamTimer) return;
        logStreamTimer = setInterval(triggerNewLog, 2000); // 1 virtual tick per 2s for UI readability
    }

    function stopLogStream() {
        if (logStreamTimer) {
            clearInterval(logStreamTimer);
            logStreamTimer = null;
        }
    }

    // ── Interaction Bindings ──────────────────────────────
    
    function togglePause() {
        isPaused = !isPaused;
        const btn = document.getElementById('btn-pause');
        const liveIndicator = document.getElementById('live-indicator');
        
        if (isPaused) {
            btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> RESUME STREAM';
            liveIndicator.classList.add('paused');
            liveIndicator.querySelector('.pulse-dot').style.animation = 'none';
        } else {
            btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg> PAUSE STREAM';
            liveIndicator.classList.remove('paused');
            liveIndicator.querySelector('.pulse-dot').style.animation = 'pulse 2s infinite';
        }
    }

    function initBindings() {
        const pauseBtn = document.getElementById('btn-pause');
        if (pauseBtn) pauseBtn.addEventListener('click', togglePause);

        const autoScrollToggle = document.getElementById('auto-scroll-toggle');
        if (autoScrollToggle) {
            autoScrollToggle.addEventListener('click', () => {
                autoScrollToggle.classList.toggle('on');
                autoScroll = autoScrollToggle.classList.contains('on');
            });
        }
    }

    // ── Boot & Page Visibility ────────────────────────────

    function onVisibilityChange() {
        if (document.visibilityState === 'visible') {
            startLogStream();
        } else {
            stopLogStream();
        }
    }

    document.addEventListener('visibilitychange', onVisibilityChange);

    if (document.visibilityState === 'visible') {
        loadInitialLogs();
        renderStats();
        initBindings();
        startLogStream();
    }

})();
