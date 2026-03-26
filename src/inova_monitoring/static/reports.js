/**
 * ══════════════════════════════════════════════════════
 * Reports Page Module
 * Hexagonal approach: this script is loaded on-demand
 * and only runs its timers/animations when the page has focus.
 * ══════════════════════════════════════════════════════
 */

(function ReportsModule() {
    'use strict';

    // ── Ports (Data Adapters) ──────────────────────────────
    const WeeklyPerformancePort = {
        getData() {
            return {
                avgUptime: (99.82).toFixed(2),
                avgUptimeTrend: "+0.4%",
                successRate: (94.1).toFixed(1),
                successRateTrend: "+2.1%",
                totalBatches: 1248,
                targetBatches: 1200,
                // Bar chart data for 7 days
                performanceTrends: [55, 62, 70, 68, 85, 95, 88]
            };
        }
    };

    const IssuesPort = {
        getData() {
            return [
                { title: 'Sensor Calibration Drift - Area D', events: 12, type: 'critical' },
                { title: 'Unauthorized Override Attempt', events: 4, type: 'warning' },
                { title: 'Low Reagent Levels - Tank 402', events: 2, type: 'info' }
            ];
        }
    };

    // ── Domain Logic & Rendering Adapters ──────────────────

    function renderPerformanceChart() {
        const data = WeeklyPerformancePort.getData().performanceTrends;
        const svg = document.getElementById('perf-trends-svg');
        if (!svg) return;

        const maxVal = Math.max(...data, 100);
        const w = 300, h = 120, pad = 10;
        const barWidth = 16;
        const spacing = (w - pad * 2 - barWidth * data.length) / (data.length - 1);

        let html = '';
        data.forEach((val, i) => {
            const barH = (val / maxVal) * (h - pad * 2);
            const x = pad + i * (barWidth + spacing);
            const y = h - pad - barH;
            
            // Highlight Saturday (index 5)
            const fill = i === 5 ? 'var(--primary-light)' : 'rgba(255, 255, 255, 0.1)';
            
            html += `<rect x="${x}" y="${y}" width="${barWidth}" height="${barH}" fill="${fill}" rx="4" class="fade-in" style="animation-delay: ${i*50}ms"/>`;
        });
        
        svg.innerHTML = html;
    }

    function renderKPIs() {
        const data = WeeklyPerformancePort.getData();
        document.getElementById('avg-uptime').textContent = data.avgUptime + '%';
        document.getElementById('avg-uptime-trend').textContent = data.avgUptimeTrend;
        document.getElementById('success-rate').textContent = data.successRate + '%';
        document.getElementById('success-rate-trend').textContent = data.successRateTrend;
        
        animateValue('total-batches', data.totalBatches);
        document.getElementById('target-batches').textContent = 'Global Site Target: ' + data.targetBatches.toLocaleString();
    }

    function renderIssues() {
        const issues = IssuesPort.getData();
        const container = document.getElementById('top-issues-list');
        if (!container) return;

        container.innerHTML = issues.map(issue => {
            let icon, colorClass;
            if(issue.type === 'critical') {
                icon = '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>';
                colorClass = 'issue-critical';
            } else if(issue.type === 'warning') {
                icon = '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>';
                colorClass = 'issue-warning';
            } else {
                icon = '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>';
                colorClass = 'issue-info';
            }

            return `
                <div class="issue-item fade-in">
                    <div class="issue-icon ${colorClass}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">${icon}</svg>
                    </div>
                    <div class="issue-text">${issue.title}</div>
                    <div class="issue-events">
                        <span class="events-num">${issue.events}</span>
                        <span class="events-label">Events</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    // ── Utilities ─────────────────────────────────────────

    function animateValue(id, target) {
        const el = document.getElementById(id);
        if (!el) return;
        const start = parseInt(el.textContent.replace(/,/g, '')) || 0;
        const range = target - start;
        if (range === 0) return;
        const startTime = performance.now();
        const duration = 600;

        function step(now) {
            const progress = Math.min((now - startTime) / duration, 1);
            const current = Math.round(start + progress * range);
            el.textContent = current.toLocaleString();
            if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    // ── Boot & Page Visibility ────────────────────────────

    function renderAll() {
        renderKPIs();
        renderPerformanceChart();
        renderIssues();
    }

    function onVisibilityChange() {
        if (document.visibilityState === 'visible') {
            renderAll();
        }
    }

    document.addEventListener('visibilitychange', onVisibilityChange);

    if (document.visibilityState === 'visible') {
        renderAll();
    }

})();
