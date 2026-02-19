"""
Mood engine: maps mood selections to concrete algorithm parameters.
"""

# Complete mood profiles controlling every aspect of generation
MOOD_PROFILES = {
    'happy': {
        'tempo_range':       (110, 140),
        'base_velocity':     95,
        'velocity_variance': 0.12,
        'preferred_intervals': [0, 2, 4, 5, 7],  # steps on scale (favour consonant jumps)
        'interval_weights':  [3, 5, 4, 3, 2],     # weight for each preferred interval
        'direction_bias':    0.55,  # >0.5 = favour ascending
        'note_density':      0.7,   # 0-1, chance a rhythm slot gets a note (vs rest)
        'octave_range':      (4, 6),
        'leap_probability':  0.15,
        'legato':            0.4,
        'arp_pattern':       'up',
    },
    'sad': {
        'tempo_range':       (60, 85),
        'base_velocity':     70,
        'velocity_variance': 0.08,
        'preferred_intervals': [0, 1, 2, 3, 5],
        'interval_weights':  [2, 5, 4, 4, 2],
        'direction_bias':    0.38,  # favour descending
        'note_density':      0.55,
        'octave_range':      (3, 5),
        'leap_probability':  0.08,
        'legato':            0.8,
        'arp_pattern':       'down',
    },
    'energetic': {
        'tempo_range':       (130, 170),
        'base_velocity':     110,
        'velocity_variance': 0.18,
        'preferred_intervals': [0, 2, 4, 7],
        'interval_weights':  [2, 3, 4, 3],
        'direction_bias':    0.52,
        'note_density':      0.9,
        'octave_range':      (4, 6),
        'leap_probability':  0.25,
        'legato':            0.2,
        'arp_pattern':       'updown',
    },
    'calm': {
        'tempo_range':       (55, 80),
        'base_velocity':     60,
        'velocity_variance': 0.06,
        'preferred_intervals': [0, 2, 4, 7],
        'interval_weights':  [4, 5, 3, 2],
        'direction_bias':    0.50,
        'note_density':      0.45,
        'octave_range':      (3, 5),
        'leap_probability':  0.05,
        'legato':            0.9,
        'arp_pattern':       'up',
    },
    'dark': {
        'tempo_range':       (70, 100),
        'base_velocity':     85,
        'velocity_variance': 0.15,
        'preferred_intervals': [0, 1, 3, 6],
        'interval_weights':  [3, 5, 4, 3],
        'direction_bias':    0.40,
        'note_density':      0.6,
        'octave_range':      (2, 4),
        'leap_probability':  0.2,
        'legato':            0.5,
        'arp_pattern':       'down',
    },
    'epic': {
        'tempo_range':       (90, 130),
        'base_velocity':     105,
        'velocity_variance': 0.2,
        'preferred_intervals': [0, 4, 5, 7],
        'interval_weights':  [2, 4, 3, 5],
        'direction_bias':    0.6,
        'note_density':      0.8,
        'octave_range':      (3, 6),
        'leap_probability':  0.3,
        'legato':            0.3,
        'arp_pattern':       'updown',
    },
    'dreamy': {
        'tempo_range':       (65, 95),
        'base_velocity':     65,
        'velocity_variance': 0.1,
        'preferred_intervals': [0, 2, 4, 5, 7],
        'interval_weights':  [3, 4, 5, 3, 3],
        'direction_bias':    0.5,
        'note_density':      0.5,
        'octave_range':      (4, 6),
        'leap_probability':  0.12,
        'legato':            0.85,
        'arp_pattern':       'random',
    },
}


def get_mood_profile(mood: str) -> dict:
    """Return the full parameter profile for a mood."""
    return MOOD_PROFILES.get(mood, MOOD_PROFILES['happy']).copy()


def suggest_tempo(mood: str) -> int:
    """Return a suggested tempo for the given mood (midpoint of range)."""
    profile = get_mood_profile(mood)
    lo, hi = profile['tempo_range']
    return (lo + hi) // 2
