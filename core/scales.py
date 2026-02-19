# Music theory: scales and note conversion.

NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

INTERVALS = {
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

DEGREE_CHORDS = {
    'major':          ['maj', 'min', 'min', 'maj', 'maj', 'min', 'dim'],
    'minor':          ['min', 'dim', 'maj', 'min', 'min', 'maj', 'maj'],
    'dorian':         ['min', 'min', 'maj', 'maj', 'min', 'dim', 'maj'],
    'mixolydian':     ['maj', 'min', 'dim', 'maj', 'min', 'min', 'maj'],
    'lydian':         ['maj', 'maj', 'min', 'dim', 'maj', 'min', 'min'],
    'phrygian':       ['min', 'maj', 'maj', 'min', 'dim', 'min', 'maj'],
    'harmonic_minor': ['min', 'dim', 'aug', 'min', 'maj', 'maj', 'dim'],
}

def name_to_midi(name: str, oct: int = 4) -> int:
    # Convert note name to MIDI number.
    return 12 * (oct + 1) + NOTES.index(name.upper())

def midi_to_name(midi: int) -> str:
    # Convert MIDI number to name.
    return f"{NOTES[midi % 12]}{(midi // 12) - 1}"

def get_scale(root: str, type: str, start: int = 3, end: int = 6) -> list[int]:
    # Build MIDI notes for scale.
    ivs = INTERVALS[type]
    off = NOTES.index(root.upper())
    res = []
    for o in range(start, end + 1):
        for i in ivs:
            m = 12 * (o + 1) + off + i
            if 0 <= m <= 127: res.append(m)
    return sorted(set(res))

def get_degree_notes(root: str, type: str, oct: int = 4) -> list[int]:
    # Scale notes in one octave.
    ivs = INTERVALS[type]
    base = name_to_midi(root, oct)
    return [base + i for i in ivs]

def get_quality(type: str, deg: int) -> str:
    # Chord quality for degree.
    chords = DEGREE_CHORDS.get(type)
    if not chords:
        parent = {'pentatonic_major':'major','pentatonic_minor':'minor','blues':'minor','whole_tone':'major'}.get(type, 'major')
        chords = DEGREE_CHORDS[parent]
    return chords[deg % len(chords)]
