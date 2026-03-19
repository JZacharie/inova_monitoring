-- ---------------------------------------------------------------------------
-- Advanced Analytics Materialized Views for Inova Monitoring
-- ---------------------------------------------------------------------------

-- 1. Daily unique users (last 30 days)
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_unique_users AS
SELECT 
    DATE_TRUNC('day', logontime) AS day,
    COUNT(DISTINCT username)     AS unique_users
FROM vsessioninfo
WHERE logontime >= NOW() - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1;

-- 2. Session duration distribution (p50/p95) - last 7 days
CREATE MATERIALIZED VIEW IF NOT EXISTS session_duration_stats AS
SELECT
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY (COALESCE(logofftime, NOW()) - logontime)) AS p50_duration,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY (COALESCE(logofftime, NOW()) - logontime)) AS p95_duration
FROM vsessioninfo
WHERE logontime >= NOW() - INTERVAL '7 days';

-- 3. Top 10 long-running sessions (last 7 days)
CREATE MATERIALIZED VIEW IF NOT EXISTS top_long_sessions AS
SELECT 
    username, 
    terminal_id, 
    logontime,
    COALESCE(logofftime, NOW()) AS logofftime,
    COALESCE(logofftime, NOW()) - logontime AS duration
FROM vsessioninfo
WHERE logontime >= NOW() - INTERVAL '7 days'
ORDER BY duration DESC
LIMIT 10;

-- 4. Frequent short sessions (last 7 days) - Reconnect loops indicator
CREATE MATERIALIZED VIEW IF NOT EXISTS reconnect_loops AS
SELECT 
    username,
    COUNT(*) FILTER (WHERE COALESCE(logofftime, NOW()) - logontime < INTERVAL '2 minutes') AS short_sessions,
    COUNT(*) AS total_sessions
FROM vsessioninfo
WHERE logontime >= NOW() - INTERVAL '7 days'
GROUP BY username
HAVING COUNT(*) FILTER (WHERE COALESCE(logofftime, NOW()) - logontime < INTERVAL '2 minutes') >= 5
ORDER BY short_sessions DESC;

-- ---------------------------------------------------------------------------
-- Refresh Indexes (to allow CONCURRENT refresh)
-- ---------------------------------------------------------------------------
CREATE UNIQUE INDEX IF NOT EXISTS idx_duu_day ON daily_unique_users(day);
-- session_duration_stats only has one row, so no unique index needed for concurrent refresh if we just rebuild it
-- top_long_sessions doesn't have a stable unique key easily, we'll refresh it normally
CREATE UNIQUE INDEX IF NOT EXISTS idx_rl_user ON reconnect_loops(username);

-- ---------------------------------------------------------------------------
-- Refresh Function
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_unique_users;
    REFRESH MATERIALIZED VIEW session_duration_stats; -- Small enough to refresh without concurrently
    REFRESH MATERIALIZED VIEW top_long_sessions;      -- Small enough
    REFRESH MATERIALIZED VIEW CONCURRENTLY reconnect_loops;
END;
$$ LANGUAGE plpgsql;
