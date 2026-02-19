"""
Rhythm pattern generation, humanization, and duration utilities.

All durations are in 'ticks' where 1 beat (quarter note) = 480 ticks.
"""
import random

TICKS_PER_BEAT = 480

# Duration constants (in ticks)
WHOLE     = TICKS_PER_BEAT * 4
HALF      = TICKS_PER_BEAT * 2
QUARTER   = TICKS_PER_BEAT
EIGHTH    = TICKS_PER_BEAT // 2
SIXTEENTH = TICKS_PER_BEAT // 4
DOTTED_Q  = int(TICKS_PER_BEAT * 1.5)
DOTTED_E  = int(TICKS_PER_BEAT * 0.75)
TRIPLET_Q = int(TICKS_PER_BEAT * 2 / 3)

# Pre-built rhythm patterns per complexity level
# Each pattern is a list of (duration, velocity_factor) tuples for one bar (4/4)
RHYTHM_PATTERNS = {
    1: [
        # Simple: whole notes and half notes
        [(WHOLE, 1.0)],
        [(HALF, 1.0), (HALF, 0.85)],
        [(HALF, 1.0), (QUARTER, 0.9), (QUARTER, 0.85)],
    ],
    2: [
        # Quarter note patterns
        [(QUARTER, 1.0), (QUARTER, 0.8), (QUARTER, 0.9), (QUARTER, 0.8)],
        [(HALF, 1.0), (QUARTER, 0.85), (QUARTER, 0.9)],
        [(QUARTER, 1.0), (HALF, 0.85), (QUARTER, 0.9)],
        [(DOTTED_Q, 1.0), (EIGHTH, 0.75), (HALF, 0.9)],
    ],
    3: [
        # Eighth note mixes
        [(QUARTER, 1.0), (EIGHTH, 0.8), (EIGHTH, 0.75),
         (QUARTER, 0.9), (QUARTER, 0.85)],
        [(EIGHTH, 1.0), (EIGHTH, 0.7), (QUARTER, 0.9),
         (EIGHTH, 0.8), (EIGHTH, 0.7), (QUARTER, 0.85)],
        [(DOTTED_Q, 1.0), (EIGHTH, 0.7), (QUARTER, 0.9),
         (EIGHTH, 0.75), (EIGHTH, 0.7)],
    ],
    4: [
        # Syncopated and varied
        [(EIGHTH, 1.0), (DOTTED_Q, 0.85), (EIGHTH, 0.8),
         (EIGHTH, 0.75), (QUARTER, 0.9)],
        [(SIXTEENTH, 0.9), (SIXTEENTH, 0.7), (EIGHTH, 0.85),
         (QUARTER, 1.0), (EIGHTH, 0.8), (EIGHTH, 0.7), (QUARTER, 0.9)],
        [(TRIPLET_Q, 1.0), (TRIPLET_Q, 0.85), (TRIPLET_Q, 0.8),
         (QUARTER, 0.9), (QUARTER, 0.85)],
    ],
    5: [
        # Dense and complex
        [(SIXTEENTH, 1.0), (SIXTEENTH, 0.7), (SIXTEENTH, 0.75), (SIXTEENTH, 0.7),
         (EIGHTH, 0.9), (EIGHTH, 0.8),
         (SIXTEENTH, 0.85), (SIXTEENTH, 0.7), (EIGHTH, 0.8), (QUARTER, 0.9)],
        [(EIGHTH, 1.0), (SIXTEENTH, 0.7), (SIXTEENTH, 0.75),
         (TRIPLET_Q, 0.9), (TRIPLET_Q, 0.85), (TRIPLET_Q, 0.8),
         (EIGHTH, 0.85), (EIGHTH, 0.7)],
        [(SIXTEENTH, 0.9), (SIXTEENTH, 0.7), (SIXTEENTH, 0.75), (SIXTEENTH, 0.7),
         (SIXTEENTH, 0.85), (SIXTEENTH, 0.7), (SIXTEENTH, 0.8), (SIXTEENTH, 0.7),
         (QUARTER, 1.0), (QUARTER, 0.9)],
    ],
}

# Mood-driven rhythm feel adjustments
MOOD_RHYTHM_FEEL = {
    'happy':    {'swing': 0.0,  'staccato': 0.3, 'velocity_boost': 10},
    'sad':      {'swing': 0.0,  'staccato': 0.0, 'velocity_boost': -10},
    'energetic':{'swing': 0.1,  'staccato': 0.6, 'velocity_boost': 15},
    'calm':     {'swing': 0.0,  'staccato': 0.0, 'velocity_boost': -15},
    'dark':     {'swing': 0.0,  'staccato': 0.2, 'velocity_boost': 5},
    'epic':     {'swing': 0.0,  'staccato': 0.1, 'velocity_boost': 20},
    'dreamy':   {'swing': 0.15, 'staccato': 0.0, 'velocity_boost': -5},
}


def get_rhythm_pattern(complexity: int, bars: int = 1) -> list[list[tuple[int, float]]]:
    """
    Return rhythm patterns for the requested number of bars.
    Each bar is a list of (duration_ticks, velocity_factor) tuples.
    """
    level = max(1, min(5, complexity))
    patterns = RHYTHM_PATTERNS[level]
    return [random.choice(patterns) for _ in range(bars)]


def humanize_velocity(base_velocity: int, amount: float = 0.1) -> int:
    """Add random variation to velocity. amount is 0.0-1.0 fraction of range."""
    jitter = int(base_velocity * amount * (random.random() * 2 - 1))
    return max(1, min(127, base_velocity + jitter))


def humanize_timing(duration: int, amount: float = 0.02) -> int:
    """Add slight timing jitter to a duration. amount is fraction of beat."""
    max_jitter = int(TICKS_PER_BEAT * amount)
    jitter = random.randint(-max_jitter, max_jitter)
    return max(1, duration + jitter)


def apply_mood_feel(velocity: int, duration: int, mood: str) -> tuple[int, int]:
    """
    Adjust velocity and duration based on mood feel.
    Returns (adjusted_velocity, note_on_duration).
    """
    feel = MOOD_RHYTHM_FEEL.get(mood, MOOD_RHYTHM_FEEL['happy'])

    # Velocity adjustment
    vel = max(1, min(127, velocity + feel['velocity_boost']))

    # Staccato: shorten note duration
    if feel['staccato'] > 0 and random.random() < feel['staccato']:
        duration = int(duration * 0.6)

    return vel, max(1, duration)


def get_chord_rhythm(complexity: int, bars: int = 1) -> list[int]:
    """
    Simpler rhythm for chord accompaniment.
    Returns list of durations (one chord change per entry).
    """
    if complexity <= 2:
        return [WHOLE] * bars  # one chord per bar
    elif complexity <= 3:
        result = []
        for _ in range(bars):
            result.extend([HALF, HALF])
        return result
    else:
        result = []
        for _ in range(bars):
            if random.random() < 0.4:
                result.extend([HALF, HALF])
            else:
                result.extend([QUARTER] * 4)
        return result
