"""
Music theory: scales, note mappings, and scale-degree chord qualities.
"""

# Chromatic note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Semitone interval patterns for each scale type
SCALE_INTERVALS = {
    'major':            [0, 2, 4, 5, 7, 9, 11],
    'minor':            [0, 2, 3, 5, 7, 8, 10],
    'dorian':           [0, 2, 3, 5, 7, 9, 10],
    'mixolydian':       [0, 2, 4, 5, 7, 9, 10],
    'lydian':           [0, 2, 4, 6, 7, 9, 11],
    'phrygian':         [0, 1, 3, 5, 7, 8, 10],
    'pentatonic_major': [0, 2, 4, 7, 9],
    'pentatonic_minor': [0, 3, 5, 7, 10],
    'blues':            [0, 3, 5, 6, 7, 10],
    'harmonic_minor':   [0, 2, 3, 5, 7, 8, 11],
    'whole_tone':       [0, 2, 4, 6, 8, 10],
}

# Chord quality for each degree of 7-note scales (triads)
# 'maj' = major, 'min' = minor, 'dim' = diminished, 'aug' = augmented
DEGREE_CHORDS = {
    'major':          ['maj', 'min', 'min', 'maj', 'maj', 'min', 'dim'],
    'minor':          ['min', 'dim', 'maj', 'min', 'min', 'maj', 'maj'],
    'dorian':         ['min', 'min', 'maj', 'maj', 'min', 'dim', 'maj'],
    'mixolydian':     ['maj', 'min', 'dim', 'maj', 'min', 'min', 'maj'],
    'lydian':         ['maj', 'maj', 'min', 'dim', 'maj', 'min', 'min'],
    'phrygian':       ['min', 'maj', 'maj', 'min', 'dim', 'min', 'maj'],
    'harmonic_minor': ['min', 'dim', 'aug', 'min', 'maj', 'maj', 'dim'],
}


def note_name_to_midi(name: str, octave: int = 4) -> int:
    """Convert note name + octave to MIDI number. C4 = 60."""
    idx = NOTE_NAMES.index(name.upper())
    return 12 * (octave + 1) + idx


def midi_to_note_name(midi_note: int) -> str:
    """Convert MIDI number to note name + octave string."""
    octave = (midi_note // 12) - 1
    name = NOTE_NAMES[midi_note % 12]
    return f"{name}{octave}"


def build_scale(root: str, scale_type: str, octave_start: int = 3, octave_end: int = 6) -> list[int]:
    """
    Build a list of MIDI note numbers spanning the given octave range
    for the requested root + scale type.
    """
    intervals = SCALE_INTERVALS[scale_type]
    root_offset = NOTE_NAMES.index(root.upper())
    notes = []
    for octave in range(octave_start, octave_end + 1):
        for interval in intervals:
            midi_note = 12 * (octave + 1) + root_offset + interval
            if 0 <= midi_note <= 127:
                notes.append(midi_note)
    return sorted(set(notes))


def get_scale_degree_notes(root: str, scale_type: str, octave: int = 4) -> list[int]:
    """Return the MIDI notes for each degree of the scale in a single octave."""
    intervals = SCALE_INTERVALS[scale_type]
    root_midi = note_name_to_midi(root, octave)
    return [root_midi + i for i in intervals]


def get_chord_quality_for_degree(scale_type: str, degree: int) -> str:
    """
    Return the chord quality (maj/min/dim/aug) for a given scale degree (0-indexed).
    Falls back to 'maj' for scales without degree chord mappings (pentatonic, etc.)
    """
    chords = DEGREE_CHORDS.get(scale_type)
    if chords is None:
        # For scales without full degree mappings, map to parent
        parent_map = {
            'pentatonic_major': 'major',
            'pentatonic_minor': 'minor',
            'blues': 'minor',
            'whole_tone': 'major',
        }
        parent = parent_map.get(scale_type, 'major')
        chords = DEGREE_CHORDS[parent]
    return chords[degree % len(chords)]
