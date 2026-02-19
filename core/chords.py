"""
Chord voicing generation, progression templates, and substitution logic.
"""
import random
from core.scales import (
    SCALE_INTERVALS, NOTE_NAMES, note_name_to_midi,
    get_chord_quality_for_degree
)

# Interval stacks (semitones from root) for chord types
CHORD_VOICINGS = {
    'maj':   [0, 4, 7],
    'min':   [0, 3, 7],
    'dim':   [0, 3, 6],
    'aug':   [0, 4, 8],
    'maj7':  [0, 4, 7, 11],
    'min7':  [0, 3, 7, 10],
    'dom7':  [0, 4, 7, 10],
    'dim7':  [0, 3, 6, 9],
    'sus2':  [0, 2, 7],
    'sus4':  [0, 5, 7],
}

# Chord progression templates per mood (scale degrees, 0-indexed)
PROGRESSION_TEMPLATES = {
    'happy':    [
        [0, 4, 5, 3],       # I – V – vi – IV
        [0, 3, 4, 4],       # I – IV – V – V
        [0, 4, 3, 5],       # I – V – IV – vi
    ],
    'sad':      [
        [0, 5, 2, 6],       # i – VI – III – VII
        [0, 3, 5, 4],       # i – iv – VI – V
        [0, 2, 3, 4],       # i – III – iv – V
    ],
    'energetic': [
        [0, 4, 3, 5],       # I – V – IV – vi
        [0, 3, 0, 4],       # I – IV – I – V
        [0, 4, 5, 3],       # I – V – vi – IV
    ],
    'calm':     [
        [0, 3, 4, 0],       # I – IV – V – I
        [0, 5, 3, 4],       # I – vi – IV – V
        [0, 2, 3, 0],       # I – iii – IV – I
    ],
    'dark':     [
        [0, 5, 4, 3],       # i – VI – V – iv
        [0, 6, 5, 4],       # i – VII – VI – V
        [0, 3, 6, 4],       # i – iv – VII – V
    ],
    'epic':     [
        [0, 5, 3, 4],       # I – vi – IV – V
        [0, 4, 5, 3],       # I – V – vi – IV
        [5, 3, 0, 4],       # vi – IV – I – V
    ],
    'dreamy':   [
        [0, 2, 5, 3],       # I – iii – vi – IV
        [0, 5, 2, 4],       # I – vi – iii – V
        [3, 0, 5, 2],       # IV – I – vi – iii
    ],
}

# Additional substitution chords for higher complexity
SUBSTITUTION_MAP = {
    'maj': ['maj7', 'sus2'],
    'min': ['min7', 'sus4'],
    'dim': ['dim7'],
    'aug': ['maj7'],
}


def build_chord(root_midi: int, quality: str = 'maj') -> list[int]:
    """Build a chord from a MIDI root note and quality string."""
    intervals = CHORD_VOICINGS.get(quality, CHORD_VOICINGS['maj'])
    return [root_midi + i for i in intervals]


def get_progression(mood: str, scale_type: str, root: str,
                    octave: int = 3, complexity: int = 1, bars: int = 4) -> list[list[int]]:
    """
    Generate a chord progression as a list of chords (each chord = list of MIDI notes).

    Args:
        mood: mood name
        scale_type: scale type name
        root: root note name
        octave: bass octave for chords
        complexity: 1-5
        bars: number of bars to generate chords for

    Returns:
        List of chords, one per bar.
    """
    templates = PROGRESSION_TEMPLATES.get(mood, PROGRESSION_TEMPLATES['happy'])
    template = random.choice(templates)

    intervals = SCALE_INTERVALS[scale_type]
    root_offset = NOTE_NAMES.index(root.upper())
    base_midi = 12 * (octave + 1) + root_offset

    progression = []
    for bar_idx in range(bars):
        degree = template[bar_idx % len(template)]
        scale_degree_idx = degree % len(intervals)
        chord_root = base_midi + intervals[scale_degree_idx]

        quality = get_chord_quality_for_degree(scale_type, scale_degree_idx)

        # At higher complexity, occasionally substitute chord quality
        if complexity >= 3 and random.random() < 0.3 * (complexity - 2) / 3:
            subs = SUBSTITUTION_MAP.get(quality, [quality])
            quality = random.choice(subs)

        chord = build_chord(chord_root, quality)
        progression.append(chord)

    return progression


def arpeggiate_chord(chord: list[int], pattern: str = 'up',
                     steps: int = 4) -> list[int]:
    """
    Turn a chord into an arpeggio pattern.

    Patterns: 'up', 'down', 'updown', 'random'
    """
    if not chord:
        return []

    if pattern == 'up':
        seq = [chord[i % len(chord)] for i in range(steps)]
    elif pattern == 'down':
        rev = list(reversed(chord))
        seq = [rev[i % len(rev)] for i in range(steps)]
    elif pattern == 'updown':
        full = chord + list(reversed(chord[1:-1])) if len(chord) > 2 else chord
        seq = [full[i % len(full)] for i in range(steps)]
    elif pattern == 'random':
        seq = [random.choice(chord) for _ in range(steps)]
    else:
        seq = [chord[i % len(chord)] for i in range(steps)]

    return seq
