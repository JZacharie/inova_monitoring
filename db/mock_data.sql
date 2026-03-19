-- Mock data for inova-sbx database
-- Table definition
CREATE TABLE IF NOT EXISTS vsessioninfo (
    username      TEXT NOT NULL,
    terminal_id   TEXT NOT NULL,
    logontime     TIMESTAMP WITH TIME ZONE NOT NULL,
    logofftime    TIMESTAMP WITH TIME ZONE
);

-- Insert sample rows covering last 30 days and 7 days
INSERT INTO vsessioninfo (username, terminal_id, logontime, logofftime) VALUES
('alice',   'term-1', NOW() - INTERVAL '1 day', NOW() - INTERVAL '23 hours'),
('bob',     'term-2', NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 day 12 hours'),
('carol',   'term-3', NOW() - INTERVAL '3 days', NULL), -- still active
('dave',    'term-4', NOW() - INTERVAL '5 days', NOW() - INTERVAL '4 days 20 hours'),
('eve',     'term-5', NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days 1 hour'),
('frank',   'term-6', NOW() - INTERVAL '8 days', NOW() - INTERVAL '7 days 22 hours'), -- older than 7 days
('grace',   'term-7', NOW() - INTERVAL '10 minutes', NULL), -- short session
('heidi',   'term-8', NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '13 minutes'), -- short session
('ivan',    'term-9', NOW() - INTERVAL '30 days', NOW() - INTERVAL '29 days 23 hours'); -- edge of 30 days
