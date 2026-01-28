-- One-time migration script to populate database with default intent patterns
--
-- This script migrates hardcoded intent patterns to the database tables.
-- It is idempotent - running it multiple times will not create duplicates.
--
-- Usage:
--     psql -d your_database -f scripts/migrate_intent_patterns_to_db.sql
--
-- Requirements:
--     - PostgreSQL database must be running and accessible
--     - Database tables must be created (via Alembic migration)
--     - Run with a user that has INSERT permissions

-- Use a transaction for atomicity
BEGIN;

-- ============================================================================
-- Device Control Intents
-- ============================================================================

-- DEVICE_ON
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'device.on',
    'Default pattern for device.on',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'turn on', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'switch on', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'power on', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'off', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'stop', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'disable', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'light', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'lights', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'lamp', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'fan', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'plug', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'device', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on'
ON CONFLICT DO NOTHING;

-- DEVICE_OFF
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'device.off',
    'Default pattern for device.off',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'turn off', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'switch off', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'power off', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'on', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'start', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'enable', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'light', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'lights', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'lamp', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'fan', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'plug', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'device', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off'
ON CONFLICT DO NOTHING;

-- DEVICE_SET
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'device.set',
    'Default pattern for device.set',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'set', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'adjust', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'change', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'temperature', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'thermostat', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'brightness', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'level', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'percent', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, '%', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set'
ON CONFLICT DO NOTHING;

-- DEVICE_OPEN
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'device.open',
    'Default pattern for device.open',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'open', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'raise', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'lift', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'close', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'lower', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'curtain', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'curtains', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'blinds', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'window', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'door', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'cover', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open'
ON CONFLICT DO NOTHING;

-- DEVICE_CLOSE
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'device.close',
    'Default pattern for device.close',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'close', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'lower', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'shut', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'open', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'raise', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'curtain', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'curtains', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'blinds', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'window', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'door', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'cover', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Media Control Intents
-- ============================================================================

-- MEDIA_PLAY
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'media.play',
    'Default pattern for media.play',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'play', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'resume', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'continue', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'stop', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'pause', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'music', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'song', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'playlist', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'media', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'track', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'album', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play'
ON CONFLICT DO NOTHING;

-- MEDIA_STOP
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'media.stop',
    'Default pattern for media.stop',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'stop', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'pause', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'halt', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'play', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'start', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'resume', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'music', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'song', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'playlist', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'media', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'playing', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop'
ON CONFLICT DO NOTHING;

-- MEDIA_NEXT
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'media.next',
    'Default pattern for media.next',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'next', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'skip', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'previous', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'back', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'song', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'track', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'music', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'picture', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'playlist', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'image', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next'
ON CONFLICT DO NOTHING;

-- MEDIA_VOLUME_SET
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'media.volume.set',
    'Default pattern for media.volume.set',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'set', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.volume.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'volume', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.volume.set'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Query Intents
-- ============================================================================

-- DEVICE_QUERY
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'device.query',
    'Default pattern for device.query',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'what is the state', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'check state', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'status', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'device', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'devices', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'light', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'lights', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query'
ON CONFLICT DO NOTHING;

-- DATA_QUERY
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'data.query',
    'Default pattern for data.query',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'list', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'what are', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'which', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'what time', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'current time', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'what is the time', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'devices', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'lights', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'windows', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'all', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'time', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query'
ON CONFLICT DO NOTHING;

-- MEDIA_QUERY
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'media.query',
    'Default pattern for media.query',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'what is playing', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'current song', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'what song', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'music', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'song', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'playlist', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'media', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Scene and Scheduling
-- ============================================================================

-- SCENE_APPLY
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'scene.apply',
    'Default pattern for scene.apply',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'activate scenery', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'apply scenery', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'scenery', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'set scenery', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'scenery', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'mode', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'preset', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply'
ON CONFLICT DO NOTHING;

-- SCHEDULE_SET
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'schedule.set',
    'Default pattern for schedule.set',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'schedule', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'set', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'remind', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'cancel', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'stop', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'delete', 'negative', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'timer', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'alarm', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set'
ON CONFLICT DO NOTHING;

-- SCHEDULE_CANCEL
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'schedule.cancel',
    'Default pattern for schedule.cancel',
    0,
    true,
    NOW(),
    NOW()
) ON CONFLICT (intent_type) DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'cancel', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'stop', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'delete', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, weight, created_at)
SELECT gen_random_uuid(), id, 'remove', 'primary', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'schedule', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'timer', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'reminder', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel'
ON CONFLICT DO NOTHING;

INSERT INTO intent_pattern_hints (id, pattern_id, hint, weight, created_at)
SELECT gen_random_uuid(), id, 'alarm', 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel'
ON CONFLICT DO NOTHING;

COMMIT;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check pattern count
-- SELECT COUNT(*) FROM intent_patterns WHERE enabled = true;

-- Check specific pattern
-- SELECT ip.intent_type,
--        array_agg(DISTINCT ipk.keyword) FILTER (WHERE ipk.keyword_type = 'primary') as primary_keywords,
--        array_agg(DISTINCT ipk.keyword) FILTER (WHERE ipk.keyword_type = 'negative') as negative_keywords,
--        array_agg(DISTINCT iph.hint) as hints
-- FROM intent_patterns ip
-- LEFT JOIN intent_pattern_keywords ipk ON ip.id = ipk.pattern_id
-- LEFT JOIN intent_pattern_hints iph ON ip.id = iph.pattern_id
-- WHERE ip.intent_type = 'device.on'
-- GROUP BY ip.intent_type;
