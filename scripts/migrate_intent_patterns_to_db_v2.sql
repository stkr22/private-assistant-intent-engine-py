-- Migration script v2: Regex-based intent patterns
-- This script removes context hints and uses combined regex patterns for explicit intent matching
-- Context hints have been eliminated in favor of patterns like "set\s+volume" instead of "set" + hint "volume"

BEGIN;

-- Add is_regex column if not exists
ALTER TABLE intent_pattern_keywords
ADD COLUMN IF NOT EXISTS is_regex BOOLEAN DEFAULT FALSE;

-- Clear existing patterns
TRUNCATE TABLE intent_patterns CASCADE;

-- ============================================================================
-- DEVICE CONTROL INTENTS
-- ============================================================================

-- DEVICE.ON - Turn on devices
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'device.on', 'Turn on devices', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'turn\s+on(\s+(the|my))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'switch\s+on', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'power\s+on', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on';

-- Negative keywords
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'off', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'stop', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.on';

-- DEVICE.OFF - Turn off devices
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'device.off', 'Turn off devices', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'turn\s+off(\s+(the|my))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'switch\s+off', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'power\s+off', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off';

-- Negative keywords
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'on', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.off';

-- DEVICE.SET - Set device properties (temperature, brightness, etc.)
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'device.set', 'Set device properties', 10, true, NOW(), NOW());

-- Specific patterns for temperature
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(set|adjust|change)\s+(the\s+)?(temperature|temp|thermostat)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set';

-- Specific patterns for brightness
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(set|adjust|change)\s+(the\s+)?(brightness|level)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.set';

-- Generic fallback patterns
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'set', 'primary', false, 0.8, NOW()
FROM intent_patterns WHERE intent_type = 'device.set';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'adjust', 'primary', false, 0.8, NOW()
FROM intent_patterns WHERE intent_type = 'device.set';

-- DEVICE.OPEN - Open curtains, blinds, doors
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'device.open', 'Open devices', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'open(\s+(the|my))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(raise|lift)(\s+(the|my))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open';

-- Negative keywords
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'close', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'lower', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.open';

-- DEVICE.CLOSE - Close curtains, blinds, doors
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'device.close', 'Close devices', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'close(\s+(the|my))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(lower|shut)(\s+(the|my))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close';

-- Negative keywords
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'open', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'raise', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.close';

-- ============================================================================
-- MEDIA CONTROL INTENTS
-- ============================================================================

-- MEDIA.PLAY - Play media
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'media.play', 'Play media', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'play(\s+(the|my|some))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(resume|continue)(\s+(the|my))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play';

-- Negative keywords
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'stop', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'pause', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'next', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.play';

-- MEDIA.STOP - Stop/pause media
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'media.stop', 'Stop or pause media', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(stop|pause|halt)(\s+(the|my))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop';

-- Negative keywords
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'play', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'resume', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.stop';

-- MEDIA.NEXT - Skip to next track
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'media.next', 'Skip to next track', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(next|skip)(\s+(song|track|music))?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next';

-- Negative keywords
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'previous', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'back', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.next';

-- MEDIA.VOLUME.SET - Set volume (specific pattern to eliminate ambiguity)
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'media.volume.set', 'Set media volume', 15, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(set|change|adjust)\s+(the\s+)?volume', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.volume.set';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'volume\s+(to|at)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.volume.set';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(increase|decrease|raise|lower)\s+(the\s+)?volume', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.volume.set';

-- ============================================================================
-- QUERY INTENTS
-- ============================================================================

-- DEVICE.QUERY - Query device state
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'device.query', 'Query device state', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'what\s+is\s+the\s+state', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'check\s+state', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'status(\s+of)?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'is\s+.+\s+(on|off)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'device.query';

-- DATA.QUERY - Query data (time, lists, etc.)
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'data.query', 'Query data or lists', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'what\s+(time|are|is)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'current\s+time', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'list(\s+all)?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'data.query';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'which', 'primary', false, 0.8, NOW()
FROM intent_patterns WHERE intent_type = 'data.query';

-- MEDIA.QUERY - Query what's playing
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'media.query', 'Query current media', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'what\s+(is\s+)?(playing|song)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'current\s+(song|track|music)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'media.query';

-- ============================================================================
-- SCENE AND SCHEDULING INTENTS
-- ============================================================================

-- SCENE.APPLY - Apply scene/scenery
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'scene.apply', 'Apply scene or mode', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(activate|apply|set)\s+(the\s+)?(scene|scenery|mode)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'scenery', 'primary', false, 0.8, NOW()
FROM intent_patterns WHERE intent_type = 'scene.apply';

-- SCHEDULE.SET - Set schedules, timers, reminders
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'schedule.set', 'Set schedules and timers', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(schedule|set)\s+(a|an|the)?\s+(timer|alarm|reminder)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'remind\s+(me)?', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set';

-- Negative keywords
INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'cancel', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set';

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, 'delete', 'negative', false, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.set';

-- SCHEDULE.CANCEL - Cancel schedules, timers
INSERT INTO intent_patterns (id, intent_type, description, priority, enabled, created_at, updated_at)
VALUES (gen_random_uuid(), 'schedule.cancel', 'Cancel schedules and timers', 10, true, NOW(), NOW());

INSERT INTO intent_pattern_keywords (id, pattern_id, keyword, keyword_type, is_regex, weight, created_at)
SELECT gen_random_uuid(), id, '(cancel|stop|delete|remove)\s+(the\s+)?(schedule|timer|reminder|alarm)', 'primary', true, 1.0, NOW()
FROM intent_patterns WHERE intent_type = 'schedule.cancel';

-- ============================================================================
-- VALIDATION
-- ============================================================================

-- Verify all 15 intent types were inserted
DO $$
DECLARE
    pattern_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO pattern_count FROM intent_patterns;
    IF pattern_count <> 15 THEN
        RAISE EXCEPTION 'Expected 15 intent patterns, found %', pattern_count;
    END IF;
    RAISE NOTICE 'Successfully inserted % intent patterns', pattern_count;
END $$;

COMMIT;
